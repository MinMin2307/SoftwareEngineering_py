import unittest

from model.user import User
from model.post import Post


class TestUser(unittest.TestCase):
    def test_add_post_creates_and_links(self):
        user = User("Alice", "Doe")
        post = user.add_post("image.png", "Hello world")

        self.assertIsInstance(post, Post)
        self.assertIn(post, user.posts)
        self.assertEqual(post.user, user)
        self.assertEqual(post.image, "image.png")
        self.assertEqual(post.text, "Hello world")


if __name__ == "__main__":
    unittest.main()

