import flet as ft
from snackhub2.models.meal import Meal
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
    return ft.Container(
        padding=ft.padding.only(left=16, top=10, right=16),
        content=ft.Row(
            [
                ft.Image(src="snackhub_raw.png", height=56, fit=ft.BoxFit.CONTAIN),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Row(
                        [
                            _menu_btn("Vorbestellung", lambda _: page.go("/vorbestellungen_kantine"), active == "vorbestellung"),
                            _menu_btn("Voting", lambda _: page.go("/voting_kantine"), active == "voting"),
                            _menu_btn("Speisekarte", lambda _: page.go("/menu_kantine"), active == "menu"),
                            _menu_btn("Feedback Übersicht", lambda _: page.go("/feedback_overview"), active == "feedback"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=14,
                        wrap=True,
                    ),
                ),
                _logout_btn(page),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

def feedback_overview_page(page: ft.Page):
    list_col = ft.Column(spacing=14)

    def load_feedbacks():
        list_col.controls.clear()
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT f.id, f.week_key, f.rating, f.comment, f.is_anonymous, f.is_done, u.username
                FROM weekly_feedback f
                JOIN users u ON u.id = f.user_id
                ORDER BY f.created_at DESC
            """)
            rows = cur.fetchall()

            if not rows:
                list_col.controls.append(ft.Text("Noch kein Feedback vorhanden.", color="gray"))
            for r in rows:
                shown_name = "Anonym" if r["is_anonymous"] else r["username"]
                stars = "⭐" * int(r["rating"])
                list_col.controls.append(
                    ft.Container(
                        bgcolor="#FFE8B5",
                        border_radius=20,
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Text(f"Name: {shown_name}", size=18, weight="bold", color="black"),
                                ft.Text(f"Woche: {r['week_key']}", color="black"),
                                ft.Text(stars, size=18),
                                ft.Text(r["comment"], color="black"),
                                ft.ElevatedButton(
                                    "Abhaken",
                                    disabled=bool(r["is_done"]),
                                    on_click=lambda e, fid=r["id"]: mark_done(fid),
                                    style=ft.ButtonStyle(
                                        bgcolor="#FFA726",
                                        color="black",
                                        shape=ft.RoundedRectangleBorder(radius=20),
                                    ),
                                ),
                            ],
                            spacing=8,
                        ),
                    )
                )
        except Exception as ex:
            list_col.controls.append(ft.Text(f"Fehler: {ex}", color="red"))
        finally:
            cur.close()
            conn.close()

    def mark_done(feedback_id: int):
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE weekly_feedback SET is_done=1, done_at=NOW() WHERE id=%s",
                (feedback_id,),
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()
        load_feedbacks()
        page.update()

    load_feedbacks()

    return ft.View(
        route="/feedback_overview",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    _kantine_top_bar(page, active="feedback"),
                    ft.Column(
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        horizontal_alignment="center",
                        controls=[
                            ft.Text("Feedback Übersicht", size=32, weight="bold", color="black"),
                            list_col,
                        ],
                        spacing=20,
                    ),
                ],
            )
        ],
    )
