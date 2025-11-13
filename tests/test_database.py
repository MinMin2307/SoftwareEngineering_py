import unittest
import importlib
import sqlite3

import database_sm
from User import User


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Reload to reset tables for isolation between tests
        self.db = importlib.reload(database_sm)

    def test_save_user_and_post(self):
        user = User("Mine", "Tester")
        self.db.save_user(user)
        self.assertIsNotNone(user.id)

        post = user.add_post("", "Test text 123")
        self.db.save_post(post)
        self.assertIsNotNone(post.id)

        urow = self.db.cur.execute(
            "SELECT first_name,last_name FROM user WHERE id=?",
            (user.id,),
        ).fetchone()
        self.assertEqual(urow, ("Mine", "Tester"))

        prow = self.db.cur.execute(
            "SELECT image,text,user_id FROM post WHERE id=?",
            (post.id,),
        ).fetchone()
        self.assertEqual(prow, ("", "Test text 123", user.id))

    def test_unique_post_text_constraint(self):
        user = User("Uniq", "Owner")
        self.db.save_user(user)

        p1 = user.add_post("", "unique text")
        self.db.save_post(p1)

        p2 = user.add_post("", "unique text")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.save_post(p2)


if __name__ == "__main__":
    unittest.main()

