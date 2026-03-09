from datetime import datetime
from snackhub2.services.db import get_conn
from snackhub2.models.poll import Poll

class PollService:
    @staticmethod
    def create_poll(dishes):
        """Erstelle eine neue Abstimmung mit Gerichten"""
        try:
            conn = get_conn()
            cursor = conn.cursor()
            
            # Erstelle Poll
            cursor.execute(
                "INSERT INTO polls (meal_id, start_date) VALUES (%s, %s)",
                (0, datetime.now())
            )
            conn.commit()
            poll_id = cursor.lastrowid
            print(f"✓ Poll erstellt mit ID: {poll_id}")
            
            # Speichere Gerichte
            for dish in dishes:
                if dish and dish.strip():
                    cursor.execute(
                        "INSERT INTO poll_dishes (poll_id, dish_name, votes) VALUES (%s, %s, %s)",
                        (poll_id, dish.strip(), 0)
                    )
                    print(f"✓ Gericht hinzugefügt: {dish}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {"poll_id": poll_id, "success": True}
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Poll: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_active_poll():
        """Hole die aktive Abstimmung mit Gerichten"""
        try:
            conn = get_conn()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT * FROM polls WHERE end_date IS NULL LIMIT 1"
            )
            poll = cursor.fetchone()
            
            if not poll:
                cursor.close()
                conn.close()
                print("⚠️  Keine aktive Poll gefunden")
                return None
            
            # Hole Gerichte für diese Poll
            cursor.execute(
                "SELECT id, dish_name, votes FROM poll_dishes WHERE poll_id = %s",
                (poll['poll_id'],)
            )
            dishes = cursor.fetchall()
            poll['dishes'] = dishes
            
            print(f"✓ Poll geladen: ID={poll['poll_id']}, Gerichte={len(dishes)}")
            
            cursor.close()
            conn.close()
            
            return poll
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der aktiven Poll: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_all_active_polls():
        """Hole ALLE aktiven Abstimmungen (für Kantine-Übersicht)"""
        try:
            conn = get_conn()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT * FROM polls WHERE end_date IS NULL"
            )
            polls = cursor.fetchall()
            
            print(f"✓ {len(polls)} aktive Polls gefunden")
            
            # Hole Gerichte für jede Poll
            for poll in polls:
                cursor.execute(
                    "SELECT id, dish_name, votes FROM poll_dishes WHERE poll_id = %s",
                    (poll['poll_id'],)
                )
                poll['dishes'] = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return polls
        except Exception as e:
            print(f"❌ Fehler beim Abrufen aller Polls: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def add_vote(poll_id, dish_id):
        """Erhöhe Stimmen für ein Gericht"""
        try:
            conn = get_conn()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE poll_dishes SET votes = votes + 1 WHERE id = %s AND poll_id = %s",
                (dish_id, poll_id)
            )
            conn.commit()
            
            print(f"✓ Stimme hinzugefügt: Poll={poll_id}, Dish={dish_id}")
            
            cursor.close()
            conn.close()
            
            return {"success": True}
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Stimme: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def close_poll(poll_id):
        """Beende eine Abstimmung"""
        try:
            conn = get_conn()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE polls SET end_date = %s WHERE poll_id = %s",
                (datetime.now(), poll_id)
            )
            conn.commit()
            
            print(f"✓ Poll beendet: ID={poll_id}")
            
            cursor.close()
            conn.close()
            
            return {"success": True}
        except Exception as e:
            print(f"❌ Fehler beim Beenden der Poll: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
