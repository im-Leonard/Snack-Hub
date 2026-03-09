import flet as ft

def landing_page(page: ft.Page):
    print("Landing Page wird geladen...")
    
    # Header mit Navigation
    header = ft.Container(
        bgcolor="#F5E6D3",
        padding=15,
        content=ft.Row([
            ft.TextButton("Shop"),
            ft.TextButton("Voting"),
            ft.TextButton("Feedback"),
            ft.Container(expand=True),
            ft.IconButton(ft.icons.ACCOUNT_CIRCLE),
        ], alignment="space_between")
    )

    # News Box
    news = ft.Container(
        bgcolor="#F5E6D3",
        border_radius=20,
        padding=20,
        content=ft.Column([
            ft.Text("Neuigkeiten", size=18, weight="bold"),
            ft.Text("Test Text", size=11)
        ])
    )

    # Logo Box (statt Bild)
    logo = ft.Container(
        width=150,
        height=150,
        bgcolor="#FF6B6B",
        border_radius=20,
        alignment=ft.alignment.center,
        content=ft.Text("SNACKHUB", color="white", weight="bold", size=16)
    )

    # Tagesmenü Box
    menu = ft.Container(
        bgcolor="#F5E6D3",
        border_radius=20,
        padding=20,
        content=ft.Column([
            ft.Text("Tagesmenü", size=18, weight="bold"),
            ft.Icon(ft.icons.LOCAL_DINING, size=30, color="#FF6B6B"),
            ft.Text("Spaghetti\nBolognese", size=13, weight="bold")
        ])
    )

    # Hauptinhaltsbereich
    main_content = ft.Row([
        news,
        logo,
        menu
    ], alignment="center", spacing=30)

    # Footer
    footer = ft.Container(
        bgcolor="#F5E6D3",
        padding=15,
        height=100,
        content=ft.Text("Footer mit Kontakt", size=12)
    )

    print("Alle Elemente erstellt, View wird zurückgegeben...")
    
    return ft.View(
        route="/",
        controls=[
            ft.Column([
                header,
                ft.Container(content=main_content, padding=40, expand=True),
                footer
            ], expand=True, spacing=0)
        ]
    )

def main(page: ft.Page):
    page.title = "SnackHub - Test"
    page.window_width = 1500
    page.window_height = 900
    page.bgcolor = "#FFFFFF"
    
    print("App startet...")
    page.views.clear()
    page.views.append(landing_page(page))
    print("View hinzugefügt")
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
