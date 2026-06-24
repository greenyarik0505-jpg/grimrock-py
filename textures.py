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
    
    # Рисуем стыки кирпичей (тени)
    for y in range(0, TILE_SIZE, 16):
        pygame.draw.line(surf, (40, 40, 40), (0, y), (TILE_SIZE, y), 2)
        offset = 16 if (y // 16) % 2 == 0 else 0
        for x in range(offset, TILE_SIZE + 16, 32):
            pygame.draw.line(surf, (40, 40, 40), (x, y), (x, y + 16), 2)
            
    # Рисуем 3D-блики на гранях кирпичей (сверху и слева)
    for y in range(0, TILE_SIZE, 16):
        pygame.draw.line(surf, (145, 145, 145), (0, y + 1), (TILE_SIZE, y + 1), 1)
        offset = 16 if (y // 16) % 2 == 0 else 0
        for x in range(offset, TILE_SIZE + 16, 32):
            pygame.draw.line(surf, (145, 145, 145), (x + 1, y + 1), (x + 1, y + 15), 1)

    # Добавляем трещины и неровности
    generate_noise(surf, amount=25, color_var=18)
    
    # Рисуем несколько глубоких трещин
    for _ in range(4):
        x1, y1 = random.randint(5, 55), random.randint(5, 55)
        x2, y2 = x1 + random.randint(-12, 12), y1 + random.randint(-12, 12)
        pygame.draw.line(surf, (35, 35, 35), (x1, y1), (x2, y2), 1)
        
    return surf

def create_mossy_texture():
    surf = create_stone_texture()
    # Добавляем зеленый мох поверх камня в трещины
    for _ in range(20):
        cx = random.randint(2, TILE_SIZE - 10)
        cy = random.randint(2, TILE_SIZE - 10)
        radius = random.randint(2, 6)
        moss_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        color = (random.randint(20, 60), random.randint(100, 170), random.randint(10, 40), random.randint(120, 180))
        pygame.draw.circle(moss_surf, color, (radius, radius), radius)
        surf.blit(moss_surf, (cx - radius, cy - radius))
    return surf

def create_door_texture():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill(BROWN)
    
    # Деревянная текстура (горизонтальные волокна)
    for y in range(TILE_SIZE):
        var = random.randint(-15, 15)
        color = (max(0, min(255, BROWN[0] + var)), max(0, min(255, BROWN[1] + var)), max(0, min(255, BROWN[2] + var)))
        pygame.draw.line(surf, color, (0, y), (TILE_SIZE, y))
        
    # Деревянные доски (вертикальные стыки)
    for x in range(0, TILE_SIZE, 8):
        pygame.draw.line(surf, (35, 20, 10), (x, 0), (x, TILE_SIZE), 2)
        
    # Железная окантовка двери
    pygame.draw.rect(surf, (60, 60, 65), (0, 0, TILE_SIZE, TILE_SIZE), 5)
    pygame.draw.rect(surf, (90, 90, 95), (1, 1, TILE_SIZE - 2, TILE_SIZE - 2), 1)
    
    # Металлические заклепки на окантовке
    for y in range(6, TILE_SIZE, 12):
        pygame.draw.circle(surf, (140, 140, 145), (2, y), 2)
        pygame.draw.circle(surf, (140, 140, 145), (TILE_SIZE - 3, y), 2)
        
    # Замковая пластина и замочная скважина
    pygame.draw.rect(surf, (80, 80, 85), (TILE_SIZE - 22, TILE_SIZE // 2 - 12, 12, 24), border_radius=2)
    pygame.draw.circle(surf, (20, 20, 20), (TILE_SIZE - 16, TILE_SIZE // 2 - 4), 3)
    pygame.draw.polygon(surf, (20, 20, 20), [(TILE_SIZE - 18, TILE_SIZE // 2), (TILE_SIZE - 14, TILE_SIZE // 2), (TILE_SIZE - 16, TILE_SIZE // 2 + 6)])
    
    # Дверная ручка (золотое кольцо)
    pygame.draw.circle(surf, (220, 190, 40), (TILE_SIZE - 16, TILE_SIZE // 2 + 4), 5, 2)
    pygame.draw.circle(surf, (180, 150, 30), (TILE_SIZE - 16, TILE_SIZE // 2 + 4), 2)
    
    generate_noise(surf, amount=10, color_var=8)
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
    pygame.draw.ellipse(surf, (210, 210, 190), (52, 16, 24, 24))
    # Тень на нижней части черепа
    pygame.draw.ellipse(surf, (160, 160, 140), (54, 28, 20, 10))
    
    # Светящиеся красные глаза (в бою светятся ярче)
    eye_color = (255, 0, 0) if frame == 1 else (180, 0, 0)
    pygame.draw.circle(surf, eye_color, (58, 26), 3)
    pygame.draw.circle(surf, eye_color, (70, 26), 3)
    if frame == 1:
        # Эффект свечения глаз в ярости
        pygame.draw.circle(surf, (255, 100, 100, 120), (58, 26), 6)
        pygame.draw.circle(surf, (255, 100, 100, 120), (70, 26), 6)
    
    # Позвоночник и ребра
    pygame.draw.line(surf, (220, 220, 200), (64, 40), (64, 80), 4) # Позвоночник
    for y in range(48, 76, 8):
        # 3D ребра с тенью
        pygame.draw.ellipse(surf, (150, 150, 130), (44, y, 40, 6), 2)
        pygame.draw.ellipse(surf, (220, 220, 200), (45, y - 1, 38, 4), 1)
        
    # Наплечники (старые ржавые железные щитки)
    pygame.draw.ellipse(surf, (80, 75, 70), (40, 42, 10, 10))
    pygame.draw.ellipse(surf, (80, 75, 70), (78, 42, 10, 10))
    # Стальные блики на наплечниках
    pygame.draw.circle(surf, (120, 110, 100), (43, 45), 2)
    pygame.draw.circle(surf, (120, 110, 100), (81, 45), 2)
    
    # Таз
    pygame.draw.rect(surf, (190, 190, 170), (50, 78, 28, 8), border_radius=2)
    
    # Руки
    if frame == 1:
        # Замахнулся костлявой рукой
        pygame.draw.lines(surf, (220, 220, 200), False, [(44, 48), (28, 30), (20, 16)], 3) # Левая поднята
        pygame.draw.lines(surf, (220, 220, 200), False, [(84, 48), (96, 60), (104, 76)], 3) # Правая опущена
        # Меч скелета (зазубренный клинок)
        pygame.draw.line(surf, (110, 110, 110), (20, 16), (8, 0), 4) # Лезвие
        pygame.draw.line(surf, (150, 150, 150), (18, 14), (6, -2), 1) # Блик на лезвии
        pygame.draw.line(surf, BROWN, (22, 18), (18, 14), 2) # Рукоять
    else:
        # Руки просто висят
        pygame.draw.lines(surf, (220, 220, 200), False, [(44, 48), (36, 68), (38, 88)], 3)
        pygame.draw.lines(surf, (220, 220, 200), False, [(84, 48), (92, 68), (90, 88)], 3)
        
    # Ноги
    pygame.draw.lines(surf, (210, 210, 190), False, [(54, 86), (50, 106), (46, 126)], 3) # Левая
    pygame.draw.lines(surf, (210, 210, 190), False, [(74, 86), (78, 106), (82, 126)], 3) # Правая
    
    # Добавляем тени и грязь
    generate_noise(surf, amount=8, color_var=12)
    
    # Скейлим для соответствия 3D проекции (redundant, but keeping structure)
    return pygame.transform.scale(surf, (TILE_SIZE * 2, TILE_SIZE * 2))

def create_weapon_sprites():
    # Оружие в руке игрока (вид от первого лица)
    # Возвращает список кадров: 0 - покой, 1 - замах, 2 - удар, 3 - возврат
    frames = []
    
    # Кадр 0: Меч спокойно держится справа снизу
    surf0 = pygame.Surface((300, 300), pygame.SRCALPHA)
    # Лезвие (направлено вверх-влево под углом, стальной градиент)
    pygame.draw.polygon(surf0, (180, 185, 190), [(150, 150), (20, 20), (35, 10), (160, 140)])
    pygame.draw.line(surf0, WHITE, (27, 15), (155, 145), 3) # Грань/яркий стальной блик
    # Гарда и эфес (золото)
    pygame.draw.line(surf0, (220, 180, 40), (130, 170), (180, 120), 10) # Золотая крестовина
    pygame.draw.line(surf0, (40, 20, 10), (155, 145), (220, 210), 12) # Кожаная рукоять
    pygame.draw.circle(surf0, (220, 180, 40), (220, 210), 12) # Золотой набалдашник
    pygame.draw.circle(surf0, (200, 0, 0), (155, 145), 4) # Красный рубин в центре эфеса
    frames.append(surf0)
    
    # Кадр 1: Меч отведен в сторону (замах)
    surf1 = pygame.Surface((300, 300), pygame.SRCALPHA)
    pygame.draw.polygon(surf1, (160, 165, 170), [(200, 180), (110, 80), (120, 70), (210, 170)])
    pygame.draw.line(surf1, WHITE, (115, 75), (205, 165), 2)
    pygame.draw.line(surf1, (220, 180, 40), (180, 195), (225, 155), 10)
    pygame.draw.line(surf1, (40, 20, 10), (205, 175), (260, 230), 12)
    pygame.draw.circle(surf1, (220, 180, 40), (260, 230), 12)
    pygame.draw.circle(surf1, (200, 0, 0), (202, 175), 4)
    frames.append(surf1)
    
    # Кадр 2: Меч бьет по диагонали (выпад вперед-влево, яркая вспышка)
    surf2 = pygame.Surface((300, 300), pygame.SRCALPHA)
    pygame.draw.polygon(surf2, (230, 235, 240), [(100, 180), (-30, 50), (-15, 35), (110, 165)])
    pygame.draw.line(surf2, WHITE, (-22, 42), (105, 172), 4) # Сверхъяркий блик при ударе
    pygame.draw.line(surf2, (220, 180, 40), (80, 200), (130, 150), 10)
    pygame.draw.line(surf2, (40, 20, 10), (105, 172), (170, 237), 12)
    pygame.draw.circle(surf2, (220, 180, 40), (170, 237), 12)
    pygame.draw.circle(surf2, (200, 0, 0), (102, 172), 4)
    
    # Отрисовка красивого дугового шлейфа удара (градиентный белый-голубой веер)
    trail_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
    pygame.draw.arc(trail_surf, (200, 240, 255, 140), (10, 10, 260, 260), 0.5, 2.5, 8)
    pygame.draw.arc(trail_surf, (255, 255, 255, 200), (10, 10, 260, 260), 0.7, 2.3, 3)
    surf2.blit(trail_surf, (0, 0))
    frames.append(surf2)
    
    # Кадр 3: Меч возвращается
    surf3 = pygame.Surface((300, 300), pygame.SRCALPHA)
    pygame.draw.polygon(surf3, (170, 175, 180), [(130, 160), (0, 30), (15, 20), (140, 150)])
    pygame.draw.line(surf3, WHITE, (7, 25), (135, 155), 2)
    pygame.draw.line(surf3, (220, 180, 40), (110, 180), (160, 130), 10)
    pygame.draw.line(surf3, (40, 20, 10), (135, 155), (200, 220), 12)
    pygame.draw.circle(surf3, (220, 180, 40), (200, 220), 12)
    pygame.draw.circle(surf3, (200, 0, 0), (132, 155), 4)
    frames.append(surf3)
    
    return frames

def create_sky_gradient():
    """Создает градиент потолка/неба (с запасом высоты для покачивания)"""
    h = VIEW_HEIGHT // 2 + 30
    surf = pygame.Surface((VIEW_WIDTH, h))
    for y in range(h):
        # От черного к темно-синему
        ratio = y / h
        color = (
            int(CEILING_COLOR[0] * (1 - ratio)),
            int(CEILING_COLOR[1] * (1 - ratio) + 15 * ratio),
            int(CEILING_COLOR[2] * (1 - ratio) + 30 * ratio)
        )
        pygame.draw.line(surf, color, (0, y), (VIEW_WIDTH, y))
    return surf

def create_floor_gradient():
    """Создает градиент пола (с запасом высоты для покачивания)"""
    h = VIEW_HEIGHT // 2 + 30
    surf = pygame.Surface((VIEW_WIDTH, h))
    for y in range(h):
        # От темно-серого к черному вдали
        ratio = y / h
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

def create_particle_sprite(color):
    """Создает спрайт круглой частицы со свечением и бликом"""
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    r, g, b, *a = color
    alpha = a[0] if a else 255
    pygame.draw.circle(surf, (r, g, b, alpha // 2), (8, 8), 8)
    pygame.draw.circle(surf, (r, g, b, alpha), (8, 8), 5)
    pygame.draw.circle(surf, (255, 255, 255, alpha), (6, 6), 2)
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
        'floor': create_floor_gradient(),      # Пол
        
        # Спрайты частиц
        'particle_fire': create_particle_sprite((255, 100, 0, 200)),
        'particle_dust': create_particle_sprite((220, 220, 220, 150)),
        'particle_blood': create_particle_sprite((180, 0, 0, 220)),
        'particle_mana': create_particle_sprite((0, 150, 255, 200))
    }
    return textures

