import sqlite3
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from database import connect_db


def get_user_by_username(username):
    with connect_db() as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            """
            SELECT
                id,
                username,
                password_hash,
                created_at
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def authenticate_user(username, password):
    user = get_user_by_username(username)

    if user is None or not check_password_hash(user["password_hash"], password):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "created_at": user["created_at"],
    }


def create_user(username, password):
    existing_user = get_user_by_username(username)
    if existing_user is not None:
        raise ValueError("Usuario ja existe")

    now = datetime.now().isoformat(timespec="seconds")
    password_hash = generate_password_hash(password)

    with connect_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, now),
        )
        user_id = cursor.lastrowid
        conn.commit()

    return {
        "id": user_id,
        "username": username,
        "created_at": now,
    }
