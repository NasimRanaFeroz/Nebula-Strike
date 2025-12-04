# Nebula Strike

A vertical scrolling space shooter game built with Python and Pygame.

## Description

Nebula Strike is an intense vertical scrolling airplane battle game that puts you in control of a powerful space fighter. Navigate through treacherous starfields, face relentless enemy waves, and engage in epic boss battles across 3 challenging levels.

## Features

- **Dynamic 4-directional movement** - Full control of your space fighter
- **Multiple weapon systems**:
  - Standard blaster with upgradeable firing patterns
  - Homing missiles that track enemies
  - Special screen-clearing laser
- **Power-up system** including health, shields, weapon upgrades, and special weapons
- **Varied enemy types** with unique movement patterns and attack behaviors
- **Epic boss battles** with multiple phases
- **3 progressive levels** with increasing difficulty

## Level Structure

### Level 1: Initial Contact

- 3 waves of basic enemies
- Mini-boss battle
- Unlock: Homing missiles

### Level 2: Advanced Threats

- Zig-zagging enemies and elite shooters
- 2-phase main boss
- Unlock: Shield barrier

### Level 3: The Final Showdown

- Mixed elite enemy waves
- 3-phase final boss with devastating attacks
- Unlock: Ultimate laser

## Installation

1. Make sure you have Python 3.8 or higher installed
2. Clone or download this repository
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python main.py
```

## Controls

- **Arrow Keys / WASD** - Move your ship
- **SPACE** - Fire weapons
- **SHIFT** - Use special weapon
- **ESC** - Pause game

## Project Structure

```
FinalGame/
├── main.py              # Main game entry point
├── src/
│   ├── player.py        # Player class and controls
│   ├── enemy.py         # Enemy types and AI
│   ├── boss.py          # Boss battles
│   ├── bullet.py        # Weapon systems
│   ├── powerup.py       # Power-up collectibles
│   └── level.py         # Level management
├── assets/
│   ├── images/          # Sprite assets (to be added)
│   └── sounds/          # Audio assets (to be added)
└── requirements.txt     # Python dependencies
```

## Adding Assets

The game is currently set up with placeholder graphics. To add your own assets:

1. Place sprite images in `assets/images/`
2. Place sound effects and music in `assets/sounds/`
3. Update the `load_assets()` methods in each class to load your images

Recommended asset sizes:

- Player ship: 50x50 pixels
- Enemies: 40x40 pixels
- Bosses: 100x100 - 150x150 pixels
- Power-ups: 30x30 pixels

## Development Status

✅ Core game structure and loop
✅ Player movement and shooting
✅ Enemy AI with multiple patterns
✅ Boss battles with multiple phases
✅ Power-up system
✅ Level progression system
✅ Collision detection
✅ HUD and scoring

🔲 Asset integration (awaiting art assets)
🔲 Sound effects and music
🔲 Particle effects
🔲 Menu polish

## Future Enhancements

- Additional levels
- More enemy types
- Achievement system
- Multiple difficulty modes
- Leaderboard system

## Credits

Game design and development: Nebula Strike Team

## License

This project is for educational purposes.
