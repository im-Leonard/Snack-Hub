import json
import os
from urllib import error, request


_OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

_TOPIC_TEXT = {
    "voting_schueler": "Auf Voting kannst du abstimmen und deine Stimme spaeter aendern.",
    "voting_kantine": "Die Kantine startet Abstimmungen, pflegt Gerichte und sieht Live-Ergebnisse.",
    "shop": "Im Shop siehst du verfuegbare Gerichte mit Preis und Kategorie.",
    "feedback_schueler": "Auf Feedback gibst du Bewertung und Kommentar, optional anonym.",
    "feedback_overview": "Hier sieht die Kantine alle Rueckmeldungen gesammelt.",
    "vorbestellen_schueler": "Auf Vorbestellen buchst du das Gewinnergericht aus dem letzten Voting.",
    "vorbestellungen_kantine": "Hier verwaltet die Kantine offene Vorbestellungen und Zahlstatus.",
    "menu_kantine": "In Speisekarte pflegt die Kantine Gerichte, Preise und Verfuegbarkeit.",
    "login_register": "Login/Registrierung steuert den Einstieg fuer Schueler und Kantine-Rolle.",
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

_OPENERS = [
    "Willkommen bei SnackHub, wie kann ich dir helfen?",
    "Hi, wobei brauchst du in SnackHub kurz Hilfe?",
    "Klar, ich helfe dir direkt mit SnackHub.",
]


def get_help_reply(user_message: str, route: str, history: list[dict] | None = None) -> str:
    message = (user_message or "").strip()
    if not message:
        return "Willkommen bei SnackHub, wie kann ich dir helfen?"

    local_hint = _build_local_help(message, route)
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        return f"{local_hint}\n\nQuelle: Lokal (OPENAI_API_KEY fehlt)"

    api_answer, api_error = _call_openai_help_api(
        api_key=api_key,
        model=_get_model(),
        user_message=message,
        route=route,
        local_hint=local_hint,
        history=history or [],
    )
    if api_answer:
        return f"{api_answer.strip()}\n\nQuelle: OpenAI"

    reason = api_error or "API nicht erreichbar"
    return f"{local_hint}\n\nQuelle: Lokal ({reason})"


def _build_local_help(user_message: str, route: str) -> str:
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

    opener = _pick_opener(user_message + route)
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


def _call_openai_help_api(
    api_key: str,
    model: str,
    user_message: str,
    route: str,
    local_hint: str,
    history: list[dict],
) -> tuple[str | None, str | None]:
    dialog_lines: list[str] = []
    for item in history[-8:]:
        if not isinstance(item, dict):
            continue
        role = (item.get("role") or "").strip()
        content = (item.get("content") or "").strip()
        if role and content:
            dialog_lines.append(f"{role}: {content}")

    conversation = "\n".join(dialog_lines)
    system_prompt = (
        "Du bist der SnackHub Hilfs-Chatbot fuer ein Schulprojekt. "
        "Antworte kurz, freundlich und in einfachem Deutsch. "
        "Bleibe bei SnackHub und erklaere konkrete Funktionen."
    )
    user_prompt = (
        f"Aktuelle Route: {route or '/'}\n"
        f"Lokale Faktenbasis:\n{local_hint}\n\n"
        f"Dialog:\n{conversation or 'leer'}\n\n"
        f"Nutzerfrage:\n{user_message}\n\n"
        "Antworte in maximal 3 kurzen Saetzen."
    )

    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_output_tokens": 180,
        "temperature": 0.6,
    }

    req = request.Request(
        _OPENAI_RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return _extract_output_text(data), None
    except error.HTTPError as http_error:
        status = f"HTTP {http_error.code}"
        body = ""
        try:
            body = http_error.read().decode("utf-8", errors="replace")
        except Exception:
            body = "<no-body>"
        print(f"[help_chat_api_http_error] status={status} body={body[:500]}")
        return None, status
    except Exception as exc:
        reason = type(exc).__name__
        print(f"[help_chat_api_error] {reason}: {exc}")
        return None, reason


def _extract_output_text(api_response: dict) -> str | None:
    output_text = api_response.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    if isinstance(output_text, list):
        merged = "".join(part for part in output_text if isinstance(part, str)).strip()
        if merged:
            return merged

    output_items = api_response.get("output")
    if not isinstance(output_items, list):
        return None

    chunks: list[str] = []
    for item in output_items:
        if not isinstance(item, dict):
            continue
        content_parts = item.get("content")
        if not isinstance(content_parts, list):
            continue
        for part in content_parts:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str):
                chunks.append(text)

    merged_chunks = "".join(chunks).strip()
    return merged_chunks or None


def _pick_opener(seed: str) -> str:
    index = sum(ord(ch) for ch in seed) % len(_OPENERS)
    return _OPENERS[index]


def _normalize(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("ae", "a")
    lowered = lowered.replace("oe", "o")
    lowered = lowered.replace("ue", "u")
    lowered = lowered.replace("ss", "s")
    lowered = lowered.replace("ä", "a")
    lowered = lowered.replace("ö", "o")
    lowered = lowered.replace("ü", "u")
    return lowered


def _get_model() -> str:
    model = (os.getenv("SNACKHUB_HELP_MODEL") or "").strip()
    return model or "gpt-4o-mini"
