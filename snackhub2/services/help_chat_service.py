import json
import os
from urllib import error, request


_OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

_TOPIC_TEXT = {
    "voting_schueler": (
        "Voting (Schueler): Du siehst das aktive Essen-Voting, kannst genau eine Stimme abgeben "
        "oder spaeter aendern. Die Prozentanzeige und Stimmenzahl aktualisieren sich ueber den "
        "Aktualisieren-Button."
    ),
    "voting_kantine": (
        "Voting (Kantine): Die Kantine kann Abstimmungen starten, Gerichte zur Umfrage hinzufuegen "
        "und Ergebnisse live beobachten. Damit steuert ihr, welches Gericht als naechstes angeboten wird."
    ),
    "shop": (
        "Shop: Schueler sehen verfuegbare Gerichte aus der Speisekarte mit Preis und Kategorie. "
        "Die Seite dient als Uebersicht der aktuell angebotenen Produkte."
    ),
    "feedback_schueler": (
        "Feedback (Schueler): Schueler geben pro Woche eine Bewertung und einen Kommentar ab, optional "
        "anonym. Das hilft der Kantine, Angebot und Qualitaet zu verbessern."
    ),
    "feedback_overview": (
        "Feedback-Uebersicht (Kantine): Die Kantine sieht eingegangene Rueckmeldungen gesammelt "
        "und kann Trends oder wiederkehrende Probleme erkennen."
    ),
    "vorbestellen_schueler": (
        "Vorbestellen (Schueler): Basierend auf dem letzten Voting-Gewinner kann ein Schueler "
        "vorbestellen. Dadurch kann die Kantine besser planen und Lebensmittel sparen."
    ),
    "vorbestellungen_kantine": (
        "Vorbestellungen (Kantine): Die Kantine sieht offene Bestellungen und kann Zahlungen "
        "bzw. den Bearbeitungsstatus verwalten."
    ),
    "menu_kantine": (
        "Speisekarte (Kantine): Hier pflegt die Kantine Gerichte, Preise, Kategorien und Verfuegbarkeit. "
        "Aenderungen wirken sich direkt auf die Shop-Ansicht aus."
    ),
    "login_register": (
        "Login/Registrierung: Nutzer melden sich mit Rolle an (Schueler oder Kantine). "
        "Je nach Rolle landen sie in unterschiedlichen Dashboards."
    ),
    "dashboard": (
        "Dashboard: Das Dashboard ist die zentrale Navigation. Schueler kommen zu Shop, Voting, "
        "Feedback und Vorbestellung. Kantine bekommt Management-Karten fuer Betrieb und Auswertung."
    ),
}

_TOPIC_KEYWORDS = {
    "voting_schueler": ["voting", "voiting", "abstimmung", "stimme", "stimmen"],
    "voting_kantine": ["voting kantine", "abstimmung kantine", "umfrage", "ergebnisse"],
    "shop": ["shop", "produkte", "gerichte", "speisekarte schueler"],
    "feedback_schueler": ["feedback", "bewertung", "kommentar", "anonym"],
    "feedback_overview": ["feedback uebersicht", "feedback overview", "rueckmeldung", "auswertung"],
    "vorbestellen_schueler": ["vorbestellen", "vorbestellung", "bestellen", "voting gewinner"],
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


def get_help_reply(user_message: str, route: str, history: list[dict] | None = None) -> str:
    message = (user_message or "").strip()
    if not message:
        return "Schreibe bitte kurz, wobei du Hilfe brauchst, z. B. 'Funktionen Voting'."

    local_hint = _build_local_help(message, route)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            f"{local_hint}\n\n"
            "Hinweis: Fuer einen echten ChatGPT-Dialog bitte OPENAI_API_KEY setzen."
        )

    api_answer = _call_openai_help_api(
        api_key=api_key,
        model=_get_model(),
        user_message=message,
        route=route,
        local_hint=local_hint,
        history=history or [],
    )
    if api_answer:
        return api_answer

    return (
        f"{local_hint}\n\n"
        "Hinweis: Die API war gerade nicht erreichbar, daher lokale Hilfeantwort."
    )


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

    if not matched_topics:
        return (
            "Ich kann dir die SnackHub-Seiten erklaeren: Voting, Shop, Feedback, "
            "Vorbestellen, Speisekarte, Login und Dashboard. "
            "Nenne einfach ein Stichwort wie 'Voting Funktionen'."
        )

    unique_topics: list[str] = []
    for topic in matched_topics:
        if topic not in unique_topics:
            unique_topics.append(topic)

    lines = ["Klar, hier ist die passende SnackHub-Hilfe:"]
    for topic in unique_topics[:3]:
        lines.append(f"- {_TOPIC_TEXT.get(topic, '')}")

    return "\n".join(lines)


def _call_openai_help_api(
    api_key: str,
    model: str,
    user_message: str,
    route: str,
    local_hint: str,
    history: list[dict],
) -> str | None:
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
        "Erklaere Funktionen praezise und kurz in einfachem Deutsch. "
        "Bleibe bei SnackHub, nenne konkrete Klickpfade und gib keine erfundenen Datenbankdetails aus."
    )
    user_prompt = (
        f"Aktuelle Route: {route or '/'}\n"
        f"Lokale Faktenbasis:\n{local_hint}\n\n"
        f"Bisheriger Dialog:\n{conversation or 'leer'}\n\n"
        f"Neue Nutzerfrage:\n{user_message}\n\n"
        "Antworte in 4 bis 8 Saetzen. Wenn die Frage unklar ist, frage gezielt nach."
    )

    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_output_tokens": 260,
        "temperature": 0.2,
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
        return _extract_output_text(data)
    except error.HTTPError as http_error:
        body = ""
        try:
            body = http_error.read().decode("utf-8", errors="replace")
        except Exception:
            body = "<no-body>"
        print(
            f"[help_chat_api_http_error] status={http_error.code} body={body[:500]}"
        )
        return None
    except Exception as exc:
        print(f"[help_chat_api_error] {exc}")
        return None


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
