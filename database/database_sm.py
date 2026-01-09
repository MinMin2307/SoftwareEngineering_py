import os
import time
import psycopg2

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "socialdb")
DB_USER = os.getenv("DB_USER", "socialuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secretpassword")

con = None
last_err = None

for _ in range(60):
    try:
        con = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        break
    except psycopg2.OperationalError as e:
        last_err = e
        time.sleep(1)

if con is None:
    raise last_err

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
    image_full BYTEA,
    image_full_mime TEXT,
    image_thumb BYTEA,
    image_thumb_mime TEXT,
    text TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    createdAt TIMESTAMP DEFAULT NOW()
)
""")

try:
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS image_full BYTEA""")
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS image_full_mime TEXT""")
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS image_thumb BYTEA""")
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS image_thumb_mime TEXT""")
    cur.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'post_unique_text'
            ) THEN
                ALTER TABLE post ADD CONSTRAINT post_unique_text UNIQUE (text);
            END IF;
        END $$;
        """
    )
except Exception:
    pass

try:
    cur.execute("""ALTER TABLE post DROP COLUMN IF EXISTS image""")
except Exception:
    pass


def save_user(first_name: str, last_name: str) -> int:
    cur.execute(
        'INSERT INTO "user"(first_name, last_name) VALUES (%s, %s) RETURNING id',
        (first_name, last_name),
    )
    return cur.fetchone()[0]


def save_post(image_full: bytes, image_full_mime: str, text: str, user_id: int) -> int:
    cur.execute(
        """
        INSERT INTO post(image_full, image_full_mime, image_thumb, image_thumb_mime, text, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            psycopg2.Binary(image_full),
            image_full_mime,
            None,
            None,
            text,
            user_id,
        ),
    )
    return cur.fetchone()[0]


def update_post_thumbnail(post_id: int, thumb_bytes: bytes, thumb_mime: str) -> None:
    cur.execute(
        """
        UPDATE post
        SET image_thumb = %s, image_thumb_mime = %s
        WHERE id = %s
        """,
        (psycopg2.Binary(thumb_bytes), thumb_mime, post_id),
    )


def get_post_full_for_resize(post_id: int):
    cur.execute(
        "SELECT image_full, image_full_mime FROM post WHERE id = %s",
        (post_id,),
    )
    return cur.fetchone()


def get_postById(id: int):
    cur.execute(
        "SELECT id, text, user_id FROM post WHERE id = %s",
        (id,),
    )
    return cur.fetchone()


def get_postImagesById(id: int):
    cur.execute(
        """
        SELECT image_full, image_full_mime, image_thumb, image_thumb_mime
        FROM post
        WHERE id = %s
        """,
        (id,),
    )
    return cur.fetchone()


def get_allPosts():
    cur.execute("SELECT id, text, user_id FROM post ORDER BY id")
    return cur.fetchall()


def get_userById(id: int):
    cur.execute(
        'SELECT id, first_name, last_name FROM "user" WHERE id = %s',
        (id,),
    )
    return cur.fetchone()


def get_postByUserId(user_id: int):
    cur.execute(
        "SELECT id, text, user_id FROM post WHERE user_id = %s ORDER BY id",
        (user_id,),
    )
    return cur.fetchall()


def search_postsByText(text: str):
    pattern = f"%{text}%"
    cur.execute(
        "SELECT id, text, user_id FROM post WHERE text ILIKE %s",
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
