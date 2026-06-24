import math
import pygame
import random
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
        self.scale_factor = 0.25 # Предметы на полу должны быть маленькими
        
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
        self.scale_factor = 0.35 # Фаерболы среднего размера
        
    def spawn_trail_particle(self, entities_list):
        # Спавним искру огня позади снаряда
        import random
        entities_list.append(Particle(
            self.x - math.cos(self.angle) * 0.2,
            self.y - math.sin(self.angle) * 0.2,
            random.uniform(-0.015, 0.015),
            random.uniform(-0.015, 0.015),
            random.randint(150, 300),
            'particle_fire',
            scale_factor=random.uniform(0.04, 0.07)
        ))

    def explode(self, entities_list):
        # Спавним вспышку из 12 частиц
        import random
        for _ in range(12):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.01, 0.04)
            dx = math.cos(ang) * spd
            dy = math.sin(ang) * spd
            entities_list.append(Particle(
                self.x, self.y, dx, dy,
                random.randint(300, 600),
                'particle_fire',
                scale_factor=random.uniform(0.05, 0.09)
            ))

    def update(self, game_map, enemies, game_log, entities_list):
        if not self.alive:
            return
            
        # Движение снаряда
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Спавн огненного шлейфа
        self.spawn_trail_particle(entities_list)
        
        # Проверка столкновения со стенами
        if game_map.is_blocking(int(self.x), int(self.y)):
            self.alive = False
            self.explode(entities_list)
            return
            
        # Проверка столкновения с врагами
        for enemy in enemies:
            if enemy.alive and enemy.type == 'enemy':
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < 0.4: # Радиус коллизии врага
                    enemy.take_damage(self.damage, game_log)
                    # Спавн крови скелета (пыль/осколки)
                    import random
                    for _ in range(6):
                        entities_list.append(Particle(
                            self.x, self.y,
                            random.uniform(-0.03, 0.03),
                            random.uniform(-0.03, 0.03),
                            random.randint(200, 400),
                            'particle_dust',
                            scale_factor=random.uniform(0.03, 0.06)
                        ))
                    self.alive = False
                    self.explode(entities_list)
                    break

class Particle(Entity):
    def __init__(self, x, y, dx, dy, life_ms, sprite_key, scale_factor=0.08):
        super().__init__(x, y, sprite_key, 'particle')
        self.dx = dx
        self.dy = dy
        self.max_life = life_ms
        self.life = life_ms
        self.scale_factor = scale_factor
        self.spawn_time = pygame.time.get_ticks()
        
    def update(self, current_time):
        elapsed = current_time - self.spawn_time
        self.life = self.max_life - elapsed
        if self.life <= 0:
            self.alive = False
            return
            
        self.x += self.dx
        self.y += self.dy

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
                # 4. Движение к игроку с обходом стен и других врагов
                if dist > 0.7:
                    # Направление к игроку
                    dir_x = (player.x - self.x) / dist
                    dir_y = (player.y - self.y) / dist
                    
                    # Разведение скелетов (Separation)
                    sep_x = 0
                    sep_y = 0
                    for other in entities_list:
                        if other != self and other.type == 'enemy' and other.alive:
                            other_dist = math.hypot(other.x - self.x, other.y - self.y)
                            if other_dist < 0.6:
                                # Сила отталкивания обратно пропорциональна расстоянию
                                if other_dist > 0.01:
                                    sep_x += (self.x - other.x) / other_dist * 0.12
                                    sep_y += (self.y - other.y) / other_dist * 0.12
                                else:
                                    sep_x += random.uniform(-0.08, 0.08)
                                    sep_y += random.uniform(-0.08, 0.08)
                                    
                    dir_x += sep_x
                    dir_y += sep_y
                    
                    # Нормализуем вектор направления движения
                    move_len = math.hypot(dir_x, dir_y)
                    if move_len > 0:
                        dir_x /= move_len
                        dir_y /= move_len
                    
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
