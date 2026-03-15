#!/usr/bin/env python3
"""Simple fullscreen dashboard for MyScreen - no browser required."""
import tkinter as tk
import subprocess
from datetime import datetime

def get_ip():
    try:
        return subprocess.check_output(["hostname", "-I"], text=True).split()[0]
    except Exception:
        return "—"

def get_uptime():
    try:
        out = subprocess.check_output(["uptime", "-p"], text=True).strip().replace("up ", "")
        return out or "—"
    except Exception:
        return "—"

def main():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg="#1a1a2e")
    root.bind("<Escape>", lambda e: root.quit())

    # Colors
    bg = "#1a1a2e"
    fg = "#e8e8e8"
    accent = "#00ff88"

    main_frame = tk.Frame(root, bg=bg, padx=60, pady=40)
    main_frame.pack(expand=True, fill="both")

    tk.Label(main_frame, text="MYSCREEN", font=("DejaVu Sans", 36, "bold"),
             fg=accent, bg=bg).pack(pady=(0, 5))
    tk.Label(main_frame, text="Raspberry Pi display", font=("DejaVu Sans", 12),
             fg=fg, bg=bg).pack(pady=(0, 30))

    time_label = tk.Label(main_frame, text="", font=("DejaVu Sans", 56),
                         fg=accent, bg=bg)
    time_label.pack(pady=15)
    date_label = tk.Label(main_frame, text="", font=("DejaVu Sans", 16),
                         fg=fg, bg=bg)
    date_label.pack(pady=(0, 30))

    info_frame = tk.Frame(main_frame, bg=bg)
    info_frame.pack(pady=20)

    hostname = subprocess.check_output(["hostname"], text=True).strip()
    ip = get_ip()
    uptime = get_uptime()

    for label, value in [("Hostname", hostname), ("IP", ip), ("Uptime", uptime)]:
        f = tk.Frame(info_frame, bg="#2a2a4e", padx=20, pady=12)
        f.pack(side="left", padx=10, pady=5)
        tk.Label(f, text=label.upper(), font=("DejaVu Sans", 9), fg="#888", bg="#2a2a4e").pack(anchor="w")
        tk.Label(f, text=value, font=("DejaVu Sans", 14, "bold"), fg=fg, bg="#2a2a4e").pack(anchor="w")

    def update_time():
        now = datetime.now()
        time_label.config(text=now.strftime("%H:%M:%S"))
        date_label.config(text=now.strftime("%A, %B %d, %Y"))
        root.after(1000, update_time)

    update_time()
    root.mainloop()

if __name__ == "__main__":
    main()
