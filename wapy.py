
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
import os
import traceback
import time
import logging
import base64


# Set up logging
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

def take_screenshot(driver):
    try:
        logging.info("📸 Calculating full page height for screenshot")

        # Get the actual page height
        total_height = driver.execute_script("""
            return Math.max(
                document.body.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.clientHeight,
                document.documentElement.scrollHeight,
                document.documentElement.offsetHeight
            );
        """)
        
        # Add some buffer (e.g., 200px) to capture any floating elements
        total_height += 200
        
        # Set viewport to match document height
        viewport_width = driver.execute_script("return window.innerWidth")
        driver.set_window_size(viewport_width, total_height)
        
        # Wait longer for layout to settle
        time.sleep(3)
        
        screenshot_data = driver.execute_cdp_cmd("Page.captureScreenshot", {
            "format": "png",
            "fromSurface": True,
            "captureBeyondViewport": True,
            "clip": {
                "width": viewport_width,
                "height": total_height,
                "x": 0,
                "y": 0,
                "scale": 1
            }
        })

        screenshot_png = base64.b64decode(screenshot_data["data"])
        logging.info(f"✅ Screenshot captured ({viewport_width}x{total_height}px)")
        return screenshot_png
    except Exception as e:
        logging.error("❌ Screenshot capture failed", exc_info=True)
        raise
def binary_version(binary_path):
    try:
        result = subprocess.run([binary_path, "--version"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"❌ Could not determine version for {binary_path}", exc_info=True)
        return f"Could not determine version: {e}"

def main():
    from selenium.common.exceptions import NoSuchElementException
    driver = get_driver()
    try:
        driver.get("https://web.whatsapp.com")
        logging.info("Navigated to WhatsApp Web. Waiting for QR scan...")

        # Your new QR code container class (use dot for each class)
        qr_check_class = (
            ".x1c4vz4f.xs83m0k.xdl72j9.x1g77sc7.xeuugli.x2lwn1j.xozqiw3.xamitd3."
            "x7v7x1q.xy296fx.xbl0rts.x4i7bpe.x15zmtp0.x1sgudl8.x1oiqv2n.x1rsuxf0."
            "xcgujcq.x1igtfuo.x13up0n2.x178xt8z.x1lun4ml.xso031l.xpilrb4.x13fuv20."
            "x18b5jzi.x1q0q8m5.x1t7ytsu.xpypsur.x1fe0zbt.x249io5.xtq6bvn.x12peec7."
            "x91od0.xvl3i4w.xfqsd3n.xzg3blf.x191sbug"
        )
        # The button you want to click after QR is scanned (use dot for each class)
        button_class = (
            ".x1c4vz4f.xs83m0k.xdl72j9.x1g77sc7.x78zum5.xozqiw3.x1oa3qoh.x12fk4p8."
            "x3pnbk8.xfex06f.xeuugli.x2lwn1j.xl56j7k.x1q0g3np.x6s0dn4"
        )

        while True:
            try:
                # Try to find the QR element
                qr_elements = driver.find_elements(By.CSS_SELECTOR, qr_check_class)
                if qr_elements:
                    logging.info("QR code still present, waiting and refreshing...")
                    time.sleep(15)
                    driver.refresh()
                else:
                    logging.info("QR code likely scanned. Checking for button to click...")
                    try:
                        button = driver.find_element(By.CSS_SELECTOR, button_class)
                        button.click()
                        logging.info("Button clicked after QR scan!")
                    except NoSuchElementException:
                        logging.info("Button with the specified class not found. Proceeding...")
                    break
            except Exception as e:
                logging.error("Unexpected error during QR scan check.", exc_info=True)
                break

        # Optionally, proceed with further automation or screenshot
        take_screenshot(driver)
        logging.info("Screenshot taken after QR scan.")
    finally:
        driver.quit()
