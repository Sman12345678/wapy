import time
import threading
from wapy import get_unread_msgs, send_msg, is_authenticated
from loguru import logger  # You can use your logger if you want

def start_ai(driver, interval=30):
    """
    Auto-reply bot that checks messages and replies to users.
    """
    logger.info("🤖 AI bot started...")

    replied_cache = set()  # Prevent replying twice to same message

    while True:
        try:
            if driver and is_authenticated(driver):
                logger.info("👁️ AI checking for unread messages...")
                messages = get_unread_msgs(driver)

                for msg in messages:
                    key = f"{msg['info']}_{msg['text']}"
                    if key in replied_cache:
                        continue  # Skip already replied

                    # Extract sender name from msg['info']
                    try:
                        sender = msg['info'].rsplit('] ', 1)[-1].split(':', 1)[0].strip()
                    except:
                        sender = "friend"

                    reply = f"Hello {sender}, thank you for messaging! 😊"
                    send_msg(driver, reply)
                    logger.info(f"💬 Replied to {sender}: {reply}")
                    replied_cache.add(key)

            else:
                logger.warning("🚫 AI Bot: Driver not authenticated.")

        except Exception as e:
            logger.error(f"💥 AI error: {e}")

        time.sleep(interval)
