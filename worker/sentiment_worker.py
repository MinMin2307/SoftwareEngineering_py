import os, json, time
import pika
from transformers import pipeline
from database.database_sm import get_post_text_for_nlp, update_post_sentiment, set_sentiment_status
from service.queue import publish_sentiment_job

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
Q_SENTIMENT = os.getenv("RABBITMQ_QUEUE_SENTIMENT", "nlp_sentiment")

SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")

def connect_with_retry():
    last = None
    for _ in range(60):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        except Exception as e:
            last = e
            time.sleep(1)
    raise last


def process_sentiment_job(post_id: int, sa) -> None:
    text = get_post_text_for_nlp(post_id)
    if not text:
        set_sentiment_status(post_id, "FAILED", "No text found.")
        return

    set_sentiment_status(post_id, "RUNNING", None)

    result = sa(text[:512])[0]
    update_post_sentiment(post_id, result["label"], float(result["score"]))


def main():
    sa = pipeline("sentiment-analysis", model=SENTIMENT_MODEL)

    conn = connect_with_retry()
    ch = conn.channel()
    ch.queue_declare(queue=Q_SENTIMENT, durable=True)
    ch.basic_qos(prefetch_count=1)

    def cb(ch, method, props, body):
        post_id = None
        retries_left = 0
        try:
            msg = json.loads(body.decode("utf-8"))
            post_id = int(msg["post_id"])
            retries_left = int(msg.get("retries_left", 0))

            process_sentiment_job(post_id, sa)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            if post_id is not None and retries_left > 0:
                set_sentiment_status(post_id, "PENDING", f"Retrying, error: {type(e).__name__}: {e}")
                publish_sentiment_job(post_id, retries_left=retries_left - 1)
            elif post_id is not None:
                set_sentiment_status(post_id, "FAILED", f"{type(e).__name__}: {e}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=Q_SENTIMENT, on_message_callback=cb)
    ch.start_consuming()


if __name__ == "__main__":
    main()
