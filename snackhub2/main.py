import os
import traceback
from pathlib import Path

import flet as ft

from snackhub2.components.help_chat import build_help_chat
from snackhub2.pages.dashboard_router import dashboard_router
from snackhub2.pages.kantine.Voting_Kantine import voting_kantine_page
from snackhub2.pages.kantine.feedback_overview import feedback_overview_page
from snackhub2.pages.kantine.landing import kantine_landing_page
from snackhub2.pages.kantine.menu_management import menu_management_page
from snackhub2.pages.kantine.vorbestellungen import vorbestellungen_kantine_page
from snackhub2.pages.landing import landing_page
from snackhub2.pages.login import login_page
from snackhub2.pages.register import register_page
from snackhub2.pages.schueler.feedback import feedback_page
from snackhub2.pages.schueler.landing import schueler_landing_page
from snackhub2.pages.schueler.shop import shop_page
from snackhub2.pages.schueler.vorbestellen import vorbestellen_page
from snackhub2.pages.schueler.voting import voting_page
from snackhub2.services.db import get_conn
from snackhub2.services.init_service import initialize_app


def _ensure_database_initialized():
    """Check and initialize the database if needed."""
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES LIKE 'polls'")
        result = cursor.fetchone()

        if result is None:
            print("Database not initialized. Starting setup...")
            from snackhub2.setup_db import setup_database
            setup_database()
        else:
            cursor.execute("SHOW TABLES LIKE 'preorders'")
            if cursor.fetchone() is None:
                print("Table 'preorders' missing. Creating automatically...")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS preorders (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        poll_id INT NOT NULL,
                        user_id INT NOT NULL,
                        dish_name VARCHAR(100) NOT NULL,
                        status ENUM('offen', 'bezahlt') NOT NULL DEFAULT 'offen',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        paid_confirmed_at TIMESTAMP NULL,
                        UNIQUE KEY uq_preorder_user_poll (poll_id, user_id),
                        FOREIGN KEY (poll_id) REFERENCES polls(poll_id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                    """
                )
                conn.commit()
                print("Table 'preorders' created")

            cursor.execute("SHOW TABLES LIKE 'weekly_feedback'")
            if cursor.fetchone() is None:
                print("Table 'weekly_feedback' missing. Creating automatically...")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS weekly_feedback (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        week_key VARCHAR(10) NOT NULL,
                        rating TINYINT NOT NULL,
                        comment TEXT NOT NULL,
                        is_anonymous BOOLEAN NOT NULL DEFAULT FALSE,
                        is_done BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        done_at TIMESTAMP NULL,
                        UNIQUE KEY uq_weekly_user (user_id, week_key),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                    """
                )
                conn.commit()
                print("Table 'weekly_feedback' created")

        cursor.close()
        conn.close()

    except Exception as exc:
        print(f"Database check failed: {exc}")
        print("Trying to run setup...")
        try:
            from snackhub2.setup_db import setup_database
            setup_database()
        except Exception as setup_error:
            print(f"Setup failed: {setup_error}")


def _build_bg_icons(page: ft.Page):
    assets_dir = Path(__file__).resolve().parent / "assets"
    sticker_sources = [
        p.name for p in assets_dir.glob("*.png")
        if p.name.lower() != "snackhub_raw.png"
    ]
    if not sticker_sources:
        sticker_sources = ["drink.png", "food-safety.png", "hamburger.png"]

    sticker_sources.sort()

    width = int(getattr(page, "window_width", 0) or 1500)
    height = int(getattr(page, "window_height", 0) or 900)

    icon_size = 50
    margin_x = 36
    margin_y = 24
    cell_w = max(150, width // 9)
    cell_h = max(115, height // 7)
    row_count = max(6, ((height - margin_y * 2) // cell_h) + 2)
    col_count = max(9, ((width - margin_x * 2) // cell_w) + 3)

    controls: list[ft.Control] = []

    for row in range(row_count):
        row_offset = (cell_w // 2) if row % 2 else 0
        for col in range(col_count):
            index = row * col_count + col
            start_x = margin_x + (col * cell_w) - row_offset
            start_y = margin_y + (row * cell_h) + ((col % 2) * 10)

            icon = ft.Container(
                left=int(start_x),
                top=int(start_y),
                content=ft.Image(
                    src=sticker_sources[index % len(sticker_sources)],
                    width=icon_size,
                    height=icon_size,
                    fit=ft.BoxFit.CONTAIN,
                    opacity=0.12,
                ),
            )
            controls.append(icon)

    old_task = getattr(page, "_bg_anim_task", None)
    if old_task is not None:
        try:
            old_task.cancel()
        except Exception:
            pass

    page._bg_anim_task = None
    return controls


def _decorate_view_with_animated_bg(page: ft.Page, view: ft.View) -> ft.View:
    bg_controls = _build_bg_icons(page)
    help_chat = build_help_chat(page)
    foreground = ft.Container(
        expand=True,
        content=ft.Column(
            controls=view.controls,
            expand=True,
            spacing=0,
        ),
    )
    view.controls = [
        ft.Stack(
            controls=[*bg_controls, foreground, help_chat],
            expand=True,
        )
    ]
    return view


def _build_runtime_error_view(route: str, error: Exception) -> ft.View:
    return ft.View(
        route=route or "/",
        bgcolor="#FFF3D2",
        controls=[
            ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text("Interner Fehler", size=30, weight="bold", color="#B71C1C"),
                    ft.Text(
                        "Beim Laden der Seite ist ein Fehler aufgetreten.",
                        size=16,
                        color="black",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        bgcolor="#FFE8B5",
                        border_radius=12,
                        padding=12,
                        width=900,
                        content=ft.Text(str(error), color="black", selectable=True),
                    ),
                    ft.Text(
                        "Bitte Seite neu laden oder erneut anmelden.",
                        size=14,
                        color="#555555",
                    ),
                ],
            )
        ],
    )


def main(page: ft.Page):
    page.title = "SnackHub"
    page.window_width = 1500
    page.window_height = 900

    def route_change(e):
        page.views.clear()

        try:
            view = None
            if page.route == "/":
                view = landing_page(page)
            elif page.route == "/schueler_landing":
                view = schueler_landing_page(page)
            elif page.route == "/login":
                view = login_page(page)
            elif page.route == "/register":
                view = register_page(page)
            elif page.route.startswith("/dashboard"):
                view = dashboard_router(page)
            elif page.route == "/shop":
                view = shop_page(page)
            elif page.route == "/voting":
                view = voting_page(page)
            elif page.route == "/voting_kantine":
                view = voting_kantine_page(page)
            elif page.route == "/feedback":
                view = feedback_page(page)
            elif page.route == "/feedback_overview":
                view = feedback_overview_page(page)
            elif page.route == "/menu_kantine":
                view = menu_management_page(page)
            elif page.route == "/voting_overview":
                page.go("/voting_kantine")
                return
            elif page.route == "/kantine_landing":
                view = kantine_landing_page(page)
            elif page.route == "/vorbestellen":
                view = vorbestellen_page(page)
            elif page.route == "/vorbestellungen_kantine":
                view = vorbestellungen_kantine_page(page)
            else:
                view = ft.View("/", [ft.Text("404 - Seite nicht gefunden", color="black")])

            page.views.append(_decorate_view_with_animated_bg(page, view))
        except Exception as route_error:
            print(f"[route_error] route={page.route} error={route_error}")
            traceback.print_exc()
            page.views.clear()
            page.views.append(_decorate_view_with_animated_bg(page, _build_runtime_error_view(page.route, route_error)))

        try:
            page.update()
        except Exception as update_error:
            print(f"[update_error] route={page.route} error={update_error}")
            traceback.print_exc()

    page.on_route_change = route_change

    if not page.route:
        page.route = "/"
    route_change(None)


_assets_dir = Path(__file__).resolve().parent / "assets"


def _get_port() -> int:
    for key in ("SNACKHUB_PORT", "PORT"):
        raw = os.getenv(key)
        if raw:
            try:
                return int(raw)
            except ValueError:
                pass
    return 0


def _get_app_view() -> ft.AppView:
    raw = (os.getenv("SNACKHUB_VIEW") or "web_browser").strip().lower()
    mapping = {
        "flet_app": ft.AppView.FLET_APP,
        "desktop": ft.AppView.FLET_APP,
        "web_browser": ft.AppView.WEB_BROWSER,
        "browser": ft.AppView.WEB_BROWSER,
        "flet_app_web": ft.AppView.FLET_APP_WEB,
        "flet_app_hidden": ft.AppView.FLET_APP_HIDDEN,
    }
    return mapping.get(raw, ft.AppView.WEB_BROWSER)


def _configure_browser_preference() -> None:
    browser_raw = (os.getenv("SNACKHUB_BROWSER") or "").strip()
    if not browser_raw:
        return

    if browser_raw.lower() == "brave":
        candidates = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            "brave",
        ]
        for candidate in candidates:
            if candidate == "brave" or Path(candidate).exists():
                os.environ["BROWSER"] = candidate
                print(f"SnackHub Browser-Override: {candidate}")
                return
        return

    os.environ["BROWSER"] = browser_raw
    print(f"SnackHub Browser-Override: {browser_raw}")


def run_app() -> None:
    initialize_app()

    port = _get_port()
    view = _get_app_view()
    _configure_browser_preference()
    print(f"SnackHub startet mit App-View: {view.value}")
    ft.run(
        main,
        assets_dir=str(_assets_dir),
        view=view,
        port=port,
    )


if __name__ == "__main__":
    _ensure_database_initialized()
    run_app()
