# Nutzungsanleitung

Dieser Abschnitt richtet sich an Endanwender und beschreibt die wichtigsten
Anwendungsfaelle fuer Schueler und Kantinenpersonal.

## Einstieg

1. Browser oeffnen
2. SnackHub starten oder bereitgestellte URL aufrufen
3. Auf `Anmelden` klicken
4. Mit einem Demo-Account oder einem registrierten Benutzer einloggen

## Demo-Zugangsdaten

| Rolle | Benutzername | Passwort |
| --- | --- | --- |
| Schueler | `schueler_test` | `test123` |
| Kantine | `kantine_test` | `test123` |

## Benutzerfluss: Schueler

### 1. Login

- Anmeldung ueber die Login-Seite
- Nach erfolgreichem Login Weiterleitung in das Schueler-Dashboard
- Bei falschen Zugangsdaten erscheint ein Popup-Hinweis

### 2. Shop und Speiseansicht

- Aufruf ueber den Navigationspunkt `Shop`
- Anzeige der fuer Schueler freigegebenen Artikel
- Fokus auf schneller Uebersicht und klarer Verfuegbarkeit

### 3. Voting

- Aufruf ueber `Voting`
- Anzeige der aktiven Abstimmung
- Auswahl eines Lieblingsgerichts
- Aenderung der Stimme innerhalb derselben aktiven Abstimmung moeglich

### 4. Vorbestellen

- Aufruf ueber `Vorbestellen`
- Auswahl des angebotenen Gerichts
- Speichern der Vorbestellung
- Status wird in der Kantinenansicht weiterverarbeitet

### 5. Feedback geben

- Aufruf ueber `Feedback`
- Abgabe einer Bewertung und eines Kommentars
- Woechentliche Beschraenkung pro Nutzer verhindert Mehrfacheintraege

## Benutzerfluss: Kantine

### 1. Login

- Anmeldung mit Kantinenrolle
- Direkte Weiterleitung in das Kantinen-Dashboard

### 2. Voting verwalten

- Neue Abstimmung anlegen
- Mindestens 3 und maximal 5 Gerichte definieren
- Laufende Abstimmung beobachten
- Abstimmung bei Bedarf beenden

### 3. Menue verwalten

- Artikel anlegen oder pflegen
- Kategorien setzen
- Sichtbarkeit fuer den Schueler-Shop steuern

### 4. Vorbestellungen pruefen

- Einsicht in eingegangene Vorbestellungen
- Unterstuetzung der Produktions- und Ausgabeplanung

### 5. Feedback auswerten

- Uebersicht ueber eingegangene Rueckmeldungen
- Erkennen von Trends, Qualitaetsproblemen oder Favoriten

## Typische Demo-Szenarien

### Szenario A: Voting-Durchlauf

1. Login als `kantine_test`
2. Neue Abstimmung mit 3 bis 5 Gerichten anlegen
3. Parallel Login als `schueler_test`
4. Stimme abgeben
5. Zurueck in die Kantinenansicht wechseln und Ergebnis zeigen

### Szenario B: Vorbestellung

1. Login als Schueler
2. Gericht vorbestellen
3. Login als Kantine
4. Vorbestellung in der Uebersicht nachvollziehen

### Szenario C: Feedback-Zyklus

1. Login als Schueler
2. Bewertung und Kommentar absenden
3. Login als Kantine
4. Rueckmeldung in der Feedback-Ansicht kontrollieren

## Screenshot-Checkliste fuer die finale Abgabe

Um die Dokumentation fuer die Bewertung noch staerker zu machen, sollten in
einer finalen Version mindestens folgende Screenshots ergaenzt werden:

- Landingpage mit Branding und Einstieg
- Login-Seite mit Demo-Hinweis
- Schueler-Voting mit aktiver Abstimmung
- Kantinen-Dashboard mit Verwaltungsansicht
- Feedback- oder Vorbestellungsuebersicht

## Vorbereitete Screenshot-Slots

Ich kann echte Screenshots hier sauber einbauen, brauche dafuer aber die
Bilddateien aus eurer laufenden App. Direkt aus dem lokalen Browser kann ich sie
in dieser Umgebung nicht selbst aufnehmen.

Empfohlene Dateinamen im Ordner `docs/assets/screenshots/`:

<div class="screenshot-grid">
  <div class="shot-card">
    <strong>Landingpage</strong>
    Startseite mit Logo, Einstieg und Hintergrund
    <div class="path-chip">landingpage.png</div>
  </div>
  <div class="shot-card">
    <strong>Login</strong>
    Login-Seite mit Demo-Hinweis oder Fehler-Popup
    <div class="path-chip">login.png</div>
  </div>
  <div class="shot-card">
    <strong>Schueler-Voting</strong>
    Aktive Abstimmung und Stimmabgabe
    <div class="path-chip">voting-schueler.png</div>
  </div>
  <div class="shot-card">
    <strong>Kantinen-Dashboard</strong>
    Verwaltungssicht nach Login als Kantine
    <div class="path-chip">kantine-dashboard.png</div>
  </div>
  <div class="shot-card">
    <strong>Menuverwaltung</strong>
    Speisekarten- oder Artikelpflege
    <div class="path-chip">menuverwaltung.png</div>
  </div>
  <div class="shot-card">
    <strong>Vorbestellungen / Feedback</strong>
    Uebersichtsseite fuer operative Auswertung
    <div class="path-chip">vorbestellungen-oder-feedback.png</div>
  </div>
</div>

Sobald du mir diese Bilder gibst oder im genannten Ordner ablegst, baue ich sie
dir direkt als echte Galerie in die Dokumentation ein.
