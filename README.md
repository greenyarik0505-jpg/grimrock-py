# grimrock-py

A retro-style 3D Dungeon Crawler game built from scratch in Python using **Pygame** and **NumPy**. It uses a classic raycasting engine to render a 3D perspective of the dungeon, complete with procedural textures, dynamic sprite rendering, enemies with AI, and dynamically generated audio.

## Features

- **3D Raycasting Engine**: Classic pseudo-3D engine rendering walls, doors, and animated sprites.
- **Procedural Textures**: Walls, floors, ceilings, and doors are generated procedurally at runtime.
- **Dynamic Audio Synthesis**: All game sounds (sword swings, fireballs, door creaks, enemy deaths, footsteps, and low cave ambient hum) are generated dynamically using mathematical functions and NumPy, requiring zero external audio assets!
- **AI Enemies**: Skeletons that track, chase, and attack the player.
- **Combat & Magic**: Attack enemies with a sword or cast fireballs.
- **Interactive Environment**: Locked doors, key pickups, and chest interactables.
- **Full Screen Support**: Smooth scaling of a virtual $800 \times 600$ viewport to match any display resolution.
- **Minimap & HUD**: On-screen compass, minimap, health bars, and combat log.

## Screenshot / Design
The game uses a dark, atmospheric dungeon color palette with visual effects and interactive UI.

## Getting Started

### Prerequisites

- Python 3.10+
- Pygame
- NumPy

Install dependencies:
```bash
pip install pygame numpy
```

### Running the Game

Launch the game by running:
```bash
python game.py
```

## Controls

- **W / A / S / D**: Move forward, left, backward, right
- **Q / E**: Turn camera left / right
- **Space**: Attack with sword
- **Shift**: Cast fireball (consumes mana/resources)
- **F**: Interact with doors/chests
- **Escape**: Exit game

## How It Works

1. **Raycasting**: Calculates the distance to walls using DDA (Digital Differential Analysis) algorithm for each vertical column of the screen.
2. **Procedural Sound**: Audio waves (sine, square, noise) are generated as NumPy arrays, shaped with ADSR envelopes, and loaded directly as Pygame Sound objects.
3. **Procedural Textures**: Custom math functions generate brick, wood, and metal patterns pixel-by-pixel when the game starts.
