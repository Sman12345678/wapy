from flask import Flask, jsonify, send_file, render_template
from wapy import get_driver, take_screenshot, main, get_qr
from io import BytesIO
import threading
import logging
from datetime import datetime

# Set up logging
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(EmojiFormatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.handlers = [handler]

app = Flask(__name__)
driver = None

def initialize_driver():
    global driver
    driver = main()
    if driver:
        logger.info("✨ Driver initialized successfully")
    else:
        logger.error("❌ Failed to initialize driver")

# Initialize the driver when starting the app
logger.info(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("Current User's Login: Sman12345678")
initialize_driver()

@app.route("/")
def index():
    try:
        if not driver:
            return render_template('index.html', error="Driver not initialized")
            
        qr_base64 = get_qr(driver)
        if qr_base64:
            return render_template('index.html', qr_base64=qr_base64)
        else:
            return render_template('index.html', error="QR code not found")
            
    except Exception as e:
        logger.error(f"Index error: {e}")
        return render_template('index.html', error=str(e))

@app.route("/api/screenshot")
def serve_screenshot_api():
    try:
        if not driver:
            return jsonify({"error": "Driver not initialized"}), 500
            
        screenshot_png = take_screenshot(driver)
        return send_file(
            BytesIO(screenshot_png),
            mimetype="image/png",
            as_attachment=False,
            download_name="screenshot.png"
        )
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/refresh")
def refresh_browser():
    try:
        if not driver:
            logger.error("❌ Driver not initialized")
            return jsonify({"error": "Driver not initialized"}), 500
            
        # Refresh the browser
        driver.refresh()
        logger.info("🔄 Browser refreshed")
        
        # Wait for page to load
        time.sleep(10)
        logger.info("⏱️ Waited 10 seconds after refresh")
        
        # Redirect back to index
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"🚨 Refresh error: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
