import os
import csv
import json
import math
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.figure as mfig

# =============================
# GUI
# =============================
class AnalyseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HUMANITY — Analyse Tool")
        self.geometry("800x600")
        self.configure(bg="#0A0E1A")

        self.data_files = []
        self.data_type = tk.StringVar(value="auto")
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#0A0E1A", height=50)
        header.pack(fill="x", padx=10, pady=10)
        tk.Label(header, text="📊 HUMANITY Analyse Tool", font=("Georgia", 18, "bold"),
                 bg="#0A0E1A", fg="#4FC3F7").pack(side="left")

        # Main frame
        main = tk.Frame(self, bg="#0A0E1A")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel
        left = tk.Frame(main, bg="#111827", width=300)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        tk.Label(left, text="Dateien auswählen:", bg="#111827", fg="#E8EAF6",
                 font=("Courier New", 10)).pack(anchor="w", padx=10, pady=10)

        self.file_listbox = tk.Listbox(left, bg="#1C2333", fg="#E8EAF6", selectmode=tk.MULTIPLE,
                                       font=("Courier New", 9))
        self.file_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = tk.Frame(left, bg="#111827")
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Dateien hinzufügen", command=self._add_files).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Auswahl entfernen", command=self._remove_files).pack(fill="x", pady=2)

        tk.Label(left, text="Dateityp:", bg="#111827", fg="#E8EAF6",
                 font=("Courier New", 10)).pack(anchor="w", padx=10, pady=5)
        ttk.Combobox(left, textvariable=self.data_type, values=["auto", "csv", "json"],
                     state="readonly").pack(fill="x", padx=10, pady=5)

        ttk.Button(left, text="Analyse starten", command=self._run_analysis).pack(fill="x", padx=10, pady=10)

        # Right panel for plots
        right = tk.Frame(main, bg="#111827")
        right.pack(side="right", fill="both", expand=True)

        self.plot_frame = tk.Frame(right, bg="#111827")
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.status_label = tk.Label(right, text="", bg="#111827", fg="#81C784",
                                     font=("Courier New", 10))
        self.status_label.pack(fill="x", padx=10, pady=5)

    def _add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("CSV/JSON", "*.csv *.json"), ("Alle Dateien", "*.*")])
        for f in files:
            if f not in self.data_files:
                self.data_files.append(f)
                self.file_listbox.insert(tk.END, os.path.basename(f))

    def _remove_files(self):
        selected = self.file_listbox.curselection()
        for i in reversed(selected):
            self.file_listbox.delete(i)
            del self.data_files[i]

    def _run_analysis(self):
        if not self.data_files:
            messagebox.showerror("Fehler", "Keine Dateien ausgewählt!")
            return

        self.status_label.config(text="Analyse läuft...")
        self.update()

        try:
            data = load_and_sort_data(self.data_files, self.data_type.get())
            if not data:
                messagebox.showerror("Fehler", "Keine gültigen Daten gefunden!")
                return

            births_per_year, deaths_per_year = calculate_births_and_deaths(data)

            # Hauptreport: 3-Chart-Kombination wie im Bild
            fig_report = create_combined_report(data, births_per_year, deaths_per_year, self.output_dir, show=True)

            # Zusätzlich einzelne Diagramme (optional)
            try:
                create_events_plot(data, self.output_dir)
            except Exception as e:
                print(f"Fehler beim Erstellen von Ereignisplot: {e}")

            self.status_label.config(text=f"Diagramme gespeichert in '{self.output_dir}'")
            messagebox.showinfo("Erfolg", f"Analyse abgeschlossen!\nDiagramme in '{self.output_dir}' gespeichert.")

            if fig_report is not None:
                self._display_plot(fig_report)
            else:
                self._display_plot(None)

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Analyse: {str(e)}")
            self.status_label.config(text="Fehler aufgetreten")

    def _display_plot(self, fig):
        # Clear previous
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        if fig is None:
            tk.Label(self.plot_frame, text="Kein Diagramm zum Anzeigen (Trotzdem wurden so viele Plots wie möglich erzeugt).", bg="#111827", fg="#E8EAF6", font=("Courier New", 11)).pack(expand=True)
            return

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

# =============================
# FUNKTIONEN (unverändert)
# =============================

# =============================
# FUNKTIONEN
# =============================
def load_and_sort_data(data_files, data_type):
    """Lädt Daten aus den angegebenen Dateien, erkennt Format automatisch oder verwendet data_type."""
    data = []
    for file in data_files:
        if not os.path.exists(file):
            print(f"Datei {file} nicht gefunden, übersprungen.")
            continue
        
        file_type = data_type if data_type != "auto" else ("json" if file.endswith(".json") else "csv")
        
        if file_type == "csv":
            try:
                with open(file, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            year = int(float(row["year"]))
                            pop = float(row["population"])
                            births = float(row["births"])
                            deaths = float(row["deaths"])
                            if not (math.isfinite(year) and math.isfinite(pop) and math.isfinite(births) and math.isfinite(deaths)):
                                raise ValueError("Ungültige Zahl (inf/NaN)")
                            data.append({
                                "Year": year,
                                "Population": pop,
                                "Births": births,
                                "Deaths": deaths,
                                "Events": row.get("events", "").strip()
                            })
                        except (KeyError, ValueError) as e:
                            print(f"Fehler in Datei {file}, Zeile übersprungen: {e}")
            except Exception as e:
                print(f"Fehler beim Lesen der CSV-Datei {file}: {e}")
        elif file_type == "json":
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    for entry in json_data.get("history", []):
                        try:
                            year = int(entry["year"])
                            pop = float(entry["population"])
                            births = float(entry["births"])
                            deaths = float(entry["deaths"])
                            if not (math.isfinite(year) and math.isfinite(pop) and math.isfinite(births) and math.isfinite(deaths)):
                                raise ValueError("Ungültige Zahl (inf/NaN)")
                            data.append({
                                "Year": year,
                                "Population": pop,
                                "Births": births,
                                "Deaths": deaths,
                                "Events": "|".join(entry.get("events", []))
                            })
                        except (KeyError, ValueError) as e:
                            print(f"Fehler in JSON-Eintrag in {file} übersprungen: {e}")
            except Exception as e:
                print(f"Fehler beim Lesen der JSON-Datei {file}: {e}")
        else:
            print(f"Unbekannter Dateityp für {file}.")
    
    # Sortiere nach Jahr
    data.sort(key=lambda x: x["Year"])
    return data

def calculate_births_and_deaths(data):
    """Verwendet die bereits vorhandenen Geburten und Todesfälle aus den Daten."""
    births_per_year = [d["Births"] for d in data if math.isfinite(d.get("Births", float('nan')))]
    deaths_per_year = [d["Deaths"] for d in data if math.isfinite(d.get("Deaths", float('nan')))]
    return births_per_year, deaths_per_year

def create_population_plot(data, output_dir, show=False):
    """Erstellt Diagramm 1: Bevölkerung über Zeit."""
    years = [d["Year"] for d in data]
    population_list = [d["Population"] for d in data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years, population_list, label="Gesamtbevölkerung", color="blue")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Bevölkerung")
    ax.set_title("Bevölkerung über Zeit")
    ax.legend()
    ax.grid(True)
    fig.savefig(os.path.join(output_dir, "bevoelkerung_ueber_zeit.png"))
    if not show:
        plt.close(fig)
    return fig if show else None

def create_births_plot(data, births_per_year, output_dir, show=False):
    """Erstellt Diagramm 2: Geburten pro Jahr."""
    years = [d["Year"] for d in data]
    cleaned_births = [v for v in births_per_year if math.isfinite(v)]
    max_births = max(cleaned_births, default=0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years, births_per_year, label="Geburten", color="orange")
    if cleaned_births:
        ax.axhline(max_births, color="red", linestyle="--", label=f"Max: {int(max_births):,}")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Geburten pro Jahr")
    ax.set_title("Geburten pro Jahr")
    ax.legend()
    ax.grid(True)
    fig.savefig(os.path.join(output_dir, "geburten_pro_jahr.png"))
    if not show:
        plt.close(fig)
    return fig if show else None

def create_deaths_plot(data, deaths_per_year, output_dir, show=False):
    """Erstellt Diagramm 3: Todesfälle pro Jahr."""
    years = [d["Year"] for d in data]
    cleaned_deaths = [v for v in deaths_per_year if math.isfinite(v)]
    max_deaths = max(cleaned_deaths, default=0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years, deaths_per_year, label="Todesfälle", color="black")
    if cleaned_deaths:
        ax.axhline(max_deaths, color="red", linestyle="--", label=f"Max: {int(max_deaths):,}")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Todesfälle pro Jahr")
    ax.set_title("Todesfälle pro Jahr")
    ax.legend()
    ax.grid(True)
    fig.savefig(os.path.join(output_dir, "todesfaelle_pro_jahr.png"))
    if not show:
        plt.close(fig)
    return fig if show else None

def create_events_plot(data, output_dir, show=False):
    """Erstellt Diagramm 4: Events über Zeit (als Text-Annotationen)."""
    years = [d["Year"] for d in data]
    events_list = [d["Events"] for d in data]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years, [0] * len(years), marker='o', linestyle='None', color="gray")  # Dummy-Plot für Events
    for i, events in enumerate(events_list):
        if events:
            ax.annotate(events, (years[i], 0), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
    ax.set_xlabel("Jahr")
    ax.set_title("Ereignisse über Zeit")
    ax.grid(True)
    fig.savefig(os.path.join(output_dir, "ereignisse_ueber_zeit.png"))
    if not show:
        plt.close(fig)
    return fig if show else None


def create_combined_report(data, births_per_year, deaths_per_year, output_dir, show=False):
    """Erstellt das zusammengesetzte Report-Layout wie im angehängten Bild."""
    years = [d["Year"] for d in data]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)

    # Oben links: Bevölkerung
    ax1 = axes[0, 0]
    ax1.plot(years, [d["Population"] for d in data], color="blue")
    ax1.set_title("Bevölkerung über Zeit")
    ax1.set_xlabel("Jahr")
    ax1.set_ylabel("Bevölkerung")
    ax1.grid(True)

    # Oben rechts: Geburten
    ax2 = axes[0, 1]
    cleaned_births = [v for v in births_per_year if math.isfinite(v)]
    max_births = max(cleaned_births, default=0)
    ax2.plot(years, births_per_year, color="orange")
    if cleaned_births:
        ax2.axhline(max_births, color="red", linestyle="--", label=f"Max: {int(max_births):,}")
    ax2.set_title("Geburten pro Jahr")
    ax2.set_xlabel("Jahr")
    ax2.set_ylabel("Geburten")
    ax2.legend() if cleaned_births else None
    ax2.grid(True)

    # Unten: Todesfälle
    ax3 = axes[1, 0]
    cleaned_deaths = [v for v in deaths_per_year if math.isfinite(v)]
    max_deaths = max(cleaned_deaths, default=0)
    ax3.plot(years, deaths_per_year, color="black")
    if cleaned_deaths:
        ax3.axhline(max_deaths, color="red", linestyle="--", label=f"Max: {int(max_deaths):,}")
    ax3.set_title("Todesfälle pro Jahr")
    ax3.set_xlabel("Jahr")
    ax3.set_ylabel("Todesfälle")
    ax3.legend() if cleaned_deaths else None
    ax3.grid(True)

    # Unten rechts: Hinweis (nicht belegt)
    ax4 = axes[1, 1]
    ax4.axis("off")
    ax4.text(0.5, 0.5, "Ereignis-Plot in einer separaten Datei", ha='center', va='center', fontsize=12)

    fig.savefig(os.path.join(output_dir, "combined_report.png"))
    if not show:
        plt.close(fig)
    return fig if show else None

# =============================
# HAUPTLOGIK
# =============================
if __name__ == "__main__":
    app = AnalyseApp()
    app.mainloop()
