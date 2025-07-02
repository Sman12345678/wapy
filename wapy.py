from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import os
import time
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
)
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.getLogger().addHandler(file_handler)

# --- Selectors Used ---
SELECTOR_QR_CANVAS = "canvas[aria-label='Scan this QR code to link a device!']"  # QR code canvas
SELECTOR_MAIN_PAGE_DIV = (
    "div.x1c4vz4f.xs83m0k.xdl72j9.x1g77sc7.xeuugli.x2lwn1j.xozqiw3."
    "x1oa3qoh.x12fk4p8.x10l6tqk.xxcbqqu.x1oozmrk"
)
SELECTOR_NEW_MESSAGE_DIV = "div._ahlk"

# --- Chrome driver setup ---
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

def wait_for_qr_scan(driver, qr_timeout=300):
    """
    Wait for the user to scan the QR code.
    If QR is not scanned in qr_timeout seconds, refresh to get a new QR.
    """
    logging.info("Waiting for QR scan (auto-refresh every 2 minutes)...")
    while True:
        timer = time.time()
        while time.time() - timer < qr_timeout:
            try:
                driver.find_element(By.CSS_SELECTOR, SELECTOR_QR_CANVAS)
            except NoSuchElementException:
                logging.info("QR code scanned!")
                return
            time.sleep(1)
        logging.info("QR code expired / not scanned, refreshing page for new QR.")
        driver.refresh()
        time.sleep(5)  # Wait for page to reload

def wait_for_main_page(driver):
    """
    Poll until main page div appears, meaning QR page has been passed.
    """
    logging.info("Polling for main page div (user must scan QR)...")
    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, SELECTOR_MAIN_PAGE_DIV)
            logging.info("Main page detected! QR scan complete.")
            return
        except NoSuchElementException:
            time.sleep(1)

def get_msg(driver):
    """
    Poll every second for new message div and click it to view.
    """
    while True:
        try:
            msg_div = driver.find_element(By.CSS_SELECTOR, SELECTOR_NEW_MESSAGE_DIV)
            msg_div.click()
            logging.info("Clicked new message to view.")
            return True
        except NoSuchElementException:
            time.sleep(1)

def main():
    try:
        driver.get("https://web.whatsapp.com")
        logging.info("Navigated to WhatsApp Web.")

        # 1. Wait for QR scan, refresh every 2 minutes if expired
        wait_for_qr_scan(driver)

        # 2. Wait until user is on the main page (QR scan complete)
        wait_for_main_page(driver)

        # 3. Poll for new messages and click to view
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
