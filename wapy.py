# TIERD.........</>
import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

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

# Logging setup with emojis
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
    options.add_argument("--window-size=1920,1080")  # Set a large window size
    
    service = Service(os.environ.get("CHROMEDRIVER_BIN", "/usr/bin/chromedriver"))
    return webdriver.Chrome(service=service, options=options)

def take_screenshot(driver, filename):
    # Set a large viewport size
    driver.set_window_size(1920, 1080)
    
    # Take the screenshot and save it
    driver.save_screenshot(filename)
    logger.info(f"📸 Screenshot saved as {filename}")

def main():
    try:
        # Initialize driver
        driver = get_driver()
        logger.info("🚀 WebDriver initialized")
        
        # Navigate to WhatsApp Web
        driver.get("https://web.whatsapp.com")
        logger.info("🌐 Navigated to WhatsApp Web")
        
        # Wait 10 seconds
        logger.info("⏱️ Waiting 10 seconds for page load...")
        time.sleep(10)
        
        # Generate timestamp for filename
        
        filename = f"initial.png"
        
        # Take screenshot
        take_screenshot(driver, filename)
        
    except Exception as e:
        logger.error(f"💥 Error: {e}")
    finally:
        if driver:
            driver.quit()
            logger.info("🚪 Browser closed")

if __name__ == "__main__":
    current_time = time.strftime('%Y-%m-%d %H:%M:%S UTC')
    current_user = os.getenv('USER', 'Suleiman')
    
    logger.info(f"⏰ Current Time: {current_time}")
    logger.info(f"👤 Running as: {current_user}")
    main()
