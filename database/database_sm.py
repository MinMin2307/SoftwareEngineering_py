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
    text TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    createdAt TIMESTAMP DEFAULT NOW()
)
""")

try:
    cur.execute("""ALTER TABLE post DROP COLUMN IF EXISTS image""")
except Exception:
    pass

try:
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS image_full BYTEA""")
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS image_full_mime TEXT""")
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS image_thumb BYTEA""")
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS image_thumb_mime TEXT""")
except Exception:
    pass

try:
    cur.execute("""ALTER TABLE post DROP CONSTRAINT IF EXISTS post_text_key""")
except Exception:
    pass

try:
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS generated_text TEXT""")
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS generated_text_status TEXT DEFAULT 'PENDING'""")
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS generated_text_error TEXT""")
    cur.execute("""ALTER TABLE post ADD COLUMN IF NOT EXISTS generated_text_updated_at TIMESTAMP""")
except Exception:
    pass


def save_user(first_name: str, last_name: str) -> int:
    cur.execute(
        'INSERT INTO "user"(first_name, last_name) VALUES (%s, %s) RETURNING id',
        (first_name, last_name),
    )
    return cur.fetchone()[0]


def save_post(image_full: bytes | None, image_full_mime: str, text: str, user_id: int) -> int:
    cur.execute(
        """
        INSERT INTO post(
            image_full, image_full_mime,
            image_thumb, image_thumb_mime,
            text, user_id,
            generated_text, generated_text_status, generated_text_error, generated_text_updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, NULL, 'PENDING', NULL, NOW())
        RETURNING id
        """,
        (
            psycopg2.Binary(image_full) if image_full is not None else None,
            image_full_mime if image_full is not None else None,
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
        """
        SELECT id, text, user_id, generated_text, generated_text_status, generated_text_error
        FROM post WHERE id = %s
        """,
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
    cur.execute("""
        SELECT id, text, user_id, generated_text, generated_text_status, generated_text_error
        FROM post
        ORDER BY id DESC
    """)
    return cur.fetchall()


def get_userById(id: int):
    cur.execute(
        'SELECT id, first_name, last_name FROM "user" WHERE id = %s',
        (id,),
    )
    return cur.fetchone()

def get_postByUserId(user_id: int):
    cur.execute("""
        SELECT id, text, user_id, generated_text, generated_text_status, generated_text_error
        FROM post
        WHERE user_id = %s
        ORDER BY id
    """, (user_id,))
    return cur.fetchall()

def search_postsByText(text: str):
    pattern = f"%{text}%"
    cur.execute("""
        SELECT id, text, user_id, generated_text, generated_text_status, generated_text_error
        FROM post
        WHERE text ILIKE %s
        ORDER BY id DESC
    """, (pattern,))
    return cur.fetchall()


def get_userByName(first_name: str, last_name: str):
    cur.execute(
        'SELECT id, first_name, last_name FROM "user" '
        "WHERE LOWER(first_name) = LOWER(%s) AND LOWER(last_name) = LOWER(%s)",
        (first_name, last_name),
    )
    return cur.fetchone()

def get_post_text_for_nlp(post_id: int):
    cur.execute("SELECT text FROM post WHERE id=%s", (post_id,))
    row = cur.fetchone()
    return row[0] if row else None

def set_textgen_status(post_id: int, status: str, error: str | None = None) -> None:
    cur.execute(
        """
        UPDATE post
        SET generated_text_status = %s,
            generated_text_error = %s,
            generated_text_updated_at = NOW()
        WHERE id = %s
        """,
        (status, error, post_id),
    )

def update_post_generated_text(post_id: int, gen_text: str) -> None:
    cur.execute(
        """
        UPDATE post
        SET generated_text = %s,
            generated_text_status = 'DONE',
            generated_text_error = NULL,
            generated_text_updated_at = NOW()
        WHERE id = %s
        """,
        (gen_text, post_id),
    )
