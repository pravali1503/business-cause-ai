
import sqlite3
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "rootcause.db"


def get_connection():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dataset_name TEXT,
            metric TEXT,
            previous_period TEXT,
            current_period TEXT,
            result_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


def create_user(name, email, password_hash):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        """, (name, email, password_hash))

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def get_user_by_email(email):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


def save_investigation(
    user_id,
    dataset_name,
    metric,
    previous_period,
    current_period,
    result_summary
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        if not isinstance(result_summary, str):
            result_summary = json.dumps(
                result_summary,
                default=str
            )

        cursor.execute("""
            INSERT INTO investigations (
                user_id,
                dataset_name,
                metric,
                previous_period,
                current_period,
                result_summary
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            dataset_name,
            metric,
            previous_period,
            current_period,
            result_summary
        ))

        connection.commit()

        return cursor.lastrowid

    finally:

        connection.close()


def get_user_investigations(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM investigations
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
    """, (user_id,))

    investigations = cursor.fetchall()

    connection.close()

    return investigations


def get_investigation_by_id(investigation_id, user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM investigations
        WHERE id = ? AND user_id = ?
    """, (investigation_id, user_id))

    investigation = cursor.fetchone()

    connection.close()

    return investigation


def delete_investigation(investigation_id, user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM investigations
        WHERE id = ? AND user_id = ?
    """, (investigation_id, user_id))

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted
