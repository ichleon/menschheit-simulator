"""
╔══════════════════════════════════════════════╗
║     HUMANITY SIMULATION  — by Claude         ║
╚══════════════════════════════════════════════╝
Requires: pip install tkinter matplotlib pandas numpy
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import random
import json
import csv
import os
from datetime import datetime
from collections import deque
import threading
import time

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    import matplotlib.figure as mfig
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.animation import FuncAnimation
    import matplotlib.patches as mpatches
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False

# ─────────────────────────────────────────────
#  SIMULATION ENGINE
# ─────────────────────────────────────────────
EVENTS = {
    "Große Pest": {
        "prob": 0.003, "duration": (5, 20),
        "birth_mod": 0.6, "death_mod": 3.5,
        "color": "#8B0000", "icon": "☣",
        "desc": "Eine verheerende Seuche dezimiert die Bevölkerung."
    },
    "Weltkrieg": {
        "prob": 0.004, "duration": (4, 8),
        "birth_mod": 0.5, "death_mod": 4.0,
        "color": "#4A0000", "icon": "⚔",
        "desc": "Globaler Konflikt fordert Millionen Leben."
    },
    "Industrialisierung": {
        "prob": 0.006, "duration": (15, 40),
        "birth_mod": 1.3, "death_mod": 0.8,
        "color": "#1a472a", "icon": "🏭",
        "desc": "Technologischer Fortschritt verbessert Lebensqualität."
    },
    "Hungersnot": {
        "prob": 0.005, "duration": (3, 10),
        "birth_mod": 0.7, "death_mod": 2.2,
        "color": "#7B3F00", "icon": "🌾",
        "desc": "Nahrungsmangel trifft die Bevölkerung hart."
    },
    "Medizinischer Durchbruch": {
        "prob": 0.007, "duration": (20, 50),
        "birth_mod": 1.1, "death_mod": 0.5,
        "color": "#003366", "icon": "💉",
        "desc": "Neue Medizin rettet unzählige Leben."
    },
    "Babyboом": {
        "prob": 0.005, "duration": (10, 20),
        "birth_mod": 1.8, "death_mod": 0.9,
        "color": "#4B0082", "icon": "👶",
        "desc": "Nachkriegszeit löst Geburtenwelle aus."
    },
    "Klimakatastrophe": {
        "prob": 0.004, "duration": (10, 30),
        "birth_mod": 0.75, "death_mod": 1.8,
        "color": "#FF6600", "icon": "🌡",
        "desc": "Extremwetter destabilisiert Gesellschaften."
    },
    "Goldenes Zeitalter": {
        "prob": 0.004, "duration": (20, 60),
        "birth_mod": 1.25, "death_mod": 0.7,
        "color": "#8B6914", "icon": "✨",
        "desc": "Frieden und Wohlstand fördern Wachstum."
    },
    "Asteroid": {
        "prob": 0.0008, "duration": (1, 3),
        "birth_mod": 0.2, "death_mod": 8.0,
        "color": "#2F1B0E", "icon": "☄",
        "desc": "Einschlag eines Himmelskörpers."
    },
    "Revolution": {
        "prob": 0.005, "duration": (2, 10),
        "birth_mod": 0.8, "death_mod": 1.6,
        "color": "#C0392B", "icon": "✊",
        "desc": "Politischer Umsturz erschüttert die Gesellschaft."
    },
}

class SimulationEngine:
    def __init__(self):
        self.reset()

    def reset(self, start_pop=7_900_000_000, start_year=2024,
              base_birth=18.5, base_death=7.7,
              speed=1, random_events=True):
        self.year = start_year
        self.population = float(start_pop)
        self.base_birth_rate = base_birth / 1000   # per capita per year
        self.base_death_rate = base_death / 1000
        self.speed = speed
        self.random_events = random_events

        self.active_events = {}   # name -> years_remaining
        self.event_log = []       # list of dicts
        self.history = []         # list of yearly snapshots

        self._birth_mod = 1.0
        self._death_mod = 1.0
        self._record_year()

    def _record_year(self):
        self.history.append({
            "year": self.year,
            "population": self.population,
            "birth_rate": self.base_birth_rate * self._birth_mod * 1000,
            "death_rate": self.base_death_rate * self._death_mod * 1000,
            "net_growth": (self.base_birth_rate * self._birth_mod -
                           self.base_death_rate * self._death_mod) * 1000,
            "events": list(self.active_events.keys()),
            "births": self.population * self.base_birth_rate * self._birth_mod,
            "deaths": self.population * self.base_death_rate * self._death_mod,
        })

    def step(self, years=1):
        """Advance simulation by N years."""
        new_events = []
        for _ in range(years):
            # ── expire events ──
            to_remove = [k for k, v in self.active_events.items() if v <= 0]
            for k in to_remove:
                del self.active_events[k]
                self.event_log.append({
                    "year": self.year, "name": k, "type": "end",
                    "color": EVENTS[k]["color"]
                })

            # ── decrement active ──
            for k in list(self.active_events):
                self.active_events[k] -= 1

            # ── trigger new events ──
            if self.random_events:
                for name, cfg in EVENTS.items():
                    if name not in self.active_events:
                        if random.random() < cfg["prob"]:
                            dur = random.randint(*cfg["duration"])
                            self.active_events[name] = dur
                            new_events.append(name)
                            self.event_log.append({
                                "year": self.year, "name": name,
                                "type": "start", "color": cfg["color"],
                                "icon": cfg["icon"], "desc": cfg["desc"],
                                "duration": dur
                            })

            # ── compute effective rates ──
            bm, dm = 1.0, 1.0
            for name in self.active_events:
                bm *= EVENTS[name]["birth_mod"]
                dm *= EVENTS[name]["death_mod"]
            self._birth_mod = bm
            self._death_mod = dm

            births = self.population * self.base_birth_rate * bm
            deaths = self.population * self.base_death_rate * dm
            self.population = max(0, self.population + births - deaths)
            self.year += 1
            self._record_year()

            if self.population <= 0:
                break

        return new_events

    @property
    def growth_rate(self):
        if len(self.history) < 2:
            return 0
        h = self.history
        return (h[-1]["net_growth"])

    @property
    def extinct(self):
        return self.population <= 0

    def export_csv(self, path):
        keys = ["year", "population", "birth_rate", "death_rate",
                "net_growth", "births", "deaths", "events"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for row in self.history:
                r = dict(row)
                r["events"] = "|".join(r["events"])
                w.writerow(r)

    def export_json(self, path):
        data = {
            "metadata": {
                "exported": datetime.now().isoformat(),
                "years_simulated": len(self.history),
                "final_population": self.population,
            },
            "history": self.history,
            "event_log": self.event_log
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────────
BG        = "#0A0E1A"
BG2       = "#111827"
BG3       = "#1C2333"
ACCENT    = "#4FC3F7"
ACCENT2   = "#81C784"
ACCENT3   = "#FF7043"
ACCENT4   = "#CE93D8"
TEXT      = "#E8EAF6"
TEXT_DIM  = "#78909C"
BORDER    = "#263238"
FONT_MONO = ("Courier New", 10)
FONT_HEAD = ("Georgia", 22, "bold")
FONT_NUM  = ("Courier New", 28, "bold")
FONT_LABEL= ("Georgia", 9)

def fmt_pop(n):
    if n >= 1e12: return f"{n/1e12:.3f} Bio."
    if n >= 1e9:  return f"{n/1e9:.3f} Mrd."
    if n >= 1e6:  return f"{n/1e6:.3f} Mio."
    if n >= 1e3:  return f"{n/1e3:.1f} Tsd."
    return str(int(n))


class HumanityApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HUMANITY — Zivilisationssimulation")
        self.configure(bg=BG)
        self.geometry("1400x900")
        self.minsize(1100, 750)
        self.resizable(True, True)

        self.sim = SimulationEngine()
        self._running = False
        self._run_thread = None
        self._recent_events = deque(maxlen=8)
        self._chart_mode = tk.StringVar(value="population")

        self._build_styles()
        self._build_layout()
        self._update_display()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Styles ─────────────────────────────────
    def _build_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame", background=BG)
        s.configure("Dark.TFrame", background=BG2)
        s.configure("Card.TFrame", background=BG3)
        s.configure("TLabel", background=BG, foreground=TEXT,
                    font=FONT_MONO)
        s.configure("Head.TLabel", background=BG, foreground=ACCENT,
                    font=("Georgia", 11, "bold"))
        s.configure("Num.TLabel", background=BG3, foreground=ACCENT,
                    font=FONT_NUM)
        s.configure("TScale", background=BG2, troughcolor=BG3,
                    sliderlength=20)
        s.configure("Accent.TButton",
                    background=ACCENT, foreground=BG,
                    font=("Courier New", 10, "bold"),
                    borderwidth=0, padding=6)
        s.map("Accent.TButton",
              background=[("active", "#81D4FA"), ("disabled", BG3)],
              foreground=[("disabled", TEXT_DIM)])
        s.configure("Red.TButton",
                    background=ACCENT3, foreground="#fff",
                    font=("Courier New", 10, "bold"),
                    borderwidth=0, padding=6)
        s.configure("Green.TButton",
                    background=ACCENT2, foreground=BG,
                    font=("Courier New", 10, "bold"),
                    borderwidth=0, padding=6)
        s.configure("TCombobox", fieldbackground=BG3, background=BG3,
                    foreground=TEXT, selectbackground=BG3)
        s.configure("Horizontal.TProgressbar",
                    troughcolor=BG3, background=ACCENT,
                    thickness=6)

    # ── Layout ─────────────────────────────────
    def _build_layout(self):
        # Header
        header = tk.Frame(self, bg=BG, height=56)
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="⬡ HUMANITY", font=("Georgia", 20, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left", padx=24, pady=12)
        tk.Label(header, text="Zivilisationssimulation",
                 font=("Georgia", 10, "italic"),
                 bg=BG, fg=TEXT_DIM).pack(side="left", pady=16)
        self._lbl_year = tk.Label(header, text="Jahr 2024",
                                  font=("Courier New", 13, "bold"),
                                  bg=BG, fg=ACCENT4)
        self._lbl_year.pack(side="right", padx=24)

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x")

        # Main body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=8)

        # Left panel (controls)
        left = tk.Frame(body, bg=BG2, width=260, bd=0)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)
        self._build_left(left)

        # Center (chart + stats)
        center = tk.Frame(body, bg=BG)
        center.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._build_center(center)

        # Right panel (event log)
        right = tk.Frame(body, bg=BG2, width=270)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_right(right)

    def _section(self, parent, title):
        tk.Label(parent, text=title.upper(),
                 font=("Courier New", 8, "bold"),
                 bg=BG2, fg=TEXT_DIM).pack(anchor="w", padx=14, pady=(14, 2))
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=10, pady=2)

    def _build_left(self, parent):
        self._section(parent, "Parameter")

        def slider_row(lbl, from_, to, var, fmt="{:.1f}", row_lbl=None):
            f = tk.Frame(parent, bg=BG2)
            f.pack(fill="x", padx=12, pady=3)
            tk.Label(f, text=lbl, bg=BG2, fg=TEXT_DIM,
                     font=FONT_MONO, width=20, anchor="w").pack(side="left")
            disp = tk.Label(f, text=fmt.format(var.get()),
                            bg=BG2, fg=ACCENT, font=FONT_MONO, width=7)
            disp.pack(side="right")
            sc = ttk.Scale(parent, from_=from_, to=to, variable=var,
                           orient="horizontal",
                           command=lambda v, d=disp, f=fmt: d.config(
                               text=f.format(float(v))))
            sc.pack(fill="x", padx=14, pady=1)
            return sc

        self._var_birth  = tk.DoubleVar(value=18.5)
        self._var_death  = tk.DoubleVar(value=7.7)
        self._var_pop    = tk.DoubleVar(value=7900)  # millions
        self._var_year   = tk.IntVar(value=2024)
        self._var_speed  = tk.IntVar(value=1)
        self._var_events = tk.BooleanVar(value=True)

        slider_row("Geburtenrate ‰", 0.5, 50, self._var_birth)
        slider_row("Sterberate ‰",   0.5, 40, self._var_death)
        slider_row("Startpop. (Mio)", 1, 20000, self._var_pop, "{:.0f}")
        slider_row("Startjahr",       0, 2100, self._var_year, "{:.0f}")
        slider_row("Sim-Speed (J/Schritt)", 1, 100, self._var_speed, "{:.0f}")

        f = tk.Frame(parent, bg=BG2)
        f.pack(fill="x", padx=14, pady=6)
        tk.Checkbutton(f, text=" Zufallsereignisse",
                       variable=self._var_events,
                       bg=BG2, fg=TEXT, selectcolor=BG3,
                       activebackground=BG2, activeforeground=ACCENT,
                       font=FONT_MONO).pack(anchor="w")

        self._section(parent, "Steuerung")

        btn_frame = tk.Frame(parent, bg=BG2)
        btn_frame.pack(fill="x", padx=12, pady=4)
        self._btn_start = ttk.Button(btn_frame, text="▶  START",
                                     style="Green.TButton",
                                     command=self._toggle_run)
        self._btn_start.pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="↺  RESET",
                   style="Red.TButton",
                   command=self._do_reset).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="⏭  +1 Jahr",
                   style="Accent.TButton",
                   command=lambda: self._step(1)).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="⏭  +10 Jahre",
                   style="Accent.TButton",
                   command=lambda: self._step(10)).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="⏭  +100 Jahre",
                   style="Accent.TButton",
                   command=lambda: self._step(100)).pack(fill="x", pady=2)

        self._section(parent, "Manuelles Ereignis")
        self._var_manual_event = tk.StringVar(value=list(EVENTS.keys())[0])
        cb = ttk.Combobox(parent, textvariable=self._var_manual_event,
                          values=list(EVENTS.keys()), state="readonly")
        cb.pack(fill="x", padx=12, pady=4)
        ttk.Button(parent, text="⚡ Ereignis auslösen",
                   style="Accent.TButton",
                   command=self._trigger_manual_event
                   ).pack(fill="x", padx=12, pady=2)

        self._section(parent, "Export")
        ttk.Button(parent, text="📊 CSV exportieren",
                   style="Accent.TButton",
                   command=lambda: self._export("csv")
                   ).pack(fill="x", padx=12, pady=2)
        ttk.Button(parent, text="📋 JSON exportieren",
                   style="Accent.TButton",
                   command=lambda: self._export("json")
                   ).pack(fill="x", padx=12, pady=2)
        if HAS_MPL:
            ttk.Button(parent, text="📈 Chart speichern",
                       style="Accent.TButton",
                       command=self._save_chart
                       ).pack(fill="x", padx=12, pady=2)

    def _build_center(self, parent):
        # Stat cards row
        cards = tk.Frame(parent, bg=BG)
        cards.pack(fill="x", pady=(0, 8))

        self._stat_widgets = {}
        stats = [
            ("🌍 Bevölkerung", "pop",  ACCENT),
            ("👶 Geburten/J",  "births", ACCENT2),
            ("💀 Tote/J",      "deaths", ACCENT3),
            ("📈 Wachstum ‰",  "growth", ACCENT4),
        ]
        for title, key, color in stats:
            card = tk.Frame(cards, bg=BG3, bd=0)
            card.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(card, text=title, bg=BG3, fg=TEXT_DIM,
                     font=("Georgia", 9, "italic")).pack(pady=(10, 2))
            lbl = tk.Label(card, text="—", bg=BG3, fg=color,
                           font=("Courier New", 16, "bold"))
            lbl.pack(pady=(0, 10))
            self._stat_widgets[key] = lbl

        # Chart area
        chart_frame = tk.Frame(parent, bg=BG3, bd=0)
        chart_frame.pack(fill="both", expand=True)

        # Chart mode selector
        sel_frame = tk.Frame(chart_frame, bg=BG3)
        sel_frame.pack(anchor="w", padx=10, pady=6)
        for label, val in [("Bevölkerung", "population"),
                            ("Geburten/Tode", "rates"),
                            ("Wachstum", "growth")]:
            rb = tk.Radiobutton(sel_frame, text=label,
                                variable=self._chart_mode, value=val,
                                bg=BG3, fg=TEXT_DIM,
                                selectcolor=BG3,
                                activebackground=BG3,
                                activeforeground=ACCENT,
                                font=FONT_MONO,
                                command=self._redraw_chart)
            rb.pack(side="left", padx=8)

        if HAS_MPL:
            self._fig = mfig.Figure(figsize=(8, 4), dpi=96,
                                    facecolor=BG3)
            self._ax  = self._fig.add_subplot(111)
            self._setup_ax()
            self._canvas = FigureCanvasTkAgg(self._fig, master=chart_frame)
            self._canvas.get_tk_widget().pack(fill="both", expand=True,
                                              padx=4, pady=4)
        else:
            # Fallback: canvas-based chart
            self._chart_canvas = tk.Canvas(chart_frame, bg="#0d1117",
                                           highlightthickness=0)
            self._chart_canvas.pack(fill="both", expand=True, padx=4, pady=4)

        # Active events strip
        self._active_frame = tk.Frame(parent, bg=BG)
        self._active_frame.pack(fill="x", pady=(6, 0))

    def _setup_ax(self):
        ax = self._ax
        ax.set_facecolor("#0D1117")
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        ax.spines["bottom"].set_color(BORDER)
        ax.spines["left"].set_color(BORDER)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.xaxis.label.set_color(TEXT_DIM)
        ax.yaxis.label.set_color(TEXT_DIM)
        self._fig.tight_layout(pad=1.5)

    def _build_right(self, parent):
        tk.Label(parent, text="EREIGNISPROTOKOLL",
                 font=("Courier New", 8, "bold"),
                 bg=BG2, fg=TEXT_DIM).pack(anchor="w", padx=14, pady=(14, 2))
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=10, pady=2)

        container = tk.Frame(parent, bg=BG2)
        container.pack(fill="both", expand=True, padx=6, pady=4)

        sb = tk.Scrollbar(container, bg=BG3, troughcolor=BG2,
                          width=8, relief="flat", borderwidth=0)
        sb.pack(side="right", fill="y")

        self._log_text = tk.Text(
            container, bg=BG2, fg=TEXT, font=("Courier New", 9),
            relief="flat", borderwidth=0, cursor="arrow",
            state="disabled", wrap="word",
            yscrollcommand=sb.set,
            selectbackground=BG3,
        )
        self._log_text.pack(fill="both", expand=True)
        sb.config(command=self._log_text.yview)

        # Color tags
        for name, cfg in EVENTS.items():
            self._log_text.tag_config(name, foreground=cfg["color"])
        self._log_text.tag_config("dim", foreground=TEXT_DIM)
        self._log_text.tag_config("end_tag", foreground="#546E7A")

        # Extinction label (hidden)
        self._extinct_lbl = tk.Label(
            parent, text="💀 MENSCHHEIT AUSGESTORBEN",
            font=("Georgia", 13, "bold"), bg=BG2, fg=ACCENT3
        )

    # ── Helpers ────────────────────────────────
    def _log(self, text, tag="dim"):
        t = self._log_text
        t.config(state="normal")
        t.insert("end", text + "\n", tag)
        t.see("end")
        t.config(state="disabled")

    def _update_display(self):
        s = self.sim
        h = s.history[-1] if s.history else {}

        self._lbl_year.config(text=f"Jahr {s.year}")
        self._stat_widgets["pop"].config(text=fmt_pop(s.population))
        self._stat_widgets["births"].config(
            text=fmt_pop(h.get("births", 0)))
        self._stat_widgets["deaths"].config(
            text=fmt_pop(h.get("deaths", 0)))

        gr = h.get("net_growth", 0)
        color = ACCENT2 if gr >= 0 else ACCENT3
        self._stat_widgets["growth"].config(
            text=f"{gr:+.2f}", fg=color)

        # Active events strip
        for w in self._active_frame.winfo_children():
            w.destroy()
        if s.active_events:
            tk.Label(self._active_frame, text="AKTIV:",
                     bg=BG, fg=TEXT_DIM,
                     font=("Courier New", 8)).pack(side="left", padx=(4, 2))
            for name, rem in s.active_events.items():
                cfg = EVENTS[name]
                badge = tk.Label(
                    self._active_frame,
                    text=f"{cfg['icon']} {name} ({rem}J)",
                    bg=cfg["color"], fg="#fff",
                    font=("Courier New", 8, "bold"),
                    padx=6, pady=2
                )
                badge.pack(side="left", padx=2)

        if HAS_MPL:
            self._redraw_chart()
        else:
            self._redraw_canvas_chart()

        if s.extinct:
            self._extinct_lbl.pack(pady=6)
            self._stop()

    def _redraw_chart(self):
        if not HAS_MPL or len(self.sim.history) < 2:
            return
        ax = self._ax
        ax.cla()
        self._setup_ax()

        mode = self._chart_mode.get()
        years = [h["year"] for h in self.sim.history]

        if mode == "population":
            pop = [h["population"] / 1e9 for h in self.sim.history]
            ax.fill_between(years, pop, alpha=0.15, color=ACCENT)
            ax.plot(years, pop, color=ACCENT, linewidth=1.8)
            ax.set_ylabel("Mrd. Menschen", color=TEXT_DIM, fontsize=8)
            ax.set_title("Weltbevölkerung", color=TEXT, fontsize=10, pad=8)

        elif mode == "rates":
            br = [h["birth_rate"] for h in self.sim.history]
            dr = [h["death_rate"] for h in self.sim.history]
            ax.fill_between(years, br, alpha=0.12, color=ACCENT2)
            ax.fill_between(years, dr, alpha=0.12, color=ACCENT3)
            ax.plot(years, br, color=ACCENT2, linewidth=1.5, label="Geburten ‰")
            ax.plot(years, dr, color=ACCENT3, linewidth=1.5, label="Tode ‰")
            ax.legend(facecolor=BG3, labelcolor=TEXT, fontsize=8, framealpha=0.8)
            ax.set_ylabel("‰", color=TEXT_DIM, fontsize=8)
            ax.set_title("Geburten- & Sterberate", color=TEXT, fontsize=10, pad=8)

        elif mode == "growth":
            gr = [h["net_growth"] for h in self.sim.history]
            colors = [ACCENT2 if g >= 0 else ACCENT3 for g in gr]
            ax.bar(years, gr, color=colors, alpha=0.75, width=max(0.8, 1))
            ax.axhline(0, color=BORDER, linewidth=0.8)
            ax.set_ylabel("Nettowachstum ‰", color=TEXT_DIM, fontsize=8)
            ax.set_title("Bevölkerungswachstum", color=TEXT, fontsize=10, pad=8)

        # Event markers
        for ev in self.sim.event_log:
            if ev["type"] == "start":
                ax.axvline(ev["year"], color=ev["color"],
                           alpha=0.45, linewidth=1, linestyle="--")

        ax.set_xlabel("Jahr", color=TEXT_DIM, fontsize=8)
        self._fig.tight_layout(pad=1.5)
        self._canvas.draw_idle()

    def _redraw_canvas_chart(self):
        """Simple fallback chart without matplotlib."""
        c = self._chart_canvas
        c.delete("all")
        w = c.winfo_width() or 600
        h = c.winfo_height() or 300
        if len(self.sim.history) < 2:
            return
        hist = self.sim.history
        pop = [r["population"] for r in hist]
        mn, mx = min(pop), max(pop)
        if mx == mn: mx = mn + 1
        pad = 40
        def px(i): return pad + (i / (len(hist) - 1)) * (w - 2*pad)
        def py(v): return h - pad - ((v - mn) / (mx - mn)) * (h - 2*pad)

        pts = []
        for i, v in enumerate(pop):
            pts += [px(i), py(v)]
        if len(pts) >= 4:
            c.create_line(pts, fill=ACCENT, width=2, smooth=True)
        # axes
        c.create_line(pad, pad, pad, h-pad, fill=BORDER, width=1)
        c.create_line(pad, h-pad, w-pad, h-pad, fill=BORDER, width=1)
        c.create_text(w//2, 12, text="Weltbevölkerung",
                      fill=TEXT, font=("Courier New", 9))

    # ── Simulation control ─────────────────────
    def _step(self, n=None):
        if n is None:
            n = int(self._var_speed.get())
        new_evs = self.sim.step(n)
        for ev_name in new_evs:
            cfg = EVENTS[ev_name]
            self._log(
                f"[{self.sim.year}] {cfg['icon']} {ev_name} — {cfg['desc']}",
                ev_name
            )
        self._update_display()

    def _toggle_run(self):
        if self._running:
            self._stop()
        else:
            self._start()

    def _start(self):
        self._running = True
        self._btn_start.config(text="⏸  PAUSE")
        self._run_loop()

    def _stop(self):
        self._running = False
        self._btn_start.config(text="▶  START")

    def _run_loop(self):
        if not self._running:
            return
        if self.sim.extinct:
            self._stop()
            return
        self._step()
        # schedule next tick: ~50ms for fast, 200ms for slow
        delay = max(30, 200 - int(self._var_speed.get()) * 2)
        self.after(delay, self._run_loop)

    def _do_reset(self):
        self._stop()
        self._log_text.config(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.config(state="disabled")
        self._extinct_lbl.pack_forget()
        for w in self._active_frame.winfo_children():
            w.destroy()

        self.sim.reset(
            start_pop=self._var_pop.get() * 1e6,
            start_year=int(self._var_year.get()),
            base_birth=self._var_birth.get(),
            base_death=self._var_death.get(),
            speed=int(self._var_speed.get()),
            random_events=self._var_events.get(),
        )
        self._update_display()
        self._log(f"[{self.sim.year}] Simulation zurückgesetzt.", "dim")

    def _trigger_manual_event(self):
        name = self._var_manual_event.get()
        if name in self.sim.active_events:
            messagebox.showinfo("Info", f"'{name}' ist bereits aktiv.")
            return
        cfg = EVENTS[name]
        dur = random.randint(*cfg["duration"])
        self.sim.active_events[name] = dur
        self.sim.event_log.append({
            "year": self.sim.year, "name": name, "type": "start",
            "color": cfg["color"], "icon": cfg["icon"],
            "desc": cfg["desc"] + " [manuell]", "duration": dur
        })
        self._log(f"[{self.sim.year}] ⚡ {cfg['icon']} {name} manuell ausgelöst!", name)
        self._update_display()

    # ── Export ─────────────────────────────────
    def _export(self, fmt):
        ext = "csv" if fmt == "csv" else "json"
        path = filedialog.asksaveasfilename(
            defaultextension=f".{ext}",
            filetypes=[(f"{ext.upper()}-Dateien", f"*.{ext}"),
                       ("Alle Dateien", "*.*")],
            initialfile=f"humanity_sim_{self.sim.year}.{ext}"
        )
        if not path:
            return
        try:
            if fmt == "csv":
                self.sim.export_csv(path)
            else:
                self.sim.export_json(path)
            messagebox.showinfo("Export erfolgreich",
                                f"Daten gespeichert:\n{path}")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def _save_chart(self):
        if not HAS_MPL:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG-Bild", "*.png"), ("SVG-Grafik", "*.svg")],
            initialfile=f"humanity_chart_{self.sim.year}.png"
        )
        if path:
            self._fig.savefig(path, dpi=150, bbox_inches="tight",
                              facecolor=BG3)
            messagebox.showinfo("Gespeichert", f"Chart gespeichert:\n{path}")

    def _on_close(self):
        # Auto-save to autosave folder
        os.makedirs("autosave", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = f"autosave/humanity_sim_{timestamp}.csv"
        json_path = f"autosave/humanity_sim_{timestamp}.json"
        try:
            self.sim.export_csv(csv_path)
            self.sim.export_json(json_path)
        except Exception as e:
            print(f"Auto-save failed: {e}")
        self.destroy()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    missing = []
    try: import matplotlib
    except ImportError: missing.append("matplotlib")
    try: import numpy
    except ImportError: missing.append("numpy")

    if missing:
        print(f"[INFO] Optionale Pakete fehlen: {', '.join(missing)}")
        print("       Installieren mit: pip install " + " ".join(missing))
        print("       Die App läuft auch ohne diese Pakete (vereinfachter Chart).")

    app = HumanityApp()
    app.mainloop()