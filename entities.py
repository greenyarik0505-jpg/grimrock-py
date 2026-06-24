import math
import pygame
from config import *

class Entity:
    def __init__(self, x, y, sprite_key, type_name):
        self.x = x
        self.y = y
        self.sprite_key = sprite_key
        self.type = type_name
        self.alive = True

    @property
    def pos(self):
        return self.x, self.y

class Pickup(Entity):
    def __init__(self, x, y, subtype):
        # subtype: 'key' или 'potion'
        # sprite_key совпадает с subtype для текстур
        super().__init__(x, y, subtype, 'pickup')
        self.subtype = subtype  # Храним подтип отдельно от type
        
    def collect(self, player, game_log):
        if self.subtype == 'key':
            player.keys += 1
            game_log.add_message("Вы нашли Золотой Ключ!", YELLOW)
        elif self.subtype == 'potion':
            player.potions += 1
            game_log.add_message("Вы нашли Зелье Здоровья!", GREEN)
        self.alive = False

class Projectile(Entity):
    def __init__(self, x, y, angle, damage):
        super().__init__(x, y, 'fireball', 'projectile')
        self.angle = angle
        self.speed = 0.15
        self.damage = damage
        self.radius = 0.2
        
    def update(self, game_map, enemies, game_log):
        if not self.alive:
            return
            
        # Движение снаряда
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Проверка столкновения со стенами
        if game_map.is_blocking(int(self.x), int(self.y)):
            self.alive = False
            return
            
        # Проверка столкновения с врагами
        for enemy in enemies:
            if enemy.alive and enemy.type == 'enemy':
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < 0.4: # Радиус коллизии врага
                    enemy.take_damage(self.damage, game_log)
                    self.alive = False
                    break

class Enemy(Entity):
    def __init__(self, x, y, enemy_type='skeleton'):
        super().__init__(x, y, f'{enemy_type}_0', 'enemy')
        self.enemy_type = enemy_type
        self.health = 50
        self.max_health = 50
        self.speed = ENEMY_SPEED
        self.damage = ENEMY_DAMAGE
        self.attack_cooldown = 0
        self.sight_distance = 6.0
        self.chasing = False
        self.dropped = False  # Флаг дропа при смерти
        
        # Анимация атаки
        self.attack_anim_duration = 300 # мс
        self.attack_start_time = 0
        self.is_attacking = False

    def take_damage(self, amount, game_log):
        if not self.alive:
            return
        self.health -= amount
        game_log.add_message(f"Скелет ранен на {amount} урона! ({self.health}/{self.max_health})", WHITE)
        self.chasing = True # Всегда агрится при получении урона
        
        if self.health <= 0:
            self.health = 0
            self.alive = False
            game_log.add_message("Скелет рассыпался в прах!", GREEN)

    def check_line_of_sight(self, player_x, player_y, game_map):
        # Простой алгоритм проверки видимости луча (Raycasting для ИИ)
        x0, y0 = self.x, self.y
        x1, y1 = player_x, player_y
        
        dist = math.hypot(x1 - x0, y1 - y0)
        
        steps = int(dist * 4)
        if steps == 0:
            return True
            
        step_x = (x1 - x0) / steps
        step_y = (y1 - y0) / steps
        
        cx, cy = x0, y0
        for _ in range(steps):
            cx += step_x
            cy += step_y
            if game_map.is_blocking(int(cx), int(cy)):
                return False
        return True

    def update(self, player, game_map, current_time, game_log, entities_list):
        if not self.alive:
            return
            
        dist = math.hypot(player.x - self.x, player.y - self.y)
        
        # 1. Проверяем анимацию атаки
        if self.is_attacking:
            if current_time - self.attack_start_time >= self.attack_anim_duration:
                self.is_attacking = False
                self.sprite_key = f'{self.enemy_type}_0'
        
        # 2. ИИ Логика поиска игрока
        if dist < self.sight_distance:
            if self.check_line_of_sight(player.x, player.y, game_map):
                self.chasing = True
        else:
            if not self.chasing:
                pass  # Если уже преследует (aggro), не сбрасываем
            
        if self.chasing:
            # 3. Атака игрока
            if dist < 0.8: # Дистанция атаки
                if current_time >= self.attack_cooldown:
                    self.attack_cooldown = current_time + ENEMY_ATTACK_COOLDOWN
                    self.is_attacking = True
                    self.attack_start_time = current_time
                    self.sprite_key = f'{self.enemy_type}_1'
                    player.take_damage(self.damage, game_log)
            else:
                # 4. Движение к игроку с обходом стен
                if dist > 0:
                    dir_x = (player.x - self.x) / dist
                    dir_y = (player.y - self.y) / dist
                    
                    # Пытаемся двигаться по X
                    new_x = self.x + dir_x * self.speed
                    # Коллизия по X (проверяем границы с небольшим запасом-радиусом)
                    radius = 0.25
                    check_x = new_x + (radius if dir_x > 0 else -radius)
                    if not game_map.is_blocking(int(check_x), int(self.y)):
                        self.x = new_x
                        
                    # Пытаемся двигаться по Y
                    new_y = self.y + dir_y * self.speed
                    check_y = new_y + (radius if dir_y > 0 else -radius)
                    if not game_map.is_blocking(int(self.x), int(check_y)):
                        self.y = new_y
