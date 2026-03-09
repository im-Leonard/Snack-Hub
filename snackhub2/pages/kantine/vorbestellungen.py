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
        if hasattr(page, "push_route"):
            page.push_route("/")
        else:
            page.go("/")
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

def vorbestellungen_kantine_page(page: ft.Page):
    search = ft.TextField(label="Benutzername suchen", width=320)
    list_col = ft.Column(spacing=12)
    feedback_text = ft.Text("", color="gray")

    def _has_paid_confirmed_at_column(conn) -> bool:
        cur = conn.cursor()
        try:
            cur.execute("SHOW COLUMNS FROM preorders LIKE 'paid_confirmed_at'")
            return cur.fetchone() is not None
        finally:
            cur.close()

    def load_orders(_=None):
        list_col.controls.clear()
        q = (search.value or "").strip()

        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT p.id, u.username, p.dish_name, p.status, p.created_at
                FROM preorders p
                JOIN users u ON u.id = p.user_id
            """
            params = []
            if q:
                sql += " WHERE u.username LIKE %s"
                params.append(f"%{q}%")
            sql += " ORDER BY p.created_at DESC"

            cur.execute(sql, tuple(params))
            rows = cur.fetchall()

            if not rows:
                list_col.controls.append(ft.Text("Keine Vorbestellungen gefunden.", color="gray"))
            for r in rows:
                list_col.controls.append(
                    ft.Container(
                        bgcolor="#FFE8B5",
                        border_radius=18,
                        padding=16,
                        content=ft.Column(
                            [
                                ft.Text(f"Benutzer: {r['username']}", weight="bold", color="black"),
                                ft.Text(f"Gericht: {r['dish_name']}", color="black"),
                                ft.Text(f"Status: {r['status']}", color="black"),
                                ft.ElevatedButton(
                                    "Bezahlung bestätigen",
                                    disabled=(r["status"] == "bezahlt"),
                                    on_click=lambda e, preorder_id=r["id"]: confirm_payment(preorder_id),
                                    style=ft.ButtonStyle(
                                        bgcolor="#FFA726",
                                        color="black",
                                        shape=ft.RoundedRectangleBorder(radius=20),
                                        padding=ft.padding.symmetric(horizontal=22, vertical=10),
                                    ),
                                ),
                            ],
                            spacing=8,
                        ),
                    )
                )
            if rows and not feedback_text.value:
                feedback_text.value = "Offene Zahlungen können hier bestätigt werden."
                feedback_text.color = "gray"
        except Exception as ex:
            feedback_text.value = f"Fehler beim Laden: {ex}"
            feedback_text.color = "red"
        finally:
            cur.close()
            conn.close()
        page.update()

    def confirm_payment(preorder_id: int):
        conn = get_conn()
        cur = conn.cursor()
        try:
            if _has_paid_confirmed_at_column(conn):
                cur.execute(
                    "UPDATE preorders SET status='bezahlt', paid_confirmed_at=NOW() WHERE id=%s",
                    (preorder_id,),
                )
            else:
                cur.execute(
                    "UPDATE preorders SET status='bezahlt' WHERE id=%s",
                    (preorder_id,),
                )

            if cur.rowcount == 0:
                feedback_text.value = "Vorbestellung nicht gefunden."
                feedback_text.color = "orange"
                return

            conn.commit()
            feedback_text.value = "Bezahlung bestätigt."
            feedback_text.color = "green"
        except Exception as ex:
            conn.rollback()
            feedback_text.value = f"Bestätigung fehlgeschlagen: {ex}"
            feedback_text.color = "red"
        finally:
            cur.close()
            conn.close()
        load_orders()

    load_orders()

    return ft.View(
        route="/vorbestellungen_kantine",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    _kantine_top_bar(page, active="vorbestellung"),
                    ft.Container(
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Text("Vorbestellungen", size=32, weight="bold", color="black"),
                                ft.Row(
                                    [
                                        search,
                                        ft.ElevatedButton(
                                            "Suchen",
                                            on_click=load_orders,
                                            style=ft.ButtonStyle(
                                                bgcolor="#FFA726",
                                                color="black",
                                                shape=ft.RoundedRectangleBorder(radius=20),
                                            ),
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                feedback_text,
                                list_col,
                            ],
                            spacing=16,
                        ),
                    ),
                ],
            )
        ],
    )
