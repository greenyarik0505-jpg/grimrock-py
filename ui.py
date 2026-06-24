import pygame
import math
from config import *

class GameLog:
    def __init__(self):
        self.messages = []  # Список кортежей (text, color)
        
    def add_message(self, text, color=WHITE):
        self.messages.append((text, color))
        # Ограничиваем лог последними 40 сообщениями
        if len(self.messages) > 40:
            self.messages.pop(0)

    def get_last_messages(self, count=4):
        return self.messages[-count:]

def draw_hud(screen, player, game_map, game_log, textures, show_full_map):
    # 1. Заливка фона HUD
    hud_rect = pygame.Rect(0, VIEW_HEIGHT, WIDTH, HUD_HEIGHT)
    pygame.draw.rect(screen, HUD_BG, hud_rect)
    # Верхняя граница-рамка
    pygame.draw.line(screen, HUD_BORDER, (0, VIEW_HEIGHT), (WIDTH, VIEW_HEIGHT), 4)
    pygame.draw.rect(screen, HUD_BORDER, hud_rect, 4)

    # Инициализация шрифтов
    try:
        font = pygame.font.SysFont('Consolas', 18, bold=True)
        small_font = pygame.font.SysFont('Consolas', 14)
    except:
        font = pygame.font.Font(None, 20)
        small_font = pygame.font.Font(None, 16)

    # 2. Отрисовка баров Здоровья (HP) и Маны (MP)
    bar_width = 180
    bar_height = 20
    
    # Здоровье
    hp_x, hp_y = 25, VIEW_HEIGHT + 25
    pygame.draw.rect(screen, (50, 0, 0), (hp_x, hp_y, bar_width, bar_height)) # Подложка
    hp_fill_w = int(bar_width * max(0, player.health) / player.max_health)
    pygame.draw.rect(screen, RED, (hp_x, hp_y, hp_fill_w, bar_height)) # Заливка
    if hp_fill_w > 0:
        pygame.draw.rect(screen, (255, 100, 100), (hp_x, hp_y, hp_fill_w, 4)) # 3D Блик сверху
    pygame.draw.rect(screen, HUD_BORDER, (hp_x, hp_y, bar_width, bar_height), 2) # Рамка
    
    hp_text = font.render(f"HP: {player.health}/{player.max_health}", True, WHITE)
    screen.blit(hp_text, (hp_x + 5, hp_y + 1))

    # Мана
    mp_x, mp_y = 25, VIEW_HEIGHT + 55
    pygame.draw.rect(screen, (0, 0, 50), (mp_x, mp_y, bar_width, bar_height))
    mp_fill_w = int(bar_width * max(0, player.mana) / player.max_mana)
    pygame.draw.rect(screen, BLUE, (mp_x, mp_y, mp_fill_w, bar_height))
    if mp_fill_w > 0:
        pygame.draw.rect(screen, (100, 200, 255), (mp_x, mp_y, mp_fill_w, 4)) # 3D Блик сверху
    pygame.draw.rect(screen, HUD_BORDER, (mp_x, mp_y, bar_width, bar_height), 2)
    
    mp_text = font.render(f"MP: {player.mana}/{player.max_mana}", True, WHITE)
    screen.blit(mp_text, (mp_x + 5, mp_y + 1))

    # 3. Инвентарь (Ключи и Зелья)
    inv_x = 240
    # Иконка ключа
    key_icon = pygame.transform.scale(textures['key'], (28, 28))
    screen.blit(key_icon, (inv_x, VIEW_HEIGHT + 22))
    keys_text = font.render(f"x {player.keys}", True, YELLOW)
    screen.blit(keys_text, (inv_x + 35, VIEW_HEIGHT + 26))

    # Иконка зелья
    potion_icon = pygame.transform.scale(textures['potion'], (28, 28))
    screen.blit(potion_icon, (inv_x, VIEW_HEIGHT + 52))
    potions_text = font.render(f"x {player.potions} (H)", True, GREEN)
    screen.blit(potions_text, (inv_x + 35, VIEW_HEIGHT + 56))

    # Подсказка по управлению в HUD
    controls_text1 = small_font.render("WASD/QE - Move  | Space - Sword", True, GRAY)
    controls_text2 = small_font.render("RMB - Fireball (10 MP) | F - Interact", True, GRAY)
    screen.blit(controls_text1, (inv_x, VIEW_HEIGHT + 95))
    screen.blit(controls_text2, (inv_x, VIEW_HEIGHT + 115))

    # 4. Лог сообщений
    log_x = 440
    log_messages = game_log.get_last_messages(5)
    for index, (msg_text, color) in enumerate(log_messages):
        # Обрезаем длинные сообщения
        display_text = msg_text[:40] if len(msg_text) > 40 else msg_text
        msg_surf = small_font.render(display_text, True, color)
        screen.blit(msg_surf, (log_x, VIEW_HEIGHT + 20 + index * 20))

    # 5. Отрисовка мини-карты на HUD (справа)
    map_size = 110
    map_x = WIDTH - map_size - 20
    map_y = VIEW_HEIGHT + 20
    pygame.draw.rect(screen, BLACK, (map_x, map_y, map_size, map_size))
    pygame.draw.rect(screen, HUD_BORDER, (map_x, map_y, map_size, map_size), 3)

    # Рисуем карту вокруг игрока (радиус видимости 4 клетки)
    radius = 4
    px, py = player.x, player.y
    cell_w = map_size / (radius * 2 + 1)

    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            map_cell_x = int(px) + dx
            map_cell_y = int(py) + dy
            
            # Проверка выхода за границы карты
            if 0 <= map_cell_x < game_map.cols and 0 <= map_cell_y < game_map.rows:
                tile = game_map.get_tile(map_cell_x, map_cell_y)
                color = (30, 30, 30) # Пол по умолчанию
                
                if tile in ('1', '2'):
                    color = (70, 70, 70) # Стена
                elif tile == 'G':
                    color = (100, 100, 150) # Решетка
                elif tile in ('D', 'K'):
                    color = (139, 69, 19) # Дверь
                elif tile == 'E':
                    color = GREEN # Выход
                    
                # Координаты на мини-карте
                draw_x = map_x + (dx + radius) * cell_w
                draw_y = map_y + (dy + radius) * cell_w
                
                pygame.draw.rect(screen, color, (draw_x, draw_y, cell_w - 1, cell_w - 1))
                
    # Рисуем маркер игрока по центру мини-карты
    player_marker_x = map_x + radius * cell_w + cell_w / 2
    player_marker_y = map_y + radius * cell_w + cell_w / 2
    pygame.draw.circle(screen, YELLOW, (int(player_marker_x), int(player_marker_y)), 4)
    
    # Направление взгляда на мини-карте
    dir_x = player_marker_x + math.cos(player.angle) * 12
    dir_y = player_marker_y + math.sin(player.angle) * 12
    pygame.draw.line(screen, YELLOW, (player_marker_x, player_marker_y), (dir_x, dir_y), 2)
    
    # Тонкие направляющие линии конуса обзора (FOV)
    left_x = player_marker_x + math.cos(player.angle - HALF_FOV) * 10
    left_y = player_marker_y + math.sin(player.angle - HALF_FOV) * 10
    right_x = player_marker_x + math.cos(player.angle + HALF_FOV) * 10
    right_y = player_marker_y + math.sin(player.angle + HALF_FOV) * 10
    pygame.draw.line(screen, (220, 220, 0), (player_marker_x, player_marker_y), (left_x, left_y), 1)
    pygame.draw.line(screen, (220, 220, 0), (player_marker_x, player_marker_y), (right_x, right_y), 1)


def draw_weapon(screen, player, textures):
    """Отрисовка оружия в руках игрока с покачиванием при ходьбе"""
    weapon_frames = textures['weapon']
    frame_idx = min(player.weapon_state, len(weapon_frames) - 1)  # Защита от выхода за границы
    weapon_surf = weapon_frames[frame_idx]
    
    # Смещение из-за анимации ходьбы (head bobbing)
    sway_x = math.cos(player.bob_angle) * 6 if player.moving else 0
    sway_y = player.bob_y / 2
    
    # Позиционирование оружия внизу по центру
    w_w, w_h = weapon_surf.get_size()
    pos_x = VIEW_WIDTH // 2 - w_w // 2 + 100 + int(sway_x)
    pos_y = VIEW_HEIGHT - w_h + 30 + int(sway_y)
    
    # Если меч в процессе удара, смещаем его вперед/влево
    if frame_idx == 2:
        pos_x -= 120
        pos_y -= 40
        
    screen.blit(weapon_surf, (pos_x, pos_y))


def draw_crosshair(screen):
    """Небольшой прицел в центре 3D экрана"""
    cx = VIEW_WIDTH // 2
    cy = VIEW_HEIGHT // 2
    # Используем обычный RGB (не RGBA) для совместимости
    pygame.draw.line(screen, WHITE, (cx - 8, cy), (cx + 8, cy), 1)
    pygame.draw.line(screen, WHITE, (cx, cy - 8), (cx, cy + 8), 1)
