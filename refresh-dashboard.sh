#!/bin/bash
# Generate dashboard with current hostname, IP, uptime
D=/home/mypi/dashboard
H=$(hostname)
I=$(hostname -I | awk '{print $1}')
U=$(uptime -p 2>/dev/null | sed 's/^up //' || echo '--')
sed -e "s/{{HOSTNAME}}/$H/g" -e "s/{{IP}}/$I/g" -e "s#{{UPTIME}}#$U#g" "$D/template.html" > "$D/index.html"
