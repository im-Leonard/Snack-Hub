# Technische Dokumentation

Dieser Abschnitt beschreibt die technische Struktur von SnackHub mit Fokus auf
Architektur, Datenmodell und zentralen Anwendungskomponenten.

## Systemarchitektur

SnackHub ist als Python-basierte Webanwendung mit Flet im Frontend und MySQL
als persistenter Datenhaltung aufgebaut. Die fachliche Logik ist ueber eine
klare Trennung von Seiten, Services und Datenzugriff organisiert.

```mermaid
flowchart LR
    A[Schueler / Kantinenpersonal] --> B[Flet Web UI]
    B --> C[Routing in snackhub2/main.py]
    C --> D[Page Layer]
    D --> E[Service Layer]
    E --> F[(MySQL Datenbank)]

    D --> D1[login.py]
    D --> D2[schueler/*.py]
    D --> D3[kantine/*.py]

    E --> E1[auth_service.py]
    E --> E2[init_service.py]
    E --> E3[poll_service.py]
    E --> E4[db.py]
```

## Architekturkomponenten

| Ebene | Verantwortung | Relevante Dateien |
| --- | --- | --- |
| Einstieg | Start, Routing, Flet-Konfiguration | `snackhub2/__main__.py`, `snackhub2/main.py` |
| UI / Pages | Rollenbasierte Ansichten und Interaktion | `snackhub2/pages/...` |
| Komponenten | Wiederverwendbare UI-Bausteine | `snackhub2/components/header.py` |
| Services | Authentifizierung, Initialisierung, Voting-Logik | `snackhub2/services/...` |
| Persistenz | Verbindungspool und SQL-Zugriff | `snackhub2/services/db.py` |
| Setup | Datenbankschema und Seed-Daten | `snackhub2/setup_db.py` |

## Datenbankmodell

Die Datenbank `schul_kantine` bildet sowohl Benutzer- und Menudaten als auch
Voting-, Vorbestell- und Feedbackprozesse ab.

```mermaid
erDiagram
    USERS ||--o{ POLL_VOTES : stimmt_ab
    USERS ||--o{ PREORDERS : bestellt
    USERS ||--o{ WEEKLY_FEEDBACK : schreibt
    USERS ||--o{ VOTES : legacy_vote
    USERS ||--o{ FEEDBACK : legacy_feedback
    USERS ||--o{ ORDERS : legacy_order

    MEALS ||--o{ VOTES : wird_gewaehlt
    MEALS ||--o{ FEEDBACK : wird_bewertet
    MEALS ||--o{ ORDERS : wird_bestellt

    POLLS ||--o{ POLL_DISHES : enthaelt
    POLLS ||--o{ POLL_VOTES : sammelt
    POLLS ||--o{ PREORDERS : erzeugt

    POLL_DISHES ||--o{ POLL_VOTES : erhaelt

    USERS {
      int id PK
      string username
      string password_hash
      string role
    }
    MEALS {
      int id PK
      string name
      string description
      decimal price
      string category
      bool available
    }
    POLLS {
      int poll_id PK
      int meal_id
      timestamp start_date
      timestamp end_date
    }
    POLL_DISHES {
      int id PK
      int poll_id FK
      string dish_name
      int dish_order
      int votes
    }
    POLL_VOTES {
      int id PK
      int poll_id FK
      int dish_id FK
      int user_id FK
    }
    PREORDERS {
      int id PK
      int poll_id FK
      int user_id FK
      string dish_name
      string status
      timestamp paid_confirmed_at
    }
    WEEKLY_FEEDBACK {
      int id PK
      int user_id FK
      string week_key
      int rating
      string comment
      bool is_anonymous
      bool is_done
    }
```

## Kernklassen und Kernfunktionen

### Authentifizierung

| Element | Aufgabe |
| --- | --- |
| `AuthService.hash_password()` | Hashing neuer Passwoerter mit `bcrypt` |
| `AuthService.check_password()` | Verifikation gespeicherter Passwort-Hashes |
| `AuthService.login_user()` | Login anhand Username + Passwort, Rueckgabe eines Domainenobjekts |
| `AuthService.register_user()` | Anlegen neuer Nutzer mit Rollenpruefung |

### Datenbank und Initialisierung

| Element | Aufgabe |
| --- | --- |
| `get_conn()` | Zugriff auf den MySQL-Connection-Pool |
| `initialize_app()` | Vorabpruefung, ob alle benoetigten Tabellen/Spalten vorhanden sind |
| `setup_database()` | Vollstaendiger Setup-Lauf fuer Schema und Testdaten |

### Fachlogik

| Bereich | Beschreibung |
| --- | --- |
| Voting | Erstellen, Anzeigen, Auswerten und Beenden von Abstimmungen |
| Menuverwaltung | Pflege sichtbarer Artikel fuer den Schueler-Shop |
| Vorbestellung | Ueberfuehrung von Poll-Ergebnissen in Bestellvorgaenge |
| Feedback | Woechentliche Rueckmeldungen zur Angebotsqualitaet |

## Routing und Rollenlogik

Die Navigation wird zentral in `main.py` ueber `page.route` gesteuert.

| Route | Rolle | Funktion |
| --- | --- | --- |
| `/` | Alle | Landingpage |
| `/login` | Alle | Anmeldung |
| `/register` | Alle | Registrierung |
| `/dashboard` | Schueler | Schueler-Dashboard |
| `/shop` | Schueler | Shop / Speisekarte |
| `/voting` | Schueler | Abstimmen |
| `/feedback` | Schueler | Feedback erfassen |
| `/vorbestellen` | Schueler | Vorbestellung |
| `/kantine_landing` | Kantine | Kantinen-Dashboard |
| `/voting_kantine` | Kantine | Abstimmung verwalten |
| `/menu_kantine` | Kantine | Menuepflege |
| `/feedback_overview` | Kantine | Feedback auswerten |
| `/vorbestellungen_kantine` | Kantine | Vorbestellungen einsehen |

## Wartbarkeit und Erweiterbarkeit

- Die UI ist in fachlich getrennte Seitenmodule aufgeteilt.
- Services kapseln fachliche Logik, damit UI-Code schlank bleibt.
- Das Setup-Skript enthaelt Migrationen fuer fehlende Tabellen und Spalten, was den Betrieb robuster macht.
- Die dokumentierte Trennung erlaubt spaeter den Austausch einzelner Layer, z. B. ein alternatives Frontend.
