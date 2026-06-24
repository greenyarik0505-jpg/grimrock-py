import pygame
import struct
import math
import random
import array

def generate_sine_wave(frequency, duration_ms, volume=0.5, sample_rate=22050):
    """Генерирует синусоидальную волну заданной частоты"""
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')  # signed short (16-bit)
    max_amp = int(32767 * volume)
    for i in range(num_samples):
        t = i / sample_rate
        value = int(max_amp * math.sin(2 * math.pi * frequency * t))
        samples.append(value)
    # Стерео: дублируем канал
    stereo = array.array('h')
    for s in samples:
        stereo.append(s)
        stereo.append(s)
    return stereo, num_samples

def apply_envelope(samples, num_samples, attack=0.05, decay=0.1, sustain_level=0.7, release=0.3):
    """Применяет ADSR огибающую к сэмплам (стерео — каждый 2-й сэмпл)"""
    total = num_samples
    attack_end = int(total * attack)
    decay_end = attack_end + int(total * decay)
    release_start = total - int(total * release)
    
    for i in range(total):
        if i < attack_end:
            env = i / max(1, attack_end)
        elif i < decay_end:
            env = 1.0 - (1.0 - sustain_level) * (i - attack_end) / max(1, decay_end - attack_end)
        elif i < release_start:
            env = sustain_level
        else:
            env = sustain_level * (1.0 - (i - release_start) / max(1, total - release_start))
        
        idx_l = i * 2
        idx_r = i * 2 + 1
        if idx_r < len(samples):
            samples[idx_l] = int(samples[idx_l] * env)
            samples[idx_r] = int(samples[idx_r] * env)

def create_sound_from_samples(samples, sample_rate=22050):
    """Создаёт pygame.mixer.Sound из массива сэмплов"""
    sound = pygame.mixer.Sound(buffer=samples.tobytes())
    return sound

def create_sword_sound():
    """Звук удара мечом — короткий свист с шумом"""
    sample_rate = 22050
    duration_ms = 200
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        # Свист (высокая частота, убывающая)
        freq = 800 - 600 * (i / num_samples)
        swoosh = math.sin(2 * math.pi * freq * t) * 0.4
        # Шум удара
        noise = random.uniform(-0.3, 0.3) * (1 - i / num_samples)
        value = int(32767 * max(-1, min(1, swoosh + noise)))
        samples.append(value)
        samples.append(value)
    
    apply_envelope(samples, num_samples, attack=0.02, decay=0.1, sustain_level=0.3, release=0.5)
    return create_sound_from_samples(samples, sample_rate)

def create_fireball_sound():
    """Звук фаербола — низкий гул с нарастанием"""
    sample_rate = 22050
    duration_ms = 400
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        # Низкий гул
        bass = math.sin(2 * math.pi * 80 * t) * 0.3
        # Средние частоты — потрескивание огня
        crackle = math.sin(2 * math.pi * 300 * t + math.sin(2 * math.pi * 50 * t) * 5) * 0.25
        # Шум огня
        noise = random.uniform(-0.15, 0.15)
        value = int(32767 * max(-1, min(1, bass + crackle + noise)))
        samples.append(value)
        samples.append(value)
    
    apply_envelope(samples, num_samples, attack=0.05, decay=0.15, sustain_level=0.5, release=0.4)
    return create_sound_from_samples(samples, sample_rate)

def create_hit_sound():
    """Звук получения урона — глухой удар"""
    sample_rate = 22050
    duration_ms = 250
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        decay = math.exp(-8 * t)
        # Глухой удар
        thump = math.sin(2 * math.pi * 100 * t) * decay * 0.5
        # Треск
        crack = random.uniform(-0.2, 0.2) * decay
        value = int(32767 * max(-1, min(1, thump + crack)))
        samples.append(value)
        samples.append(value)
    
    return create_sound_from_samples(samples, sample_rate)

def create_pickup_sound():
    """Звук подбора предмета — мелодичный звон"""
    sample_rate = 22050
    duration_ms = 300
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        decay = math.exp(-5 * t)
        # Два тона (аккорд)
        tone1 = math.sin(2 * math.pi * 880 * t) * 0.3
        tone2 = math.sin(2 * math.pi * 1320 * t) * 0.2
        # Высокий перезвон
        chime = math.sin(2 * math.pi * 1760 * t) * 0.1
        value = int(32767 * max(-1, min(1, (tone1 + tone2 + chime) * decay)))
        samples.append(value)
        samples.append(value)
    
    return create_sound_from_samples(samples, sample_rate)

def create_door_sound():
    """Звук открытия двери — скрип"""
    sample_rate = 22050
    duration_ms = 400
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        # Скрипящий звук (модулированная частота)
        freq = 200 + 150 * math.sin(2 * math.pi * 3 * t)
        creak = math.sin(2 * math.pi * freq * t) * 0.3
        # Низкий стук
        thud = math.sin(2 * math.pi * 60 * t) * 0.2 * math.exp(-3 * t)
        noise = random.uniform(-0.1, 0.1) * (1 - t * 2)
        value = int(32767 * max(-1, min(1, creak + thud + noise)))
        samples.append(value)
        samples.append(value)
    
    apply_envelope(samples, num_samples, attack=0.02, decay=0.2, sustain_level=0.4, release=0.4)
    return create_sound_from_samples(samples, sample_rate)

def create_enemy_death_sound():
    """Звук смерти скелета — костяной рассыпающийся звук"""
    sample_rate = 22050
    duration_ms = 500
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        decay = math.exp(-4 * t)
        # Костяной стук (несколько частот)
        bone1 = math.sin(2 * math.pi * 200 * t) * 0.2 * decay
        bone2 = math.sin(2 * math.pi * 350 * t + 1) * 0.15 * decay
        # Рассыпающийся шум
        rattle = random.uniform(-0.3, 0.3) * decay
        value = int(32767 * max(-1, min(1, bone1 + bone2 + rattle)))
        samples.append(value)
        samples.append(value)
    
    return create_sound_from_samples(samples, sample_rate)

def create_step_sound():
    """Звук шага по камню"""
    sample_rate = 22050
    duration_ms = 150
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        decay = math.exp(-15 * t)
        # Глухой удар ноги
        step = math.sin(2 * math.pi * 120 * t) * 0.3 * decay
        # Эхо по камню
        echo = math.sin(2 * math.pi * 250 * t) * 0.1 * decay
        # Лёгкий скрежет
        scrape = random.uniform(-0.15, 0.15) * decay
        value = int(32767 * max(-1, min(1, step + echo + scrape)))
        samples.append(value)
        samples.append(value)
    
    return create_sound_from_samples(samples, sample_rate)

def create_ambient_loop():
    """Фоновый эмбиент — мягкий тёплый гул ветра в пещере"""
    sample_rate = 22050
    duration_ms = 6000  # 6 секунд, плавно зациклится
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        # Очень мягкий, тёплый дрон — только чистые низкие синусы
        # Основной тон — глубокий бас на 36 Гц (едва слышимый)
        drone = math.sin(2 * math.pi * 36 * t) * 0.04
        # Второй обертон чуть выше — создаёт объём
        overtone = math.sin(2 * math.pi * 48 * t) * 0.02
        # Медленное дыхание — амплитудная модуляция (как будто ветер)
        breath = (1.0 + math.sin(2 * math.pi * 0.15 * t)) * 0.5
        
        # Плавное затухание на краях для бесшовного зацикливания
        fade = 1.0
        fade_samples = int(sample_rate * 0.5)  # 0.5 сек фейд
        if i < fade_samples:
            fade = i / fade_samples
        elif i > num_samples - fade_samples:
            fade = (num_samples - i) / fade_samples
        
        value = int(32767 * (drone + overtone) * breath * fade)
        value = max(-32767, min(32767, value))
        samples.append(value)
        samples.append(value)
    
    return create_sound_from_samples(samples, sample_rate)

def load_all_sounds():
    """Создаёт и возвращает все звуки игры"""
    sounds = {
        'sword': create_sword_sound(),
        'fireball': create_fireball_sound(),
        'hit': create_hit_sound(),
        'pickup': create_pickup_sound(),
        'door': create_door_sound(),
        'enemy_death': create_enemy_death_sound(),
        'step': create_step_sound(),
        'ambient': create_ambient_loop(),
    }
    # Регулировка громкости
    sounds['sword'].set_volume(0.6)
    sounds['fireball'].set_volume(0.5)
    sounds['hit'].set_volume(0.7)
    sounds['pickup'].set_volume(0.5)
    sounds['door'].set_volume(0.4)
    sounds['enemy_death'].set_volume(0.6)
    sounds['step'].set_volume(0.25)
    sounds['ambient'].set_volume(0.06)  # Очень тихо — едва слышный фон
    
    return sounds

