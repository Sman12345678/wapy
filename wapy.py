import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time

class SquareBoxFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        msg_lines = msg.split('\n')
        max_len = max(len(line) for line in msg_lines)
        box_width = max(22, max_len + 6)  # minimum width, adjust as needed
        top_bot = '=' * box_width
        empty = '=' + ' ' * (box_width - 2) + '='
        # Center each line in the box
        boxed_lines = [
            '=' + line.center(box_width - 2) + '='
            for line in msg_lines
        ]
        return '\n'.join([top_bot, empty, *boxed_lines, empty, top_bot])

logging.basicConfig(level=logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(SquareBoxFormatter("%(asctime)s [%(levelname)s] %(message)s"))
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(SquareBoxFormatter("%(asctime)s [%(levelname)s] %(message)s"))
root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

SELECTOR_QR_CANVAS = "canvas[aria-label='Scan this QR code to link a device!']"
SELECTOR_QR_CONTAINER = "div.x579bpy.xo1l8bm.xggjnk3.x1hql6x6"
SELECTOR_NEW_MESSAGE_DIV = "div._ahlk"

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
)
chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
chromedriver_bin = os.environ.get("CHROMEDRIVER_BIN", "/usr/bin/chromedriver")

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

driver = get_driver()

def take_screenshot(driver):
    return driver.get_screenshot_as_png()

def is_qr_still_visible(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, SELECTOR_QR_CONTAINER)
        return True
    except NoSuchElementException:
        return False

def wait_for_qr_scan(driver, qr_timeout=300):
    logging.info("Waiting for QR scan (auto-refresh every 5 minutes)...")
    timer = time.time()
    while time.time() - timer < qr_timeout:
        if not is_qr_still_visible(driver):
            logging.info("QR container div gone. Assuming QR scanned.")
            return
        time.sleep(1)
    logging.info("QR code expired / not scanned, refreshing page for new QR.")
    driver.refresh()
    time.sleep(5)
    wait_for_qr_scan(driver, qr_timeout)

def get_msg(driver):
    while True:
        try:
            msg_div = driver.find_element(By.CSS_SELECTOR, SELECTOR_NEW_MESSAGE_DIV)
            msg_div.click()
            logging.info("Clicked new message to view.")
            return True
        except NoSuchElementException:
            time.sleep(1)

def copy_qr(driver):
    try:
        qr_canvas = driver.find_element(By.CSS_SELECTOR, SELECTOR_QR_CANVAS)
        qr_base64 = driver.execute_script("""
            var canvas = arguments[0];
            return canvas.toDataURL('image/png').substring('data:image/png;base64,'.length);
        """, qr_canvas)
        return qr_base64
    except NoSuchElementException:
        return None

def main():
    try:
        driver.get("https://web.whatsapp.com")
        logging.info("Navigated to WhatsApp Web.")
        time.sleep(10)
        wait_for_qr_scan(driver)
        take_screenshot(driver)
        logging.info("Polling for new messages...")
        while True:
            get_msg(driver)
            time.sleep(1)
    except Exception as e:
        logging.error(f"Error in WhatsApp automation: {e}", exc_info=True)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
