import unittest

from database import database_sm
from dto.RequesDTO import CreateUserDTO
from service.userService import createUser
from worker.textgen_worker import process_textgen_job
from worker.sentiment_worker import process_sentiment_job
from worker.headline_worker import process_headline_job


class DummyTextGen:
    def __call__(self, prompt, **kwargs):
        return [{"generated_text": "Nice continuation. Second sentence."}]


class DummySentiment:
    def __call__(self, text):
        return [{"label": "POSITIVE", "score": 0.987}]


class DummyHeadline:
    def __call__(self, prompt, **kwargs):
        return [{"generated_text": "Great Day Ahead"}]


class TestWorkers(unittest.TestCase):
    def setUp(self):
        database_sm.cur.execute("DELETE FROM post")
        database_sm.cur.execute('DELETE FROM "user"')
        database_sm.con.commit()
        self.user = createUser(CreateUserDTO(first_name="Worker", last_name="Tester"))

    def _create_post(self, text: str) -> int:
        return database_sm.save_post(
            image_full=None,
            image_full_mime="application/octet-stream",
            text=text,
            user_id=self.user.id,
        )

    def test_textgen_worker_updates_post(self):
        post_id = self._create_post("Testing text generation.")
        process_textgen_job(post_id, DummyTextGen())

        row = database_sm.get_postById(post_id)
        self.assertEqual(row[0], post_id)
        self.assertEqual(row[4], "DONE")
        self.assertIsNotNone(row[3])

    def test_sentiment_worker_updates_post(self):
        post_id = self._create_post("Testing sentiment.")
        process_sentiment_job(post_id, DummySentiment())

        row = database_sm.get_postById(post_id)
        self.assertEqual(row[6], "POSITIVE")
        self.assertAlmostEqual(row[7], 0.987, places=3)
        self.assertEqual(row[8], "DONE")

    def test_headline_worker_updates_post(self):
        post_id = self._create_post("Testing headline generation.")
        process_headline_job(post_id, DummyHeadline())

        row = database_sm.get_postById(post_id)
        self.assertEqual(row[10], "Great Day Ahead")
        self.assertEqual(row[11], "DONE")


if __name__ == "__main__":
    unittest.main()
