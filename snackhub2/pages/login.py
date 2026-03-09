import flet as ft
from snackhub2.services.auth_service import AuthService

def login_page(page: ft.Page):
    auth = AuthService()

    username = ft.TextField(
        label="Benutzername",
        width=300,
        bgcolor="white",
        border_radius=8,
        text_style=ft.TextStyle(color="black"),
        label_style=ft.TextStyle(color="#555555"),
        border_color="#CCCCCC"
    )
    pw = ft.TextField(
        label="Passwort",
        password=True,
        width=300,
        bgcolor="white",
        border_radius=8,
        text_style=ft.TextStyle(color="black"),
        label_style=ft.TextStyle(color="#555555"),
        border_color="#CCCCCC"
    )

    login_error_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Login fehlgeschlagen", color="black"),
        content=ft.Text(
            "Bitte prüfe Benutzername und Passwort.\n\nDemo:\nschueler_test / test123\nkantine_test / test123",
            color="black",
        ),
        actions=[
            ft.TextButton(
                "OK",
                on_click=lambda _: _close_login_error(),
                style=ft.ButtonStyle(color="#D35400"),
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor="#FFF3D2",
    )

    def _close_login_error():
        login_error_dialog.open = False
        page.update()

    def handle_login(e):
        username.value = (username.value or "").strip()
        password_value = pw.value or ""
        user = auth.login_user(username.value, password_value)

        if not user:
            page.dialog = login_error_dialog
            login_error_dialog.open = True
            page.update()
            return

        if not hasattr(page, 'data') or page.data is None:
            page.data = {}
        # Objekt ablegen (für Klassen-Nachweis) + kompatible Keys behalten
        page.data["user"] = user
        page.data.update(user.to_page_data())

        if page.data.get("role") == "schueler":
            page.go("/dashboard")
        elif page.data.get("role") == "kantine":
            page.go("/kantine_landing")
        else:
            page.go("/")

    return ft.View(
        route="/login",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,  # NEW
                controls=[
                    ft.Container(
                        padding=ft.padding.only(left=20, top=10),
                        content=ft.TextButton(
                            "← Zurück",
                            on_click=lambda _: page.go("/"),
                            style=ft.ButtonStyle(color="black"),
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Container(
                            bgcolor="#FFE8B5",
                            border_radius=20,
                            padding=25,
                            content=ft.Column(
                                [
                                    ft.Image(
                                        src="snackhub_raw.png",
                                        height=120,
                                        fit=ft.BoxFit.CONTAIN,
                                    ),
                                    ft.Text("Anmelden", size=22, weight="bold", color="black"),
                                    username,
                                    pw,
                                    ft.ElevatedButton(
                                        "Login",
                                        on_click=handle_login,
                                        width=300,
                                        style=ft.ButtonStyle(
                                            bgcolor="#FFA726",
                                            color="black",
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                    ),
                                    ft.ElevatedButton(
                                        "Registrieren",
                                        on_click=lambda _: page.go("/register"),
                                        width=300,
                                        style=ft.ButtonStyle(
                                            bgcolor="#FFA726",
                                            color="black",
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                    ),
                                    ft.Text(
                                        "Demo-Logins:\nschueler_test / test123\nkantine_test / test123",
                                        size=12,
                                        color="#444444",
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=15,
                            ),
                        ),
                    ),
                ],
            ),
        ]
    )
