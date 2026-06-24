import math

# Настройки экрана
WIDTH = 800
HEIGHT = 600

# Настройки 3D-экрана (оставляем нижнюю часть под HUD)
HUD_HEIGHT = 150
VIEW_WIDTH = WIDTH
VIEW_HEIGHT = HEIGHT - HUD_HEIGHT

# Настройки Raycasting
FOV = math.pi / 3  # 60 градусов
HALF_FOV = FOV / 2
NUM_RAYS = 200  # Количество лучей (баланс между FPS и качеством)
SCALE = WIDTH // NUM_RAYS  # Ширина одной вертикальной полосы стены
MAX_DEPTH = 16  # Максимальное расстояние видимости (в клетках)

# Параметры сетки
TILE_SIZE = 64

# Вычисление константы проецирования
# Высота стены на расстоянии 1.0 должна примерно равняться VIEW_HEIGHT
PROJ_COEFF = VIEW_HEIGHT / (2 * math.tan(HALF_FOV))

# Цвета (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (30, 30, 30)
HUD_BG = (15, 15, 20)
HUD_BORDER = (80, 70, 60)
RED = (200, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 215, 0)
ORANGE = (255, 120, 0)
PURPLE = (128, 0, 128)
BROWN = (100, 65, 40)
DARK_BROWN = (50, 30, 20)
FLOOR_COLOR = (25, 20, 20)
CEILING_COLOR = (15, 15, 20)

# Параметры игрока
PLAYER_HEALTH = 100
PLAYER_MANA = 50
FIREBALL_MANA_COST = 10
SWORD_DAMAGE = 25
FIREBALL_DAMAGE = 40
SWORD_COOLDOWN = 300  # в миллисекундах
FIREBALL_COOLDOWN = 600

# Параметры ИИ
ENEMY_SPEED = 0.03
ENEMY_DAMAGE = 10
ENEMY_ATTACK_COOLDOWN = 1000  # в миллисекундах

# Ограничение частоты кадров
FPS = 60

# Полноэкранный режим (True — запуск на весь экран)
FULLSCREEN = True

# Звук
SOUND_ENABLED = True
SOUND_SAMPLE_RATE = 22050
SOUND_CHANNELS = 2
SOUND_BUFFER = 1024

