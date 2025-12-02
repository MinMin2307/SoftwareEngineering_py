import unittest

from database import database_sm
from dto.RequesDTO import CreateUserDTO
from dto.ResponseDTO import UserResponseDTO
from service.userService import createUser


class TestUser(unittest.TestCase):
    def setUp(self):
        database_sm.cur.execute("DELETE FROM post")
        database_sm.cur.execute("DELETE FROM user")
        database_sm.con.commit()

    def test_create_user_creates_and_persists(self):
        data = CreateUserDTO(first_name="Alice", last_name="Doe")
        user = createUser(data)

        self.assertIsInstance(user, UserResponseDTO)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.posts, [])

        row = database_sm.cur.execute(
            "SELECT first_name, last_name FROM user WHERE id = ?",
            (user.id,),
        ).fetchone()
        self.assertEqual(row, ("Alice", "Doe"))

    def test_create_user_returns_existing_if_duplicate(self):
        data1 = CreateUserDTO(first_name="Bob", last_name="Smith")
        user1 = createUser(data1)

        data2 = CreateUserDTO(first_name="Bob", last_name="Smith")
        user2 = createUser(data2)

        self.assertEqual(user1.id, user2.id)
        self.assertEqual(user1.first_name, user2.first_name)
        self.assertEqual(user1.last_name, user2.last_name)


if __name__ == "__main__":
    unittest.main()
