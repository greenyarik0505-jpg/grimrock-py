import pygame
import sys
import math
import random
from config import *
from map_data import GameMap, LEVELS
from player import Player
from entities import Enemy, Pickup, Projectile
from textures import load_all_textures
from engine import raycast, render_sprites
from ui import draw_hud, draw_weapon, draw_crosshair, GameLog

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        # Инициализация звука
        if SOUND_ENABLED:
            pygame.mixer.pre_init(SOUND_SAMPLE_RATE, -16, SOUND_CHANNELS, SOUND_BUFFER)
            pygame.mixer.init()
        
        # Настройка экрана
        if FULLSCREEN:
            display_info = pygame.display.Info()
            self.real_width = display_info.current_w
            self.real_height = display_info.current_h
            self.screen = pygame.display.set_mode((self.real_width, self.real_height), pygame.FULLSCREEN)
        else:
            self.real_width = WIDTH
            self.real_height = HEIGHT
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        # Рендерим в виртуальный буфер фиксированного размера (WIDTH x HEIGHT)
        # и масштабируем на реальный экран
        self.render_surface = pygame.Surface((WIDTH, HEIGHT))
        
        pygame.display.set_caption("Grimrock Py: 3D Dungeon Crawler")
        self.clock = pygame.time.Clock()
        
        # Загрузка текстур
        self.textures = load_all_textures()
        
        # Загрузка звуков
        self.sounds = {}
        if SOUND_ENABLED:
            try:
                from sounds import load_all_sounds
                self.sounds = load_all_sounds()
            except Exception as e:
                print(f"Sound init error: {e}")
        
        # Состояния игры
        # 0: MENU, 1: PLAYING, 2: GAME_OVER, 3: VICTORY
        self.state = 0 
        
        self.current_level_idx = 0
        self.game_log = GameLog()
        
        self.game_map = None
        self.player = None
        self.entities = []
        self.enemies = []
        
        # Состояние ввода
        self.show_full_map = False
        
        # Запуск фонового эмбиента
        self._start_ambient()

    def play_sound(self, name):
        """Проигрывает звуковой эффект по имени"""
        if SOUND_ENABLED and name in self.sounds:
            self.sounds[name].play()

    def _start_ambient(self):
        """Запускает зацикленный фоновый эмбиент"""
        if SOUND_ENABLED and 'ambient' in self.sounds:
            self.sounds['ambient'].play(loops=-1)

    def load_level(self, level_idx):
        self.current_level_idx = level_idx
        self.game_map = GameMap(level_idx)
        
        start_x, start_y = self.game_map.start_pos
        self.player = Player(start_x, start_y, self.game_map.start_angle)
        
        self.entities = []
        self.enemies = []
        
        # Спавним начальные сущности
        for ent_data in self.game_map.initial_entities:
            t = ent_data['type']
            x, y = ent_data['pos']
            if t == 'skeleton':
                enemy = Enemy(x, y, 'skeleton')
                self.entities.append(enemy)
                self.enemies.append(enemy)
            elif t == 'key':
                self.entities.append(Pickup(x, y, 'key'))
            elif t == 'potion':
                self.entities.append(Pickup(x, y, 'potion'))
        
        self.game_log.add_message(f"--- LEVEL {level_idx + 1} ---", YELLOW)
        self.game_log.add_message("You wake in a dark labyrinth...", GRAY)
        self.game_log.add_message("Find the gold key and descend.", WHITE)

    def next_level(self):
        if self.current_level_idx + 1 < len(LEVELS):
            self.load_level(self.current_level_idx + 1)
        else:
            self.state = 3 # Победа!

    def draw_menu(self):
        self.render_surface.fill(BLACK)
        
        try:
            title_font = pygame.font.SysFont('Consolas', 64, bold=True)
            font = pygame.font.SysFont('Consolas', 24)
            small_font = pygame.font.SysFont('Consolas', 16)
        except:
            title_font = pygame.font.Font(None, 74)
            font = pygame.font.Font(None, 30)
            small_font = pygame.font.Font(None, 20)
            
        title_surf = title_font.render("GRIMROCK PY", True, YELLOW)
        subtitle_surf = font.render("3D Retro Dungeon Crawler", True, WHITE)
        start_surf = font.render("Press SPACE or ENTER to start", True, GREEN)
        
        # Рамка
        pygame.draw.rect(self.render_surface, HUD_BORDER, (50, 50, WIDTH - 100, HEIGHT - 100), 4)
        
        self.render_surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 150))
        self.render_surface.blit(subtitle_surf, (WIDTH // 2 - subtitle_surf.get_width() // 2, 230))
        self.render_surface.blit(start_surf, (WIDTH // 2 - start_surf.get_width() // 2, 380))
        
        # Подсказки
        fs_text = small_font.render("F11 - Toggle Fullscreen | ESC - Quit", True, GRAY)
        self.render_surface.blit(fs_text, (WIDTH // 2 - fs_text.get_width() // 2, 440))
        
        author_surf = small_font.render("Made with Antigravity AI | 2026", True, GRAY)
        self.render_surface.blit(author_surf, (WIDTH // 2 - author_surf.get_width() // 2, 520))

    def draw_game_over(self):
        self.render_surface.fill(BLACK)
        try:
            title_font = pygame.font.SysFont('Consolas', 64, bold=True)
            font = pygame.font.SysFont('Consolas', 24)
        except:
            title_font = pygame.font.Font(None, 74)
            font = pygame.font.Font(None, 30)
            
        title_surf = title_font.render("YOU DIED", True, RED)
        sub_surf = font.render("The dungeon consumed your soul...", True, GRAY)
        restart_surf = font.render("Press ENTER to return to menu", True, WHITE)
        
        self.render_surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 180))
        self.render_surface.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, 270))
        self.render_surface.blit(restart_surf, (WIDTH // 2 - restart_surf.get_width() // 2, 380))

    def draw_victory(self):
        self.render_surface.fill(BLACK)
        try:
            title_font = pygame.font.SysFont('Consolas', 64, bold=True)
            font = pygame.font.SysFont('Consolas', 24)
        except:
            title_font = pygame.font.Font(None, 74)
            font = pygame.font.Font(None, 30)
            
        title_surf = title_font.render("VICTORY!", True, GREEN)
        sub_surf = font.render("You escaped the dungeon!", True, YELLOW)
        restart_surf = font.render("Press ENTER to return to menu", True, WHITE)
        
        self.render_surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 180))
        self.render_surface.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, 270))
        self.render_surface.blit(restart_surf, (WIDTH // 2 - restart_surf.get_width() // 2, 380))

    def toggle_fullscreen(self):
        """Переключение полноэкранного/оконного режима"""
        current_flags = self.screen.get_flags()
        if current_flags & pygame.FULLSCREEN:
            # Переключаемся в оконный режим
            self.real_width = WIDTH
            self.real_height = HEIGHT
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        else:
            # Переключаемся в полноэкранный
            display_info = pygame.display.Info()
            self.real_width = display_info.current_w
            self.real_height = display_info.current_h
            self.screen = pygame.display.set_mode((self.real_width, self.real_height), pygame.FULLSCREEN)

    def handle_events(self, current_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                # Глобальные клавиши
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    
                if self.state == 0:  # MENU
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.load_level(0)
                        self.state = 1  # PLAYING
                elif self.state in (2, 3):  # GAME_OVER or VICTORY
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = 0  # MENU
                elif self.state == 1:  # PLAYING
                    if event.key == pygame.K_f:
                        # Взаимодействие
                        res = self.player.interact(self.game_map, self.game_log)
                        if res == "NEXT_LEVEL":
                            self.next_level()
                        elif res == "DOOR_OPENED":
                            self.play_sound('door')
                    elif event.key == pygame.K_h:
                        # Использование зелья
                        if self.player.potions > 0:
                            if self.player.heal(40, self.game_log):
                                self.player.potions -= 1
                                self.play_sound('pickup')
                        else:
                            self.game_log.add_message("No Health Potions!", RED)
                    elif event.key == pygame.K_SPACE:
                        # Атака мечом
                        if self.player.attack(current_time, self.enemies, self.game_log):
                            self.play_sound('sword')
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == 1:
                    if event.button == 1:  # ЛКМ - удар мечом
                        if self.player.attack(current_time, self.enemies, self.game_log):
                            self.play_sound('sword')
                    elif event.button == 3:  # ПКМ - фаербол
                        if self.player.cast_fireball(current_time, self.game_log, self.entities):
                            self.play_sound('fireball')

    def update(self, current_time):
        if self.state != 1:
            return
            
        # 1. Считываем зажатые клавиши для ходьбы/поворотов по сетке
        keys = pygame.key.get_pressed()
        if not self.player.moving and not self.player.turning:
            moved = False
            if keys[pygame.K_w]:
                self.player.start_move(1, 0, self.game_map, current_time)
                moved = True
            elif keys[pygame.K_s]:
                self.player.start_move(-1, 0, self.game_map, current_time)
                moved = True
            elif keys[pygame.K_q]:
                self.player.start_move(0, -1, self.game_map, current_time)
                moved = True
            elif keys[pygame.K_e]:
                self.player.start_move(0, 1, self.game_map, current_time)
                moved = True
            elif keys[pygame.K_a]:
                self.player.start_turn(-1, current_time)
            elif keys[pygame.K_d]:
                self.player.start_turn(1, current_time)
            
            # Звук шага, если игрок начал двигаться
            if moved and self.player.moving:
                self.play_sound('step')
                
        # 2. Обновляем игрока
        self.player.update(current_time)
        
        # 3. Обновляем снаряды и врагов (копия списка, чтобы не ломать итерацию)
        prev_enemy_alive = {id(e): e.alive for e in self.enemies}
        
        for ent in list(self.entities):
            if not ent.alive:
                continue
            if ent.type == 'projectile':
                ent.update(self.game_map, self.enemies, self.game_log)
            elif ent.type == 'enemy':
                ent.update(self.player, self.game_map, current_time, self.game_log, self.entities)
        
        # Проверяем, кто из врагов только что умер — проигрываем звук
        for e in self.enemies:
            if prev_enemy_alive.get(id(e), True) and not e.alive:
                self.play_sound('enemy_death')
        
        # Проверяем, получил ли игрок урон
        # (реализуем через отслеживание здоровья)
                
        # 4. Проверяем автоподбор предметов (когда игрок вступает в ту же клетку)
        player_tile = self.player.tile_pos
        for ent in self.entities:
            if ent.alive and ent.type == 'pickup':
                ent_tile = (int(ent.x), int(ent.y))
                if player_tile == ent_tile:
                    ent.collect(self.player, self.game_log)
                    self.play_sound('pickup')
        
        # 5. Проверяем, стоит ли игрок на лестнице (автоматический переход)
        tile_at_player = self.game_map.get_tile(player_tile[0], player_tile[1])
        if tile_at_player == 'E' and not self.player.moving:
            self.game_log.add_message("You descend the stairs...", GREEN)
            self.next_level()
            return
                    
        # 6. Обрабатываем дроп при смерти врагов (ДО удаления мёртвых из списка!)
        new_pickups = []
        for ent in self.entities:
            if ent.type == 'enemy' and not ent.alive and not ent.dropped:
                ent.dropped = True
                # Шанс 60% выпадения зелья
                if random.random() < 0.6:
                    new_pickups.append(Pickup(ent.x, ent.y, 'potion'))
                    self.game_log.add_message("Potion found in the bones!", GREEN)
                    
        self.entities.extend(new_pickups)
        
        # 7. Удаляем неактивные сущности
        self.entities = [e for e in self.entities if e.alive]
        self.enemies = [e for e in self.enemies if e.alive]
        
        # 8. Проверка проигрыша
        if self.player.health <= 0:
            self.play_sound('hit')
            self.state = 2 # Конец игры

    def draw(self):
        if self.state == 0:
            self.draw_menu()
        elif self.state == 2:
            self.draw_game_over()
        elif self.state == 3:
            self.draw_victory()
        elif self.state == 1:
            # 1. 3D Рендеринг сцены
            z_buffer = raycast(self.player, self.game_map, self.textures, self.render_surface)
            
            # Отрисовка спрайтов
            render_sprites(self.player, self.entities, self.textures, z_buffer, self.render_surface)
            
            # 2. Отрисовка оружия в руке
            draw_weapon(self.render_surface, self.player, self.textures)
            
            # 3. Отрисовка прицела
            draw_crosshair(self.render_surface)
            
            # 4. Отрисовка HUD
            draw_hud(self.render_surface, self.player, self.game_map, self.game_log, self.textures, self.show_full_map)
        
        # Масштабируем виртуальный буфер на реальный экран
        if self.real_width != WIDTH or self.real_height != HEIGHT:
            scaled = pygame.transform.scale(self.render_surface, (self.real_width, self.real_height))
            self.screen.blit(scaled, (0, 0))
        else:
            self.screen.blit(self.render_surface, (0, 0))
            
        pygame.display.flip()

    def run(self):
        while True:
            current_time = pygame.time.get_ticks()
            self.handle_events(current_time)
            self.update(current_time)
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
