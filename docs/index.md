<div class="hero-shell">
  <div class="hero-grid">
    <div>
      <img src="assets/snackhub-logo.png" alt="SnackHub Logo" class="hero-mark" />
      <p class="hero-kicker">Digitale Kantinenorganisation fuer Schulumgebungen</p>
      <h1>SnackHub</h1>
      <p>
        SnackHub ist eine browserbasierte Webanwendung, die den Bestell-, Voting- und
        Feedback-Prozess zwischen Schuelern und Kantinenpersonal digital abbildet.
        Die Anwendung reduziert manuelle Abstimmungen, beschleunigt Rueckmeldungen
        zum Speiseangebot und schafft eine klare Datenbasis fuer die Tagesplanung.
        Im Zentrum stehen ein niedrigschwelliger Zugang fuer Schueler, eine schlanke
        Verwaltungsoberflaeche fuer die Kantine und ein reproduzierbarer technischer
        Betrieb auf Python- und MySQL-Basis.
      </p>
      <div class="quick-points">
        <span>Schueler-Votings</span>
        <span>Vorbestellungen</span>
        <span>Wochenfeedback</span>
        <span>Menuverwaltung</span>
      </div>
    </div>
    <div class="hero-side">
      <h3>Value Proposition</h3>
      <p>
        SnackHub adressiert das Problem, dass Essenswahl, Vorbestellung und Feedback
        in Schulkantinen oft unstrukturiert, analog und schlecht auswertbar sind.
        Die Zielgruppe sind Schueler als Endnutzer sowie Kantinen- oder Kioskpersonal
        als organisatorische Instanz. Die Software loest dieses Problem durch eine
        gemeinsame Plattform fuer Abstimmungen, Speiseverwaltung, Vorbestellungen und
        Rueckmeldungen mit rollenbasierten Oberflaechen.
      </p>
      <p><strong>Kurz gesagt:</strong> SnackHub macht in wenigen Sekunden klar, was angeboten wird, was gewaehlt wurde und was vorbereitet werden muss.</p>
    </div>
  </div>
  <div class="callout-strip">
    Innerhalb weniger Sekunden wird sichtbar, was SnackHub leistet und warum die Plattform fuer schulische Verpflegung organisatorisch relevant ist.
  </div>
</div>

![Status](https://img.shields.io/badge/status-studienprojekt-F59E0B?style=flat-square)
![Version](https://img.shields.io/badge/version-0.1.0-EA580C?style=flat-square)
![Lizenz](https://img.shields.io/badge/lizenz-schulprojekt-7C2D12?style=flat-square)
![Stack](https://img.shields.io/badge/stack-Python%20%7C%20Flet%20%7C%20MySQL-78350F?style=flat-square)
![Docs](https://img.shields.io/badge/docs-MkDocs%20ready-D97706?style=flat-square)

## Projektueberblick

SnackHub ist ein Full-Stack-Schulprojekt mit Fokus auf klarer Rollenverteilung und
einem nachvollziehbaren Datenfluss. Die Anwendung trennt fachlich zwischen
Schueler-Ansicht und Kantinen-Ansicht. Schueler koennen Speisen ansehen,
abstimmen, vorbestellen und Feedback geben. Das Kantinenpersonal kann Menues
verwalten, Umfragen starten, Vorbestellungen einsehen und Auswertungen nutzen.

## Zielgruppen

- **Schueler:** schnelle Interaktion mit Voting, Shop, Vorbestellung und Feedback
- **Kantine/Kiosk:** operative Planung, Menusteuerung und Rueckmeldungsanalyse
- **Projektbetreuer:** nachvollziehbare Architektur, reproduzierbare Inbetriebnahme und sauber dokumentierte Entscheidungen

## Kernfunktionen

- Rollenbasierte Anmeldung fuer `schueler` und `kantine`
- Voting-System mit aktiver Umfrage, Live-Zwischenstand und Stimmenaenderung
- Speisekarten- und Artikelverwaltung fuer die Kantine
- Vorbestellung mit Status fuer Bezahlbestaetigung
- Woechentliches Feedback mit Bewertung und Kommentar

## Dokumentations-Navigation

- [Installation & Quick Start](installation.md)
- [Technische Dokumentation](technical.md)
- [Nutzungsanleitung](user-guide.md)
- [Technische Strategie](strategy.md)

## Projektstatus

SnackHub liegt als lauffaehiger Prototyp mit echter Datenbankanbindung vor.
Die aktuelle Implementierung ist auf Vorfuehrbarkeit, klare Rollenlogik und
technische Nachvollziehbarkeit optimiert. Fuer eine produktive Weiterentwicklung
waeren Deployment-Haertung, erweiterte Tests und ein ausgebautes Rechtekonzept
die naechsten logischen Schritte.

## Screenshot-Integration

Die Dokumentation ist bereits so vorbereitet, dass echte UI-Screenshots direkt
integriert werden koennen. Dafuer ist der Ordner `docs/assets/screenshots/`
angelegt. Sobald dort echte Bilder abgelegt werden, koennen sie gezielt in die
Nutzungsanleitung eingebunden werden.
