import sqlite3

con = sqlite3.connect('database.db', isolation_level=None )
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS post")
cur.execute("DROP TABLE IF EXISTS user")

cur.execute("""CREATE TABLE IF NOT EXISTS user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
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

def save_user(user):
    cur.execute("INSERT INTO user(first_name,last_name) VALUES(?,?)",
                (user.first_name, user.last_name))
    user.id = cur.lastrowid

def save_post(post):
    cur.execute("INSERT INTO post(image,text,user_id) VALUES(?,?,?)",
                (post.image, post.text, post.user.id))
    post.id = cur.lastrowid

