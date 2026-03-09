import json
import os
from urllib import error, request


_TOPIC_TEXT = {
    "voting_schueler": "Auf Voting kannst du abstimmen und deine Stimme spaeter aendern.",
    "voting_kantine": "Die Kantine startet Abstimmungen, pflegt Gerichte und sieht Live-Ergebnisse.",
    "shop": "Im Shop siehst du verfuegbare Gerichte mit Preis und Kategorie.",
    "feedback_schueler": "Auf Feedback gibst du Bewertung und Kommentar, optional anonym.",
    "feedback_overview": "Hier sieht die Kantine alle Rueckmeldungen gesammelt.",
    "vorbestellen_schueler": "Auf Vorbestellen buchst du das Gewinnergericht aus dem letzten Voting.",
    "vorbestellungen_kantine": "Hier verwaltet die Kantine offene Vorbestellungen und Zahlstatus.",
    "menu_kantine": "In Speisekarte pflegt die Kantine Gerichte, Preise und Verfuegbarkeit.",
    "login_register": "Login und Registrierung steuern den Einstieg fuer Schueler und Kantine.",
    "dashboard": "Das Dashboard ist die zentrale Navigation zu allen Hauptfunktionen.",
}

_TOPIC_KEYWORDS = {
    "voting_schueler": ["voting", "voiting", "abstimmung", "stimme", "stimmen"],
    "voting_kantine": ["voting kantine", "abstimmung kantine", "umfrage", "ergebnisse"],
    "shop": ["shop", "produkte", "gerichte"],
    "feedback_schueler": ["feedback", "bewertung", "kommentar", "anonym"],
    "feedback_overview": ["feedback uebersicht", "feedback overview", "rueckmeldung", "auswertung"],
    "vorbestellen_schueler": ["vorbestellen", "vorbestellung", "bestellen"],
    "vorbestellungen_kantine": ["offene zahlungen", "vorbestellungen kantine", "bezahlt", "offen"],
    "menu_kantine": ["menu", "menue", "speisekarte", "preise", "kategorie"],
    "login_register": ["login", "anmelden", "registrieren", "konto", "rolle"],
    "dashboard": ["dashboard", "startseite", "landing", "navigation"],
}

_ROUTE_TOPIC = {
    "/": "dashboard",
    "/login": "login_register",
    "/register": "login_register",
    "/dashboard": "dashboard",
    "/shop": "shop",
    "/voting": "voting_schueler",
    "/voting_kantine": "voting_kantine",
    "/feedback": "feedback_schueler",
    "/feedback_overview": "feedback_overview",
    "/menu_kantine": "menu_kantine",
    "/kantine_landing": "dashboard",
    "/vorbestellen": "vorbestellen_schueler",
    "/vorbestellungen_kantine": "vorbestellungen_kantine",
}

_STYLE_CONFIG = {
    "slang": {
        "label": "Slang",
        "openers": [
            "Yo, willkommen bei SnackHub. Was geht?",
            "Hey, ich hab dich. Wobei brauchst du Hilfe?",
            "Nice, frag einfach. Ich erklaer dir das fix.",
        ],
        "ollama_instruction": (
            "Sprich locker mit leichtem Jugend-Slang, aber bleib klar und respektvoll. "
            "Nutze kurze Saetze und konkrete Erklaerungen."
        ),
    },
    "normal": {
        "label": "Normal",
        "openers": [
            "Willkommen bei SnackHub, wie kann ich dir helfen?",
            "Hi, wobei brauchst du kurz Hilfe?",
            "Klar, ich helfe dir direkt mit SnackHub.",
        ],
        "ollama_instruction": (
            "Antworte freundlich, sachlich und leicht verstaendlich in normalem Deutsch."
        ),
    },
    "praesentation": {
        "label": "Praesentation",
        "openers": [
            "Willkommen zur SnackHub-Uebersicht. Wie kann ich helfen?",
            "Gern erklaere ich die Funktionen fuer eure Praesentation.",
            "Lass uns die SnackHub-Funktionen kompakt durchgehen.",
        ],
        "ollama_instruction": (
            "Antworte professionell, klar und praesentationstauglich. "
            "Nenne wenn passend kurze Stichpunkte in einem Satzfluss."
        ),
    },
}

AVAILABLE_CHAT_STYLES = tuple(_STYLE_CONFIG.keys())


def get_help_reply(
    user_message: str,
    route: str,
    history: list[dict] | None = None,
    style: str | None = None,
) -> str:
    message = (user_message or "").strip()
    style_key = _resolve_style(style)

    if not message:
        return _pick_opener(style_key, route or "/")

    local_hint = _build_local_help(message, route, style_key)
    ollama_answer, ollama_error = _call_ollama_help_api(
        model=_get_model(),
        base_url=_get_ollama_base_url(),
        user_message=message,
        route=route,
        local_hint=local_hint,
        history=history or [],
        style_key=style_key,
    )
    if ollama_answer:
        return f"{ollama_answer.strip()}\n\nQuelle: Ollama | Stil: {_style_label(style_key)}"

    reason = ollama_error or "Ollama nicht erreichbar"
    return f"{local_hint}\n\nQuelle: Lokal ({reason}) | Stil: {_style_label(style_key)}"


def _build_local_help(user_message: str, route: str, style_key: str) -> str:
    normalized_message = _normalize(user_message)
    matched_topics: list[str] = []

    for topic, keywords in _TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if _normalize(keyword) in normalized_message:
                matched_topics.append(topic)
                break

    route_topic = _ROUTE_TOPIC.get((route or "").split("?")[0], "")
    if not matched_topics and route_topic:
        matched_topics.append(route_topic)

    opener = _pick_opener(style_key, user_message + route)
    if not matched_topics:
        return f"{opener} Nenne einfach ein Stichwort wie 'Voting Funktionen'."

    unique_topics: list[str] = []
    for topic in matched_topics:
        if topic not in unique_topics:
            unique_topics.append(topic)

    first = _TOPIC_TEXT.get(unique_topics[0], "Ich erklaere dir gern die Funktionen.")
    if len(unique_topics) == 1:
        return f"{opener} {first}"

    second = _TOPIC_TEXT.get(unique_topics[1], "")
    if second:
        return f"{opener} {first} {second}"
    return f"{opener} {first}"


def _call_ollama_help_api(
    model: str,
    base_url: str,
    user_message: str,
    route: str,
    local_hint: str,
    history: list[dict],
    style_key: str,
) -> tuple[str | None, str | None]:
    dialog_lines: list[str] = []
    for item in history[-8:]:
        if not isinstance(item, dict):
            continue
        role = (item.get("role") or "").strip().lower()
        content = (item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            dialog_lines.append(f"{role}: {content}")

    conversation = "\n".join(dialog_lines) or "leer"
    prompt = (
        "Du bist der SnackHub Hilfs-Chatbot fuer ein Schulprojekt.\n"
        f"{_STYLE_CONFIG[style_key]['ollama_instruction']}\n"
        "Bleibe bei SnackHub und erklaere konkrete Funktionen.\n"
        "Antworte in maximal 3 kurzen Saetzen.\n\n"
        f"Aktuelle Route: {route or '/'}\n"
        f"Lokale Faktenbasis: {local_hint}\n\n"
        f"Dialog bisher:\n{conversation}\n\n"
        f"Nutzerfrage: {user_message}\n"
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7 if style_key == "slang" else 0.5,
        },
    }

    endpoint = f"{base_url}/api/generate"
    req = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=35) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = (data.get("response") or "").strip()
        if text:
            return text, None
        return None, "Leere Ollama-Antwort"
    except error.HTTPError as http_error:
        status = f"HTTP {http_error.code}"
        body = ""
        try:
            body = http_error.read().decode("utf-8", errors="replace")
        except Exception:
            body = "<no-body>"
        print(f"[help_chat_ollama_http_error] status={status} body={body[:500]}")
        return None, status
    except error.URLError as url_error:
        reason = str(getattr(url_error, "reason", "URLError"))
        print(f"[help_chat_ollama_url_error] {reason}")
        return None, f"Ollama nicht erreichbar: {reason}"
    except Exception as exc:
        reason = type(exc).__name__
        print(f"[help_chat_ollama_error] {reason}: {exc}")
        return None, reason


def _pick_opener(style_key: str, seed: str) -> str:
    openers = _STYLE_CONFIG[style_key]["openers"]
    index = sum(ord(ch) for ch in seed) % len(openers)
    return openers[index]


def _normalize(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("ae", "a")
    lowered = lowered.replace("oe", "o")
    lowered = lowered.replace("ue", "u")
    lowered = lowered.replace("ss", "s")
    return lowered


def _get_model() -> str:
    model = (os.getenv("SNACKHUB_HELP_MODEL") or "").strip()
    return model or "llama3.2:3b"


def _get_ollama_base_url() -> str:
    url = (os.getenv("OLLAMA_BASE_URL") or "").strip()
    if not url:
        return "http://127.0.0.1:11434"
    return url.rstrip("/")


def _resolve_style(style: str | None) -> str:
    raw = (style or os.getenv("SNACKHUB_CHAT_STYLE") or "slang").strip().lower()
    if raw in _STYLE_CONFIG:
        return raw
    return "slang"


def _style_label(style_key: str) -> str:
    return _STYLE_CONFIG.get(style_key, _STYLE_CONFIG["slang"])["label"]
