import flet as ft
from pages.landing import landing_page
from pages.login import login_page
from pages.register import register_page
from pages.dashboard_router import dashboard_router

def main(page: ft.Page):
    page.title = "SnackHub"
    page.window_width = 1500
    page.window_height = 900

    def route_change(route):
        page.views.clear()

        if page.route == "/":
            page.views.append(landing_page(page))

        elif page.route == "/login":
            page.views.append(login_page(page))

        elif page.route == "/register":
            page.views.append(register_page(page))

        elif page.route.startswith("/dashboard"):
            page.views.append(dashboard_router(page))

        else:
            page.views.append(ft.View("/", [ft.Text("404 – Seite nicht gefunden")]))

        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main, assets_dir="assets")
