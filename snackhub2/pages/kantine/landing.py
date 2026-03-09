import asyncio

import flet as ft

from snackhub2.services.db import get_conn


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


def _kantine_top_bar(page: ft.Page, active: str = ""):
    active = (active or "").lower()
    menu = ft.Row(
        [
            _menu_btn(
                "Vorbestellung",
                lambda _: page.go("/vorbestellungen_kantine"),
                active == "vorbestellung",
            ),
            _menu_btn("Voting", lambda _: page.go("/voting_kantine"), active == "voting"),
            _menu_btn(
                "Speisekarte",
                lambda _: page.go("/menu_kantine"),
                active == "menu",
            ),
            _menu_btn(
                "Feedback",
                lambda _: page.go("/feedback_overview"),
                active == "feedback",
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=14,
        wrap=True,
    )
    return ft.Container(
        padding=ft.padding.only(left=16, top=10, right=16),
        content=ft.Row(
            [
                ft.Image(src="snackhub_raw.png", height=56, fit=ft.BoxFit.CONTAIN),
                ft.Container(expand=True, alignment=ft.Alignment.CENTER, content=menu),
                _logout_btn(page),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def _kantine_hero_logo(page: ft.Page):
    hero = ft.Container(
        alignment=ft.Alignment.CENTER,
        scale=ft.Scale(0.7),
        animate_scale=ft.Animation(520, ft.AnimationCurve.EASE_OUT_BACK),
        content=ft.Image(
            src="snackhub_raw.png",
            height=260,
            fit=ft.BoxFit.CONTAIN,
        ),
    )

    async def pop():
        await asyncio.sleep(0.05)
        try:
            hero.scale = ft.Scale(1.0)
            page.update()
        except Exception:
            return

    page.run_task(pop)
    return hero


def _get_dashboard_stats() -> dict:
    stats = {
        "open_preorders": 0,
        "active_menu_items": 0,
        "has_active_poll": False,
    }

    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SHOW TABLES LIKE 'preorders'")
        if cur.fetchone() is not None:
            cur.execute("SELECT COUNT(*) FROM preorders WHERE status='offen'")
            stats["open_preorders"] = int(cur.fetchone()[0])

        cur.execute("SHOW TABLES LIKE 'meals'")
        if cur.fetchone() is not None:
            cur.execute("SELECT COUNT(*) FROM meals WHERE available=1")
            stats["active_menu_items"] = int(cur.fetchone()[0])

        cur.execute("SHOW TABLES LIKE 'polls'")
        if cur.fetchone() is not None:
            cur.execute("SELECT poll_id FROM polls WHERE end_date IS NULL LIMIT 1")
            stats["has_active_poll"] = cur.fetchone() is not None
    except Exception:
        return stats
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return stats


def _dashboard_card(
    title: str,
    subtitle: str,
    on_click,
    accent: str,
):
    return ft.Container(
        bgcolor="white",
        border_radius=24,
        padding=24,
        width=330,
        height=180,
        ink=True,
        on_click=on_click,
        border=ft.border.all(1, "#E8D5AC"),
        content=ft.Column(
            [
                ft.Container(
                    width=52,
                    height=10,
                    bgcolor=accent,
                    border_radius=12,
                ),
                ft.Text(title, size=24, weight="bold", color="black"),
                ft.Text(subtitle, size=16, color="#555555"),
            ],
            spacing=14,
        ),
    )


def kantine_landing_page(page: ft.Page):
    stats = _get_dashboard_stats()

    cards = [
        _dashboard_card(
            "Vorbestellungen",
            f"{stats['open_preorders']} offene Zahlungen prüfen",
            lambda _: page.go("/vorbestellungen_kantine"),
            "#FFB74D",
        ),
        _dashboard_card(
            "Voting",
            "Aktive Abstimmung läuft"
            if stats["has_active_poll"]
            else "Neue Abstimmung starten",
            lambda _: page.go("/voting_kantine"),
            "#81C784",
        ),
        _dashboard_card(
            "Speisekarte",
            f"{stats['active_menu_items']} Artikel im Schüler-Shop sichtbar",
            lambda _: page.go("/menu_kantine"),
            "#4FC3F7",
        ),
        _dashboard_card(
            "Feedback",
            "Rückmeldungen der Schüler ansehen",
            lambda _: page.go("/feedback_overview"),
            "#EF9A9A",
        ),
    ]

    footer = ft.Container(
        bgcolor="#FFE8B5",
        padding=15,
        alignment=ft.Alignment.CENTER,
        content=ft.Text("(c) 2025 SnackHub - Schulprojekt", color="black", size=14),
    )

    return ft.View(
        route="/kantine_landing",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    _kantine_top_bar(page, active=""),
                    ft.Container(
                        padding=20,
                        content=ft.Column(
                            [
                                _kantine_hero_logo(page),
                                ft.Text(
                                    "Kantinen-Dashboard",
                                    size=32,
                                    weight="bold",
                                    color="black",
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "Verwalte Voting, Vorbestellungen und die komplette Speisekarte an einem Ort.",
                                    size=16,
                                    color="#555555",
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Row(
                                    cards,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=18,
                                    wrap=True,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=24,
                        ),
                    ),
                    footer,
                ],
            )
        ],
    )
