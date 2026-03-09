import flet as ft

from snackhub2.pages.dashboard_router import student_top_bar
from snackhub2.services.db import get_conn


def _format_price(price_value) -> str:
    if price_value is None:
        return "Preis offen"
    return f"{float(price_value):0.2f} EUR".replace(".", ",")


def shop_page(page: ft.Page):
    menu_sections = ft.Column(spacing=20)
    status_text = ft.Text("Lade Speisekarte...", color="gray")

    def load_menu():
        menu_sections.controls.clear()

        conn = None
        cur = None
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)

            cur.execute("SHOW COLUMNS FROM meals LIKE 'category'")
            has_category = cur.fetchone() is not None

            if has_category:
                cur.execute(
                    """
                    SELECT id, name, price,
                           COALESCE(NULLIF(TRIM(category), ''), 'Allgemein') AS category
                    FROM meals
                    WHERE available = 1
                    ORDER BY category ASC, name ASC
                    """
                )
                rows = cur.fetchall()
            else:
                cur.execute(
                    """
                    SELECT id, name, price
                    FROM meals
                    WHERE available = 1
                    ORDER BY name ASC
                    """
                )
                rows = cur.fetchall()
                for row in rows:
                    row["category"] = "Allgemein"

            if not rows:
                status_text.value = "Noch keine Speisekarte verfuegbar."
                status_text.color = "orange"
                menu_sections.controls.append(
                    ft.Container(
                        bgcolor="#FFE8B5",
                        border_radius=20,
                        padding=24,
                        content=ft.Text(
                            "Die Kantine hat noch keine Artikel freigegeben.",
                            color="black",
                            size=16,
                        ),
                    )
                )
                page.update()
                return

            grouped: dict[str, list[dict]] = {}
            for row in rows:
                grouped.setdefault(row["category"], []).append(row)

            status_text.value = "Aktuelle Speisekarte"
            status_text.color = "#2E7D32"

            for category, items in grouped.items():
                cards = []
                for item in items:
                    cards.append(
                        ft.Container(
                            width=260,
                            bgcolor="#FFE8B5",
                            border_radius=20,
                            padding=20,
                            content=ft.Column(
                                [
                                    ft.Text(
                                        item["name"],
                                        size=20,
                                        weight="bold",
                                        color="black",
                                    ),
                                    ft.Text(
                                        "Preis: " + _format_price(item["price"]),
                                        color="black",
                                    ),
                                ],
                                horizontal_alignment="center",
                                spacing=10,
                            ),
                        )
                    )

                menu_sections.controls.append(
                    ft.Container(
                        width=1100,
                        bgcolor="white",
                        border_radius=24,
                        padding=20,
                        border=ft.border.all(1, "#E8D5AC"),
                        content=ft.Column(
                            [
                                ft.Text(
                                    category,
                                    size=24,
                                    weight="bold",
                                    color="black",
                                ),
                                ft.Row(
                                    cards,
                                    alignment=ft.MainAxisAlignment.START,
                                    spacing=18,
                                    wrap=True,
                                ),
                            ],
                            spacing=16,
                        ),
                    )
                )

        except Exception as ex:
            status_text.value = f"Speisekarte konnte nicht geladen werden: {ex}"
            status_text.color = "red"
            menu_sections.controls.append(
                ft.Text(
                    "Bitte spaeter erneut versuchen oder die Kantine informieren.",
                    color="black",
                )
            )
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        page.update()

    load_menu()

    return ft.View(
        route="/shop",
        bgcolor="#FFF3D2",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    student_top_bar(page, active="shop"),
                    ft.Column(
                        expand=True,
                        horizontal_alignment="center",
                        controls=[
                            ft.Text("Speisekarte", size=32, weight="bold", color="black"),
                            ft.Text(
                                "Alles, was heute im Sortiment verfuegbar ist",
                                size=16,
                                color="gray",
                            ),
                            status_text,
                            ft.ElevatedButton(
                                "Aktualisieren",
                                on_click=lambda _: load_menu(),
                                style=ft.ButtonStyle(
                                    bgcolor="#FFA726",
                                    color="black",
                                    shape=ft.RoundedRectangleBorder(radius=20),
                                ),
                            ),
                            menu_sections,
                        ],
                        spacing=24,
                    ),
                ],
            )
        ],
    )
