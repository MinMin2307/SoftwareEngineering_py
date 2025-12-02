import unittest
import sqlite3

from database import database_sm
from dto.RequesDTO import CreateUserDTO, CreatePostDTO
from service.userService import createUser
from service.postService import createPost


class TestDatabase(unittest.TestCase):
    def setUp(self):
        database_sm.cur.execute("DELETE FROM post")
        database_sm.cur.execute("DELETE FROM user")
        database_sm.con.commit()
        self.db = database_sm

    def test_save_user_and_post(self):
        user_dto = CreateUserDTO(first_name="Mine", last_name="Tester")
        user = createUser(user_dto)

        self.assertIsNotNone(user.id)

        post_dto = CreatePostDTO(image="", text="Test text 123", user_id=user.id)
        post = createPost(post_dto)

        self.assertIsNotNone(post.id)

        urow = self.db.cur.execute(
            "SELECT first_name, last_name FROM user WHERE id = ?",
            (user.id,),
        ).fetchone()
        self.assertEqual(urow, ("Mine", "Tester"))

        prow = self.db.cur.execute(
            "SELECT image, text, user_id FROM post WHERE id = ?",
            (post.id,),
        ).fetchone()
        self.assertEqual(prow, ("", "Test text 123", user.id))

    def test_unique_post_text_constraint(self):
        user_dto = CreateUserDTO(first_name="Sana", last_name="Bhutto")
        user = createUser(user_dto)

        p1_dto = CreatePostDTO(image="", text="unique text", user_id=user.id)
        createPost(p1_dto)

        p2_dto = CreatePostDTO(image="", text="unique text", user_id=user.id)
        with self.assertRaises(sqlite3.IntegrityError):
            createPost(p2_dto)


if __name__ == "__main__":
    unittest.main()
