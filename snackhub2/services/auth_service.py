import bcrypt
from mysql.connector import errors as mysql_errors

from snackhub2.models.users import User, user_from_db_row
from snackhub2.services.db import get_conn


class AuthService:
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def login_user(self, username: str, password: str) -> User | None:
        username = (username or "").strip()
        password = password or ""
        if not username or not password:
            return None

        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        if not self.check_password(password, row["password_hash"]):
            return None

        return user_from_db_row(row)

    def register_user(self, username: str, password: str, role: str) -> None:
        username = (username or "").strip()
        if not username:
            raise ValueError("Benutzername darf nicht leer sein")
        if not password:
            raise ValueError("Passwort darf nicht leer sein")
        if role not in ("schueler", "kantine"):
            raise ValueError("Ungültige Rolle")

        conn = get_conn()
        cursor = conn.cursor()

        hashed_pw = self.hash_password(password)

        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, hashed_pw, role),
            )
            conn.commit()
        except mysql_errors.IntegrityError as e:
            # i.d.R. Duplicate username
            raise ValueError("Benutzername existiert bereits") from e
        finally:
            cursor.close()
            conn.close()


_auth = AuthService()


def hash_password(password: str) -> str:
    return _auth.hash_password(password)


def check_password(password: str, hashed: str) -> bool:
    return _auth.check_password(password, hashed)


def login_user(username: str, password: str):
    return _auth.login_user(username, password)


def register_user(username: str, password: str, role: str) -> None:
    return _auth.register_user(username, password, role)
