import flet as ft
from snackhub2.components.header import global_header


def landing_page(page: ft.Page):
    # --- Box 1: Neuigkeiten ---
    news_box = ft.Container(
        bgcolor="#FFE8B5",
        padding=25,
        border_radius=20,
        width=420,
        height=220,
        content=ft.Column(
            [
                ft.Text("Einmal Schnitzel bitte!", size=26, weight="bold", color="black"),
                ft.Text("Jetzt für Gerichte in deiner Kantine abstimmen!", size=16, color="black"),
            ],
            spacing=10,
        ),
    )

    # --- Box 2: Tagesmenü ---
    menu_box = ft.Container(
        bgcolor="#FFE8B5",
        padding=25,
        border_radius=20,
        width=420,
        height=220,
        content=ft.Column(
            [
                ft.Text("Zahle dein Gericht im Voraus!", size=26, weight="bold", color="black"),
                ft.Text("Dein Kiosk kann Lebensmittel einsparen wenn du dein Gericht im Voraus bezahlst und bestätigst!", size=16, color="black"),
            ],
            spacing=10,
        ),
    )

    # --- Großes Logo + Slogan ---
    logo_section = ft.Column(
        [
            ft.Image(
                src="snackhub_raw.png",
                height=260,
                fit=ft.BoxFit.CONTAIN,
            ),
            ft.Text(
                "Deine Kantine oder Kiosk, jetzt online!",
                size=20,
                weight="bold",
                color="black",
            ),
        ],
        horizontal_alignment="center",
        spacing=10,
    )

    # --- Footer ---
    footer = ft.Container(
        bgcolor="#FFE8B5",
        padding=15,
        alignment=ft.Alignment.CENTER,
        content=ft.Text("© 2025 SnackHub – Schulprojekt", color="black", size=14),
    )

    return ft.View(
        route="/",
        bgcolor="#FFF3D2",
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,  # NEW
                controls=[
                    global_header(page),

                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        padding=ft.padding.only(top=10),
                        content=ft.ElevatedButton(
                            "Anmelden/Registrieren",
                            on_click=lambda _: page.go("/login"),
                            style=ft.ButtonStyle(
                                bgcolor="#FFA726",
                                color="black",
                                shape=ft.RoundedRectangleBorder(radius=20),
                                padding=ft.padding.symmetric(horizontal=28, vertical=14),
                            ),
                        ),
                    ),

                    ft.Column(
                        expand=True,
                        horizontal_alignment="center",
                        controls=[
                            ft.Row(
                                [news_box, logo_section, menu_box],
                                alignment="center",
                                spacing=50,
                            ),
                        ],
                    ),

                    footer,
                ],
            )
        ],
    )
