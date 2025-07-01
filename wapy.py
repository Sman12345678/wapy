from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
import os
import time
import logging
import base64

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.getLogger().addHandler(file_handler)

ADMIN_CODE = "ICU14CU"

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"

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

def take_screenshot(driver, filename):
    logging.info("📸 Forcing giant viewport for full screenshot")
    driver.set_window_size(1920, 5000)
    time.sleep(1)
    screenshot_data = driver.execute_cdp_cmd("Page.captureScreenshot", {
        "format": "png",
        "fromSurface": True,
        "captureBeyondViewport": True
    })
    screenshot_png = base64.b64decode(screenshot_data["data"])
    with open(filename, "wb") as f:
        f.write(screenshot_png)
    logging.info(f"✅ Screenshot saved as {filename}")
    return screenshot_png

def binary_version(binary_path):
    try:
        result = subprocess.run([binary_path, "--version"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"❌ Could not determine version for {binary_path}", exc_info=True)
        return f"Could not determine version: {e}"

def css_selector_from_classes(class_list):
    return "." + ".".join(class_list)

def main():
    driver = get_driver()
    try:
        driver.get("https://web.whatsapp.com")
        logging.info("Navigated to WhatsApp Web. Waiting for QR scan...")

        qr_classes = ["x1lliihq"]
        login_alt_classes = [
            "x1c4vz4f", "xs83m0k", "xdl72j9", "x1g77sc7", "x78zum5", "xozqiw3",
            "x1oa3qoh", "x12fk4p8", "xeuugli", "x2lwn1j", "x1nhvcw1", "xdt5ytf", "x1cy8zhl"
        ]
        login_alt_text = "Log in with phone number"

        qr_selector = css_selector_from_classes(qr_classes)
        login_alt_selector = css_selector_from_classes(login_alt_classes)

        qr_screenshot_taken = False

        while True:
            qr_present = False
            login_alt_present = False

            qr_elements = driver.find_elements(By.CSS_SELECTOR, qr_selector)
            if qr_elements:
                qr_present = True
                if not qr_screenshot_taken:
                    take_screenshot(driver, "wa_qr.png")
                    qr_screenshot_taken = True

            login_alt_elements = driver.find_elements(By.CSS_SELECTOR, login_alt_selector)
            for el in login_alt_elements:
                if el.text.strip() == login_alt_text:
                    login_alt_present = True
                    break

            if qr_present or login_alt_present:
                logging.info("QR code or login alternative still present, waiting and refreshing...")
                time.sleep(15)
                driver.refresh()
            else:
                logging.info("QR has been scanned. Proceeding...")
                break

        take_screenshot(driver, "wa_after_login.png")
        logging.info("Screenshot taken after QR scan.")
    finally:
        driver.quit()
