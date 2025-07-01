from flask import Flask, jsonify, send_file
from wapy import take_screenshot, get_driver
from io import BytesIO

app = Flask(__name__)

# Step 1: Start the browser and go to the WhatsApp Web page
driver = get_driver()
driver.get("https://web.whatsapp.com")

@app.route("/api/screenshot")
def serve_screenshot_api():
    try:
        # Step 2: Take a screenshot of the current page
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
    app.run(host='0.0.0.0', port=10000, debug=False)
