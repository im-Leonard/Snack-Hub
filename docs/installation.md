# Installation & Quick Start

Dieser Abschnitt dokumentiert die reproduzierbare Inbetriebnahme von SnackHub
und der zugehoerigen Projektdokumentation.

## Voraussetzungen

### Laufzeitumgebung

- Python 3.12 oder neuer
- Windows PowerShell (aktuelle Projektumgebung)
- Lokaler Browser fuer die Flet-Weboberflaeche

### Datenbanksystem

- MySQL oder MariaDB mit lokalem Zugriff
- Standardkonfiguration im Projekt:
  - Host: `localhost`
  - User: `root`
  - Datenbank: `schul_kantine`

### Python-Abhaengigkeiten

Das Applikationsprojekt nutzt folgende Kernbibliotheken:

- `flet`
- `bcrypt`
- `mysql-connector-python`

Diese Abhaengigkeiten sind im Projekt in `snackhub2/pyproject.toml` definiert.

## Schritt-fuer-Schritt-Start

### 1. Repository klonen

```bash
git clone <REPOSITORY-URL>
cd Snackhub
```

### 2. Virtuelle Umgebung anlegen

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Python-Abhaengigkeiten installieren

Variante A - direkt aus dem Paket:

```bash
pip install -e .\snackhub2
```

Variante B - manuell:

```bash
pip install flet bcrypt mysql-connector-python
```

### 4. Datenbank konfigurieren

Die MySQL-Zugangsdaten werden in `snackhub2/config.py` gepflegt.

Standardwert:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "schul_kantine",
}
```

Falls lokal ein MySQL-Passwort gesetzt ist, muss `password` angepasst werden.

### 5. Datenbank initialisieren

```bash
python -m snackhub2.setup_db
```

Dabei werden die benoetigten Tabellen sowie die Demo-Accounts erstellt.

### 6. Anwendung starten

```bash
python -m snackhub2
```

Die Anwendung startet als Flet-Web-App im Browser.

## Quick Start fuer die Demo

Nach erfolgreichem Setup stehen folgende Testnutzer zur Verfuegung:

| Rolle | Benutzername | Passwort |
| --- | --- | --- |
| Schueler | `schueler_test` | `test123` |
| Kantine | `kantine_test` | `test123` |

## Sicherheits- und Konfigurationshinweise

- Die Standardkonfiguration nutzt einen lokalen Root-Zugang fuer MySQL und ist nur fuer Entwicklungs- oder Demo-Umgebungen gedacht.
- Zugangsdaten sollten in einer erweiterten Version in eine `.env`-Datei oder in sichere Deployment-Variablen ausgelagert werden.
- Passwoerter werden bereits per `bcrypt` gehasht gespeichert, nicht im Klartext.

## Dokumentation lokal starten

Fuer die Projektdokumentation selbst wird MkDocs verwendet.

### Doku-Abhaengigkeiten installieren

```bash
pip install -r requirements-docs.txt
```

### Lokalen Doku-Server starten

```bash
mkdocs serve
```

Standardadresse:

```text
http://127.0.0.1:8000
```

## GitHub Pages Deployment

Die Dokumentation kann direkt auf GitHub Pages veroeffentlicht werden:

```bash
mkdocs gh-deploy
```

Damit ist die Dokumentation oeffentlich erreichbar und entspricht der geforderten
Web-Dokumentationsform fuer den Projektabschluss.
