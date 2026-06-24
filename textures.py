import pygame
import random
from config import *

def generate_noise(surface, amount=15, color_var=10):
    """Добавляет шум на текстуру для реалистичности"""
    width, height = surface.get_size()
    for _ in range(int(width * height * (amount / 100))):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r, g, b, *a = surface.get_at((x, y))
        # Изменяем цвет случайным образом
        var = random.randint(-color_var, color_var)
        nr = max(0, min(255, r + var))
        ng = max(0, min(255, g + var))
        nb = max(0, min(255, b + var))
        surface.set_at((x, y), (nr, ng, nb))

def create_stone_texture():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill((100, 100, 100)) # Базовый серый камень
    
    # Рисуем стыки кирпичей
    for y in range(0, TILE_SIZE, 16):
        pygame.draw.line(surf, (50, 50, 50), (0, y), (TILE_SIZE, y), 2)
        # Вертикальные стыки со смещением
        offset = 16 if (y // 16) % 2 == 0 else 0
        for x in range(offset, TILE_SIZE + 16, 32):
            pygame.draw.line(surf, (50, 50, 50), (x, y), (x, y + 16), 2)
            
    # Добавляем трещины и неровности
    generate_noise(surf, amount=20, color_var=15)
    
    # Рисуем несколько глубоких трещин
    for _ in range(3):
        x1, y1 = random.randint(5, 55), random.randint(5, 55)
        x2, y2 = x1 + random.randint(-10, 10), y1 + random.randint(-10, 10)
        pygame.draw.line(surf, (40, 40, 40), (x1, y1), (x2, y2), 1)
        
    return surf

def create_mossy_texture():
    surf = create_stone_texture()
    # Добавляем зеленый мох поверх камня
    for _ in range(15):
        cx = random.randint(5, TILE_SIZE - 15)
        cy = random.randint(5, TILE_SIZE - 15)
        radius = random.randint(3, 8)
        # Рисуем пятна мха с альфа-смешиванием или просто зеленым цветом с шумом
        moss_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(moss_surf, (0, random.randint(80, 140), 0, 120), (radius, radius), radius)
        surf.blit(moss_surf, (cx - radius, cy - radius))
    return surf

def create_door_texture():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill(BROWN)
    
    # Деревянные доски (вертикальные полосы)
    for x in range(0, TILE_SIZE, 8):
        pygame.draw.line(surf, DARK_BROWN, (x, 0), (x, TILE_SIZE), 2)
        
    # Железная окантовка двери
    pygame.draw.rect(surf, (80, 80, 80), (0, 0, TILE_SIZE, TILE_SIZE), 4)
    # Металлические заклепки на окантовке
    for y in range(4, TILE_SIZE, 12):
        pygame.draw.circle(surf, (120, 120, 120), (2, y), 2)
        pygame.draw.circle(surf, (120, 120, 120), (TILE_SIZE - 3, y), 2)
        
    # Дверная ручка (кольцо)
    pygame.draw.circle(surf, (200, 180, 50), (TILE_SIZE - 16, TILE_SIZE // 2), 6, 2)
    pygame.draw.circle(surf, (200, 180, 50), (TILE_SIZE - 16, TILE_SIZE // 2), 2)
    
    generate_noise(surf, amount=10, color_var=10)
    return surf

def create_gate_texture():
    # Решетка (с прозрачным фоном)
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0)) # Полностью прозрачный
    
    # Рисуем металлические прутья
    for x in range(8, TILE_SIZE, 12):
        pygame.draw.line(surf, (70, 70, 70), (x, 0), (x, TILE_SIZE), 4)
        # Блик на прутьях
        pygame.draw.line(surf, (110, 110, 110), (x - 1, 0), (x - 1, TILE_SIZE), 1)
        
    # Горизонтальные соединительные балки
    for y in [12, TILE_SIZE // 2, TILE_SIZE - 12]:
        pygame.draw.line(surf, (50, 50, 50), (0, y), (TILE_SIZE, y), 5)
        for x in range(8, TILE_SIZE, 12):
            # Заклепки на пересечениях
            pygame.draw.circle(surf, (140, 140, 140), (x, y), 3)
            
    return surf

def create_key_sprite():
    # Спрайт золотого ключа
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    # Кольцо ключа
    pygame.draw.circle(surf, YELLOW, (32, 20), 10, 3)
    # Стержень ключа
    pygame.draw.line(surf, YELLOW, (32, 30), (32, 52), 4)
    # Бородка ключа
    pygame.draw.line(surf, YELLOW, (32, 45), (42, 45), 3)
    pygame.draw.line(surf, YELLOW, (32, 50), (42, 50), 3)
    # Блики
    pygame.draw.circle(surf, WHITE, (30, 18), 2)
    return surf

def create_potion_sprite():
    # Спрайт зелья здоровья (красный бутылек)
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    
    # Горлышко
    pygame.draw.rect(surf, (150, 200, 255), (28, 10, 8, 12))
    pygame.draw.rect(surf, BROWN, (26, 8, 12, 4)) # Пробка
    
    # Колба
    points = [(28, 22), (16, 40), (16, 54), (48, 54), (48, 40), (36, 22)]
    pygame.draw.polygon(surf, (150, 200, 255), points) # Стеклянная колба
    
    # Красная жидкость внутри
    liq_points = [(29, 28), (19, 41), (19, 52), (45, 52), (45, 41), (35, 28)]
    pygame.draw.polygon(surf, RED, liq_points)
    # Пузырьки/блики
    pygame.draw.circle(surf, WHITE, (24, 44), 3)
    pygame.draw.circle(surf, (255, 100, 100), (38, 48), 2)
    
    # Контур
    pygame.draw.polygon(surf, (50, 50, 50), points, 2)
    
    return surf

def create_skeleton_sprite(frame=0):
    # Процедурный скелет. frame=0: обычный, frame=1: атакующий
    surf = pygame.Surface((128, 128), pygame.SRCALPHA)
    
    # Череп
    pygame.draw.ellipse(surf, (220, 220, 200), (52, 16, 24, 24))
    # Глазницы
    pygame.draw.circle(surf, RED if frame == 1 else BLACK, (58, 26), 3)
    pygame.draw.circle(surf, RED if frame == 1 else BLACK, (70, 26), 3)
    
    # Позвоночник и ребра
    pygame.draw.line(surf, (220, 220, 200), (64, 40), (64, 80), 4) # Позвоночник
    for y in range(48, 76, 8):
        pygame.draw.ellipse(surf, (220, 220, 200), (44, y, 40, 6), 2) # Ребра
        
    # Таз
    pygame.draw.rect(surf, (200, 200, 180), (50, 78, 28, 8), border_radius=2)
    
    # Руки
    if frame == 1:
        # Замахнулся костлявой рукой
        pygame.draw.lines(surf, (220, 220, 200), False, [(44, 48), (28, 30), (20, 16)], 3) # Левая поднята
        pygame.draw.lines(surf, (220, 220, 200), False, [(84, 48), (96, 60), (104, 76)], 3) # Правая опущена
        # Меч скелета
        pygame.draw.line(surf, (150, 150, 150), (20, 16), (8, 0), 4) # Лезвие
        pygame.draw.line(surf, BROWN, (22, 18), (18, 14), 2) # Рукоять
    else:
        # Руки просто висят
        pygame.draw.lines(surf, (220, 220, 200), False, [(44, 48), (36, 68), (38, 88)], 3)
        pygame.draw.lines(surf, (220, 220, 200), False, [(84, 48), (92, 68), (90, 88)], 3)
        
    # Ноги
    pygame.draw.lines(surf, (220, 220, 200), False, [(54, 86), (50, 106), (46, 126)], 3) # Левая
    pygame.draw.lines(surf, (220, 220, 200), False, [(74, 86), (78, 106), (82, 126)], 3) # Правая
    
    # Добавляем тени и грязь
    generate_noise(surf, amount=5, color_var=10)
    
    # Скейлим для соответствия 3D проекции
    return pygame.transform.scale(surf, (TILE_SIZE * 2, TILE_SIZE * 2))

def create_weapon_sprites():
    # Оружие в руке игрока (вид от первого лица)
    # Возвращает список кадров: 0 - покой, 1 - замах, 2 - удар, 3 - возврат
    frames = []
    
    # Кадр 0: Меч спокойно держится справа снизу
    surf0 = pygame.Surface((300, 300), pygame.SRCALPHA)
    # Лезвие (направлено вверх-влево под углом)
    pygame.draw.polygon(surf0, (200, 200, 200), [(150, 150), (20, 20), (35, 10), (160, 140)])
    pygame.draw.line(surf0, WHITE, (27, 15), (155, 145), 2) # Грань/блик
    # Гарда и эфес
    pygame.draw.line(surf0, (180, 150, 50), (130, 170), (180, 120), 10) # Крестовина
    pygame.draw.line(surf0, BROWN, (155, 145), (220, 210), 12) # Рукоять
    pygame.draw.circle(surf0, (180, 150, 50), (220, 210), 10) # Набалдашник
    frames.append(surf0)
    
    # Кадр 1: Меч отведен в сторону (замах)
    surf1 = pygame.Surface((300, 300), pygame.SRCALPHA)
    pygame.draw.polygon(surf1, (180, 180, 180), [(200, 180), (110, 80), (120, 70), (210, 170)])
    pygame.draw.line(surf1, (180, 150, 50), (180, 195), (225, 155), 10)
    pygame.draw.line(surf1, BROWN, (205, 175), (260, 230), 12)
    pygame.draw.circle(surf1, (180, 150, 50), (260, 230), 10)
    frames.append(surf1)
    
    # Кадр 2: Меч бьет по диагонали (выпад вперед-влево)
    surf2 = pygame.Surface((300, 300), pygame.SRCALPHA)
    pygame.draw.polygon(surf2, (240, 240, 240), [(100, 180), (-30, 50), (-15, 35), (110, 165)])
    pygame.draw.line(surf2, WHITE, (-22, 42), (105, 172), 2)
    pygame.draw.line(surf2, (180, 150, 50), (80, 200), (130, 150), 10)
    pygame.draw.line(surf2, BROWN, (105, 172), (170, 237), 12)
    pygame.draw.circle(surf2, (180, 150, 50), (170, 237), 10)
    # Рисуем эффект взмаха (белая дуга)
    pygame.draw.arc(surf2, (255, 255, 255, 150), (0, 0, 250, 250), 0.5, 2.5, 3)
    frames.append(surf2)
    
    # Кадр 3: Меч возвращается
    surf3 = pygame.Surface((300, 300), pygame.SRCALPHA)
    pygame.draw.polygon(surf3, (190, 190, 190), [(130, 160), (0, 30), (15, 20), (140, 150)])
    pygame.draw.line(surf3, (180, 150, 50), (110, 180), (160, 130), 10)
    pygame.draw.line(surf3, BROWN, (135, 155), (200, 220), 12)
    pygame.draw.circle(surf3, (180, 150, 50), (200, 220), 10)
    frames.append(surf3)
    
    return frames

def create_sky_gradient():
    """Создает градиент потолка/неба"""
    surf = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT // 2))
    for y in range(VIEW_HEIGHT // 2):
        # От черного к темно-синему
        ratio = y / (VIEW_HEIGHT // 2)
        color = (
            int(CEILING_COLOR[0] * (1 - ratio)),
            int(CEILING_COLOR[1] * (1 - ratio) + 15 * ratio),
            int(CEILING_COLOR[2] * (1 - ratio) + 30 * ratio)
        )
        pygame.draw.line(surf, color, (0, y), (VIEW_WIDTH, y))
    return surf

def create_floor_gradient():
    """Создает градиент пола"""
    surf = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT // 2))
    for y in range(VIEW_HEIGHT // 2):
        # От темно-серого к черному вдали
        ratio = y / (VIEW_HEIGHT // 2)
        color = (
            int(10 * ratio + FLOOR_COLOR[0] * (1 - ratio)),
            int(8 * ratio + FLOOR_COLOR[1] * (1 - ratio)),
            int(8 * ratio + FLOOR_COLOR[2] * (1 - ratio))
        )
        pygame.draw.line(surf, color, (0, y), (VIEW_WIDTH, y))
    return surf

def create_fireball_sprite():
    """Спрайт огненного шара"""
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    # Внешнее свечение (оранжевое)
    pygame.draw.circle(surf, (255, 100, 0, 80), (32, 32), 28)
    # Среднее ядро (ярко-оранжевое)
    pygame.draw.circle(surf, (255, 160, 0, 160), (32, 32), 20)
    # Внутреннее ядро (жёлтое)
    pygame.draw.circle(surf, (255, 220, 50, 220), (32, 32), 12)
    # Центральная яркая точка (белая)
    pygame.draw.circle(surf, (255, 255, 200, 255), (32, 32), 5)
    return surf

def load_all_textures():
    """Генерирует и возвращает все текстуры игры в словаре"""
    textures = {
        '1': create_stone_texture(),          # Обычная каменная стена
        '2': create_mossy_texture(),          # Стена со мхом
        'D': create_door_texture(),           # Обычная дверь
        'K': create_door_texture(),           # Запертая дверь (внешне такая же, но требует ключ)
        'G': create_gate_texture(),           # Решетка (прозрачная)
        'key': create_key_sprite(),           # Предмет: Ключ
        'potion': create_potion_sprite(),     # Предмет: Зелье
        'fireball': create_fireball_sprite(), # Снаряд: Огненный шар
        'skeleton_0': create_skeleton_sprite(0), # Скелет (покой)
        'skeleton_1': create_skeleton_sprite(1), # Скелет (атака)
        'weapon': create_weapon_sprites(),     # Оружие игрока (список кадров)
        'sky': create_sky_gradient(),         # Небо/Потолок
        'floor': create_floor_gradient()      # Пол
    }
    return textures

