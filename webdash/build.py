#!/usr/bin/env python3
import subprocess
from pathlib import Path

TEMPLATE = Path("/home/mypi/webdash/template.html")
OUT = Path("/home/mypi/webdash/index.html")

def cmd(args, default="-"):
    try:
        out = subprocess.check_output(args, text=True).strip()
        return out or default
    except Exception:
        return default

def main():
    host = cmd(["hostname"])[:32]
    ip = cmd(["hostname", "-I"]).split()[0] if cmd(["hostname", "-I"]) != "-" else "-"
    up = cmd(["uptime", "-p"]).replace("up ", "")[:32]

    tpl = TEMPLATE.read_text(encoding="utf-8")
    html = (
        tpl
        .replace("{{HOSTNAME}}", host)
        .replace("{{IP}}", ip)
        .replace("{{UPTIME}}", up)
    )
    OUT.write_text(html, encoding="utf-8")

if __name__ == "__main__":
    main()

