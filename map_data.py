import math

# Легенда карты:
# ' ' или '.' - пустое пространство (пол)
# '1' - обычная каменная стена
# '2' - замшелая каменная стена
# 'G' - решетка (прозрачная стена, через нее видно, но нельзя пройти)
# 'D' - деревянная дверь (открывается кнопкой E)
# 'K' - запертая дверь (требует золотой ключ)
# 'E' - лестница вниз (выход с уровня)

LEVELS = [
    # УРОВЕНЬ 1
    {
        'map': [
            "1111111111111111",
            "1..1......1....1",
            "1..D..11..K..2.1",
            "1..1..11..1222.1",
            "1.21.GG...1....1",
            "1....11...D..s.1",
            "1.s..11...1....1",
            "111111111111E111"
        ],
        'start_pos': (1.5, 1.5),  # Центр клетки (1, 1)
        'start_angle': 0.0,       # Смотрит на восток (вправо)
        'entities': [
            {'type': 'key', 'pos': (1.5, 5.5)},       # Ключ лежит в тупике слева
            {'type': 'potion', 'pos': (13.5, 1.5)},   # Зелье в правом верхнем углу
            {'type': 'skeleton', 'pos': (8.5, 4.5)},  # Скелет в центральной комнате
            {'type': 'skeleton', 'pos': (13.5, 5.5)}, # Скелет около выхода
        ]
    },
    # УРОВЕНЬ 2
    {
        'map': [
            "11111111111111111111",
            "1....1.........1...1",
            "1.s..D.11111G1.D.s.1",
            "1....1.1...1.1.1...1",
            "11D111.1.s.1.1.11111",
            "1....1.1...1.1.....1",
            "1.p..1.11D11.1111K11",
            "111111.......1.....1",
            "1......11111.D..s..1",
            "1111111111111111E111"
        ],
        'start_pos': (1.5, 1.5),
        'start_angle': math.pi / 2, # Смотрит на юг (вниз)
        'entities': [
            {'type': 'key', 'pos': (9.5, 5.5)},       # Ключ за дверью в центре
            {'type': 'potion', 'pos': (1.5, 8.5)},    # Зелье в левом нижнем углу
            {'type': 'potion', 'pos': (18.5, 1.5)},   # Зелье в правом верхнем углу
            {'type': 'skeleton', 'pos': (5.5, 8.5)},  # Скелет патрулирует снизу
            {'type': 'skeleton', 'pos': (18.5, 8.5)}, # Скелет в комнате перед выходом
        ]
    }
]

class GameMap:
    def __init__(self, level_index):
        level_data = LEVELS[level_index]
        # Преобразуем список строк в двумерный список символов, чтобы сетку можно было изменять во время игры
        self.grid = [list(row) for row in level_data['map']]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0
        self.start_pos = level_data['start_pos']
        self.start_angle = level_data['start_angle']
        self.initial_entities = level_data['entities']

    def get_tile(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[y][x]
        return '1' # Всё за границами карты считается сплошной стеной

    def set_tile(self, x, y, val):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.grid[y][x] = val

    def is_wall(self, x, y):
        tile = self.get_tile(x, y)
        return tile in ('1', '2', 'G', 'D', 'K')

    def is_blocking(self, x, y):
        tile = self.get_tile(x, y)
        return tile in ('1', '2', 'G', 'D', 'K')

