import flet as ft
from pathlib import Path

def global_header(page: ft.Page):
    # Prüfe ob Nutzer eingeloggt ist
    if not hasattr(page, "data") or page.data is None:
        page.data = {}
    user_id = page.data.get("user_id")
    username = page.data.get("username")
    role = page.data.get("role")

    # Logout-Funktion
    def logout(e):
        if hasattr(page, "data") and page.data:
            page.data.clear()
        page.go("/login")

    # Navigation nur für eingeloggte Nutzer
    nav_buttons = []
    if user_id and role == "schueler":
        nav_buttons = [
            ft.TextButton(
                "Shop",
                on_click=lambda _: page.go("/shop"),
                style=ft.ButtonStyle(
                    color="black",
                    text_style=ft.TextStyle(size=22, weight="bold"),
                ),
            ),
            ft.TextButton(
                "Voting",
                on_click=lambda _: page.go("/voting"),
                style=ft.ButtonStyle(
                    color="black",
                    text_style=ft.TextStyle(size=22, weight="bold"),
                ),
            ),
            ft.TextButton(
                "Feedback",
                on_click=lambda _: page.go("/feedback"),
                style=ft.ButtonStyle(
                    color="black",
                    text_style=ft.TextStyle(size=22, weight="bold"),
                ),
            ),
        ]
    elif user_id and role == "kantine":
        nav_buttons = [
            ft.TextButton(
                "Feedback Übersicht",
                on_click=lambda _: page.go("/feedback_overview"),
                style=ft.ButtonStyle(
                    color="black",
                    text_style=ft.TextStyle(size=22, weight="bold"),
                ),
            ),
        ]

    # Login/Logout Button
    if user_id:
        auth_button = ft.Row(
            [
                ft.Text(f"{username}", size=16, color="black", weight="bold"),
                ft.IconButton(
                    icon=ft.icons.Icons.LOGOUT,
                    icon_color="black",
                    icon_size=30,
                    on_click=logout,
                    tooltip="Logout",
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
        )
    else:
        auth_button = ft.IconButton(
            icon=ft.icons.Icons.ACCOUNT_CIRCLE,
            icon_color="black",
            icon_size=30,
            on_click=lambda _: page.go("/login"),
            tooltip="Login",
        )

    def _logo_control() -> ft.Control:
        filenames = [
            "snackhub_raw.png",
            "snackhub_raw.PNG",
            "snackhub_logo_gross.png",  # Fallback, falls raw fehlt
            "snackhub_logo_gross.PNG",
        ]

        base_dirs = [
            Path(__file__).resolve().parents[1] / "assets",  # snackhub2/assets
            Path(__file__).resolve().parents[2] / "assets",  # projekt_root/assets (falls vorhanden)
            Path.cwd() / "assets",                           # cwd/assets
        ]

        for d in base_dirs:
            for name in filenames:
                p = d / name
                if p.exists():
                    return ft.Image(
                        src=name,
                        height=80,
                        fit=ft.BoxFit.CONTAIN,
                    )

        # Fallback: nutzt Flet asset serving (sollte durch main.py jetzt funktionieren)
        return ft.Image(
            src="snackhub_raw.png",
            height=80,
            fit=ft.BoxFit.CONTAIN,
        )

    logo_section = ft.Container(
        content=_logo_control(),
        width=300,
        alignment=ft.Alignment.CENTER_LEFT,
    )

    nav_section = ft.Container(
        content=ft.Row(
            controls=nav_buttons,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        ),
        expand=True,
        alignment=ft.Alignment.CENTER,
    )

    auth_section = ft.Container(
        content=auth_button,
        width=300,
        alignment=ft.Alignment.CENTER_RIGHT,
    )

    header_content = ft.Row(
        controls=[logo_section, nav_section, auth_section],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        content=header_content,
        bgcolor="#FFF3D2",
        height=70,
        padding=ft.padding.symmetric(horizontal=20),
    )
