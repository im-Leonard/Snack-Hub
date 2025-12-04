import bcrypt
from services.db import get_conn

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def login_user(username, password):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        return None

    if not check_password(password, user["password_hash"]):
        return None

    return user


def register_user(username, password, role):
    conn = get_conn()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
        (username, hashed_pw, role)
    )

    conn.commit()
    cursor.close()
    conn.close()
