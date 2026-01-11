import os, json, time, re
import pika
from transformers import pipeline
from database.database_sm import get_post_text_for_nlp, update_post_generated_text, set_textgen_status
from service.queue import publish_textgen_job

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
Q_TEXTGEN = os.getenv("RABBITMQ_QUEUE_TEXTGEN", "nlp_textgen")

TEXTGEN_MODEL = os.getenv("TEXTGEN_MODEL", "gpt2")
MAX_NEW_TOKENS = int(os.getenv("TEXTGEN_MAX_NEW_TOKENS", "40"))

def connect_with_retry():
    last = None
    for _ in range(60):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        except Exception as e:
            last = e
            time.sleep(1)
    raise last


def process_textgen_job(post_id: int, tg) -> None:
    prompt = get_post_text_for_nlp(post_id)
    if not prompt:
        set_textgen_status(post_id, "FAILED", "No prompt text found.")
        return

    set_textgen_status(post_id, "RUNNING", None)

    raw = prompt.strip().replace("\n", " ").replace("\r", " ")
    raw = " ".join(raw.split())
    seed = raw[:200]

    better_prompt = (
        "TASK: You are a professional English copywriter.\n"
        "Write a short, coherent continuation of the post below.\n"
        "RULES:\n"
        "- Write EXACTLY 1 or 2 sentences.\n"
        "- Stay on the same topic.\n"
        "- No hashtags, no emojis.\n"
        "- Do not repeat phrases from the post.\n"
        "POST:\n"
        f"{seed}\n"
        "CONTINUATION:\n"
    )

    gen = tg(
        better_prompt,
        max_new_tokens=60,
        do_sample=True,
        temperature=0.4,
        top_p=0.75,
        no_repeat_ngram_size=4,
        repetition_penalty=1.25,
        return_full_text=False,
    )[0]["generated_text"].strip()

    sentences = re.split(r'(?<=[.!?])\s+', gen)
    out = " ".join(sentences[:2]).strip()

    # Fallback if model produced no sentence punctuation
    if not out:
        out = gen[:240].strip()

    update_post_generated_text(post_id, out)


def main():
    tg = pipeline("text-generation", model=TEXTGEN_MODEL)

    conn = connect_with_retry()
    ch = conn.channel()
    ch.queue_declare(queue=Q_TEXTGEN, durable=True)
    ch.basic_qos(prefetch_count=1)

    def cb(ch, method, props, body):
        msg = None
        post_id = None
        retries_left = 0

        try:
            msg = json.loads(body.decode("utf-8"))
            post_id = int(msg["post_id"])
            retries_left = int(msg.get("retries_left", 0))

            process_textgen_job(post_id, tg)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            if post_id is not None and retries_left > 0:
                set_textgen_status(post_id, "PENDING", f"Retrying, error: {type(e).__name__}: {e}")
                publish_textgen_job(post_id, retries_left=retries_left - 1)
            elif post_id is not None:
                set_textgen_status(post_id, "FAILED", f"{type(e).__name__}: {e}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=Q_TEXTGEN, on_message_callback=cb)
    ch.start_consuming()


if __name__ == "__main__":
    main()
