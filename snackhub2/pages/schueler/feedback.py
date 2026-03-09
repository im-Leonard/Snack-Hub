import flet as ft
from datetime import datetime
from snackhub2.services.db import get_conn
from snackhub2.pages.dashboard_router import student_top_bar

def feedback_page(page: ft.Page):
    status_text = ft.Text("", color="gray")
    rating = ft.Dropdown(
        label="Sterne (1-5)",
        width=220,
        options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
        value="5",
    )
    anonymous = ft.Checkbox(label="Anonym senden", value=False)
    comment = ft.TextField(
        label="Dein Feedback",
        multiline=True,
        min_lines=4,
        max_lines=8,
        width=620,
    )

    def _get_user_id():
        if isinstance(page.data, dict):
            if page.data.get("user_id"):
                return page.data["user_id"]
            if page.data.get("id"):
                return page.data["id"]
            user_obj = page.data.get("user")
            if user_obj and hasattr(user_obj, "id"):
                return user_obj.id
        return None

    def _week_key():
        d = datetime.now().isocalendar()
        return f"{d.year}-W{d.week:02d}"

    def submit_feedback(_):
        uid = _get_user_id()
        if not uid:
            status_text.value = "❌ Bitte erneut einloggen."
            status_text.color = "red"
            page.update()
            return
        if not (comment.value or "").strip():
            status_text.value = "❌ Bitte ein Feedback eingeben."
            status_text.color = "red"
            page.update()
            return

        wk = _week_key()
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id FROM weekly_feedback WHERE user_id=%s AND week_key=%s",
                (uid, wk),
            )
            if cur.fetchone():
                status_text.value = "⚠️ Du hast diese Woche bereits Feedback eingereicht."
                status_text.color = "orange"
                page.update()
                return

            cur.execute(
                """
                INSERT INTO weekly_feedback (user_id, week_key, rating, comment, is_anonymous)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (uid, wk, int(rating.value or "5"), (comment.value or "").strip(), bool(anonymous.value)),
            )
            conn.commit()
            comment.value = ""
            anonymous.value = False
            rating.value = "5"
            status_text.value = "✅ Feedback eingereicht. Danke!"
            status_text.color = "green"
        except Exception as ex:
            status_text.value = f"❌ Fehler: {ex}"
            status_text.color = "red"
        finally:
            cur.close()
            conn.close()
            page.update()

    return ft.View(
        route="/feedback",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    student_top_bar(page, active="feedback"),
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Text("Feedback", size=32, weight="bold", color="black"),
                                ft.Container(
                                    bgcolor="#FFE8B5",
                                    border_radius=20,
                                    padding=24,
                                    width=680,
                                    content=ft.Column(
                                        [
                                            rating,
                                            anonymous,
                                            comment,
                                            ft.ElevatedButton(
                                                "Feedback senden",
                                                on_click=submit_feedback,
                                                style=ft.ButtonStyle(
                                                    bgcolor="#FFA726",
                                                    color="black",
                                                    shape=ft.RoundedRectangleBorder(radius=20),
                                                ),
                                            ),
                                            status_text,
                                        ],
                                        spacing=12,
                                    ),
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=18,
                        ),
                    ),
                ],
            )
        ],
    )
