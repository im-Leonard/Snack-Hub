from snackhub2.services.db import get_conn

def initialize_app():
    """Initialisiere die App und Datenbank beim Start"""
    print("\n" + "="*60)
    print("SNACKHUB INITIALIZATION")
    print("="*60)
    
    try:
        print("\n✓ Prüfe Datenbankverbindung...")
        conn = get_conn()
        cursor = conn.cursor()
        
        required_tables = (
            "meals",
            "polls",
            "poll_dishes",
            "poll_votes",
            "preorders",
            "weekly_feedback",
        )
        missing_tables = []
        missing_columns = []

        for table_name in required_tables:
            cursor.execute("SHOW TABLES LIKE %s", (table_name,))
            if cursor.fetchone() is None:
                missing_tables.append(table_name)

        if "preorders" not in missing_tables:
            cursor.execute("SHOW COLUMNS FROM preorders LIKE 'paid_confirmed_at'")
            if cursor.fetchone() is None:
                missing_columns.append("preorders.paid_confirmed_at")

        if "meals" not in missing_tables:
            cursor.execute("SHOW COLUMNS FROM meals LIKE 'category'")
            if cursor.fetchone() is None:
                missing_columns.append("meals.category")

        cursor.close()
        conn.close()

        if missing_tables or missing_columns:
            print("⚠️  Datenbank nicht vollständig initialisiert!")
            if missing_tables:
                print(f"→ Fehlende Tabellen: {', '.join(missing_tables)}")
            if missing_columns:
                print(f"→ Fehlende Spalten: {', '.join(missing_columns)}")
            print("→ Starte Datenbank-Setup...\n")
            from snackhub2.setup_db import setup_database
            setup_database()
        else:
            print("✓ Datenbank OK")
            print("="*60 + "\n")
            
    except Exception as e:
        print(f"❌ Fehler bei der Initialisierung: {e}")
        print("\nVersuche Datenbank-Setup...")
        try:
            from snackhub2.setup_db import setup_database
            setup_database()
        except Exception as setup_error:
            print(f"❌ Setup fehlgeschlagen: {setup_error}")
            print("Warnung: App startet trotzdem weiter; einzelne Seiten koennen eingeschraenkt sein.")

