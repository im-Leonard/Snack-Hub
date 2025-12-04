import flet as ft

def dashboard_router(page: ft.Page):
    role = page.session.get("role")

    if not role:
        return ft.View("/dashboard", [ft.Text("Keine Berechtigung")])

    if role == "schueler":
        return ft.View("/dashboard", [ft.Text("Schüler Dashboard")])

    if role == "kantine":
        return ft.View("/dashboard", [ft.Text("Kantinen Dashboard")])

    return ft.View("/dashboard", [ft.Text("Unbekannte Rolle")])
