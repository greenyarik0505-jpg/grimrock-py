import math
import pygame
from config import *

class Player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        
        # Характеристики
        self.health = PLAYER_HEALTH
        self.mana = PLAYER_MANA
        self.max_health = PLAYER_HEALTH
        self.max_mana = PLAYER_MANA
        
        # Инвентарь
        self.keys = 0
        self.potions = 0
        
        # Плавное движение и повороты (интерполяция)
        self.start_x = x
        self.start_y = y
        self.target_x = x
        self.target_y = y
        self.moving = False
        self.move_direction = (0, 0) # (dx, dy) на сетке
        self.move_start_time = 0
        self.move_duration = 200 # мс
        
        self.start_angle = angle
        self.target_angle = angle
        self.turning = False
        self.turn_start_time = 0
        self.turn_duration = 150 # мс
        
        # Анимация оружия (меч)
        self.weapon_state = 0 # 0 - покой, 1 - замах, 2 - удар, 3 - возврат
        self.weapon_anim_time = 0
        self.weapon_cooldown = 0
        
        # Стрейф (боковое движение)
        self.strafe_direction = 0 # -1 лево, 1 право, 0 нет
        
        # Покачивание камеры при движении (Head bobbing)
        self.bob_angle = 0
        self.bob_y = 0

    @property
    def tile_pos(self):
        return int(self.x), int(self.y)

    def take_damage(self, damage, game_log):
        self.health -= damage
        game_log.add_message(f"Вы получили {damage} урона!", RED)
        if self.health < 0:
            self.health = 0

    def heal(self, amount, game_log):
        if self.health >= self.max_health:
            game_log.add_message("Здоровье уже полно!", WHITE)
            return False
        self.health = min(self.max_health, self.health + amount)
        game_log.add_message(f"Вы восстановили {amount} здоровья!", GREEN)
        return True

    def restore_mana(self, amount, game_log):
        if self.mana >= self.max_mana:
            return False
        self.mana = min(self.max_mana, self.mana + amount)
        game_log.add_message(f"Восстановлено {amount} маны!", BLUE)
        return True

    def attack(self, current_time, enemies, game_log):
        if self.weapon_state == 0 and current_time >= self.weapon_cooldown:
            self.weapon_state = 1
            self.weapon_anim_time = current_time
            self.weapon_cooldown = current_time + SWORD_COOLDOWN
            
            # Логика нанесения урона мечом (в клетке прямо перед игроком)
            dx = round(math.cos(self.angle))
            dy = round(math.sin(self.angle))
            target_tile_x = int(self.x) + dx
            target_tile_y = int(self.y) + dy
            
            # Проверяем, есть ли враг в этой клетке
            hit_any = False
            for enemy in enemies:
                if enemy.alive and int(enemy.x) == target_tile_x and int(enemy.y) == target_tile_y:
                    enemy.take_damage(SWORD_DAMAGE, game_log)
                    hit_any = True
                    break
            
            if hit_any:
                game_log.add_message("Удар мечом! Попадание!", YELLOW)
            else:
                game_log.add_message("Взмах мечом в пустоту...", GRAY)
            return True
        return False

    def cast_fireball(self, current_time, game_log, entities_list):
        if self.mana < FIREBALL_MANA_COST:
            game_log.add_message("Недостаточно маны!", PURPLE)
            return False
            
        if current_time >= self.weapon_cooldown: # Общий кулдаун на атаку
            self.mana -= FIREBALL_MANA_COST
            self.weapon_cooldown = current_time + FIREBALL_COOLDOWN
            game_log.add_message("Огненный шар запущен!", ORANGE)
            
            # Создаем снаряд
            from entities import Projectile
            # Спавним чуть впереди игрока
            proj_x = self.x + math.cos(self.angle) * 0.4
            proj_y = self.y + math.sin(self.angle) * 0.4
            proj = Projectile(proj_x, proj_y, self.angle, FIREBALL_DAMAGE)
            entities_list.append(proj)
            return True
        return False

    def start_move(self, dx, dy, game_map, current_time):
        if self.moving or self.turning:
            return
            
        # dx, dy - смещение относительно игрока на основе угла взгляда
        # Определяем мировые координаты целевой клетки
        # Направление взгляда округляем до ровных углов
        angle_rounded = round(self.angle / (math.pi / 2)) * (math.pi / 2)
        
        # Направление вперед
        fwd_x = round(math.cos(angle_rounded))
        fwd_y = round(math.sin(angle_rounded))
        
        # Направление вправо
        right_x = round(math.cos(angle_rounded + math.pi / 2))
        right_y = round(math.sin(angle_rounded + math.pi / 2))
        
        # Итоговое мировое смещение
        world_dx = fwd_x * dx + right_x * dy
        world_dy = fwd_y * dx + right_y * dy
        
        target_grid_x = int(self.x) + world_dx
        target_grid_y = int(self.y) + world_dy
        
        # Проверяем коллизии
        if not game_map.is_blocking(target_grid_x, target_grid_y):
            self.start_x = self.x
            self.start_y = self.y
            self.target_x = target_grid_x + 0.5 # Центр клетки
            self.target_y = target_grid_y + 0.5
            self.moving = True
            self.move_start_time = current_time
            self.move_direction = (world_dx, world_dy)
        else:
            # Дверь закрыта? Попробуем подсказать
            tile = game_map.get_tile(target_grid_x, target_grid_y)
            if tile == 'D':
                pass # Сообщение о двери выведется при взаимодействии на кнопку E
            elif tile == 'K':
                pass

    def start_turn(self, direction, current_time):
        if self.moving or self.turning:
            return
            
        self.start_angle = self.angle
        # direction: -1 (влево), 1 (вправо)
        self.target_angle = self.angle + direction * (math.pi / 2)
        self.turning = True
        self.turn_start_time = current_time

    def interact(self, game_map, game_log):
        if self.moving or self.turning:
            return None
            
        # Определяем клетку перед лицом игрока
        angle_rounded = round(self.angle / (math.pi / 2)) * (math.pi / 2)
        dx = round(math.cos(angle_rounded))
        dy = round(math.sin(angle_rounded))
        
        target_x = int(self.x) + dx
        target_y = int(self.y) + dy
        
        tile = game_map.get_tile(target_x, target_y)
        
        if tile == 'D':
            # Открываем обычную деревянную дверь
            game_map.set_tile(target_x, target_y, '.')
            game_log.add_message("Door opened.", WHITE)
            return "DOOR_OPENED"
        elif tile == 'K':
            # Проверяем ключ для запертой двери
            if self.keys > 0:
                self.keys -= 1
                game_map.set_tile(target_x, target_y, '.')
                game_log.add_message("Locked door opened with key!", YELLOW)
                return "DOOR_OPENED"
            else:
                game_log.add_message("Door is locked! Need a Gold Key.", RED)
        elif tile == 'E':
            # Лестница вниз
            game_log.add_message("You descend the stairs...", GREEN)
            return "NEXT_LEVEL"
        else:
            game_log.add_message("Nothing interesting here.", GRAY)
        return None

    def update(self, current_time):
        # 1. Обновление плавного движения
        if self.moving:
            t = (current_time - self.move_start_time) / self.move_duration
            if t >= 1.0:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
                self.bob_y = 0
            else:
                self.x = self.start_x + (self.target_x - self.start_x) * t
                self.y = self.start_y + (self.target_y - self.start_y) * t
                # Эффект покачивания головы при ходьбе
                self.bob_angle += 0.3
                self.bob_y = math.sin(self.bob_angle) * 8
        
        # 2. Обновление плавного поворота
        if self.turning:
            t = (current_time - self.turn_start_time) / self.turn_duration
            if t >= 1.0:
                self.angle = self.target_angle % (2 * math.pi)
                self.turning = False
            else:
                self.angle = self.start_angle + (self.target_angle - self.start_angle) * t
                
        # 3. Обновление анимации оружия
        if self.weapon_state > 0:
            elapsed = current_time - self.weapon_anim_time
            # 4 кадра анимации, на каждый отводим по 75 мс
            frame_duration = SWORD_COOLDOWN // 4
            self.weapon_state = 1 + int(elapsed // frame_duration)
            if self.weapon_state > 3:
                self.weapon_state = 0
