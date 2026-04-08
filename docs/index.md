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
        Im Zentrum stehen ein niedrigschwelliger Zugang fuer Schueler, eine saubere
        Verwaltungsoberfläche fuer die Kantine und ein reproduzierbarer technischer
        Betrieb auf Python- und MySQL-Basis.
      </p>
      <div class="quick-points">
        <span>Schueler-Votings</span>
        <span>Vorbestellungen</span>
        <span>Wochenfeedback</span>
        <span>Menüverwaltung</span>
      </div>
    </div>
    <div class="hero-side">
      <h3>Value Proposition</h3>
      <p>
        SnackHub adressiert das Problem, dass Essenswahl, Vorbestellung und Feedback
        in Schulkantinen oft unstrukturiert, analog und schlecht auswertbar sind.
        Die Zielgruppe sind Schueler als Endnutzer sowie Kantinen- oder Kioskpersonal
        als organisatorische Instanz. Die Software löst dieses Problem durch eine
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

<div class="badge-row">
  <span class="local-badge">Status: Studienprojekt</span>
  <span class="local-badge">Version: 0.1.0</span>
  <span class="local-badge">Lizenz: Schulprojekt</span>
  <span class="local-badge">Stack: Python | Flet | MySQL</span>
  <span class="local-badge">Docs: MkDocs ready</span>
</div>

# Projektueberblick

SnackHub ist ein Full-Stack-Schulprojekt mit Fokus auf klarer Rollenverteilung und
einem nachvollziehbaren Datenfluss. Die Anwendung trennt fachlich zwischen
Schueler-Ansicht und Kantinen-Ansicht. Schueler koennen Speisen ansehen,
abstimmen, vorbestellen und Feedback geben. Das Kantinenpersonal kann Menues
verwalten, Umfragen starten, Vorbestellungen einsehen und Auswertungen nutzen.

# Zielgruppen

- **Schueler:** schnelle Interaktion mit Voting, Shop, Vorbestellung und Feedback
- **Kantine/Kiosk:** operative Planung, Menusteuerung und Rueckmeldungsanalyse
- **Projektbetreuer:** nachvollziehbare Architektur, reproduzierbare Inbetriebnahme und sauber dokumentierte Entscheidungen

# Kernfunktionen

- Rollenbasierte Anmeldung fuer `schueler` und `kantine`
- Voting-System mit aktiver Umfrage, Live-Zwischenstand und Stimmenaenderung
- Speisekarten- und Artikelverwaltung fuer die Kantine
- Vorbestellung mit Status fuer Bezahlbestaetigung
- Woechentliches Feedback mit Bewertung und Kommentar

# Dokumentations-Navigation

- [Installation & Quick Start](installation.md)
- [Technische Dokumentation](technical.md)
- [Nutzungsanleitung](user-guide.md)
- [Technische Strategie](strategy.md)

# Projektstatus

SnackHub liegt als lauffähiger Prototyp mit echter Datenbankanbindung vor.
Die aktuelle Implementierung ist auf Vorfuehrbarkeit, klare Rollenlogik und
technische Nachvollziehbarkeit optimiert. Für eine produktive Weiterentwicklung
wären Deployment-Haertung, erweiterte Tests und ein ausgebautes Rechtekonzept
die naechsten logischen Schritte.

## Screenshot-Integration

Die Dokumentation ist bereits so vorbereitet, dass echte UI-Screenshots direkt
integriert werden können. Dafuer ist der Ordner `docs/assets/screenshots/`
angelegt. Sobald dort echte Bilder abgelegt werden, können sie gezielt in die
Nutzungsanleitung eingebunden werden.
