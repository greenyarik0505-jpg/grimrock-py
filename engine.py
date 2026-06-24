import pygame
import math
import random
from config import *

# Глобальный буфер затенения для ускорения работы
shadow_overlays = {}
column_cache = {}

def get_shadow_overlay(alpha, width, height):
    """Возвращает или создает черную полупрозрачную поверхность для затенения"""
    alpha = max(0, min(255, int(alpha)))
    if width <= 0 or height <= 0:
        return None
    key = (alpha, width, height)
    if key not in shadow_overlays:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        shadow_overlays[key] = overlay
    return shadow_overlays[key]

def get_scaled_column(texture, tex_x, scale, height, texture_key):
    """Кэширует отмасштабированные срезы текстур для повышения FPS"""
    height = max(1, (height // 4) * 4)
    key = (texture_key, tex_x, scale, height)
    if key not in column_cache:
        if len(column_cache) > 3000:
            column_cache.clear()
        try:
            wall_column = texture.subsurface((tex_x, 0, 1, TILE_SIZE))
            column_cache[key] = pygame.transform.scale(wall_column, (scale, height))
        except pygame.error:
            fallback = pygame.Surface((scale, height))
            fallback.fill((120, 120, 120))
            column_cache[key] = fallback
    return column_cache[key]

def raycast(player, game_map, textures, screen):
    # Инициализируем Z-буфер (хранит скорректированные расстояния — proj_dist)
    z_buffer = [MAX_DEPTH] * NUM_RAYS
    
    # 1. Отрисовка пола и потолка (градиентные фоны с учетом покачивания головы)
    # Смещаем отрисовку на bob_y, чтобы не было швов и разрывов на горизонте
    sky_y = int(player.bob_y) - 15
    screen.blit(textures['sky'], (0, sky_y))
    floor_y = VIEW_HEIGHT // 2 + int(player.bob_y) - 15
    screen.blit(textures['floor'], (0, floor_y))

    # Направление взгляда игрока
    ox, oy = player.x, player.y
    player_angle = player.angle

    # Динамический эффект мерцания факела (изменяет дальность освещения)
    ticks = pygame.time.get_ticks()
    # Волнообразная и случайная пульсация
    flicker = 1.0 + math.sin(ticks * 0.015) * 0.03 + random.uniform(-0.01, 0.01)

    # 2. Отрисовка стен
    for i in range(NUM_RAYS):
        # Угол луча
        ray_angle = player_angle - HALF_FOV + i * FOV / NUM_RAYS
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # DDA Алгоритм (Digital Differential Analysis)
        map_x, map_y = int(ox), int(oy)
        
        # Длина луча при переходе на 1 клетку по сетке
        delta_dist_x = abs(1 / cos_a) if cos_a != 0 else 1e30
        delta_dist_y = abs(1 / sin_a) if sin_a != 0 else 1e30

        # Направление движения луча и начальные расстояния
        if cos_a < 0:
            step_x = -1
            side_dist_x = (ox - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - ox) * delta_dist_x

        if sin_a < 0:
            step_y = -1
            side_dist_y = (oy - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - oy) * delta_dist_y

        # Поиск пересечения со стеной
        wall_tile = None
        side = 0 # 0 - вертикальное пересечение, 1 - горизонтальное
        dist = MAX_DEPTH

        # Проходим циклом по сетке
        for _ in range(int(MAX_DEPTH * 2)):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            tile = game_map.get_tile(map_x, map_y)
            if tile and game_map.is_wall(map_x, map_y):
                wall_tile = tile
                # Вычисляем расстояние до стены
                if side == 0:
                    dist = (map_x - ox + (1 - step_x) / 2) / cos_a
                else:
                    dist = (map_y - oy + (1 - step_y) / 2) / sin_a
                break

        # Устранение эффекта рыбьего глаза
        proj_dist = dist * math.cos(ray_angle - player_angle)
        proj_dist = max(0.01, proj_dist)

        # Записываем СКОРРЕКТИРОВАННОЕ расстояние в Z-буфер
        z_buffer[i] = proj_dist

        if wall_tile:
            # Высота проецируемой стены
            wall_height = int(PROJ_COEFF / proj_dist)

            # Текстурирование
            # Вычисляем координату X на текстуре (wall_x)
            if side == 0:
                wall_x = oy + dist * sin_a
            else:
                wall_x = ox + dist * cos_a
            
            wall_x -= math.floor(wall_x)
            tex_x = int(wall_x * TILE_SIZE)
            # Защита от выхода за границы текстуры
            tex_x = max(0, min(TILE_SIZE - 1, tex_x))

            # Зеркальное отражение текстуры во избежание флиппинга
            if side == 0 and cos_a > 0:
                tex_x = TILE_SIZE - tex_x - 1
            if side == 1 and sin_a < 0:
                tex_x = TILE_SIZE - tex_x - 1

            # Рендеринг вертикальной полоски стены
            texture = textures.get(wall_tile, textures['1'])
            
            # Ограничиваем высоту стены разумным пределом
            render_height = min(VIEW_HEIGHT * 3, wall_height)
            
            # Используем кэш масштабирования для колонок стен
            scaled_column = get_scaled_column(texture, tex_x, SCALE, render_height, wall_tile)

            # Вычисляем верхнюю координату стены с учетом покачивания головы
            wall_top = int(VIEW_HEIGHT / 2 + player.bob_y - render_height / 2)

            # Рисуем полосу стены
            screen.blit(scaled_column, (i * SCALE, wall_top))

            # Эффект затухания света (тени в глубине лабиринта + мерцание)
            depth_shadow = 1.0 / (1.0 + proj_dist * proj_dist * 0.05 * flicker)
            if side == 1:
                depth_shadow *= 0.8
                
            shadow_alpha = int((1.0 - depth_shadow) * 255)
            if shadow_alpha > 5:
                shadow_y = max(0, wall_top)
                shadow_h = min(VIEW_HEIGHT - shadow_y, render_height - max(0, -wall_top))
                if shadow_h > 0:
                    shadow = get_shadow_overlay(shadow_alpha, SCALE, shadow_h)
                    if shadow:
                        screen.blit(shadow, (i * SCALE, shadow_y))
                    
    return z_buffer

def render_sprites(player, entities, textures, z_buffer, screen):
    """Сортирует и отрисовывает 3D спрайты (врагов, предметы, снаряды)"""
    projected_sprites = []
    
    for entity in entities:
        if not entity.alive:
            continue
            
        dx = entity.x - player.x
        dy = entity.y - player.y
        dist = math.hypot(dx, dy)
        
        if dist < 0.1:
            continue  # Слишком близко — не рендерить
        
        # Угол между игроком и спрайтом
        theta = math.atan2(dy, dx)
        # Относительный угол взгляда
        gamma = theta - player.angle
        
        # Нормализация угла в диапазон [-pi, pi]
        gamma = (gamma + math.pi) % (2 * math.pi) - math.pi
        
        # Ограничиваем угол видимости с небольшим запасом
        if abs(gamma) < HALF_FOV + 0.5:
            # Коррекция дисторсии (рыбьего глаза) для спрайтов
            proj_dist = dist * math.cos(gamma)
            if proj_dist > 0.1:
                projected_sprites.append((proj_dist, gamma, entity))
                
    # Сортируем спрайты по глубине (от дальних к ближним — Painter's Algorithm)
    projected_sprites.sort(key=lambda s: s[0], reverse=True)
    
    # Отрисовываем каждый спрайт
    for proj_dist, gamma, entity in projected_sprites:
        # Высота и ширина спрайта на экране с учетом его scale_factor
        scale_factor = getattr(entity, 'scale_factor', 0.7)
        sprite_size = int(PROJ_COEFF / proj_dist * scale_factor)
        
        if sprite_size <= 0 or sprite_size > VIEW_HEIGHT * 3:
            continue
        
        # Позиция по горизонтали на экране
        screen_x = int((NUM_RAYS / 2) * (1 + math.tan(gamma) / math.tan(HALF_FOV))) * SCALE
        screen_x_left = screen_x - sprite_size // 2
        
        # Позиция по вертикали с учетом покачивания головы
        screen_y_top = int(VIEW_HEIGHT / 2 + player.bob_y - sprite_size / 2)
        
        # Получаем текстуру спрайта
        sprite_surf = textures.get(entity.sprite_key, textures.get('potion'))
        if sprite_surf is None:
            continue
        tex_w, tex_h = sprite_surf.get_size()
        
        # Определяем диапазон лучей, которые перекрывает спрайт
        start_ray = max(0, screen_x_left // SCALE)
        end_ray = min(NUM_RAYS - 1, (screen_x_left + sprite_size) // SCALE)
        
        # Коэффициент затенения спрайта
        depth_shadow = 1.0 / (1.0 + proj_dist * proj_dist * 0.05)
        shadow_alpha = int((1.0 - depth_shadow) * 255)
        
        # Отрисовываем спрайт по вертикальным полосам с учетом Z-буфера
        for ray_idx in range(start_ray, end_ray + 1):
            if ray_idx < 0 or ray_idx >= NUM_RAYS:
                continue
            # Z-buffer теперь хранит proj_dist, так что сравнение корректно
            if proj_dist < z_buffer[ray_idx]:
                col_x = ray_idx * SCALE
                tex_col = int((col_x - screen_x_left) / sprite_size * tex_w)
                
                if 0 <= tex_col < tex_w:
                    try:
                        sprite_column = sprite_surf.subsurface((tex_col, 0, 1, tex_h))
                        scaled_col = pygame.transform.scale(sprite_column, (SCALE, sprite_size))
                        
                        if shadow_alpha > 5:
                            shadow = get_shadow_overlay(shadow_alpha, SCALE, sprite_size)
                            if shadow:
                                scaled_col.blit(shadow, (0, 0))
                            
                        screen.blit(scaled_col, (col_x, screen_y_top))
                    except pygame.error:
                        pass
