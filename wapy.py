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
    
    # Set your specific user agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')
    
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

def get_qr(driver):
    try:
        # Wait for QR canvas to be present
        logger.info("🔍 Looking for QR code...")
        
        # Execute JavaScript to get QR code from canvas
        qr_base64 = driver.execute_script("""
            const canvas = document.querySelector('canvas[aria-label="Scan this QR code to link a device!"][role="img"]');
            if (!canvas) return null;
            
            // Ensure canvas is the correct size
            if (canvas.width !== 228 || canvas.height !== 228) {
                console.log('Canvas size mismatch:', canvas.width, canvas.height);
                return null;
            }
            
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
    # Print exact format as requested
    logger.info(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Current User's Login: Sman12345678")
    main()
