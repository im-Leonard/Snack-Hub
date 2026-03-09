import asyncio
import os

import flet as ft

from snackhub2.services.help_chat_service import AVAILABLE_CHAT_STYLES, get_help_reply


def build_help_chat(page: ft.Page) -> ft.Control:
    state = _get_chat_state(page)

    messages_column = ft.Column(
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    status_text = ft.Text("", size=12, color="#6A6A6A")
    input_field = ft.TextField(
        hint_text="Frage zu SnackHub eingeben...",
        multiline=True,
        min_lines=1,
        max_lines=3,
        bgcolor="white",
        border_radius=10,
        border_color="#E0CFA0",
        text_style=ft.TextStyle(color="black"),
    )

    def safe_update():
        try:
            page.update()
        except Exception:
            return

    def render_messages():
        messages_column.controls.clear()
        for item in state["history"][-24:]:
            role = item.get("role")
            content = item.get("content", "")
            is_user = role == "user"

            bubble = ft.Container(
                bgcolor="#FFD68A" if is_user else "#FFFFFF",
                border=ft.border.all(1, "#E7D4AD"),
                border_radius=12,
                padding=10,
                content=ft.Text(content, color="black", selectable=True),
            )
            messages_column.controls.append(
                ft.Container(
                    alignment=ft.Alignment.CENTER_RIGHT if is_user else ft.Alignment.CENTER_LEFT,
                    content=bubble,
                )
            )

        if state.get("busy"):
            messages_column.controls.append(
                ft.Container(
                    alignment=ft.Alignment.CENTER_LEFT,
                    content=ft.Text("Bot schreibt...", color="#777777", size=12),
                )
            )

    async def run_help_request(user_text: str):
        try:
            reply = await asyncio.to_thread(
                get_help_reply,
                user_text,
                page.route or "/",
                state["history"],
                state.get("style", "slang"),
            )
        except Exception as exc:
            reply = f"Fehler beim Helfer-Chat: {exc}"

        state["history"].append({"role": "assistant", "content": reply})
        state["busy"] = False
        status_text.value = ""
        render_messages()
        safe_update()

    def send_message(_):
        user_text = (input_field.value or "").strip()
        if not user_text or state.get("busy"):
            return

        state["history"].append({"role": "user", "content": user_text})
        input_field.value = ""
        state["busy"] = True
        status_text.value = "Antwort wird geladen..."
        render_messages()
        safe_update()
        page.run_task(run_help_request, user_text)

    def ask_quick(topic: str):
        input_field.value = f"Erklaere mir bitte kurz die Funktionen der {topic}-Seite."
        send_message(None)

    def toggle_chat(_):
        state["open"] = not state["open"]
        panel.visible = state["open"]
        chat_toggle_label.value = "x" if state["open"] else "Hilfe"
        safe_update()

    def on_style_change(_):
        selected = (style_dropdown.value or "slang").strip().lower()
        if selected not in AVAILABLE_CHAT_STYLES:
            selected = "slang"
        state["style"] = selected
        state["history"].append(
            {
                "role": "assistant",
                "content": (
                    f"Stil gesetzt auf {style_mapping.get(selected, selected)}. "
                    "Frag mich was zu Voting, Shop oder Feedback."
                ),
            }
        )
        render_messages()
        safe_update()

    style_dropdown.on_select = on_style_change

    quick_row = ft.Row(
        controls=[
            ft.OutlinedButton("Voting", on_click=lambda _: ask_quick("Voting")),
            ft.OutlinedButton("Shop", on_click=lambda _: ask_quick("Shop")),
            ft.OutlinedButton("Feedback", on_click=lambda _: ask_quick("Feedback")),
        ],
        wrap=True,
        spacing=6,
    )

    render_messages()

    panel = ft.Container(
        visible=state["open"],
        width=360,
        height=460,
        bgcolor="#FFF7E6",
        border=ft.border.all(1, "#E7D4AD"),
        border_radius=16,
        padding=12,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=16,
            color="#55000000",
            offset=ft.Offset(0, 6),
        ),
        content=ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text("SnackHub Hilfe", size=18, weight="bold", color="black", expand=True),
                        ft.TextButton("Schliessen", on_click=toggle_chat),
                    ]
                ),
                ft.Text(
                    "Frag nach Funktionen wie Voting, Shop, Feedback oder Vorbestellen.",
                    size=12,
                    color="#555555",
                ),
                ft.Row(
                    controls=[
                        ft.Text("Antwortstil:", size=12, color="#555555"),
                        style_dropdown,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                quick_row,
                ft.Container(
                    expand=True,
                    bgcolor="#FFF3D2",
                    border_radius=10,
                    padding=8,
                    content=messages_column,
                ),
                status_text,
                ft.Row(
                    [
                        ft.Container(expand=True, content=input_field),
                        ft.ElevatedButton(
                            "Senden",
                            on_click=send_message,
                            style=ft.ButtonStyle(
                                bgcolor="#FFA726",
                                color="black",
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
            ],
            spacing=8,
            expand=True,
        ),
    )

    chat_toggle_label = ft.Text(
        "x" if state["open"] else "Hilfe",
        color="black",
        weight="bold",
    )

    toggle_button = ft.Container(
        bgcolor="#FFA726",
        border_radius=999,
        padding=ft.padding.symmetric(horizontal=18, vertical=12),
        border=ft.border.all(1, "#E09E2F"),
        content=chat_toggle_label,
        ink=True,
        on_click=toggle_chat,
    )

    return ft.Container(
        right=18,
        bottom=18,
        content=ft.Column(
            controls=[panel, toggle_button],
            horizontal_alignment=ft.CrossAxisAlignment.END,
            spacing=8,
            tight=True,
        ),
    )


def _get_chat_state(page: ft.Page) -> dict:
    if not hasattr(page, "data") or page.data is None:
        page.data = {}

    chat_state = page.data.get("_help_chat")
    if isinstance(chat_state, dict):
        if "history" not in chat_state:
            chat_state["history"] = []
        if "open" not in chat_state:
            chat_state["open"] = False
        if "busy" not in chat_state:
            chat_state["busy"] = False
        if "style" not in chat_state or chat_state["style"] not in AVAILABLE_CHAT_STYLES:
            chat_state["style"] = _default_style()
        return chat_state

    chat_state = {
        "open": False,
        "busy": False,
        "style": _default_style(),
        "history": [
            {
                "role": "assistant",
                "content": _initial_welcome(_default_style()),
            }
        ],
    }
    page.data["_help_chat"] = chat_state
    return chat_state


def _default_style() -> str:
    raw = (os.getenv("SNACKHUB_CHAT_STYLE") or "slang").strip().lower()
    if raw in AVAILABLE_CHAT_STYLES:
        return raw
    return "slang"


def _initial_welcome(style: str) -> str:
    if style == "praesentation":
        return (
            "Willkommen zur SnackHub-Uebersicht. "
            "Nenne z. B. 'Voting Funktionen'."
        )
    if style == "normal":
        return (
            "Willkommen bei SnackHub, wie kann ich dir helfen? "
            "Nenne z. B. 'Voting Funktionen'."
        )
    return (
        "Yo, willkommen bei SnackHub. "
        "Nenne z. B. 'Voting Funktionen'."
    )
    style_mapping = {
        "slang": "Slang",
        "normal": "Normal",
        "praesentation": "Praesentation",
    }

    style_dropdown = ft.Dropdown(
        label="Stil",
        width=145,
        value=state.get("style", "slang"),
        bgcolor="white",
        border_radius=10,
        border_color="#E0CFA0",
        dense=True,
        text_size=12,
        options=[
            ft.dropdown.Option(k, style_mapping.get(k, k.title()))
            for k in AVAILABLE_CHAT_STYLES
        ],
    )
