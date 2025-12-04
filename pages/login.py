import flet as ft
from services.auth_service import login_user

def login_page(page: ft.Page):

    username = ft.TextField(label="Benutzername", width=300)
    pw = ft.TextField(label="Passwort", password=True, width=300)

    def handle_login(e):
        user = login_user(username.value, pw.value)

        if not user:
            page.snack_bar = ft.SnackBar(ft.Text("Login fehlgeschlagen"))
            page.snack_bar.open = True
            page.update()
            return

        page.session.set("user_id", user["user_id"])
        page.session.set("role", user["role"])
        page.go("/dashboard")

    return ft.View(
        route="/login",
        controls=[
            ft.Column(
                [
                    ft.Image(src="assets/snackhub_logo.png", height=120),
                    ft.Text("Anmelden", size=28, weight="bold"),
                    username,
                    pw,
                    ft.ElevatedButton("Login", on_click=handle_login),
                    ft.TextButton("Registrieren", on_click=lambda _: page.go("/register")),
                ],
                alignment="center",
                horizontal_alignment="center"
            )
        ]
    )
