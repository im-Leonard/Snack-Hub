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
                            _menu_btn(
                                "Vorbestellung",
                                lambda _: page.go("/vorbestellungen_kantine"),
                                active == "vorbestellung",
                            ),
                            _menu_btn(
                                "Voting",
                                lambda _: page.go("/voting_kantine"),
                                active == "voting",
                            ),
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
                    ),
                ),
                _logout_btn(page),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def _format_price(price_value) -> str:
    if price_value is None:
        return "Preis offen"
    return f"{float(price_value):0.2f} EUR".replace(".", ",")


def menu_management_page(page: ft.Page):
    name_input = ft.TextField(
        label="Artikelname",
        hint_text="z.B. Brezel oder Kaesesemmel",
        width=320,
    )
    category_input = ft.TextField(
        label="Kategorie",
        hint_text="z.B. Gebaeck, Snacks, Getraenke",
        value="Allgemein",
        width=260,
    )
    price_input = ft.TextField(
        label="Preis in Euro",
        hint_text="z.B. 2,50",
        width=180,
    )
    status_text = ft.Text("", color="gray")
    menu_list = ft.Column(spacing=16)

    def _ensure_meals_category_column(conn) -> None:
        cur = conn.cursor()
        try:
            cur.execute("SHOW COLUMNS FROM meals LIKE 'category'")
            if cur.fetchone() is None:
                cur.execute(
                    "ALTER TABLE meals ADD COLUMN category VARCHAR(50) NOT NULL DEFAULT 'Allgemein'"
                )
                conn.commit()
        finally:
            cur.close()

    def _parse_price(raw_value: str) -> float:
        normalized = (raw_value or "").strip().replace(",", ".")
        if not normalized:
            raise ValueError("Bitte einen Preis eingeben.")

        price = float(normalized)
        if price <= 0:
            raise ValueError("Der Preis muss groesser als 0 sein.")
        return round(price, 2)

    def load_meals():
        menu_list.controls.clear()

        conn = None
        cur = None
        try:
            conn = get_conn()
            _ensure_meals_category_column(conn)
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, name, price, category, available
                FROM meals
                ORDER BY category ASC, name ASC
                """
            )
            rows = cur.fetchall()

            if not rows:
                menu_list.controls.append(
                    ft.Container(
                        bgcolor="#FFE8B5",
                        border_radius=18,
                        padding=18,
                        content=ft.Text(
                            "Noch keine Artikel in der Speisekarte. Lege oben den ersten Eintrag an.",
                            color="black",
                        ),
                    )
                )
                page.update()
                return

            grouped: dict[str, list[dict]] = {}
            for row in rows:
                category = (row.get("category") or "Allgemein").strip() or "Allgemein"
                grouped.setdefault(category, []).append(row)

            for category, items in grouped.items():
                item_cards = []
                for item in items:
                    is_available = bool(item["available"])
                    item_cards.append(
                        ft.Container(
                            bgcolor="white",
                            border_radius=16,
                            padding=16,
                            border=ft.border.all(1, "#E6D2A7"),
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                item["name"],
                                                size=18,
                                                weight="bold",
                                                color="black",
                                                expand=True,
                                            ),
                                            ft.Text(
                                                _format_price(item["price"]),
                                                size=16,
                                                weight="bold",
                                                color="#A65D00",
                                            ),
                                        ]
                                    ),
                                    ft.Text(
                                        "Aktiv sichtbar"
                                        if is_available
                                        else "Derzeit ausgeblendet",
                                        color="#2E7D32" if is_available else "#C62828",
                                    ),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                "Ausblenden"
                                                if is_available
                                                else "Einblenden",
                                                on_click=lambda e, meal_id=item["id"], new_state=not is_available: toggle_meal(
                                                    meal_id,
                                                    new_state,
                                                ),
                                                style=ft.ButtonStyle(
                                                    bgcolor="#FFA726",
                                                    color="black",
                                                    shape=ft.RoundedRectangleBorder(radius=18),
                                                ),
                                            ),
                                            ft.TextButton(
                                                "Loeschen",
                                                on_click=lambda e, meal_id=item["id"]: delete_meal(meal_id),
                                                style=ft.ButtonStyle(color="#B71C1C"),
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                ],
                                spacing=10,
                            ),
                        )
                    )

                menu_list.controls.append(
                    ft.Container(
                        bgcolor="#FFE8B5",
                        border_radius=20,
                        padding=18,
                        content=ft.Column(
                            [
                                ft.Text(
                                    category,
                                    size=22,
                                    weight="bold",
                                    color="black",
                                ),
                                ft.Column(item_cards, spacing=12),
                            ],
                            spacing=14,
                        ),
                    )
                )

        except Exception as ex:
            menu_list.controls.append(
                ft.Text(f"Fehler beim Laden der Speisekarte: {ex}", color="red")
            )
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        page.update()

    def add_meal(_):
        name = (name_input.value or "").strip()
        category = (category_input.value or "").strip() or "Allgemein"

        if not name:
            status_text.value = "Bitte zuerst einen Artikelnamen eingeben."
            status_text.color = "red"
            page.update()
            return

        try:
            price = _parse_price(price_input.value or "")
        except ValueError as ex:
            status_text.value = str(ex)
            status_text.color = "red"
            page.update()
            return

        conn = None
        cur = None
        try:
            conn = get_conn()
            _ensure_meals_category_column(conn)
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO meals (name, price, category, available)
                VALUES (%s, %s, %s, %s)
                """,
                (name, price, category, True),
            )
            conn.commit()

            name_input.value = ""
            price_input.value = ""
            status_text.value = "Artikel wurde in die Speisekarte aufgenommen."
            status_text.color = "green"
        except Exception as ex:
            if conn:
                conn.rollback()
            status_text.value = f"Speichern fehlgeschlagen: {ex}"
            status_text.color = "red"
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

        load_meals()

    def toggle_meal(meal_id: int, new_state: bool):
        conn = None
        cur = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "UPDATE meals SET available=%s WHERE id=%s",
                (1 if new_state else 0, meal_id),
            )
            conn.commit()
            status_text.value = (
                "Artikel ist jetzt fuer Schueler sichtbar."
                if new_state
                else "Artikel wurde aus der Schueler-Speisekarte ausgeblendet."
            )
            status_text.color = "green" if new_state else "orange"
        except Exception as ex:
            if conn:
                conn.rollback()
            status_text.value = f"Aktualisieren fehlgeschlagen: {ex}"
            status_text.color = "red"
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

        load_meals()

    def delete_meal(meal_id: int):
        conn = None
        cur = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM meals WHERE id=%s", (meal_id,))
            conn.commit()
            status_text.value = "Artikel wurde entfernt."
            status_text.color = "orange"
        except Exception as ex:
            if conn:
                conn.rollback()
            status_text.value = f"Loeschen fehlgeschlagen: {ex}"
            status_text.color = "red"
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

        load_meals()

    load_meals()

    return ft.View(
        route="/menu_kantine",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    _kantine_top_bar(page, active="menu"),
                    ft.Container(
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Speisekarte verwalten",
                                    size=30,
                                    weight="bold",
                                    color="black",
                                ),
                                ft.Text(
                                    "Hier pflegst du alle Artikel, die im Schüler-Shop sichtbar sein sollen.",
                                    color="black",
                                ),
                                ft.Container(
                                    bgcolor="#FFE8B5",
                                    border_radius=20,
                                    padding=20,
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Neuen Artikel anlegen",
                                                size=20,
                                                weight="bold",
                                                color="black",
                                            ),
                                            ft.Row(
                                                [
                                                    name_input,
                                                    category_input,
                                                    price_input,
                                                ],
                                                wrap=True,
                                                spacing=12,
                                            ),
                                            ft.Row(
                                                [
                                                    ft.ElevatedButton(
                                                        "Artikel speichern",
                                                        on_click=add_meal,
                                                        style=ft.ButtonStyle(
                                                            bgcolor="#FFA726",
                                                            color="black",
                                                            shape=ft.RoundedRectangleBorder(
                                                                radius=20
                                                            ),
                                                            padding=ft.padding.symmetric(
                                                                horizontal=24,
                                                                vertical=12,
                                                            ),
                                                        ),
                                                    ),
                                                    ft.ElevatedButton(
                                                        "Liste aktualisieren",
                                                        on_click=lambda _: load_meals(),
                                                        style=ft.ButtonStyle(
                                                            bgcolor="white",
                                                            color="black",
                                                            shape=ft.RoundedRectangleBorder(
                                                                radius=20
                                                            ),
                                                        ),
                                                    ),
                                                ],
                                                spacing=12,
                                                wrap=True,
                                            ),
                                            status_text,
                                        ],
                                        spacing=14,
                                    ),
                                ),
                                menu_list,
                            ],
                            spacing=20,
                        ),
                    ),
                ],
            )
        ],
    )
