# Technische Strategie

Dieser Abschnitt reflektiert die bewusst getroffenen Technologie- und
Architekturentscheidungen des Projekts.

## Technologie-Stack

| Technologie | Einsatz | Begruendung |
| --- | --- | --- |
| Python 3.12 | Hauptsprache | Einheitliche Sprache fuer Logik, Setup und UI |
| Flet | Web-UI | Schnelle Umsetzung einer browserbasierten Oberflaeche ohne getrennten JavaScript-Stack |
| MySQL | Persistenz | Relationales Datenmodell fuer Nutzer, Voting und Bestellungen |
| bcrypt | Passwortschutz | Sichere Hashing-Strategie fuer Benutzerkonten |
| MkDocs | Projektdokumentation | Strukturierte, versionierbare und GitHub-Pages-faehige Dokumentation |

## Warum diese Auswahl sinnvoll ist

### Flet statt klassischem Frontend-Framework

Flet erlaubt es, UI und Anwendungslogik in einem konsistenten Python-Stack zu
entwickeln. Das reduziert Komplexitaet im Projektkontext, weil kein separates
Frontend mit JavaScript, Build-Tooling und API-Schicht notwendig ist. Fuer ein
Schulprojekt mit klarer Fokussetzung auf Produktidee, Datenfluss und Rollenlogik
ist das ein sinnvoller Trade-off.

### MySQL statt rein dateibasierter Speicherung

SnackHub verarbeitet relationale Informationen mit klaren Beziehungen:
Benutzer, Umfragen, Gerichte, Stimmen, Vorbestellungen und Feedback. Ein
relationales Datenbanksystem ist daher fachlich konsistenter und besser
auswertbar als JSON- oder Dateispeicherung.

## Bewertungsdimensionen

### Skalierbarkeit

- Die Service-Schicht trennt Fachlogik von der UI.
- Das Datenmodell ist relationell erweiterbar.
- Neue Rollen oder Module koennen ueber weitere Seiten und Services ergaenzt werden.

### Wartbarkeit

- Die Seiten sind in fachliche Unterordner (`schueler`, `kantine`) gegliedert.
- Datenbanksetup und Migrationen sind zentral dokumentiert und automatisierbar.
- Der Einstiegspunkt ist uebersichtlich und fuehrt das Routing an einer Stelle zusammen.

### Performance

- Die Anwendung ist fuer kleine bis mittlere Demo-Szenarien ausgelegt.
- Statische Hintergrundgestaltung ist im Browser robuster als komplexe Animationen.
- Der MySQL-Connection-Pool reduziert die Kosten wiederholter Verbindungsaufbauten.

## Herausforderungen und Loesungen

### 1. Browserstart mit Flet

**Problem:** In der Web-Variante blieb die Seite zeitweise beim Flet-Logo stehen.  
**Loesung:** Vereinfachung des initialen Renderpfads, Reduktion auf leichtere
Hintergrundgestaltung und robuste Startlogik.

### 2. Windows-Encoding in der Konsole

**Problem:** Unicode-Ausgaben in `print()` konnten unter Windows `cp1252` zum
Startabbruch fuehren.  
**Loesung:** Fruehe Umstellung von `stdout`/`stderr` auf UTF-8 im Einstiegspunkt.

### 3. Schema-Drift bei der Datenbank

**Problem:** Unterschiedliche lokale Datenbankstaende fuehren schnell zu
fehlenden Tabellen oder Spalten.  
**Loesung:** `initialize_app()` und `setup_db.py` pruefen Tabellen und fuehren
fehlende Teile automatisch nach.

### 4. Demo-Tauglichkeit

**Problem:** Bei Vorfuehrungen muessen Login, Setup und Navigation ohne
Rueckfragen funktionieren.  
**Loesung:** Testnutzer, Popup-Fehlermeldungen beim Login und dokumentierte
Quick-Start-Schritte.

## Weiterentwicklung

Folgende Schritte waeren fuer eine naechste Projektphase sinnvoll:

- Auslagerung sensibler Konfiguration in `.env`
- Automatisierte Tests fuer Kern-Services
- Deployment der Anwendung selbst, nicht nur der Dokumentation
- Erweitertes Rollen- und Rechtemodell
- Logging und Monitoring fuer stabileren Betrieb

## Dokumentationsstrategie

Die vorliegende Dokumentation ist nicht nur als Abgabe gedacht, sondern als
technische Referenz fuer Betrieb, Weiterentwicklung und Vorfuehrung. Durch
MkDocs bleibt sie versionierbar, ueber GitHub Pages veroeffentlichbar und kann
parallel zum Code gepflegt werden.
