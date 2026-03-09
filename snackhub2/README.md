Test Nutzer:

Schüler Account:
  Benutzername: schueler_test
  Passwort:     test123
  Rolle:        schueler

Kantine Account:
  Benutzername: kantine_test
  Passwort:     test123
  Rolle:        kantine

## Voting-System

### Kantine (`/voting_kantine`)
- Erstelle eine neue Abstimmung mit **mind. 3** und **max. 5** Gerichten
- Sieh auf der Seite die Live-Auswertung inkl. führendem Gericht
- Beende die Abstimmung jederzeit

### Schüler (`/voting`)
- Sieh die aktive Abstimmung mit Live-Ergebnissen
- Stimme für dein Lieblingsessen ab
- Ändere deine Stimme jederzeit
## Start (Windows)

Nutze am einfachsten einen der Starter im Projekt-Root:

- `start_snackhub.ps1`
- `start_snackhub.bat`

Wichtig:
- Starte nicht aus `snackhub2` mit `python -m snackhub2`, sonst kommt `No module named snackhub2`.

## Chatbot (Ollama)

1. Ollama installieren und starten.
2. Modell laden:
   - `ollama pull llama3.2:3b`
3. Im Projekt-Root `.env.example` nach `.env` kopieren.
4. App starten (`start_snackhub.ps1` oder `start_snackhub.bat`).

Im Chat steht dann unten `Quelle: Ollama`, wenn die echte Ollama-API genutzt wird.

### Chat-Stile

Der Chatbot hat drei Modi:
- `slang` (locker)
- `normal` (neutral)
- `praesentation` (formal)

Du kannst den Stil direkt im Chatfenster umschalten oder in `.env` per `SNACKHUB_CHAT_STYLE` setzen.
