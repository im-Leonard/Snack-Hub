"""
Script zum Erstellen von Test-Nutzern für SnackHub
"""
from snackhub2.services.auth_service import AuthService
from snackhub2.services.db import get_conn

def create_test_users():
    """Erstellt Test-Nutzer für Schüler und Kantine"""

    auth = AuthService()
    
    try:
        # Prüfe ob Nutzer bereits existieren
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        
        # Test-Nutzer 1: Schüler
        cursor.execute("SELECT * FROM users WHERE username = %s", ("schueler_test",))
        if cursor.fetchone() is None:
            print("Erstelle Schüler Test-Nutzer...")
            auth.register_user("schueler_test", "test123", "schueler")
            print("✓ Schüler erstellt: schueler_test / test123")
        else:
            print("ℹ Schüler Test-Nutzer existiert bereits")
        
        # Test-Nutzer 2: Kantine
        cursor.execute("SELECT * FROM users WHERE username = %s", ("kantine_test",))
        if cursor.fetchone() is None:
            print("Erstelle Kantine Test-Nutzer...")
            auth.register_user("kantine_test", "test123", "kantine")
            print("✓ Kantine erstellt: kantine_test / test123")
        else:
            print("ℹ Kantine Test-Nutzer existiert bereits")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*50)
        print("TEST-NUTZER ÜBERSICHT:")
        print("="*50)
        print("Schüler:")
        print("  Benutzername: schueler_test")
        print("  Passwort:     test123")
        print("  Rolle:        schueler")
        print()
        print("Kantine:")
        print("  Benutzername: kantine_test")
        print("  Passwort:     test123")
        print("  Rolle:        kantine")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Test-Nutzer: {e}")
        print("\nHinweis: Stelle sicher, dass:")
        print("1. MySQL läuft")
        print("2. Die Datenbank 'schul_kantine' existiert")
        print("3. Die Tabelle 'users' existiert")

if __name__ == "__main__":
    create_test_users()
