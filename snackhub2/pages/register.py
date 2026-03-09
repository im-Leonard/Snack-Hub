import flet as ft
from snackhub2.components.header import global_header
from snackhub2.services.auth_service import AuthService

def register_page(page: ft.Page):
    auth = AuthService()

    def _show_success_dialog() -> None:
        def close_and_go(_):
            page.pop_dialog()
            page.go("/login")

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor="#FFE8B5",
            title=ft.Column(
                [
                    ft.Image(src="snackhub_raw.png", height=80, fit=ft.BoxFit.CONTAIN),
                    ft.Text("Registrierung erfolgreich!", weight="bold", color="#222"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            content=ft.Text("Du bist jetzt startklar, Bitte logge dich ein!.", color="black"),
            actions=[
                ft.ElevatedButton(
                    "OK",
                    on_click=close_and_go,
                    style=ft.ButtonStyle(
                        bgcolor="#FFA726",
                        color="black",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog)

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
    role = ft.Dropdown(
        label="Rolle",
        width=300,
        bgcolor="white",
        border_radius=8,
        text_style=ft.TextStyle(color="black"),
        label_style=ft.TextStyle(color="#555555"),
        border_color="#CCCCCC",
        options=[
            ft.dropdown.Option("Schüler"),
            ft.dropdown.Option("Kantine"),
        ]
    )

    def handle_reg(e):
        role_mapping = {
            "Schüler": "schueler",
            "Kantine": "kantine"
        }
        role_value = role_mapping.get(role.value, "schueler")
        try:
            auth.register_user((username.value or "").strip(), pw.value or "", role_value)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Registrierung fehlgeschlagen: {ex}", color="white"),
                bgcolor="red",
            )
            page.snack_bar.open = True
            page.update()
            return

        _show_success_dialog()

    return ft.View(
        route="/register",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,  # NEW
                controls=[
                    global_header(page),
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
                                    ft.Text("Registrieren", size=22, weight="bold", color="black"),
                                    username,
                                    pw,
                                    role,
                                    ft.ElevatedButton(
                                        "Registrieren",
                                        on_click=handle_reg,
                                        width=300,
                                        style=ft.ButtonStyle(
                                            bgcolor="#FFA726",
                                            color="black",
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=15,
                            ),
                        ),
                    ),
                ],
            )
        ]
    )
