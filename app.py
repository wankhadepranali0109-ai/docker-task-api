import os
import time

import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request , render_template

app = Flask(__name__)


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=os.getenv("DATABASE_PORT", "5432"),
        dbname=os.getenv("DATABASE_NAME", "tasks"),
        user=os.getenv("DATABASE_USER", "taskuser"),
        password=os.getenv("DATABASE_PASSWORD", "taskpassword"),
        row_factory=dict_row,
    )


def initialise_database():
    for attempt in range(10):
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tasks (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            done BOOLEAN NOT NULL DEFAULT FALSE
                        );
                    """)

            print("Database is ready and tasks table exists.")
            return

        except psycopg.OperationalError as error:
            print(f"Database is not ready yet ({attempt + 1}/10): {error}")
            time.sleep(2)

    raise RuntimeError("Could not connect to PostgreSQL after 10 attempts.")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/tasks")
def list_tasks():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks ORDER BY id;")
            tasks = cursor.fetchall()

    return jsonify(tasks), 200


@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify(error="title is required"), 400

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                RETURNING id, title, done;
                """,
                (title, False),
            )
            task = cursor.fetchone()

    return jsonify(task), 201


if __name__ == "__main__":
    initialise_database()

    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)