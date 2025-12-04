import flet as ft

def landing_page(page: ft.Page):
    logo = ft.Image(src="assets/snackhub_logo.png", height=120)

    news = ft.Container(
        bgcolor="#FFF3D2",
        border_radius=20,
        padding=20,
        content=ft.Column([
            ft.Text("Neuigkeiten", size=26, weight="bold"),
            ft.Text("Noch keine Einträge.")
        ])
    )

    menu = ft.Container(
        bgcolor="#FFF3D2",
        border_radius=20,
        padding=20,
        content=ft.Column([
            ft.Text("Tagesmenü", size=26, weight="bold"),
            ft.Text("Keine Angaben.")
        ])
    )

    return ft.View(
        route="/",
        controls=[
            ft.Column(
                [
                    logo,
                    ft.Row(
                        [ft.TextButton("Login", on_click=lambda _: page.go("/login"))],
                        alignment="center"
                    ),
                    ft.Row([news, menu], alignment="center", spacing=40)
                ],
                horizontal_alignment="center",
                alignment="center"
            )
        ]
    )
