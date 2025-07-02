import logging
import os
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
        # Add emoji to the log level
        record.levelname = f"{self.EMOJI_MAP.get(record.levelname, '')} {record.levelname}"
        return super().format(record)

# Logging setup with emojis
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(EmojiFormatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.handlers = [handler]

# Chrome setup
user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
)
chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
chromedriver_bin = os.environ.get("CHROMEDRIVER_BIN", "/usr/bin/chromedriver")

# Updated selector for QR canvas
QR_SELECTORS = [
    # Exact match from the HTML structure
    'div[data-ref] canvas[aria-label="Scan this QR code to link a device!"]',
    # More specific selector using the class
    'div._akau canvas[aria-label="Scan this QR code to link a device!"]',
    # Try with data-ref attribute
    'div[data-ref^="2@"] canvas',
    # Fallback to just the canvas
    'canvas[aria-label="Scan this QR code to link a device!"]',
]

def get_driver():
    options = Options()
    options.binary_location = chrome_bin
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    service = Service(chromedriver_bin)
    return webdriver.Chrome(service=service, options=options)

def take_screenshot(driver):
    screenshot = driver.get_screenshot_as_png()
    logger.info("📸 Screenshot captured")
    return screenshot

def wait_for_qr_container(driver, timeout=30):
    """Wait for the QR container to be present"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-ref^="2@"]'))
        )
        logger.info("🎯 QR container found")
        return True
    except TimeoutException:
        logger.error("⏳ Timeout waiting for QR container")
        return False

def copy_qr(driver):
    try:
        # First wait for the container
        if not wait_for_qr_container(driver):
            return None
            
        # Log the structure we're looking for
        logger.debug("🔍 Looking for QR code in the following structure:")
        logger.debug("📦 div[data-ref] > canvas[aria-label]")
        
        # Try each selector
        for selector in QR_SELECTORS:
            try:
                logger.debug(f"🎯 Trying selector: {selector}")
                qr_canvas = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"✅ Found QR canvas with selector: {selector}")
                
                # Ensure the canvas is ready
                WebDriverWait(driver, 5).until(
                    lambda d: d.execute_script("""
                        var canvas = arguments[0];
                        var context = canvas.getContext('2d');
                        var pixelData = context.getImageData(0, 0, 1, 1);
                        return pixelData.data[3] !== 0;  // Check if pixel is not transparent
                    """, qr_canvas)
                )
                
                # Get canvas data
                qr_base64 = driver.execute_script("""
                    var canvas = arguments[0];
                    try {
                        // Force a small delay to ensure canvas is painted
                        return new Promise((resolve) => {
                            setTimeout(() => {
                                try {
                                    resolve(canvas.toDataURL('image/png')
                                           .substring('data:image/png;base64,'.length));
                                } catch (e) {
                                    resolve(null);
                                }
                            }, 500);
                        });
                    } catch (e) {
                        return null;
                    }
                """, qr_canvas)
                
                if qr_base64:
                    logger.info("🎉 QR code successfully captured")
                    return qr_base64
                else:
                    logger.warning("⚠️ Canvas found but could not get image data")
                    
            except NoSuchElementException:
                logger.debug(f"⚠️ Selector not found: {selector}")
                continue
                
        # If we get here, log the page source for debugging
        logger.error("❌ No working QR code selector found")
        log_page_source(driver)
        return None
        
    except Exception as e:
        logger.error(f"💥 Error capturing QR code: {e}")
        return None


def main():
    driver = None
    try:
        driver = get_driver()
        logger.info("🚀 WebDriver initialized")
        
        # Navigate to WhatsApp Web
        driver.get("https://web.whatsapp.com")
        logger.info("🌐 Navigated to WhatsApp Web")
        
        # Initial wait for page load
        logger.info("⏱️ Waiting for page load...")
        time.sleep(5)
        take_screenshot(driver)# Reduced initial wait since we have explicit waits now
        
        # Try to get QR code
        qr_data = copy_qr(driver)
        if qr_data:
            logger.info("✅ QR code extracted successfully")
        else:
            logger.error("❌ Failed to extract QR code")
            
        return driver
            
    except Exception as e:
        logger.error(f"💥 Error in main function: {e}")
        if driver:
            driver.quit()
        return None

if __name__ == "__main__":
    logger.info(f"🕐 Starting script at {time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    main()
