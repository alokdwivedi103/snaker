# Multiplayer Snake (Terminal Edition)

A two-player snake game that runs right in your terminal using Python's built-in `curses` library. No external dependencies needed on Mac/Linux.

## Requirements

- Python 3.6+
- A real terminal (Terminal.app, iTerm2, GNOME Terminal, WSL, Git Bash, etc.)
- **Windows only:** the plain Command Prompt / PowerShell doesn't ship with `curses`. Either use WSL / Git Bash, or install the Windows port:
  ```
  pip install windows-curses
  ```

## Running the Game

1. Download `multiplayer_snake.py`.
2. Open a terminal and navigate to the folder containing the file:
   ```
   cd path/to/folder
   ```
3. Run it:
   ```
   python3 multiplayer_snake.py
   ```
4. Resize your terminal window to be reasonably large before starting — the board scales to fill the window, and anything smaller than ~22 columns x 13 rows won't work.

## Controls

| Player | Move Up | Move Down | Move Left | Move Right |
|--------|---------|-----------|-----------|------------|
| Player 1 (green) | `W` | `S` | `A` | `D` |
| Player 2 (yellow) | `↑` | `↓` | `←` | `→` |

Press `q` at any time to quit.

## Rules

- Eat the red `*` food to grow one segment and score a point.
- A new piece of food spawns randomly after each one is eaten.
- You die if you:
  - Hit a wall
  - Run into your own body
  - Run into the other player's snake
- If both snakes crash head-on into each other, it's a draw.
- The round ends as soon as one or both snakes die. The last snake standing wins.
- Final scores are shown on the game-over screen — press any key to exit.

## Notes

- Both players share the same keyboard, so play works best with two people who can comfortably reach WASD and the arrow keys at the same time.
- Game speed is fixed at a moderate pace (~10 ticks/second). If you'd like it faster or slower, open `multiplayer_snake.py` and adjust the value in:
  ```python
  stdscr.timeout(100)  # milliseconds per tick — lower = faster
  ```

Enjoy!
