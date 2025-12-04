import flet as ft
from services.auth_service import register_user

def register_page(page: ft.Page):

    username = ft.TextField(label="Benutzername", width=300)
    pw = ft.TextField(label="Passwort", password=True, width=300)
    role = ft.Dropdown(
        label="Rolle",
        width=300,
        options=[
            ft.dropdown.Option("schueler"),
            ft.dropdown.Option("kantine"),
        ]
    )

    def handle_reg(e):
        register_user(username.value, pw.value, role.value)
        page.snack_bar = ft.SnackBar(ft.Text("Registrierung erfolgreich"))
        page.snack_bar.open = True
        page.update()
        page.go("/login")

    return ft.View(
        route="/register",
        controls=[
            ft.Column(
                [
                    ft.Image(src="assets/snackhub_logo.png", height=120),
                    ft.Text("Registrieren", size=28, weight="bold"),
                    username,
                    pw,
                    role,
                    ft.ElevatedButton("Registrieren", on_click=handle_reg),
                ],
                alignment="center",
                horizontal_alignment="center"
            )
        ]
    )
