#!/usr/bin/env python3
"""
Multiplayer Snake — terminal edition (1 or 2 players, same keyboard)

Mode select at launch:
  1 - Single player   (WASD or Arrow keys both control your snake)
  2 - Two player       Player 1 (green): W A S D
                        Player 2 (yellow): Arrow keys

Rules:
- Eat food (*) to grow and score.
- Crashing into a wall or yourself kills you.
- In two-player mode, crashing into the other snake kills you too,
  and a head-on collision kills both snakes at once.
- Game ends when zero or one snake remains alive.
- Press 'q' to quit at any time.

Run with:  python3 multiplayer_snake.py
"""

import curses
import random


def choose_mode(stdscr):
    """Show a mode-select screen and return True for two-player, False for single-player."""
    stdscr.nodelay(False)
    stdscr.timeout(-1)
    curses.curs_set(0)
    stdscr.erase()

    lines = [
        "MULTIPLAYER SNAKE",
        "",
        "Select a mode:",
        "",
        "  [1]  Single player   (WASD or Arrow keys)",
        "  [2]  Two player      (P1: WASD, P2: Arrows)",
        "",
        "  [q]  Quit",
    ]
    height, width = stdscr.getmaxyx()
    start_y = max(1, height // 2 - len(lines) // 2)
    for i, line in enumerate(lines):
        x = max(0, (width - len(line)) // 2)
        try:
            attr = curses.A_BOLD if i == 0 else curses.A_NORMAL
            stdscr.addstr(start_y + i, x, line, attr)
        except curses.error:
            pass
    stdscr.refresh()

    while True:
        k = stdscr.getch()
        if k in (ord('1'),):
            return False
        if k in (ord('2'),):
            return True
        if k in (ord('q'), ord('Q')):
            return None


def main(stdscr):
    two_player = choose_mode(stdscr)
    if two_player is None:
        return

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)  # ms per tick -> controls game speed
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # Player 1
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Player 2
    curses.init_pair(3, curses.COLOR_RED, -1)     # Food / messages
    curses.init_pair(4, curses.COLOR_CYAN, -1)    # Border / UI

    height, width = stdscr.getmaxyx()
    # Leave a border and a status line at top
    top_margin = 2
    board_h = height - top_margin - 1
    board_w = width - 2

    if board_h < 10 or board_w < 20:
        stdscr.nodelay(False)
        stdscr.addstr(0, 0, "Terminal too small. Resize to at least 22x13 and rerun.")
        stdscr.getch()
        return

    def rand_empty_cell(occupied):
        while True:
            y = random.randint(1, board_h - 2) + top_margin
            x = random.randint(1, board_w - 2) + 1
            if (y, x) not in occupied:
                return (y, x)

    # Initial snake positions: p1 on the left moving right, p2 on the right moving left
    p1 = {
        "body": [(top_margin + board_h // 2, 4 + i) for i in range(3)][::-1],
        "dir": (0, 1),
        "alive": True,
        "score": 0,
        "color": curses.color_pair(1) | curses.A_BOLD,
        "grow": 0,
    }
    p2 = {
        "body": [(top_margin + board_h // 2, board_w - 4 - i) for i in range(3)][::-1],
        "dir": (0, -1),
        "alive": two_player,   # inactive placeholder in single-player mode
        "score": 0,
        "color": curses.color_pair(2) | curses.A_BOLD,
        "grow": 0,
    }

    occupied = set(p1["body"]) | (set(p2["body"]) if two_player else set())
    food = rand_empty_cell(occupied)

    # In single-player mode, BOTH WASD and arrow keys steer p1.
    key_map_p1 = {
        ord('w'): (-1, 0), ord('s'): (1, 0),
        ord('a'): (0, -1), ord('d'): (0, 1),
    }
    key_map_p2 = {
        curses.KEY_UP: (-1, 0), curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1), curses.KEY_RIGHT: (0, 1),
    }
    key_map_p1_solo_extra = {
        curses.KEY_UP: (-1, 0), curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1), curses.KEY_RIGHT: (0, 1),
    }

    def opposite(d):
        return (-d[0], -d[1])

    def draw_border():
        stdscr.attron(curses.color_pair(4))
        for x in range(0, board_w + 2):
            stdscr.addch(top_margin - 1, x, curses.ACS_HLINE)
            try:
                stdscr.addch(top_margin + board_h, x, curses.ACS_HLINE)
            except curses.error:
                pass
        for y in range(top_margin - 1, top_margin + board_h + 1):
            try:
                stdscr.addch(y, 0, curses.ACS_VLINE)
                stdscr.addch(y, board_w + 1, curses.ACS_VLINE)
            except curses.error:
                pass
        stdscr.attroff(curses.color_pair(4))

    running = True
    winner_msg = ""
    active_players = (p1, p2) if two_player else (p1,)

    while running:
        # ---- Input ----
        keys_this_tick = []
        try:
            while True:
                k = stdscr.getch()
                if k == -1:
                    break
                keys_this_tick.append(k)
        except curses.error:
            pass

        for k in keys_this_tick:
            if k in (ord('q'), ord('Q')):
                return
            if k in key_map_p1 and p1["alive"]:
                nd = key_map_p1[k]
                if nd != opposite(p1["dir"]):
                    p1["dir"] = nd
            if two_player:
                if k in key_map_p2 and p2["alive"]:
                    nd = key_map_p2[k]
                    if nd != opposite(p2["dir"]):
                        p2["dir"] = nd
            else:
                if k in key_map_p1_solo_extra and p1["alive"]:
                    nd = key_map_p1_solo_extra[k]
                    if nd != opposite(p1["dir"]):
                        p1["dir"] = nd

        # ---- Move snakes ----
        for p in active_players:
            if not p["alive"]:
                continue
            head_y, head_x = p["body"][0]
            dy, dx = p["dir"]
            new_head = (head_y + dy, head_x + dx)
            p["_new_head"] = new_head

        # ---- Collision detection (walls, self, other) ----
        occupied_bodies = {
            "p1": set(p1["body"][:-1]) if p1["grow"] == 0 else set(p1["body"]),
            "p2": set(p2["body"][:-1]) if p2["grow"] == 0 else set(p2["body"]),
        }

        checks = [("p1", p1, p2 if two_player else None)]
        if two_player:
            checks.append(("p2", p2, p1))

        for name, p, other in checks:
            if not p["alive"]:
                continue
            ny, nx = p["_new_head"]
            hit_wall = not (top_margin <= ny < top_margin + board_h and 1 <= nx <= board_w)
            hit_self = (ny, nx) in occupied_bodies[name]
            hit_other = bool(other) and other["alive"] and (ny, nx) in set(other["body"])
            if hit_wall or hit_self or hit_other:
                p["alive"] = False

        # Head-on collision: both move into each other's old head cell
        if two_player and p1["alive"] and p2["alive"]:
            if p1["_new_head"] == p2["_new_head"]:
                p1["alive"] = False
                p2["alive"] = False

        # ---- Apply moves for survivors ----
        for p in active_players:
            if not p["alive"]:
                continue
            p["body"].insert(0, p["_new_head"])
            if p["_new_head"] == food:
                p["score"] += 1
                p["grow"] += 1
                occ = set(p1["body"]) | (set(p2["body"]) if two_player else set())
                food = rand_empty_cell(occ)
            if p["grow"] > 0:
                p["grow"] -= 1
            else:
                p["body"].pop()

        # ---- Draw ----
        stdscr.erase()
        draw_border()

        if two_player:
            status = (f" P1 (WASD) score: {p1['score']}{' [DEAD]' if not p1['alive'] else ''}   |   "
                       f"P2 (Arrows) score: {p2['score']}{' [DEAD]' if not p2['alive'] else ''}   |   q: quit ")
        else:
            status = f" Score: {p1['score']}{' [DEAD]' if not p1['alive'] else ''}   |   q: quit "
        try:
            stdscr.addstr(0, 1, status[: width - 2], curses.color_pair(4) | curses.A_BOLD)
        except curses.error:
            pass

        try:
            stdscr.addch(food[0], food[1], '*', curses.color_pair(3) | curses.A_BOLD)
        except curses.error:
            pass

        for p in active_players:
            for i, (y, x) in enumerate(p["body"]):
                ch = '@' if i == 0 else 'o'
                try:
                    stdscr.addch(y, x, ch, p["color"])
                except curses.error:
                    pass

        stdscr.refresh()

        # ---- End condition ----
        if two_player:
            if not p1["alive"] or not p2["alive"]:
                if not p1["alive"] and not p2["alive"]:
                    winner_msg = "Both snakes died — it's a draw!"
                elif not p1["alive"]:
                    winner_msg = "Player 2 (Arrows) wins!"
                else:
                    winner_msg = "Player 1 (WASD) wins!"
                running = False
        else:
            if not p1["alive"]:
                winner_msg = "Game over!"
                running = False

    # ---- Game over screen ----
    stdscr.nodelay(False)
    stdscr.timeout(-1)
    if two_player:
        msg = f"{winner_msg}  Final score — P1: {p1['score']}  P2: {p2['score']}   (press any key to exit)"
    else:
        msg = f"{winner_msg}  Final score: {p1['score']}   (press any key to exit)"
    try:
        stdscr.addstr(top_margin + board_h // 2, max(1, (board_w - len(msg)) // 2), msg,
                       curses.color_pair(3) | curses.A_BOLD)
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
