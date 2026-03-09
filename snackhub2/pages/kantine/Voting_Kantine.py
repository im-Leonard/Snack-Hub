import flet as ft
from datetime import datetime
from snackhub2.components.header import global_header
from snackhub2.services.db import get_conn
import traceback

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

def voting_kantine_page(page: ft.Page):
    voting_active = False
    current_voting = None
    
    title_input = ft.TextField(
        label="Abstimmungs-Titel",
        hint_text="z.B. 'Nächste Woche Montag'",
        width=400
    )
    
    dish1_input = ft.TextField(
        label="Gericht 1 (erforderlich)",
        hint_text="z.B. 'Schnitzel mit Pommes'",
        width=400
    )
    
    dish2_input = ft.TextField(
        label="Gericht 2 (optional)",
        hint_text="z.B. 'Gemüsepfanne'",
        width=400
    )
    
    dish3_input = ft.TextField(
        label="Gericht 3 (optional)",
        hint_text="z.B. 'Pizza Margherita'",
        width=400
    )
    
    dish4_input = ft.TextField(
        label="Gericht 4 (optional)",
        hint_text="z.B. 'Burger'",
        width=400
    )
    
    dish5_input = ft.TextField(
        label="Gericht 5 (optional)",
        hint_text="z.B. 'Salat'",
        width=400
    )
    
    status_text = ft.Text("Keine aktive Abstimmung", size=16, color="gray")
    voting_display = ft.Column(visible=False)
    
    def _check_poll_schema(conn) -> tuple[bool, str]:
        cur = conn.cursor(buffered=True)
        try:
            cur.execute("SELECT 1 FROM polls LIMIT 1")
            cur.fetchone()  # wichtig: Result konsumieren
            cur.execute("SELECT 1 FROM poll_dishes LIMIT 1")
            cur.fetchone()  # wichtig: Result konsumieren
            return True, ""
        except Exception as ex:
            return False, str(ex)
        finally:
            cur.close()

    def _create_poll_in_db(dishes: list[str]) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_conn()

            ok, err = _check_poll_schema(conn)
            if not ok:
                return {"success": False, "error": f"Tabellen fehlen/keine Rechte: {err}"}

            cursor = conn.cursor()

            cursor.execute("UPDATE polls SET end_date = NOW() WHERE end_date IS NULL")
            cursor.execute(
                "INSERT INTO polls (meal_id, start_date, end_date) VALUES (%s, NOW(), NULL)",
                (0,),
            )
            poll_id = cursor.lastrowid

            for i, dish in enumerate(dishes, start=1):
                cursor.execute(
                    "INSERT INTO poll_dishes (poll_id, dish_name, dish_order, votes) VALUES (%s, %s, %s, 0)",
                    (poll_id, dish, i),
                )

            conn.commit()
            return {"success": True, "poll_id": poll_id}
        except Exception as ex:
            if conn:
                conn.rollback()
            traceback.print_exc()
            return {"success": False, "error": str(ex)}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _get_active_poll():
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT poll_id, start_date FROM polls WHERE end_date IS NULL ORDER BY start_date DESC LIMIT 1")
        poll = cur.fetchone()
        cur.close()
        conn.close()
        return poll

    def _get_results(poll_id: int):
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT id, dish_name, votes FROM poll_dishes WHERE poll_id=%s ORDER BY dish_order ASC, id ASC",
                (poll_id,),
            )
        except Exception:
            cur.execute(
                "SELECT id, dish_name, votes FROM poll_dishes WHERE poll_id=%s ORDER BY id ASC",
                (poll_id,),
            )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def create_voting(e):
        title = (title_input.value or "").strip()
        dish1 = (dish1_input.value or "").strip()
        dish2 = (dish2_input.value or "").strip()
        dish3 = (dish3_input.value or "").strip()
        dish4 = (dish4_input.value or "").strip()
        dish5 = (dish5_input.value or "").strip()
        
        if not title or not dish1:
            status_text.value = "❌ Titel und mindestens ein Gericht erforderlich!"
            status_text.color = "red"
            page.update()
            return
        
        dishes = [d for d in [dish1, dish2, dish3, dish4, dish5] if d]

        if len(dishes) < 3:
            status_text.value = "❌ Bitte mindestens 3 Gerichte angeben."
            status_text.color = "red"
            page.update()
            return
        if len(dishes) > 5:
            status_text.value = "❌ Maximal 5 Gerichte erlaubt."
            status_text.color = "red"
            page.update()
            return
        if len({d.lower() for d in dishes}) != len(dishes):
            status_text.value = "❌ Gerichte dürfen nicht doppelt sein."
            status_text.color = "red"
            page.update()
            return

        result = _create_poll_in_db(dishes)
        if not result.get("success"):
            status_text.value = f"❌ Fehler beim Speichern: {result.get('error', 'Unbekannter Fehler')}"
            status_text.color = "red"
            page.update()
            return
        
        nonlocal voting_active, current_voting
        voting_active = True
        poll_id = result["poll_id"]
        current_voting = {
            "poll_id": poll_id,
            "title": title,
            "dishes": dishes,
            "votes": {d: 0 for d in dishes},
            "created_at": datetime.now()
        }
        
        print(f"DEBUG: Poll erstellt mit ID={poll_id}")
        
        # Eingabefelder leeren und deaktivieren
        title_input.value = ""
        dish1_input.value = ""
        dish2_input.value = ""
        dish3_input.value = ""
        dish4_input.value = ""
        dish5_input.value = ""
        title_input.disabled = True
        dish1_input.disabled = True
        dish2_input.disabled = True
        dish3_input.disabled = True
        dish4_input.disabled = True
        dish5_input.disabled = True
        
        status_text.value = f"✅ Abstimmung '{title}' gestartet! (ID: {poll_id})"
        status_text.color = "green"
        
        update_voting_display()
        page.update()
    
    def close_voting(e):
        nonlocal voting_active, current_voting
        
        if current_voting and current_voting.get("poll_id"):
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE polls SET end_date = NOW() WHERE poll_id=%s", (current_voting["poll_id"],))
            conn.commit()
            cur.close()
            conn.close()
        
        voting_active = False
        
        # Eingabefelder wieder aktivieren
        title_input.disabled = False
        dish1_input.disabled = False
        dish2_input.disabled = False
        dish3_input.disabled = False
        dish4_input.disabled = False
        dish5_input.disabled = False
        
        status_text.value = "✅ Abstimmung beendet und in DB gespeichert"
        status_text.color = "orange"
        voting_display.visible = False
        current_voting = None
        page.update()
    
    def delete_voting(e):
        nonlocal voting_active, current_voting
        if not current_voting or not current_voting.get("poll_id"):
            return

        poll_id = current_voting["poll_id"]
        conn = None
        cur = None
        try:
            conn = get_conn()
            cur = conn.cursor()

            # robust, auch wenn einzelne Tabellen in älteren DB-Ständen fehlen
            if _table_exists(conn, "poll_votes"):
                cur.execute("DELETE FROM poll_votes WHERE poll_id=%s", (poll_id,))
            if _table_exists(conn, "poll_dishes"):
                cur.execute("DELETE FROM poll_dishes WHERE poll_id=%s", (poll_id,))
            cur.execute("DELETE FROM polls WHERE poll_id=%s", (poll_id,))
            conn.commit()

            voting_active = False
            current_voting = None
            voting_display.visible = False

            # Eingabefelder wieder aktivieren
            title_input.disabled = False
            dish1_input.disabled = False
            dish2_input.disabled = False
            dish3_input.disabled = False
            dish4_input.disabled = False
            dish5_input.disabled = False

            status_text.value = "🗑️ Abstimmung vollständig gelöscht."
            status_text.color = "red"

        except Exception as ex:
            if conn:
                conn.rollback()
            status_text.value = f"❌ Löschen fehlgeschlagen: {ex}"
            status_text.color = "red"
            traceback.print_exc()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
            page.update()

    def _table_exists(conn, table_name: str) -> bool:
        cur = conn.cursor()
        try:
            cur.execute("SHOW TABLES LIKE %s", (table_name,))
            return cur.fetchone() is not None
        finally:
            cur.close()

    def update_voting_display():
        if not voting_active or not current_voting:
            return

        rows = _get_results(current_voting["poll_id"])
        leader = max(rows, key=lambda x: x["votes"])["dish_name"] if rows else "—"

        dishes_info = []
        for row in rows:
            dishes_info.append(
                ft.Container(
                    bgcolor="#FFE8B5",
                    border_radius=10,
                    padding=15,
                    content=ft.Column([
                        ft.Text(row["dish_name"], size=18, weight="bold", color="black"),
                        ft.Text(f"Stimmen: {row['votes']}", size=14, color="gray")
                    ], spacing=5)
                )
            )

        voting_display.controls = [
            ft.Text(f"Aktuelle Abstimmung (ID: {current_voting['poll_id']})", size=20, weight="bold"),
            ft.Text(f"Führendes Gericht: {leader}", size=16, weight="bold", color="#2E7D32"),
            ft.Column(dishes_info, spacing=10),
            ft.Row([
                ft.ElevatedButton("Ergebnisse aktualisieren", on_click=lambda _: (update_voting_display(), page.update())),
                ft.ElevatedButton("Abstimmung beenden", on_click=close_voting, bgcolor="#FF6B6B", color="white"),
                ft.ElevatedButton("Abstimmung löschen", on_click=delete_voting, bgcolor="#C62828", color="white"),
            ])
        ]
        voting_display.visible = True

    # NEU: beim Öffnen aktive Poll aus DB übernehmen
    active = _get_active_poll()
    if active:
        voting_active = True
        current_voting = {
            "poll_id": active["poll_id"],
            "title": f"Aktive Abstimmung #{active['poll_id']}",
            "dishes": [],
            "votes": {},
            "created_at": active["start_date"],
        }
        title_input.disabled = True
        dish1_input.disabled = True
        dish2_input.disabled = True
        dish3_input.disabled = True
        dish4_input.disabled = True
        dish5_input.disabled = True
        status_text.value = f"✅ Aktive Abstimmung gefunden (ID: {active['poll_id']})"
        status_text.color = "green"
        update_voting_display()

    return ft.View(
        route="/voting_kantine",
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
                        spacing=20,
                        controls=[
                            ft.Text("Abstimmung erstellen", size=28, weight="bold", color="black"),
                            
                            ft.Container(
                                bgcolor="white",
                                border_radius=15,
                                padding=20,
                                content=ft.Column([
                                    ft.Text("Neue Abstimmung", size=18, weight="bold"),
                                    title_input,
                                    ft.Text("Gerichte (max. 5):", size=14, weight="bold"),
                                    dish1_input,
                                    dish2_input,
                                    dish3_input,
                                    dish4_input,
                                    dish5_input,
                                    ft.ElevatedButton(
                                        "Abstimmung starten",
                                        on_click=create_voting,
                                        bgcolor="#FFA726",
                                        color="white",
                                        width=400
                                    )
                                ], spacing=10)
                            ),
                            
                            status_text,
                            
                            ft.Container(
                                bgcolor="#E8F5E9",
                                border_radius=15,
                                padding=20,
                                content=voting_display
                            )
                        ]
                    )
                ]
            )
        ]
    )
