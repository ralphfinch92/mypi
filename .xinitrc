#!/bin/sh
# Minimal X session: disable blanking and run Chromium kiosk on local dashboard
xset s off
xset s noblank
xset -dpms
openbox &
sleep 2
# Safer flags for Pi: disable GPU and sandbox quirks
exec chromium \
  --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --disable-session-crashed-bubble \
  --disable-restore-session-state \
  --disable-gpu \
  --use-gl=egl \
  --incognito \
  http://127.0.0.1:8080/

