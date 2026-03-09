import flet as ft
import asyncio
from snackhub2.pages.kantine.landing import kantine_landing_page
from snackhub2.components.header import global_header

def _menu_btn(label: str, on_click, active: bool = False):
    return ft.ElevatedButton(
        label,
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor="#F4A62A" if active else "#FFA726",
            color="black",
            text_style=ft.TextStyle(size=18, weight=ft.FontWeight.W_600),
            shape=ft.RoundedRectangleBorder(radius=24),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
        ),
    )

def _student_menu_row(page: ft.Page, active: str = ""):
    active = (active or "").lower()
    return ft.Row(
        [
            _menu_btn("Shop", lambda _: page.go("/shop"), active == "shop"),
            _menu_btn("Voting", lambda _: page.go("/voting"), active == "voting"),
            _menu_btn("Feedback", lambda _: page.go("/feedback"), active == "feedback"),
            _menu_btn("Vorbestellen", lambda _: page.go("/vorbestellen"), active == "vorbestellen"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=14,
        wrap=True,
    )

def student_menu_bar(page: ft.Page, active: str = ""):
    # bleibt für Kompatibilität bestehen
    return ft.Container(
        alignment=ft.Alignment.TOP_CENTER,
        padding=ft.padding.only(top=10, bottom=12),
        content=_student_menu_row(page, active),
    )

def student_top_bar(page: ft.Page, active: str = ""):
    return ft.Container(
        padding=ft.padding.only(left=16, top=10, right=16),
        content=ft.Row(
            [
                ft.Image(src="snackhub_raw.png", height=56, fit=ft.BoxFit.CONTAIN),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=_student_menu_row(page, active),
                ),
                _logout_btn(page),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

def _logout_btn(page: ft.Page):
    def _logout(_):
        page.data = {}
        page.views.clear()
        page.route = "/"
        if page.on_route_change:
            page.on_route_change(None)
        else:
            page.update()

    return ft.ElevatedButton(
        "Logout",
        on_click=_logout,
        style=ft.ButtonStyle(
            bgcolor="#FFA726",
            color="black",
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_600),
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.padding.symmetric(horizontal=18, vertical=10),
        ),
    )

def _student_hero_logo(page: ft.Page):
    hero = ft.Container(
        alignment=ft.Alignment.CENTER,
        scale=ft.Scale(0.7),
        animate_scale=ft.Animation(520, ft.AnimationCurve.EASE_OUT_BACK),
        content=ft.Image(
            src="snackhub_raw.png",
            height=320,  # größer
            fit=ft.BoxFit.CONTAIN,
        ),
    )

    async def pop():
        await asyncio.sleep(0.05)
        hero.scale = ft.Scale(1.0)
        page.update()

    page.run_task(pop)
    return hero

def dashboard_router(page: ft.Page):
    if not hasattr(page, "data") or page.data is None:
        page.data = {}
    role = page.data.get("role")

    if role == "schueler":
        return ft.View(
            route="/dashboard",
            bgcolor="#FFF3D2",
            controls=[
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        student_top_bar(page, active=""),
                        _student_hero_logo(page),
                    ],
                )
            ],
        )

    if role == "kantine":
        return kantine_landing_page(page)

    return ft.View(
        route="/dashboard",
        bgcolor="#FFF3D2",
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    global_header(page),
                    ft.Text("Keine Berechtigung", color="black"),
                ],
            )
        ],
    )
