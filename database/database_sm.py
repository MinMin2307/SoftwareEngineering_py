import os
import psycopg2

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "socialdb")
DB_USER = os.getenv("DB_USER", "socialuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secretpassword")

con = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
)
con.autocommit = True
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS "user"(
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    CONSTRAINT user_unique_name UNIQUE (first_name, last_name)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS post(
    id SERIAL PRIMARY KEY,
    image TEXT,
    text TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    createdAt TIMESTAMP DEFAULT NOW()
)
""")

# --------- FUNKTIONEN, WIE SIE DEIN SERVICE-CODE ERWARTET ---------

def save_user(first_name: str, last_name: str) -> int:
    """Neuen User speichern und ID zurückgeben."""
    cur.execute(
        'INSERT INTO "user"(first_name, last_name) VALUES (%s, %s) RETURNING id',
        (first_name, last_name),
    )
    user_id = cur.fetchone()[0]
    return user_id


def save_post(image: str, text: str, user_id: int) -> int:
    """Neuen Post speichern und ID zurückgeben."""
    cur.execute(
        "INSERT INTO post(image, text, user_id) VALUES (%s, %s, %s) RETURNING id",
        (image, text, user_id),
    )
    post_id = cur.fetchone()[0]
    return post_id


def get_postById(id: int):
    cur.execute(
        "SELECT id, image, text, user_id FROM post WHERE id = %s",
        (id,),
    )
    return cur.fetchone()


def get_allPosts():
    cur.execute("SELECT id, image, text, user_id FROM post ORDER BY id")
    return cur.fetchall()


def get_userById(id: int):
    cur.execute(
        'SELECT id, first_name, last_name FROM "user" WHERE id = %s',
        (id,),
    )
    return cur.fetchone()


def get_postByUserId(user_id: int):
    cur.execute(
        "SELECT id, image, text, user_id FROM post WHERE user_id = %s ORDER BY id",
        (user_id,),
    )
    return cur.fetchall()


def search_postsByText(text: str):
    pattern = f"%{text}%"
    cur.execute(
        "SELECT id, image, text, user_id FROM post WHERE text ILIKE %s",
        (pattern,),
    )
    return cur.fetchall()


def get_userByName(first_name: str, last_name: str):
    cur.execute(
        'SELECT id, first_name, last_name FROM "user" '
        "WHERE LOWER(first_name) = LOWER(%s) AND LOWER(last_name) = LOWER(%s)",
        (first_name, last_name),
    )
    return cur.fetchone()
