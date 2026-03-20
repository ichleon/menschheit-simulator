# HUMANITY — Zivilisationssimulation

## Übersicht

Dieses Projekt implementiert eine interaktive Simulation der menschlichen Zivilisation, entwickelt mit Python. Es umfasst eine grafische Benutzeroberfläche (GUI) zur Steuerung der Simulation sowie ein Analyse-Tool zur Auswertung der generierten Daten. Die Simulation modelliert Bevölkerungswachstum, zufällige Ereignisse und historische Entwicklungen über Jahrhunderte hinweg.

## Funktionen

### Hauptsimulation (`ms.py`)
- **Interaktive GUI**: Steuerung der Simulation über eine benutzerfreundliche Oberfläche mit Tkinter.
- **Bevölkerungsmodellierung**: Berechnung von Geburten, Todesfällen und Bevölkerungswachstum basierend auf konfigurierbaren Raten.
- **Zufällige Ereignisse**: Integration historischer Ereignisse wie Kriege, Seuchen oder technologische Durchbrüche, die die Simulation beeinflussen.
- **Echtzeit-Visualisierung**: Anzeige von Diagrammen zur Bevölkerungsentwicklung (optional mit Matplotlib).
- **Exportfunktionen**: Automatische Speicherung der letzten Sitzung beim Schließen sowie manuelle Exporte in CSV- und JSON-Format.
- **Anpassbare Parameter**: Einstellbare Startwerte für Bevölkerung, Geburtenrate, Sterberate und mehr.

### Analyse-Tool (`analyse.py`)
- **Datenanalyse**: Laden und Verarbeitung von exportierten Simulationsdaten (CSV/JSON).
- **Grafische Auswertung**: Erstellung von Diagrammen zur Bevölkerung, Geburten, Todesfällen und Ereignissen.
- **Kombinierter Report**: Zusammengesetzte Ansicht mit mehreren Diagrammen in einem Layout.
- **GUI für Analyse**: Einfache Auswahl von Dateien und automatische Generierung von Berichten.
- **Fehlerresistenz**: Robuste Verarbeitung von Daten, auch bei ungültigen Werten (z. B. inf/NaN).

## Systemanforderungen

- **Python-Version**: 3.7 oder höher.
- **Betriebssystem**: Kompatibel mit Windows, macOS und Linux.
- **Abhängigkeiten**:
  - `tkinter` (standardmäßig in Python enthalten; auf Linux ggf. separat installieren: `sudo apt-get install python3-tk`).
  - `matplotlib` (für Diagramme: `pip install matplotlib`).
  - `numpy` (für numerische Berechnungen: `pip install numpy`).
  - Optional: `pandas` (für erweiterte Datenverarbeitung: `pip install pandas`).

## Installation

1. **Repository klonen**:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Virtuelle Umgebung erstellen** (empfohlen):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Auf Windows: venv\Scripts\activate
   ```

3. **Abhängigkeiten installieren**:
   ```bash
   pip install matplotlib numpy
   # Optional: pip install pandas
   ```

4. **Tkinter überprüfen** (auf Linux):
   Falls Tkinter fehlt, installieren Sie es systemweit:
   ```bash
   sudo apt-get install python3-tk
   ```

## Nutzung

### Simulation starten
Führen Sie die Hauptdatei aus:
```bash
python ms.py
```
- Passen Sie Parameter wie Geburtenrate, Sterberate und Startbevölkerung an.
- Starten Sie die Simulation und beobachten Sie die Entwicklung.
- Exportieren Sie Daten manuell oder lassen Sie sie automatisch beim Schließen speichern (in `autosave/`).

### Daten analysieren
Führen Sie das Analyse-Tool aus:
```bash
python analyse.py
```
- Wählen Sie exportierte Dateien (CSV/JSON) aus.
- Starten Sie die Analyse, um Diagramme zu generieren und anzuzeigen.
- Die Ergebnisse werden in `autosave/output/` gespeichert.

## Projektstruktur

```
/
├── ms.py                    # Hauptsimulation mit GUI
├── analyse.py               # Analyse-Tool mit GUI
├── readme.md                # Diese Datei
└── autosave/
    ├── output/              # Generierte Diagramme
    ├── humanity_sim_*.csv   # Exportierte Simulationsdaten (CSV)
    └── humanity_sim_*.json  # Exportierte Simulationsdaten (JSON)
```

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz veröffentlicht. Siehe `LICENSE` für Details (falls vorhanden).

## Beiträge

Beiträge sind willkommen! Bitte erstellen Sie einen Pull-Request oder melden Sie Issues auf der GitHub-Seite.

## Kontakt

Für Fragen oder Feedback: [Ihre E-Mail oder GitHub-Handle hier einfügen].

---

*Entwickelt mit Python und Tkinter. Inspiriert von historischen und demografischen Modellen.*
