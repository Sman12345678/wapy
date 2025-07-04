import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from selenium.webdriver.common.keys import Keys

# Emoji-enhanced logging setup
class EmojiFormatter(logging.Formatter):
    EMOJI_MAP = {
        'DEBUG': '🔍',
        'INFO': '✨',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    def format(self, record):
        record.levelname = f"{self.EMOJI_MAP.get(record.levelname, '')} {record.levelname}"
        return super().format(record)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(EmojiFormatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.handlers = [handler]

def get_driver():
    options = Options()
    options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')
    user_data_dir = os.path.abspath("chrome_data")
    options.add_argument(f'--user-data-dir={user_data_dir}')
    service = Service(os.environ.get("CHROMEDRIVER_BIN", "/usr/bin/chromedriver"))
    return webdriver.Chrome(service=service, options=options)

def is_authenticated(driver):
    try:
        qr_element = driver.find_elements(By.CSS_SELECTOR, 'canvas[aria-label="Scan this QR code to link a device!"]')
        if qr_element:
            logger.info("🔒 Not authenticated - QR code present")
            return False
        chat_list = driver.find_elements(By.CSS_SELECTOR, 'div._ahlk')
        if chat_list:
            logger.info("✅ WhatsApp Web authenticated")
            return True
        logger.info("🔄 Authentication status unclear")
        return False
    except Exception as e:
        logger.error(f"💥 Error checking authentication: {e}")
        return False

def post_auth_continue(driver, wait_seconds=5):
    logger.info(f"⏳ Waiting {wait_seconds} seconds post-authentication for page load.")
    time.sleep(wait_seconds)
    try:
        # Try clicking the Continue button if it exists
        continue_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.x889kno.x1a8lsjc.x13jy36j.x64bnmy.x1n2onr6.x1rg5ohu.xk50ysn.x1f6kntn.xyesn5m.x1rl75mt.x19t5iym.xz7t8uv.x13xmedi.x178xt8z.x1lun4ml.xso031l.xpilrb4.x13fuv20.x18b5jzi.x1q0q8m5.x1t7ytsu.x1v8p93f.x1o3jo1z.x16stqrj.xv5lvn5.x1hl8ikr.xfagghw.x9dyr19.x9lcvmn.x1pse0pq.xcjl5na.xfn3atn.x1k3x3db.x9qntcr.xuxw1ft.xv52azi'))
        )
        continue_btn.click()
        logger.info("✅ Clicked the Continue button after QR scan.")
        time.sleep(2)
        return True
    except TimeoutException:
        logger.info("ℹ️ Continue button not present, checking if chats are loaded...")
        # Check if chat list is present (as a fallback)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div._ahlk'))
            )
            logger.info("✅ Chat list loaded, proceeding without Continue button.")
            return True
        except TimeoutException:
            logger.error("❌ Neither Continue button nor chat list found! Cannot proceed.")
            return False
    except Exception as e:
        logger.error(f"❌ Error clicking Continue button: {e}")
        return False

def take_screenshot(driver):
    driver.set_window_size(1920, 1080)
    screenshot_png = driver.get_screenshot_as_png()
    logger.info("📸 Screenshot captured")
    return screenshot_png

def get_qr(driver):
    try:
        qr_base64 = driver.execute_script("""
            const canvas = document.querySelector('canvas[aria-label="Scan this QR code to link a device!"][role="img"]');
            if (!canvas) return null;
            try {
                return canvas.toDataURL('image/png').substring('data:image/png;base64,'.length);
            } catch (e) {
                console.error('Canvas error:', e);
                return null;
            }
        """)
        if qr_base64:
            logger.info("✅ QR code successfully captured")
            return qr_base64
        else:
            logger.error("❌ QR code not found or cannot be captured")
            return None
    except Exception as e:
        logger.error(f"💥 Error capturing QR code: {e}")
        return None

def find_unread_chats(driver):
    """Return list of unread badge elements (one per unread chat)."""
    try:
        chats = driver.find_elements(By.CSS_SELECTOR, 'div._ahlk span[aria-label*="unread messages"]')
        logger.info(f"🔎 Found {len(chats)} chats with unread messages")
        return chats
    except Exception as e:
        logger.error(f"❌ Error finding unread chats: {e}")
        return []

def last_msg(driver):
    """Return last message (not from Nova, must have text) in current chat, else None."""
    try:
        msgs = driver.find_elements(By.CSS_SELECTOR, 'div.copyable-text[data-pre-plain-text]')
        if not msgs:
            logger.info("💬 No messages found in chat.")
            return None
        m = msgs[-1]
        info = m.get_attribute('data-pre-plain-text')
        if not info or ':' not in info:
            logger.info("⚠️ Message info missing or malformed.")
            return None
        sender = info.rsplit('] ', 1)[-1].split(':', 1)[0].strip()
        if sender.lower() == 'nova':
            logger.info("🙅 Last message is from Nova, skipping.")
            return None
        # Try to extract the message text, else mark as unsupported
        try:
            text_elem = m.find_element(By.CSS_SELECTOR, 'span.selectable-text.copyable-text span')
            text = text_elem.text
            if not text.strip():
                logger.info("🛑 Unsupported message (empty text), skipping.")
                return None
        except Exception:
            logger.info("🛑 Unsupported message type (no text), skipping.")
            return None
        logger.info(f"✅ Last message from '{sender}': {text}")
        return {'info': info, 'text': text}
    except Exception as e:
        logger.error(f"❌ Error getting last message: {e}")
        return None

def get_unread_msgs(driver):
    """Collect last unread message (not from Nova) from each unread chat."""
    res = []
    # Check post-auth status before proceeding
    if not post_auth_continue(driver, wait_seconds=5):
        logger.error("❌ Cannot proceed: WhatsApp Web not ready after authentication.")
        return res
    unread = find_unread_chats(driver)
    for badge in unread:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", badge)
            badge.click()
            logger.info("👆 Opened unread chat")
            time.sleep(2)
            m = last_msg(driver)
            if m:
                res.append(m)
        except Exception as e:
            logger.error(f"❌ Error in unread chat loop: {e}")
            continue
    logger.info(f"📦 Collected {len(res)} unread messages.")
    return res

def send_msg(driver, msg):
    msg_box = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Type a message"][contenteditable="true"]')
    msg_box.click()
    msg_box.clear()
    msg_box.send_keys(msg)
    time.sleep(0.1)
    send_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Send"]')
    send_btn.click()
    return True

def start_unread_watcher(driver, interval=60):
    while True:
        try:
            if driver and is_authenticated(driver):
                logger.info("🔄 [BOT] Checking for unread messages...")
                messages = get_unread_msgs(driver)
                if messages:
                    logger.info(f"📥 [BOT] Found {len(messages)} unread messages:")
                    for msg in messages:
                        logger.info(f"💬 [BOT] Message: {msg['text']}")
                else:
                    logger.info("📭 [BOT] No new unread messages.")
            else:
                logger.warning("🚫 [BOT] Not authenticated. Skipping check.")
        except Exception as e:
            logger.error(f"💥 [BOT] Error during message check: {e}")
        time.sleep(interval)


def main():
    try:
        driver = get_driver()
        logger.info("🚀 WebDriver initialized")
        driver.get("https://web.whatsapp.com")
        logger.info("🌐 Navigated to WhatsApp Web")
        logger.info("⏱️ Waiting 10 seconds for QR or page load...")
        time.sleep(10)

        # ✅ Start background thread to watch for unread messages
        watcher_thread = threading.Thread(target=start_unread_watcher, args=(driver,), daemon=True)
        watcher_thread.start()
        logger.info("👁️ Started background message watcher thread")

        return driver

    except Exception as e:
        logger.error(f"💥 Error: {e}")
        if 'driver' in locals():
            driver.quit()
        return None

if __name__ == "__main__":
    logger.info(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Current User's Login: Sman12345678")
    main()
