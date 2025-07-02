import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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

def take_screenshot(driver):
    # Set a large viewport size
    driver.set_window_size(1920, 1080)
    
    # Take the screenshot and return the PNG data
    screenshot_png = driver.get_screenshot_as_png()
    logger.info("📸 Screenshot captured")
    return screenshot_png

def save_screenshot(driver, filename="initial.png"):
    # Set a large viewport size
    driver.set_window_size(1920, 1080)
    
    # Save the screenshot to file
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
        
        # Save initial screenshot
        save_screenshot(driver)
        
        return driver
        
    except Exception as e:
        logger.error(f"💥 Error: {e}")
        if driver:
            driver.quit()
        return None

if __name__ == "__main__":
    logger.info("Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): " + 
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("Current User's Login: Sman12345678")
    main()
