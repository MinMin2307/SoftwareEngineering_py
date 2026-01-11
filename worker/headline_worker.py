import os, json, time, re
import pika
from transformers import pipeline
from database.database_sm import get_post_text_for_nlp, update_post_headline, set_headline_status
from service.queue import publish_headline_job

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
Q_HEADLINE = os.getenv("RABBITMQ_QUEUE_HEADLINE", "nlp_headline")

HEADLINE_MODEL = os.getenv("HEADLINE_MODEL", "gpt2")
MAX_NEW_TOKENS = int(os.getenv("HEADLINE_MAX_NEW_TOKENS", "12"))

def connect_with_retry():
    last = None
    for _ in range(60):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        except Exception as e:
            last = e
            time.sleep(1)
    raise last

def _clean_headline(text: str) -> str:
    cleaned = " ".join(text.replace("\n", " ").replace("\r", " ").split())
    cleaned = re.sub(r"[\"'`]+", "", cleaned).strip()
    cleaned = cleaned[:80].strip()
    return cleaned

def process_headline_job(post_id: int, tg) -> None:
    prompt = get_post_text_for_nlp(post_id)
    if not prompt:
        set_headline_status(post_id, "FAILED", "No prompt text found.")
        return

    set_headline_status(post_id, "RUNNING", None)

    raw = prompt.strip().replace("\n", " ").replace("\r", " ")
    raw = " ".join(raw.split())
    seed = raw[:200]

    better_prompt = (
        "TASK: Write a short, clear headline (3 to 6 words).\n"
        "RULES:\n"
        "- No hashtags, no emojis.\n"
        "- Stay on the post topic.\n"
        "- Output only the headline.\n"
        "POST:\n"
        f"{seed}\n"
        "HEADLINE:\n"
    )

    gen = tg(
        better_prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        no_repeat_ngram_size=3,
        repetition_penalty=1.2,
        return_full_text=False,
    )[0]["generated_text"]

    headline = _clean_headline(gen)
    if not headline:
        set_headline_status(post_id, "FAILED", "Generated empty headline.")
        return

    update_post_headline(post_id, headline)

def main():
    tg = pipeline("text-generation", model=HEADLINE_MODEL)

    conn = connect_with_retry()
    ch = conn.channel()
    ch.queue_declare(queue=Q_HEADLINE, durable=True)
    ch.basic_qos(prefetch_count=1)

    def cb(ch, method, props, body):
        post_id = None
        retries_left = 0
        try:
            msg = json.loads(body.decode("utf-8"))
            post_id = int(msg["post_id"])
            retries_left = int(msg.get("retries_left", 0))

            process_headline_job(post_id, tg)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            if post_id is not None and retries_left > 0:
                set_headline_status(post_id, "PENDING", f"Retrying, error: {type(e).__name__}: {e}")
                publish_headline_job(post_id, retries_left=retries_left - 1)
            elif post_id is not None:
                set_headline_status(post_id, "FAILED", f"{type(e).__name__}: {e}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=Q_HEADLINE, on_message_callback=cb)
    ch.start_consuming()

if __name__ == "__main__":
    main()
