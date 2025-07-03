from flask import Flask, jsonify, send_file, render_template, redirect, url_for
from wapy import get_driver, take_screenshot, main, get_qr, is_authenticated
from wapy import  find_unread_chats, last_msg, get_unread_msgs
from io import BytesIO
import threading
import logging
from datetime import datetime
import time

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

# Initialize with exact time format
logger.info(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("Current User's Login: Sman12345678")
initialize_driver()

@app.route("/refresh")
def refresh_browser():
    try:
        if not driver:
            logger.error("❌ Driver not initialized")
            return jsonify({"error": "Driver not initialized"}), 500
            
        driver.refresh()
        logger.info("🔄 Browser refreshed")
        time.sleep(10)
        logger.info("⏱️ Waited 10 seconds after refresh")
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"🚨 Refresh error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages")
def get_messages():
    try:
        if not driver:
            return render_template('messages.html', 
                                error="Driver not initialized",
                                current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            
        if not is_authenticated(driver):
            return render_template('messages.html', 
                                error="Please scan QR code first",
                                authenticated=False,
                                current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Use new logic for unread messages
        messages = get_unread_msgs(driver)
        if messages:
            unread_count = len(messages)
            return render_template('messages.html',
                                authenticated=True,
                                unread_count=unread_count,
                                messages=messages,
                                current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            return render_template('messages.html',
                                authenticated=True,
                                error="No unread messages found",
                                current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            
    except Exception as e:
        logger.error(f"Messages error: {e}")
        return render_template('messages.html', 
                            error=str(e),
                            current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))


@app.route("/")
def index():
    try:
        if not driver:
            return render_template('index.html', 
                                error="Driver not initialized",
                                current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            
        qr_base64 = get_qr(driver)
        if qr_base64:
            return render_template('index.html', 
                                qr_base64=qr_base64,
                                current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            return render_template('index.html', 
                                error="QR code not found",
                                current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            
    except Exception as e:
        logger.error(f"Index error: {e}")
        return render_template('index.html', 
                            error=str(e),
                            current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', 
                         current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
