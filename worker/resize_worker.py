import os
import json
import time
from io import BytesIO
import pika
from PIL import Image
from database.database_sm import get_post_full_for_resize, update_post_thumbnail

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE_RESIZE", "image_resize")
THUMB_MAX_SIZE = (256, 256)

def make_thumb_jpeg(image_bytes: bytes) -> bytes:
    with Image.open(BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail(THUMB_MAX_SIZE)
        out = BytesIO()
        img.save(out, format="JPEG", quality=85, optimize=True)
        return out.getvalue()

def connect_with_retry():
    last_err = None
    for _ in range(60):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise last_err

def main():
    conn = connect_with_retry()
    ch = conn.channel()
    ch.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    ch.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        try:
            msg = json.loads(body.decode("utf-8"))
            post_id = int(msg["post_id"])
            row = get_post_full_for_resize(post_id)
            if row is None or row[0] is None:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            full_bytes = bytes(row[0])
            thumb_bytes = make_thumb_jpeg(full_bytes)
            update_post_thumbnail(post_id, thumb_bytes, "image/jpeg")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    ch.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
    ch.start_consuming()

if __name__ == "__main__":
    main()
