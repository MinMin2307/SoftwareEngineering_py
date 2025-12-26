import os
import json
import time
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

QUEUE_RESIZE = os.getenv("RABBITMQ_QUEUE_RESIZE", "image_resize")
QUEUE_TEXTGEN = os.getenv("RABBITMQ_QUEUE_TEXTGEN", "nlp_textgen")

def _connect_with_retry():
    last = None
    for _ in range(60):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        except Exception as e:
            last = e
            time.sleep(1)
    raise last

def _publish(queue_name: str, payload: dict) -> None:
    conn = _connect_with_retry()
    ch = conn.channel()
    ch.queue_declare(queue=queue_name, durable=True)
    body = json.dumps(payload).encode("utf-8")
    ch.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=body,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    conn.close()

def publish_resize_job(post_id: int) -> None:
    _publish(QUEUE_RESIZE, {"post_id": post_id})

def publish_textgen_job(post_id: int, retries_left: int = 3) -> None:
    _publish(QUEUE_TEXTGEN, {"post_id": post_id, "retries_left": retries_left})
