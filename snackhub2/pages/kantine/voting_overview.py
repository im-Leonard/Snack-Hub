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
                            _menu_btn("Voting Übersicht", lambda _: page.go("/voting_overview"), active == "voting"),
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

def voting_overview_page(page: ft.Page):
    polls_container = ft.Column(spacing=20)
    ACTIVE_WHERE = "end_date IS NULL"  # statt 0000-00-00 Vergleich

    def _get_active_polls():
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT poll_id, start_date FROM polls WHERE {ACTIVE_WHERE} ORDER BY start_date DESC")
        polls = cur.fetchall()
        for p in polls:
            try:
                cur.execute(
                    "SELECT id, dish_name, votes FROM poll_dishes WHERE poll_id=%s ORDER BY votes DESC, dish_order ASC",
                    (p["poll_id"],),
                )
            except Exception:
                cur.execute(
                    "SELECT id, dish_name, votes FROM poll_dishes WHERE poll_id=%s ORDER BY votes DESC, id ASC",
                    (p["poll_id"],),
                )
            p["dishes"] = cur.fetchall()
        cur.close()
        conn.close()
        return polls

    def load_polls():
        polls_container.controls.clear()
        try:
            polls = _get_active_polls()
        except Exception as ex:
            polls_container.controls.append(ft.Text(f"Fehler beim Laden: {ex}", color="red"))
            return

        if not polls:
            polls_container.controls.append(ft.Text("Keine aktiven Abstimmungen", size=18, color="orange", weight="bold"))
            return

        for poll in polls:
            total_votes = sum(d["votes"] for d in poll["dishes"])
            leader = poll["dishes"][0]["dish_name"] if poll["dishes"] else "—"

            # Erstelle Gericht-Cards
            dishes_cards = []
            for dish in poll.get('dishes', []):
                percent = int((dish['votes'] / total_votes) * 100) if total_votes > 0 else 0
                dishes_cards.append(
                    ft.Container(
                        bgcolor="#FFE8B5",
                        border_radius=10,
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(dish['dish_name'], size=16, weight="bold", color="black", expand=True),
                                ft.Text(f"{percent}%", size=14, weight="bold", color="#FFA726")
                            ]),
                            ft.Container(
                                width=300,
                                height=20,
                                bgcolor="#F9E6C8",
                                border_radius=10,
                                content=ft.Container(
                                    width=int(300 * percent / 100) if percent > 0 else 0,
                                    height=20,
                                    bgcolor="#FFA726",
                                    border_radius=10
                                )
                            ),
                            ft.Text(f"{dish['votes']} Stimmen", size=12, color="gray")
                        ], spacing=5)
                    )
                )

            # Poll-Card
            poll_card = ft.Container(
                bgcolor="white",
                border_radius=15,
                padding=20,
                content=ft.Column([
                    ft.Text(f"Poll ID: {poll['poll_id']}", size=14, weight="bold", color="black"),
                    ft.Text(f"Gesamtstimmen: {total_votes}", size=14, color="gray"),
                    ft.Text(f"Führendes Gericht: {leader}", size=14, weight="bold", color="#2E7D32"),
                    ft.Divider(),
                    ft.Column(dishes_cards, spacing=10),
                    ft.ElevatedButton(
                        "Beenden",
                        on_click=lambda e, poll_id=poll["poll_id"]: close_poll_handler(poll_id),
                        bgcolor="#FF6B6B",
                        color="white",
                        width=300
                    )
                ], spacing=10)
            )
            polls_container.controls.append(poll_card)

    def close_poll_handler(poll_id):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE polls SET end_date = NOW() WHERE poll_id=%s", (poll_id,))
        conn.commit()
        cur.close()
        conn.close()
        load_polls()
        page.update()

    # Initiales Laden
    load_polls()

    return ft.View(
        route="/voting_overview",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    _kantine_top_bar(page, active="voting"),
                    ft.Column(
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        horizontal_alignment="center",
                        controls=[
                            ft.Text("Aktive Abstimmungen", size=32, weight="bold", color="black"),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    [polls_container],
                                    scroll=ft.ScrollMode.AUTO,
                                    spacing=10
                                )
                            ),
                            ft.ElevatedButton(
                                "Aktualisieren",
                                on_click=lambda e: (load_polls(), page.update()),
                                bgcolor="#FFA726",
                                color="white"
                            )
                        ],
                        spacing=20,
                    ),
                ],
            )
        ],
    )
