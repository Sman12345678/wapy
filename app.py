from flask import Flask, jsonify, send_file, render_template
from wapy import get_driver, take_screenshot, main
from io import BytesIO
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
initialize_driver()

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
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
