#!/bin/bash
# Run from .profile on tty1: show graphical dashboard on framebuffer (no X)
# If fb script exits, fall back to console dashboard then retry
while true; do
  # Rotate the rendered framebuffer image so the physical screen can be used in landscape.
  MYSCREEN_ROTATE=90 python3 /home/mypi/dashboard_fb.py
  export TERM=linux
  python3 /home/mypi/dashboard_console.py
  sleep 2
done
