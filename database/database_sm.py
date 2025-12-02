import sqlite3

con = sqlite3.connect('database.db', check_same_thread=False )
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS post")
cur.execute("DROP TABLE IF EXISTS user")

cur.execute("""CREATE TABLE IF NOT EXISTS user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL COLLATE NOCASE,
    last_name  TEXT NOT NULL COLLATE NOCASE,
    UNIQUE(first_name, last_name)
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS post(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image TEXT,
    text TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    createdAt INTEGER DEFAULT (strftime('%Y-%m-%d %H:%M:%f','now')),
    UNIQUE(text),
    FOREIGN KEY(user_id) REFERENCES user(id)
)""")

def save_user(first_name: str, last_name: str) -> int:
    cur.execute( "INSERT INTO user(first_name, last_name) VALUES(?, ?)", (first_name, last_name))
    return cur.lastrowid

def save_post(image:str, text:str, user_id: int) -> int:
    cur.execute("INSERT INTO post(image,text,user_id) VALUES(?,?,?)",
                (image, text, user_id))
    return cur.lastrowid

def get_postById(id: int ):
    post_row = cur.execute("SELECT * FROM post WHERE id = ?", (id,)).fetchone()
    return post_row

def get_allPosts():
    post_allRows = cur.execute(
        "SELECT id, image, text, user_id FROM post").fetchall()
    return post_allRows

def get_userById(id: int):
    user_row = cur.execute("SELECT * FROM user WHERE id = ?", (id,)).fetchone()
    return user_row

def get_postByUserId(user_id: int):
    post_userRow = cur.execute("SELECT * FROM post WHERE user_id = ?", (user_id,)).fetchall()
    return post_userRow

def search_postsByText(text: str):
    text_rows = cur.execute(
        "SELECT id, image, text, user_id FROM post WHERE text LIKE ?",(f"%{text}%",)).fetchall()
    return text_rows

def get_userByName(first_name: str, last_name: str):
    user_row = cur.execute(
        "SELECT * FROM user WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?)",
        (first_name, last_name)
    ).fetchone()
    return user_row





