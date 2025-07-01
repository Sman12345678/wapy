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

driver = get_driver()

def take_screenshot(driver):
    return driver.get_screenshot_as_png()

#def binary_version(binary_path):
#    try:
#        result = subprocess.run([binary_path, "--version"], capture_output=True, text=True, check=True)
#        return result.stdout.strip()
 #   except Exception as e:
 #       logging.error(f"❌ Could not determine version for {binary_path}", exc_info=True)
  #      return f"Could not determine version: {e}"

def main():
    try:
        driver.get("https://web.whatsapp.com")
        logging.info("Navigated to WhatsApp Web. Waiting for QR scan...")
        time.sleep(10)
        take_screenshot(driver)
        

       
