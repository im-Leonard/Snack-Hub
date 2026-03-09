import flet as ft
from snackhub2.services.db import get_conn
from snackhub2.pages.dashboard_router import student_top_bar

def vorbestellen_page(page: ft.Page):
    info_text = ft.Text("", color="black", size=18)
    status_text = ft.Text("", color="gray", size=14)
    winner = {"poll_id": None, "dish_name": None, "votes": 0}

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

    def load_winner():
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT poll_id FROM polls WHERE end_date IS NOT NULL ORDER BY end_date DESC LIMIT 1")
            last_poll = cur.fetchone()
            if not last_poll:
                info_text.value = "Noch kein beendetes Voting vorhanden."
                status_text.value = ""
                return

            poll_id = last_poll["poll_id"]
            try:
                cur.execute(
                    "SELECT dish_name, votes FROM poll_dishes WHERE poll_id=%s ORDER BY votes DESC, dish_order ASC, id ASC LIMIT 1",
                    (poll_id,),
                )
            except Exception:
                cur.execute(
                    "SELECT dish_name, votes FROM poll_dishes WHERE poll_id=%s ORDER BY votes DESC, id ASC LIMIT 1",
                    (poll_id,),
                )
            row = cur.fetchone()
            if not row:
                info_text.value = "Kein Gewinnergericht gefunden."
                status_text.value = ""
                return

            winner["poll_id"] = poll_id
            winner["dish_name"] = row["dish_name"]
            winner["votes"] = row["votes"]
            info_text.value = f'Jetzt "{row["dish_name"]}" vorbestellen'
            status_text.value = f"Gewinner mit {row['votes']} Stimmen."
        except Exception as ex:
            info_text.value = f"Fehler: {ex}"
            status_text.value = ""
        finally:
            cur.close()
            conn.close()

    def do_preorder(_):
        uid = _get_user_id()
        if not uid:
            status_text.value = "Bitte erneut einloggen."
            status_text.color = "red"
            page.update()
            return
        if not winner["poll_id"] or not winner["dish_name"]:
            status_text.value = "Kein Gewinnergericht vorhanden."
            status_text.color = "orange"
            page.update()
            return

        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id FROM preorders WHERE poll_id=%s AND user_id=%s",
                (winner["poll_id"], uid),
            )
            if cur.fetchone():
                status_text.value = "Du hast bereits vorbestellt."
                status_text.color = "orange"
                page.update()
                return

            cur.execute(
                "INSERT INTO preorders (poll_id, user_id, dish_name, status) VALUES (%s, %s, %s, 'offen')",
                (winner["poll_id"], uid, winner["dish_name"]),
            )
            conn.commit()
            status_text.value = "✅ Vorbestellung gespeichert. Bitte in der Kantine bezahlen."
            status_text.color = "green"
        except Exception as ex:
            status_text.value = f"❌ Fehler: {ex}"
            status_text.color = "red"
        finally:
            cur.close()
            conn.close()
            page.update()

    load_winner()

    return ft.View(
        route="/vorbestellen",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    student_top_bar(page, active="vorbestellen"),
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Text("Vorbestellung", size=32, weight="bold", color="black"),
                                ft.Container(
                                    bgcolor="#FFE8B5",
                                    border_radius=20,
                                    padding=24,
                                    width=620,
                                    content=ft.Column(
                                        [
                                            info_text,
                                            status_text,
                                            ft.ElevatedButton(
                                                "Jetzt vorbestellen",
                                                on_click=do_preorder,
                                                style=ft.ButtonStyle(
                                                    bgcolor="#FFA726",
                                                    color="black",
                                                    shape=ft.RoundedRectangleBorder(radius=20),
                                                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                                ),
                                            ),
                                        ],
                                        spacing=14,
                                    ),
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                        ),
                    ),
                ],
            )
        ],
    )
