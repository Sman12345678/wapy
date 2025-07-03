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

def post_auth_continue(driver, wait_seconds=4):
    logger.info(f"⏳ Waiting {wait_seconds} seconds post-authentication for page load.")
    time.sleep(wait_seconds)
    try:
        # Try clicking the Continue button if it exists
        continue_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.x889kno.x1a8lsjc.x13jy36j.x64bnmy.x1n2onr6.x1rg5ohu.xk50ysn.x1f6kntn.xyesn5m.x1rl75mt.x19t5iym.xz7t8uv.x13xmedi.x178xt8z.x1lun4ml.x1y1aw1k.xwib8y2.x1glnyev.x1ix68h3.x19i3t5v.x1tk7jg1.x1vjfegm.x1l6b2ym'))
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

def get_unread_messages(driver):
    try:
        if not is_authenticated(driver):
            logger.warning("⚠️ Please scan QR code first")
            return None
        # Wait for page and continue button after authentication
        post_auth_continue(driver, wait_seconds=6)
        unread_badge = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div._ahlk span[aria-label*="unread messages"]'))
        )
        unread_count = int(''.join(filter(str.isdigit, unread_badge.get_attribute('aria-label'))))
        logger.info(f"📬 Found {unread_count} unread messages")
        unread_badge.click()
        logger.info("👆 Clicked unread messages indicator")
        time.sleep(2)
        return unread_count
    except Exception as e:
        logger.error(f"💥 Error getting unread messages: {e}")
        return None

def get_msg(driver):
    """
    For each chat, click and get the latest message.
    If the sender is 'Nova', skip.
    If message content/structure is missing, skip.
    Returns a list of messages (dicts) from all chats except those from Nova.
    """
    messages_info = []
    try:
        # Wait for chat list to load
        chat_list = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div._21S-L'))
        )
        for chat in chat_list:
            try:
                chat.click()
                # Wait for messages in the chat
                chat_messages = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.copyable-text[data-pre-plain-text]'))
                )
                # Get the last message
                last_msg = chat_messages[-1]
                msg_info = last_msg.get_attribute('data-pre-plain-text')
                try:
                    msg_text = last_msg.find_element(By.CSS_SELECTOR, 'span.selectable-text.copyable-text span').text
                except Exception:
                    continue  # Skip if expected structure not found

                # Extract sender from data-pre-plain-text (format: [HH:MM, DD/MM/YYYY] Sender Name: )
                sender = None
                if msg_info:
                    # Example: "[14:09, 03/07/2025] Nova: Hello"
                    p1 = msg_info.find('] ')
                    p2 = msg_info.find(':', p1)
                    if p1 != -1 and p2 != -1:
                        sender = msg_info[p1+2:p2]

                if sender and sender.strip() == 'Nova':
                    continue  # Ignore messages from Nova

                messages_info.append({
                    'sender': sender,
                    'text': msg_text
                })
            except Exception as e:
                logger.error(f"Error parsing chat: {e}")
                continue
        logger.info(f"📨 Found {len(messages_info)} messages from all chats (excluding 'Nova')")
        return messages_info
    except Exception as e:
        logger.error(f"💥 Error getting messages: {e}")
        return None

def main():
    try:
        driver = get_driver()
        logger.info("🚀 WebDriver initialized")
        driver.get("https://web.whatsapp.com")
        logger.info("🌐 Navigated to WhatsApp Web")
        logger.info("⏱️ Waiting 10 seconds for page load...")
        time.sleep(10)
        return driver
    except Exception as e:
        logger.error(f"💥 Error: {e}")
        if 'driver' in locals():
            driver.quit()
        return None

if __name__ == "__main__":
    logger.info(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Current User's Login: Suleiman")
    main()
