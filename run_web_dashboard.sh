#!/bin/bash
# Start X and Chromium kiosk on the Pi, serving the HTML dashboard.
# Does NOT change boot behaviour; you can reboot to go back to framebuffer dashboard.

set -e

DASH_DIR="/home/mypi/webdash"
cd "$DASH_DIR"

# Rebuild HTML with current host/IP/uptime
python3 build.py || true

# Start simple HTTP server in background if not already
if ! pgrep -f "python3 -m http.server 8080" >/dev/null 2>&1; then
  nohup python3 -m http.server 8080 >/tmp/webdash_http.log 2>&1 &
  sleep 1
fi

# Minimal .xinitrc for Chromium kiosk
cat > /home/mypi/.xinitrc << 'EOF'
#!/bin/sh
xset s off
xset s noblank
xset -dpms
openbox &
sleep 2
exec chromium --kiosk --noerrdialogs --disable-infobars --no-first-run --disable-session-crashed-bubble --disable-restore-session-state --incognito http://127.0.0.1:8080/
EOF
chmod +x /home/mypi/.xinitrc

# Run X on the current tty; when you reboot, you'll go back to the old behaviour
startx

