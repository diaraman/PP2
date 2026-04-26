# TSIS 4 - Snake

This version includes:

- Main menu, leaderboard, settings, and game over screens
- PostgreSQL leaderboard with `psycopg2`
- Username entry on the main menu
- Personal best tracking
- Weighted and disappearing foods
- Poison food
- Power-ups
- Obstacle blocks from level 3
- Background music from `assets/music.mp3`

## Run

```bash
python3 TSIS4/main.py
```

Smoke test:

```bash
python3 TSIS4/main.py --headless --max-frames 5
```

## Controls

- `Arrow keys` or `WASD` - move
- `Enter` - start from menu
- `R` - restart after game over
- `Esc` - quit / go back
- `Q` - quit

## Repository Layout

- `main.py` - app entry point
- `game.py` - Snake game interface
- `db.py` - PostgreSQL leaderboard access
- `config.py` - file paths and shared constants
- `settings.json` - saved preferences
- `leaderboard.json` - local leaderboard cache

This layout matches the TSIS4 assignment structure and keeps the game files split by responsibility.

Folder marker: 4
