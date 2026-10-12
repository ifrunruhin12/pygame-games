# Pygame Arcade Games Collection

A collection of polished classic arcade games built in Python using Pygame, designed to explore game architecture, mechanics, physics, and game feel.

## Games Included:
- [x] **Pac-Man**: Authentic arcade maze with animated chomp, 4-ghost AI (Blinky, Pinky, Inky, Clyde), Energizer power pellets & frightened mode, side warp tunnels, lives, and high scores.
- [x] **Rapid Roll**: Nokia arcade classic recreated with vertical scrolling, ball physics, ceiling spike hazards, 6 platform varieties (Normal, Spike, Spring, Moving, Crumble, Ice), heart & gem collectibles, and high scores.
- [x] **Bricks Breaker**: Breakout arcade game with colorful beveled brick rows, paddle angle deflection, particle burst effects, lives, and level progression.
- [x] **Snake Game**: Retro snake with expressive head eyes pointing towards movement, glowing pulsing apples, food eating sparkle particles, score HUD, and game over overlays.
- [ ] Flappy Bird
- [ ] Space Invaders
- [ ] Tetris
- [x] **Pong**: Classic table tennis arcade game with 1-Player (vs AI) and 2-Player local PvP, angle deflection, speed ramping rallies, particle effects, and scoreboard.

---

## How to Run the Games

### 1. Prerequisites
Ensure Python (3.9+) and `pygame` are installed:
```bash
pip install pygame
```
Or activate the local virtual environment:
```bash
source venv/bin/activate
```

### 2. Launching Games

- **Pong**:
  ```bash
  python3 pong/main.py
  ```
  - **Modes**: Press `1` for 1-Player (vs Computer) or `2` for 2-Player (Local PvP).
  - **Controls**: P1 uses `W`/`S`, P2 uses `UP`/`DOWN`.
  - **Serve / Start**: `SPACE` | **Pause**: `P` | **Quit**: `ESC` | **Restart**: `ENTER`

- **Pac-Man**:
  ```bash
  python3 pacman/main.py
  ```
  - **Controls**: Arrow Keys or `W`/`A`/`S`/`D` to steer Pac-Man.
  - **Pause**: `P` | **Quit**: `ESC` | **Restart**: `ENTER` / `SPACE`

- **Rapid Roll**:
  ```bash
  python3 rapid-roll/main.py
  ```
  - **Controls**: `A`/`D` or Left/Right Arrow Keys to roll the ball.
  - **Pause**: `P` | **Quit**: `ESC` | **Start / Restart**: `SPACE` / `ENTER`

- **Bricks Breaker**:
  ```bash
  python3 brick-break/main.py
  ```
  - **Controls**: `A`/`D` or Left/Right Arrow Keys to move the paddle.
  - **Launch Ball**: `SPACE` or `UP` | **Pause**: `P` | **Restart**: `ENTER`

- **Snake Game**:
  ```bash
  python3 snake-game/main.py
  ```
  - **Controls**: Arrow Keys or `W`/`A`/`S`/`D` to turn.
  - **Pause**: `P` | **Quit**: `ESC` | **Restart**: `ENTER`

---

## Game Architecture & Features
- **Common UI & Font Layer** (`common_ui.py`): Robust text rendering and HUD panels with Python 3.14+ compatibility (supporting `pygame._freetype` and `pygame.font`), plus persistent high-score management.
- **Game Loops & State Management**: Complete title screens, pause overlays (`P`), animated transitions, and game over / restart flows.
- **Particle Systems**: Dynamic debris and sparkle effects on impacts and collections.

---

## Contributing
Pull requests, suggestions, and new game additions are welcome! Fork the repository and open a pull request.
