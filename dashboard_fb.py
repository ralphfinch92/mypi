#!/usr/bin/env python3
"""
Graphical dashboard drawn to the Linux framebuffer (/dev/fb0).
No X required - draws a real image (PIL) and writes to the display.
For Waveshare 11.9" 320x1480.
"""
import os
import sys
import time
import struct
import subprocess
import mmap
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Install: sudo apt install python3-pil", file=sys.stderr)
    sys.exit(1)

FB_DEV = "/dev/fb0"
FB_SYS = "/sys/class/graphics/fb0"
W, H = 320, 1480  # Waveshare 11.9"

# Rotate the *rendered image* before writing to the framebuffer.
# This avoids risky kernel-level HDMI rotation that previously caused black screen.
# 0, 90, 180, 270 are supported. You can change it via environment variable.
ROTATE_DEG = int(os.environ.get("MYSCREEN_ROTATE", "0"))


# --- Simple dummy candle data (normalized) for initial chart rendering ---
# Each candle: (open, high, low, close) in [0.0, 1.0] vertical range (0=bottom,1=top)
def _generate_dummy_candles(n=80):
    import math
    candles = []
    for i in range(n):
        t = i / max(1, n - 1)
        mid = 0.5 + 0.35 * math.sin(t * 3.0)
        height = 0.12 + 0.05 * math.cos(t * 5.0)
        low = max(0.05, mid - height)
        high = min(0.95, mid + height)
        body = height * 0.6
        if i % 2 == 0:
            o = mid - body / 2
            c = mid + body / 2
        else:
            o = mid + body / 2
            c = mid - body / 2
        candles.append((o, high, low, c))
    return candles


CANDLES = _generate_dummy_candles()

def get_fb_size():
    try:
        with open(os.path.join(FB_SYS, "virtual_size")) as f:
            s = f.read().strip()
            w, h = map(int, s.split(","))
            return w, h
    except Exception:
        return W, H

def get_uptime():
    try:
        out = subprocess.check_output(["uptime", "-p"], text=True).strip().replace("up ", "")
        out = out.replace(" minutes", "m").replace(" minute", "m").replace(" hours", "h").replace(" hour", "h")
        out = out.replace(" days", "d").replace(" day", "d").replace(", ", " ")
        return out[:14] or "-"
    except Exception:
        return "-"

def get_ip():
    try:
        return subprocess.check_output(["hostname", "-I"], text=True).split()[0]
    except Exception:
        return "-"

def get_hostname():
    try:
        return subprocess.check_output(["hostname"], text=True).strip()[:12]
    except Exception:
        return "-"

def rgb_to_rgb565(r, g, b):
    return (r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)

def image_to_rgb565_bytes(im):
    """Convert PIL RGB image to RGB565 packed bytes for framebuffer."""
    try:
        import numpy as np
        arr = np.array(im)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
        return rgb565.astype(np.uint16).byteswap().tobytes()
    except ImportError:
        w, h = im.size
        out = bytearray(w * h * 2)
        pix = im.load()
        for y in range(h):
            for x in range(w):
                r, g, b = pix[x, y][:3]
                v = rgb_to_rgb565(r, g, b)
                i = (y * w + x) * 2
                out[i] = v >> 8
                out[i + 1] = v & 0xFF
        return bytes(out)

def find_font(size=28):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _text_size(draw, text, font):
    """Text measurement helper compatible with multiple Pillow versions."""
    if hasattr(draw, "textbbox"):
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        return right - left, bottom - top
    return draw.textsize(text, font=font)


def _draw_candles(draw, x0, y0, x1, y1, candles):
    """Render simple candlesticks into the given rectangle."""
    if not candles:
        return
    width = max(1, x1 - x0)
    height = max(1, y1 - y0)

    # Layout: body 5px, gap 1px
    max_candles = min(len(candles), width // 6)
    if max_candles <= 0:
        return
    start = len(candles) - max_candles
    view = candles[start:]
    gap = 1
    body_w = 5

    # Colors
    up_color = (0x00, 0xff, 0x88)
    down_color = (0xff, 0x55, 0x55)
    wick_color = (0xdd, 0xdd, 0xdd)

    for idx, (o, h, l, c) in enumerate(view):
        # Clamp normalized values
        o = min(max(o, 0.0), 1.0)
        h = min(max(h, 0.0), 1.0)
        l = min(max(l, 0.0), 1.0)
        c = min(max(c, 0.0), 1.0)

        cx = x0 + idx * (body_w + gap) + body_w // 2

        # y mapping: 1.0 = top, 0.0 = bottom
        def ny(v):
            return int(y1 - v * height)

        yo = ny(o)
        yc = ny(c)
        yh = ny(h)
        yl = ny(l)

        # Wick
        draw.line([(cx, yh), (cx, yl)], fill=wick_color, width=1)

        # Body
        top_y = min(yo, yc)
        bot_y = max(yo, yc)
        if bot_y == top_y:  # make at least 1px high
            bot_y = top_y + 1

        color = up_color if c >= o else down_color
        draw.rectangle(
            [cx - body_w // 2, top_y, cx + (body_w - 1) // 2, bot_y],
            fill=color,
            outline=None,
        )

def draw_dashboard(w, h):
    """Draw trading-style dashboard into a logical canvas of size (w, h)."""
    # Base image
    im = Image.new("RGB", (w, h), (0x10, 0x10, 0x1e))
    draw = ImageDraw.Draw(im)

    # Colors
    bg = (0x10, 0x10, 0x1e)
    panel = (0x1e, 0x1e, 0x34)
    border = (0x30, 0x30, 0x50)
    cyan = (0x00, 0xd9, 0xff)
    white = (0xe8, 0xe8, 0xe8)
    muted = (0x99, 0x99, 0x99)

    # Data
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S UTC")
    date_str = now.strftime("%Y-%m-%d")
    hostname = get_hostname()
    ip = get_ip()
    uptime = get_uptime()

    # Fonts: larger, cleaner
    try:
        font_header = find_font(22)
        font_small = find_font(16)
    except Exception:
        font_header = font_small = ImageFont.load_default()

    # Layout metrics (landscape canvas, e.g. 1480x320)
    header_h = 44           # SECTION 1 height
    footer_h = 44           # SECTION 3 height
    gap = 4
    chart_top = header_h + gap
    chart_bottom = max(chart_top + 80, h - footer_h - gap)

    # ========== SECTION 1: HEADER BAR ==========
    draw.rectangle([0, 0, w, header_h], fill=panel)
    draw.line([(0, header_h - 1), (w, header_h - 1)], fill=border)

    title_text = "MYSCREEN DASHBOARD"
    draw.text((10, 8), title_text, fill=cyan, font=font_header)

    # Right: time + date (stacked, right-aligned)
    ts = time_str
    ds = date_str
    tw, th = _text_size(draw, ts, font_small)
    dw, dh = _text_size(draw, ds, font_small)
    right_x = w - 10
    time_x = right_x - tw
    date_x = right_x - dw
    draw.text((time_x, 4), ts, fill=white, font=font_small)
    draw.text((date_x, 4 + th + 2), ds, fill=muted, font=font_small)

    # ========== SECTION 2: MAIN CHART AREA ==========
    chart_left = 8
    chart_right = w - 8
    draw.rectangle(
        [chart_left, chart_top, chart_right, chart_bottom],
        fill=panel,
        outline=border,
        width=1,
    )

    label = "Price chart"
    lw, lh = _text_size(draw, label, font_small)
    draw.text(
        (chart_left + 6, chart_top + 4),
        label,
        fill=muted,
        font=font_small,
    )

    # Candlestick plot area (leave a small margin inside panel)
    pad_y = 10
    candle_top = chart_top + lh + pad_y
    candle_bottom = chart_bottom - 8
    if candle_bottom > candle_top + 8:
        _draw_candles(
            draw,
            chart_left + 4,
            candle_top,
            chart_right - 4,
            candle_bottom,
            CANDLES,
        )

    # ========== SECTION 3: STATUS BAR ==========
    footer_top = h - footer_h
    draw.rectangle([0, footer_top, w, h], fill=panel)
    draw.line([(0, footer_top), (w, footer_top)], fill=border)

    status = f"Host: {hostname}   IP: {ip}   Up: {uptime}"
    max_status_width = w - 20
    while True:
        sw, _ = _text_size(draw, status, font_small)
        if sw <= max_status_width or len(status) <= 3:
            break
        status = status[:-4] + "..."

    draw.text(
        (10, footer_top + (footer_h - 18) // 2),
        status,
        fill=white,
        font=font_small,
    )

    return im

def rotate_for_framebuffer(im, w, h):
    deg = ROTATE_DEG % 360
    if deg == 0:
        return im
    # PIL rotate with expand keeps full image; then we center-crop / letterbox to fb size.
    rim = im.rotate(deg, expand=True)
    if rim.size == (w, h):
        return rim
    # Fit rotated image into framebuffer size while preserving content
    out = Image.new("RGB", (w, h), (0x1a, 0x1a, 0x2e))
    rw, rh = rim.size
    # center-crop if larger, else center-place
    sx = max(0, (rw - w) // 2)
    sy = max(0, (rh - h) // 2)
    crop = rim.crop((sx, sy, sx + min(w, rw), sy + min(h, rh)))
    cx = max(0, (w - crop.size[0]) // 2)
    cy = max(0, (h - crop.size[1]) // 2)
    out.paste(crop, (cx, cy))
    return out

def main():
    fb_w, fb_h = get_fb_size()
    # Logical canvas we draw into before rotation: for 90/270, use landscape canvas.
    if ROTATE_DEG % 180 == 90:
        w, h = fb_h, fb_w
    else:
        w, h = fb_w, fb_h
    size_bytes = fb_w * fb_h * 2  # 16 bpp

    try:
        fb = os.open(FB_DEV, os.O_RDWR)
    except PermissionError:
        print("Run as user in 'video' group or with access to", FB_DEV, file=sys.stderr)
        sys.exit(1)

    try:
        mem = mmap.mmap(fb, size_bytes, mmap.MAP_SHARED, mmap.PROT_WRITE)
    except Exception as e:
        print("Framebuffer mmap failed:", e, file=sys.stderr)
        os.close(fb)
        sys.exit(1)

    try:
        while True:
            im = draw_dashboard(w, h)
            im = rotate_for_framebuffer(im, fb_w, fb_h)
            raw = image_to_rgb565_bytes(im)
            if len(raw) != size_bytes:
                raw = raw[:size_bytes].ljust(size_bytes, b"\x00")
            mem.seek(0)
            mem.write(raw)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        mem.close()
        os.close(fb)

if __name__ == "__main__":
    main()
