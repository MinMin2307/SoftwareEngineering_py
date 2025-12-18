import unittest

from fastapi.testclient import TestClient

import api as api_module
import database.database_sm as db_module


class TestAPI(unittest.TestCase):
    def setUp(self):
        # Datenbank zwischen den Tests leeren
        db_module.cur.execute("DELETE FROM post")
        db_module.cur.execute('DELETE FROM "user"')
        db_module.con.commit()
        self.client = TestClient(api_module.app)

    def test_create_user_and_post_and_list_posts(self):
        # Create user
        user_resp = self.client.post(
            "/user",
            json={"first_name": "Alice", "last_name": "Tester"},
        )
        self.assertEqual(user_resp.status_code, 200)
        user = user_resp.json()
        self.assertIn("id", user)

        # Create post for this user (multipart with image)
        dummy_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        post_resp = self.client.post(
            "/post",
            data={"text": "Hello from API test", "user_id": str(user["id"])},
            files={"file": ("hello.png", dummy_image, "image/png")},
        )
        self.assertEqual(post_resp.status_code, 200)
        post = post_resp.json()
        self.assertEqual(post["text"], "Hello from API test")
        self.assertEqual(post["user_id"], user["id"])
        self.assertIn("image_full_url", post)
        self.assertIn("image_thumb_url", post)

        # List all posts and check that our post is present
        list_resp = self.client.get("/posts")
        self.assertEqual(list_resp.status_code, 200)
        posts = list_resp.json()
        self.assertTrue(any(p["id"] == post["id"] for p in posts))

    def test_get_posts_for_user_by_id(self):
        # Arrange: create user and two posts
        user_resp = self.client.post(
            "/user",
            json={"first_name": "Bob", "last_name": "User"},
        )
        user = user_resp.json()

        texts = ["Post 1", "Post 2"]
        for t in texts:
            self.client.post(
                "/post",
                data={"text": t, "user_id": str(user["id"])},
                files={"file": ("hello.png", b"\x89PNG\r\n\x1a\n", "image/png")},
            )

        # Act: fetch user (with posts) by ID
        resp = self.client.get(f"/user/{user['id']}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["id"], user["id"])
        returned_texts = [p["text"] for p in data["posts"]]
        for t in texts:
            self.assertIn(t, returned_texts)

    def test_search_posts_by_text(self):
        # Arrange: create user and posts with different texts
        user_resp = self.client.post(
            "/user",
            json={"first_name": "Carla", "last_name": "Search"},
        )
        user = user_resp.json()

        self.client.post(
            "/post",
            data={"text": "This is about FastAPI testing", "user_id": str(user["id"])},
            files={"file": ("a.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        )
        self.client.post(
            "/post",
            data={"text": "Completely different content", "user_id": str(user["id"])},
            files={"file": ("b.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        )

        # Act: search for posts containing "FastAPI"
        resp = self.client.get("/posts/search", params={"text": "FastAPI"})
        self.assertEqual(resp.status_code, 200)
        results = resp.json()

        self.assertTrue(
            any("FastAPI" in p["text"] for p in results),
            msg="Expected at least one post containing 'FastAPI'",
        )


if __name__ == "__main__":
    unittest.main()
