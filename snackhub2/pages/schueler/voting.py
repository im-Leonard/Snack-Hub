import flet as ft
from snackhub2.components.header import global_header
from snackhub2.services.db import get_conn
from snackhub2.pages.dashboard_router import student_top_bar

def voting_page(page: ft.Page):
    user_vote_dish_id = None
    active_poll_id = None
    options = []
    poll_votes_available = True
    bars_container = ft.Column(spacing=15)
    status_text = ft.Text("Lade Abstimmung...", size=16, color="gray")
    vote_feedback = ft.Text("", size=14, color="#2E7D32")

    def _get_user_id():
        # kompatibel zu deinem page.data Aufbau
        if isinstance(page.data, dict):
            if page.data.get("user_id"):
                return page.data["user_id"]
            if page.data.get("id"):
                return page.data["id"]
            user_obj = page.data.get("user")
            if user_obj and hasattr(user_obj, "id"):
                return user_obj.id
        return None

    def _check_core_tables() -> tuple[bool, str]:
        conn = None
        cur = None
        try:
            conn = get_conn()
            cur = conn.cursor(buffered=True)
            cur.execute("SELECT 1 FROM polls LIMIT 1")
            cur.fetchone()  # wichtig: Result konsumieren
            cur.execute("SELECT 1 FROM poll_dishes LIMIT 1")
            cur.fetchone()  # wichtig: Result konsumieren
            return True, ""
        except Exception as ex:
            return False, str(ex)
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def _check_poll_votes_table() -> bool:
        conn = None
        cur = None
        try:
            conn = get_conn()
            cur = conn.cursor(buffered=True)
            cur.execute("SELECT 1 FROM poll_votes LIMIT 1")
            cur.fetchone()  # wichtig: Result konsumieren
            return True
        except Exception:
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def load_active_poll():
        nonlocal active_poll_id, options, user_vote_dish_id, poll_votes_available
        conn = None
        cur = None
        try:
            core_ok, err = _check_core_tables()
            if not core_ok:
                status_text.value = f"❌ Voting nicht verfügbar (DB): {err}"
                status_text.color = "red"
                return

            poll_votes_available = _check_poll_votes_table()

            conn = get_conn()
            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT poll_id FROM polls WHERE end_date IS NULL ORDER BY start_date DESC LIMIT 1")
            poll = cur.fetchone()

            if not poll:
                active_poll_id = None
                options = []
                user_vote_dish_id = None
                status_text.value = "⚠️ Keine aktive Abstimmung"
                status_text.color = "orange"
                return

            active_poll_id = poll["poll_id"]

            try:
                cur.execute(
                    "SELECT id, dish_name, votes FROM poll_dishes WHERE poll_id=%s ORDER BY dish_order ASC, id ASC",
                    (active_poll_id,),
                )
            except Exception:
                cur.execute(
                    "SELECT id, dish_name, votes FROM poll_dishes WHERE poll_id=%s ORDER BY id ASC",
                    (active_poll_id,),
                )

            options = cur.fetchall()

            uid = _get_user_id()
            user_vote_dish_id = None
            if uid and poll_votes_available:
                try:
                    cur.execute("SELECT dish_id FROM poll_votes WHERE poll_id=%s AND user_id=%s", (active_poll_id, uid))
                    row = cur.fetchone()
                    if row:
                        user_vote_dish_id = row["dish_id"]
                except Exception:
                    poll_votes_available = False

            status_text.value = f"✅ Abstimmung aktiv (ID: {active_poll_id})"
            status_text.color = "green"

            if not poll_votes_available:
                vote_feedback.value = "⚠️ Abstimmen aktuell nicht möglich (poll_votes fehlt)."
                vote_feedback.color = "orange"
            else:
                vote_feedback.value = ""

        except Exception as ex:
            status_text.value = f"❌ Voting konnte nicht geladen werden: {ex}"
            status_text.color = "red"
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def cast_vote(dish_id: int) -> tuple[bool, str]:
        uid = _get_user_id()
        if not uid or not active_poll_id:
            return False, "Bitte erneut einloggen."
        if not poll_votes_available:
            return False, "Abstimmen aktuell nicht möglich."

        conn = None
        cur = None
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT dish_id FROM poll_votes WHERE poll_id=%s AND user_id=%s", (active_poll_id, uid))
            existing = cur.fetchone()

            if existing is None:
                cur.execute(
                    "INSERT INTO poll_votes (poll_id, dish_id, user_id) VALUES (%s, %s, %s)",
                    (active_poll_id, dish_id, uid),
                )
                cur.execute("UPDATE poll_dishes SET votes = votes + 1 WHERE id=%s AND poll_id=%s", (dish_id, active_poll_id))
                conn.commit()
                return True, "✅ Stimme erfolgreich abgegeben."

            if existing["dish_id"] != dish_id:
                old_id = existing["dish_id"]
                cur.execute("UPDATE poll_votes SET dish_id=%s WHERE poll_id=%s AND user_id=%s", (dish_id, active_poll_id, uid))
                cur.execute("UPDATE poll_dishes SET votes = GREATEST(votes - 1, 0) WHERE id=%s AND poll_id=%s", (old_id, active_poll_id))
                cur.execute("UPDATE poll_dishes SET votes = votes + 1 WHERE id=%s AND poll_id=%s", (dish_id, active_poll_id))
                conn.commit()
                return True, "✅ Stimme erfolgreich geändert."

            return True, "ℹ️ Du hast dieses Gericht bereits gewählt."

        except Exception as ex:
            return False, f"❌ Stimme konnte nicht gespeichert werden: {ex}"
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def on_vote_click(dish_id: int):
        nonlocal user_vote_dish_id
        ok, msg = cast_vote(dish_id)
        vote_feedback.value = msg
        vote_feedback.color = "#2E7D32" if ok else "red"

        if ok:
            user_vote_dish_id = dish_id  # sofortiges visuelles Feedback
            load_active_poll()

        update_display()

    def update_display():
        bars_container.controls.clear()
        total_votes = sum(int(o["votes"]) for o in options) if options else 0
        max_width = 350

        try:
            if not options:
                bars_container.controls.append(
                    ft.Container(
                        bgcolor="#FFE8B5",
                        border_radius=15,
                        padding=20,
                        content=ft.Text("Aktuell sind keine Gerichte zur Abstimmung verfügbar.", color="black")
                    )
                )
                page.update()
                return

            for o in options:
                percent = int((o["votes"] / total_votes) * 100) if total_votes > 0 else 0
                bar_width = int(max_width * percent / 100)
                is_selected = o["id"] == user_vote_dish_id

                bars_container.controls.append(
                    ft.Container(
                        bgcolor="#FFE8B5",
                        border_radius=15,
                        padding=15,
                        border=ft.border.all(2, "#4CAF50") if is_selected else ft.border.all(1, "#E0CFA0"),
                        content=ft.Column([
                            ft.Row([
                                ft.Text(o["dish_name"], size=18, weight="bold", color="black", expand=True),
                                ft.Text("✅ gewählt" if is_selected else f"{percent}%", size=16, weight="bold", color="#FFA726")
                            ]),
                            ft.Container(
                                width=max_width,
                                height=25,
                                bgcolor="#F9E6C8",
                                border_radius=10,
                                content=ft.Container(
                                    width=bar_width,
                                    height=25,
                                    bgcolor="#FFA726",
                                    border_radius=10
                                )
                            ),
                            ft.Text(f"{o['votes']} Stimmen", size=12, color="gray"),
                            ft.ElevatedButton(
                                "✓ Abgestimmt" if is_selected else "Abstimmen",
                                on_click=lambda e, dish_id=o["id"]: on_vote_click(dish_id),
                                bgcolor="#4CAF50" if is_selected else "#FF6B6B",
                                color="white",
                                width=max_width,
                                disabled=False  # wichtig: kein Ausgrauen mehr
                            )
                        ], spacing=8)
                    )
                )
            page.update()
        except Exception as ex:
            status_text.value = f"❌ Darstellungsfehler: {ex}"
            status_text.color = "red"
            page.update()

    load_active_poll()
    update_display()

    return ft.View(
        route="/voting",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    student_top_bar(page, active="voting"),
                    ft.Column(
                        expand=True,
                        horizontal_alignment="center",
                        controls=[
                            ft.Text("Wähle dein Lieblingsessen", size=32, weight="bold", color="black"),
                            ft.Text("für nächste Woche", size=16, color="gray"),
                            status_text,
                            vote_feedback,  # NEU
                            ft.ElevatedButton(
                                "Aktualisieren",
                                on_click=lambda _: (load_active_poll(), update_display()),
                                bgcolor="#FFA726",
                                color="white"
                            ),
                            bars_container,
                            ft.Container(height=20),
                        ],
                    ),
                ],
            )
        ],
    )
