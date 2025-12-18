import os
import json
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "image_resize")

def publish_resize_job(post_id: int) -> None:
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    ch = conn.channel()
    ch.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    body = json.dumps({"post_id": post_id}).encode("utf-8")
    ch.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=body,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    conn.close()
