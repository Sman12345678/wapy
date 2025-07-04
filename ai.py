import time
from wapy import get_unread_msgs, send_msg, is_authenticated
import logging

logger = logging.getLogger(__name__)

def start_ai(driver, interval=30):
    logger.info("🤖 AI bot started...")

    if not driver:
        logger.error("❌ Driver is None. Cannot start AI.")
        return
    
    replied_cache = set()

    while True:
        try:
            if is_authenticated(driver):
                logger.info("👁️ AI checking for unread messages...")
                messages = get_unread_msgs(driver)
                for msg in messages:
                    key = f"{msg['info']}_{msg['text']}"
                    if key in replied_cache:
                        continue

                    try:
                        sender = msg['info'].rsplit('] ', 1)[-1].split(':', 1)[0].strip()
                    except:
                        sender = "friend"

                    reply = f"Hey {sender}, I received your message!"
                    send_msg(driver, reply)
                    logger.info(f"💬 Replied to {sender}: {reply}")
                    replied_cache.add(key)
            else:
                logger.warning("⚠️ Not authenticated yet.")
        except Exception as e:
            logger.error(f"🔥 AI bot error: {e}")
        time.sleep(interval)
