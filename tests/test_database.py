import unittest
import psycopg2

from database import database_sm
from dto.RequesDTO import CreateUserDTO
from service.userService import createUser
from service.postService import createPost


class TestDatabase(unittest.TestCase):
    def setUp(self):
        database_sm.cur.execute("DELETE FROM post")
        database_sm.cur.execute('DELETE FROM "user"')
        database_sm.con.commit()
        self.db = database_sm

    def test_save_user_and_post(self):
        user_dto = CreateUserDTO(first_name="Mine", last_name="Tester")
        user = createUser(user_dto)

        self.assertIsNotNone(user.id)

        post = createPost(
            image_bytes=b"\x89PNG\r\n\x1a\n",
            image_mime="image/png",
            text="Test text 123",
            user_id=user.id,
        )

        self.assertIsNotNone(post.id)

        self.db.cur.execute(
            'SELECT first_name, last_name FROM "user" WHERE id = %s',
            (user.id,),
        )
        urow = self.db.cur.fetchone()
        self.assertEqual(urow, ("Mine", "Tester"))

        self.db.cur.execute(
            "SELECT text, user_id FROM post WHERE id = %s",
            (post.id,),
        )
        prow = self.db.cur.fetchone()
        self.assertEqual(prow, ("Test text 123", user.id))

    def test_unique_post_text_constraint(self):
        user_dto = CreateUserDTO(first_name="Sana", last_name="Bhutto")
        user = createUser(user_dto)

        createPost(
            image_bytes=b"\x89PNG\r\n\x1a\n",
            image_mime="image/png",
            text="unique text",
            user_id=user.id,
        )

        with self.assertRaises(psycopg2.IntegrityError):
            createPost(
                image_bytes=b"\x89PNG\r\n\x1a\n",
                image_mime="image/png",
                text="unique text",
                user_id=user.id,
            )


if __name__ == "__main__":
    unittest.main()
