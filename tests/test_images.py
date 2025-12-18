import unittest
from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

import api as api_module
import database.database_sm as db_module
from dto.RequesDTO import CreateUserDTO
from service.postService import createPost
from service.userService import createUser
from worker.resize_worker import make_thumb_jpeg
from database.database_sm import update_post_thumbnail


def make_png_bytes(color=(255, 0, 0), size=(16, 16)) -> bytes:
    """Produce a tiny PNG for upload/thumbnail tests."""
    buf = BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


class TestImages(unittest.TestCase):
    def setUp(self):
        db_module.cur.execute("DELETE FROM post")
        db_module.cur.execute('DELETE FROM "user"')
        db_module.con.commit()
        self.client = TestClient(api_module.app)

    def test_full_image_endpoint_returns_upload(self):
        user = createUser(CreateUserDTO(first_name="Img", last_name="Full"))
        image_bytes = make_png_bytes()

        with patch("service.postService.publish_resize_job") as mock_publish:
            post = createPost(
                image_bytes=image_bytes,
                image_mime="image/png",
                text="full-image-test",
                user_id=user.id,
            )

        resp = self.client.get(f"/post/{post.id}/image/full")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "image/png")
        self.assertEqual(resp.content, image_bytes)

        thumb_resp = self.client.get(f"/post/{post.id}/image/thumb")
        self.assertEqual(thumb_resp.status_code, 404)

        mock_publish.assert_called_once_with(post.id)

    def test_thumbnail_served_after_worker_updates(self):
        user = createUser(CreateUserDTO(first_name="Thumb", last_name="Maker"))
        full_bytes = make_png_bytes()

        with patch("service.postService.publish_resize_job"):
            post = createPost(
                image_bytes=full_bytes,
                image_mime="image/png",
                text="thumb-test",
                user_id=user.id,
            )

        thumb_bytes = make_thumb_jpeg(full_bytes)
        update_post_thumbnail(post.id, thumb_bytes, "image/jpeg")

        resp = self.client.get(f"/post/{post.id}/image/thumb")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "image/jpeg")
        self.assertGreater(len(resp.content), 0)


if __name__ == "__main__":
    unittest.main()
