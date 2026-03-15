#!/usr/bin/env python3
"""Graphical-style console dashboard for Waveshare 11.9" - panels, boxes, bar."""
import curses
import subprocess
from datetime import datetime

WAVESHARE_11_9_COLS = 40

# Box-drawing (use ASCII if terminal doesn't support Unicode)
try:
    B = {"tl": "\u250c", "tr": "\u2510", "bl": "\u2514", "br": "\u2518",
         "h": "\u2500", "v": "\u2502", "tl2": "\u256d", "tr2": "\u256e",
         "bl2": "\u2570", "br2": "\u256f"}
    BAR_FULL = "\u2588"   # full block
    BAR_EMPTY = "\u2591"  # light shade
except Exception:
    B = {"tl": "+", "tr": "+", "bl": "+", "br": "+", "h": "-", "v": "|",
         "tl2": "+", "tr2": "+", "bl2": "+", "br2": "+"}
    BAR_FULL = "#"
    BAR_EMPTY = "-"

def get_uptime():
    try:
        out = subprocess.check_output(["uptime", "-p"], text=True).strip().replace("up ", "")
        if not out:
            return "-"
        out = out.replace(" minutes", "m").replace(" minute", "m")
        out = out.replace(" hours", "h").replace(" hour", "h")
        out = out.replace(" days", "d").replace(" day", "d")
        out = out.replace(", ", "").replace("  ", " ")
        return out[:10] or "-"
    except Exception:
        return "-"

def get_ip():
    try:
        return subprocess.check_output(["hostname", "-I"], text=True).split()[0]
    except Exception:
        return "-"

def get_hostname():
    try:
        return subprocess.check_output(["hostname"], text=True).strip()[:8]
    except Exception:
        return "-"

def day_pct():
    """Fraction of day elapsed (0.0-1.0) for progress bar."""
    now = datetime.now()
    secs = now.hour * 3600 + now.minute * 60 + now.second
    return secs / 86400.0

def main(scr):
    curses.curs_set(0)
    scr.timeout(1000)
    try:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_WHITE, -1)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)
        green = curses.color_pair(1)
        cyan = curses.color_pair(2)
        white = curses.color_pair(3)
        inv_green = curses.color_pair(4)
    except Exception:
        green = cyan = white = inv_green = curses.A_NORMAL

    while True:
        try:
            scr.clear()
            h, w = scr.getmaxyx()
            max_w = min(w, WAVESHARE_11_9_COLS)
            if h < 10 or max_w < 20:
                try:
                    scr.addstr(0, 0, "MYSCREEN"[:max_w])
                except curses.error:
                    pass
                scr.refresh()
                continue

            max_col = max(0, max_w - 1)

            def add(r, c, text, attr=curses.A_NORMAL):
                if r < 0 or r >= h or c < 0:
                    return
                s = str(text)[: max_col - c]
                if not s:
                    return
                try:
                    scr.addstr(r, min(c, w - len(s)), s, attr)
                except curses.error:
                    pass

            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%a %b%d")
            hostname = get_hostname()
            ip = get_ip()
            uptime = get_uptime()
            pct = day_pct()
            bar_len = 14
            filled = int(pct * bar_len)
            bar = BAR_FULL * filled + BAR_EMPTY * (bar_len - filled)

            row = 0
            # Top border
            add(row, 0, B["tl"] + B["h"] * (max_w - 2) + B["tr"], cyan)
            row += 1
            # Title bar
            title = "  MYSCREEN  "
            add(row, 0, B["v"], cyan)
            add(row, 1, title.center(max_w - 2)[: max_w - 2], green)
            add(row, max_w - 1, B["v"], cyan)
            row += 1
            add(row, 0, B["tl2"] + B["h"] * (max_w - 2) + B["tr2"], cyan)
            row += 1
            # Clock panel (small box)
            add(row, 0, B["v"], cyan)
            add(row, 1, " " + B["tl"] + B["h"] * 10 + B["tr"] + " " * (max_w - 15), cyan)
            row += 1
            add(row, 0, B["v"] + " " + B["v"], cyan)
            add(row, 3, time_str.center(10), green)
            add(row, 13, B["v"] + " " * (max_w - 15) + B["v"], cyan)
            row += 1
            add(row, 0, B["v"] + " " + B["v"], cyan)
            add(row, 3, date_str.center(10), white)
            add(row, 13, B["v"] + " " * (max_w - 15) + B["v"], cyan)
            row += 1
            add(row, 0, B["v"] + " " + B["bl"] + B["h"] * 10 + B["br"] + " " * (max_w - 15) + B["v"], cyan)
            row += 1
            # Day progress bar
            add(row, 0, B["v"], cyan)
            day_txt = (" Day [" + bar + "] " + str(int(pct * 100)) + "%")[: max_w - 2]
            add(row, 1, day_txt, white)
            add(row, max_w - 1, B["v"], cyan)
            row += 1
            # Info lines
            add(row, 0, B["v"], cyan)
            add(row, 1, ("Host: " + hostname + "  " + ip)[: max_w - 2], white)
            add(row, max_w - 1, B["v"], cyan)
            row += 1
            add(row, 0, B["v"], cyan)
            add(row, 1, ("Up: " + uptime)[: max_w - 2], white)
            add(row, max_w - 1, B["v"], cyan)
            row += 1
            # Bottom border
            add(row, 0, B["bl"] + B["h"] * (max_w - 2) + B["br"], cyan)
            scr.refresh()
        except Exception:
            try:
                scr.clear()
                scr.addstr(0, 0, "MYSCREEN")
                scr.refresh()
            except Exception:
                pass

        key = scr.getch()
        if key == 27:
            break

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception:
        pass
    except KeyboardInterrupt:
        pass
