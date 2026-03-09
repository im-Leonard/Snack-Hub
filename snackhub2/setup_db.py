"""
Setup Script für die SnackHub Datenbank
Erstellt die Datenbank, Tabellen und Test-Nutzer
"""
import mysql.connector
from snackhub2.config import DB_CONFIG
from snackhub2.services.auth_service import hash_password

def setup_database():
    """Erstellt die Datenbank und Tabellen"""
    
    print("="*60)
    print("SNACKHUB DATENBANK SETUP")
    print("="*60)
    
    try:
        # Verbinde zu MySQL ohne Datenbank-Auswahl
        conn_config = DB_CONFIG.copy()
        db_name = conn_config.pop('database')
        
        print(f"\n1. Verbinde zu MySQL Server ({conn_config['host']})...")
        conn = mysql.connector.connect(**conn_config)
        cursor = conn.cursor()
        
        # Erstelle Datenbank
        print(f"2. Erstelle Datenbank '{db_name}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        print(f"   ✓ Datenbank '{db_name}' bereit")
        
        # Erstelle users Tabelle
        print("3. Erstelle Tabelle 'users'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('schueler', 'kantine') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✓ Tabelle 'users' erstellt")
        
        # Erstelle meals Tabelle
        print("4. Erstelle Tabelle 'meals'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(5,2),
                category VARCHAR(50) NOT NULL DEFAULT 'Allgemein',
                available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✓ Tabelle 'meals' erstellt")

        cursor.execute("SHOW COLUMNS FROM meals LIKE 'category'")
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE meals ADD COLUMN category VARCHAR(50) NOT NULL DEFAULT 'Allgemein'"
            )
            print("   ✓ Spalte 'category' ergänzt")
        
        # Erstelle polls Tabelle
        print("5. Erstelle Tabelle 'polls'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS polls (
                poll_id INT AUTO_INCREMENT PRIMARY KEY,
                meal_id INT,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP NULL,
                INDEX (meal_id)
            )
        """)
        print("   ✓ Tabelle 'polls' erstellt")
        
        # Erstelle votes Tabelle
        print("6. Erstelle Tabelle 'votes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                meal_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (meal_id) REFERENCES meals(id)
            )
        """)
        print("   ✓ Tabelle 'votes' erstellt")
        
        # Erstelle feedback Tabelle
        print("7. Erstelle Tabelle 'feedback'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                meal_id INT,
                rating INT CHECK (rating BETWEEN 1 AND 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (meal_id) REFERENCES meals(id)
            )
        """)
        print("   ✓ Tabelle 'feedback' erstellt")
        
        # Erstelle orders Tabelle
        print("8. Erstelle Tabelle 'orders'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                meal_id INT,
                quantity INT DEFAULT 1,
                status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (meal_id) REFERENCES meals(id)
            )
        """)
        print("   ✓ Tabelle 'orders' erstellt")
        
        # Erstelle poll_dishes Tabelle
        print("9. Erstelle Tabelle 'poll_dishes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS poll_dishes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                poll_id INT NOT NULL,
                dish_name VARCHAR(100) NOT NULL,
                dish_order INT NOT NULL DEFAULT 1,
                votes INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (poll_id) REFERENCES polls(poll_id) ON DELETE CASCADE
            )
        """)
        print("   ✓ Tabelle 'poll_dishes' erstellt")

        # Migration für bestehende DBs: dish_order nachrüsten, falls fehlt
        cursor.execute("SHOW COLUMNS FROM poll_dishes LIKE 'dish_order'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE poll_dishes ADD COLUMN dish_order INT NOT NULL DEFAULT 1")
            print("   ✓ Spalte 'dish_order' ergänzt")

        # Eine Stimme pro User pro Poll
        print("10. Erstelle Tabelle 'poll_votes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS poll_votes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                poll_id INT NOT NULL,
                dish_id INT NOT NULL,
                user_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_poll_user (poll_id, user_id),
                FOREIGN KEY (poll_id) REFERENCES polls(poll_id) ON DELETE CASCADE,
                FOREIGN KEY (dish_id) REFERENCES poll_dishes(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("   ✓ Tabelle 'poll_votes' erstellt")

        print("11. Erstelle Tabelle 'preorders'...")
        cursor.execute("""
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
        """)
        print("   ✓ Tabelle 'preorders' erstellt")

        cursor.execute("SHOW COLUMNS FROM preorders LIKE 'paid_confirmed_at'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE preorders ADD COLUMN paid_confirmed_at TIMESTAMP NULL")
            print("   ✓ Spalte 'paid_confirmed_at' ergänzt")

        print("12. Erstelle Tabelle 'weekly_feedback'...")
        cursor.execute("""
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
        """)
        print("   ✓ Tabelle 'weekly_feedback' erstellt")
        
        # Test-Nutzer erstellen
        print("\n13. Erstelle Test-Nutzer...")
        
        # Schüler Test-Nutzer
        cursor.execute("SELECT * FROM users WHERE username = %s", ("schueler_test",))
        if cursor.fetchone() is None:
            hashed_pw = hash_password("test123")
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                ("schueler_test", hashed_pw, "schueler")
            )
            print("   ✓ Schüler Test-Nutzer erstellt")
        else:
            print("   ℹ Schüler Test-Nutzer existiert bereits")
        
        # Kantine Test-Nutzer
        cursor.execute("SELECT * FROM users WHERE username = %s", ("kantine_test",))
        if cursor.fetchone() is None:
            hashed_pw = hash_password("test123")
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                ("kantine_test", hashed_pw, "kantine")
            )
            print("   ✓ Kantine Test-Nutzer erstellt")
        else:
            print("   ℹ Kantine Test-Nutzer existiert bereits")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✓ SETUP ERFOLGREICH ABGESCHLOSSEN!")
        print("="*60)
        print("\nTEST-NUTZER:")
        print("-"*60)
        print("Schüler Account:")
        print("  Benutzername: schueler_test")
        print("  Passwort:     test123")
        print("  Rolle:        schueler")
        print()
        print("Kantine Account:")
        print("  Benutzername: kantine_test")
        print("  Passwort:     test123")
        print("  Rolle:        kantine")
        print("="*60)
        print("\nDu kannst dich jetzt mit diesen Zugangsdaten anmelden!")
        
    except mysql.connector.Error as e:
        print(f"\n❌ MySQL Fehler: {e}")
        print("\nHinweise:")
        print("- Stelle sicher, dass MySQL läuft")
        print("- Prüfe die Zugangsdaten in config.py")
        print(f"  Host: {DB_CONFIG.get('host', 'localhost')}")
        print(f"  User: {DB_CONFIG.get('user', 'root')}")
        
    except Exception as e:
        print(f"\n❌ Fehler: {e}")

if __name__ == "__main__":
    setup_database()
