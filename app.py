from flask import Flask, jsonify, send_file
from wapy import get_driver, take_screenshot  # You already have this setup
from io import BytesIO
import time

app = Flask(__name__)


@app.route("/api/screenshot")
def serve_screenshot_api():
    try:
        screenshot_png = take_screenshot(driver)
        return send_file(
            BytesIO(screenshot_png),
            mimetype="image/png",
            as_attachment=False,
            download_name="screenshot.png"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return jsonify({"hello": "test"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
