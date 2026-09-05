# VersatzebenenTool

<!-- version:start -->
**Aktuelle Version: 1.2.1**
<!-- version:end -->

[English README](README.md) · [Versionshistorie](doku/version.md)

Ein Python-Add-in für Autodesk Fusion zum Erstellen von Versatzebenen, optionalen Skizzen und Timeline-Gruppen. Unterstützt Windows und macOS; eine Inno-Setup-Installerdefinition für Windows ist enthalten.

## Aktueller Projektstand

- 1–50 Ebenen ausgehend von einer Konstruktionsebene in der Stammkomponente erstellen.
- Gleichmäßigen Abstand für die Serie festlegen. Die erste Ebene hat Versatz 0: Fünf Ebenen mit 1 cm Abstand liegen bei 0, 1, 2, 3 und 4 cm.
- Optional eine leere Skizze auf jeder Ebene erstellen.
- Basisnamen für Ebenen und Skizzen mit automatischer Nummerierung vergeben; der Standard ist `vref`.
- Erstellte Objekte optional in der Timeline gruppieren (Konstruktionsverlauf erforderlich).
- Aktuelle Version im Befehlstitel anzeigen.
- Beschriftungen, Auswahlhinweise, Meldungen und erzeugte Gruppennamen des aktiven Befehls in Englisch, Deutsch, Französisch, Spanisch und Polnisch anzeigen.

Individuelle Abstände je Ebene sind nicht implementiert. Bitte eine Konstruktionsebene auswählen: Der vorhandene Auswahlfilter bietet auch planare Flächen an, die Ausführung weist diese jedoch derzeit zurück. Geometrieerstellung und native Oberfläche müssen direkt in Fusion getestet werden.

![Befehlsdialog (frühere deutsche Oberfläche)](images/VersatzebenenToolDialog.png)
![Erstellte Ebenen](images/VersatzebenenErstellt.png)

## Installation

### Windows-Installer

1. Die [GitHub-Releases](https://github.com/know-how-schmiede/VersatzebenenTool/releases) öffnen.
2. Falls für die gewünschte Version verfügbar, `VersatzebenenTool_Setup_<Version>.exe` herunterladen und ausführen.
3. Der Installer verwendet `%AppData%\Autodesk\Autodesk Fusion 360\API\AddIns\VersatzebenenTool`.
4. In Fusion unter **Skripte und Zusatzmodule → Zusatzmodule** das **VersatzebenenTool** auswählen und starten. Optional den automatischen Start aktivieren.

### Manuelle Installation (Windows und macOS)

1. Ein Release-Archiv oder dieses Repository herunterladen und entpacken.
2. Den vollständigen Ordner `fusion_addin/VersatzebenenTool` zusammenhalten. Er enthält `VersatzebenenTool.py` und `VersatzebenenTool.manifest`.
3. Unter **Skripte und Zusatzmodule → Zusatzmodule** mit **+ / Hinzufügen** diesen Ordner auswählen, nicht das Repository-Hauptverzeichnis. Das Add-in starten.
4. Für Updates das Add-in stoppen, seine Dateien ersetzen und erneut starten.

## Bedienung und Sprache

Beim Start des Add-ins öffnet sich der Dialog. Er lässt sich anschließend im Arbeitsbereich Konstruktion über das Panel **Erstellen** erneut öffnen. Eine Konstruktionsebene auswählen, Anzahl und Abstand einstellen, Namen und bei Bedarf Skizzen/Gruppierung festlegen und bestätigen.

Das Add-in liest beim Start die Fusion-Sprache über [GeneralPreferences.userLanguage](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeneralPreferences_userLanguage.htm). Zum Wechseln die Benutzersprache in den allgemeinen Fusion-Voreinstellungen ändern und Fusion neu starten. Bei nicht unterstützten Sprachen oder nicht verfügbaren Einstellungen wird Englisch verwendet. Selbst eingegebene Namen bleiben unverändert.

Die Übersetzungen liegen zentral in `fusion_addin/VersatzebenenTool/localization.py`. Ungenutzte Beispielbefehle unter `commands/` sind Vorlagencode und gehören nicht zur aktiven übersetzten Oberfläche.

![Befehl im Menü (frühere Oberfläche)](images/VersatzebenenToolMenu.png)

## Entwicklung und Versionspflege

- `fusion_addin/VersatzebenenTool/`: installierbares Add-in.
- `installer/VersatzebenenTool_installer.iss`: Inno-Setup-Installerdefinition; kompilierte Ausgabe unter `dist/`.
- `doku/version.md`: Versionshistorie.
- `tools/sync_version.py`: Versionsabgleich.

Für eine neue Version `VERSION` in `fusion_addin/VersatzebenenTool/version.py` ändern, `python tools/sync_version.py` ausführen und die Änderungen in `doku/version.md` ergänzen. Mit `python tools/sync_version.py --check` werden abweichende Versionsangaben ohne Dateiänderungen erkannt. Historische Einträge behalten ihre ursprüngliche Versionsnummer. Anschließend den Installer kompilieren.

Lizenz: [GPL-3.0](LICENSE).
