import flet as ft
from snackhub2.components.header import global_header

def schueler_landing_page(page: ft.Page):
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
                ft.Text("Jetzt für Gerichte in deiner Kantine abstimmen", size=16, color="black"),
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
                ft.Text("Vorbestellen", size=26, weight="bold", color="black"),
                ft.Text("Zahle für deine Gerichte im Voraus!", size=16, color="black"),
            ],
            spacing=10,
        ),
    )

    # --- Großes Logo + Slogan ---
    logo_section = ft.Column(
        [
            ft.Container(
                width=200,
                height=200,
                bgcolor="#FF6B6B",
                border_radius=20,
                alignment=ft.Alignment.CENTER,
                content=ft.Text("SNACKHUB", color="white", weight="bold", size=24)
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
        content=ft.Text("© 2025 SnackHub – Projektarbeit RDF 2026", color="black", size=14),
    )

    return ft.View(
        route="/schueler_landing",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                controls=[
                    global_header(page),
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
