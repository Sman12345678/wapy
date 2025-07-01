from flask import Flask, jsonify, request, send_file, render_template
from wapy import take_screenshot, binary_version, chrome_bin, chromedriver_bin, get_driver
from wapy import main
from io import ByteIO

driver = get_driver()
app = Flask(__name__)

@app.route("/api/screenshot")
def serve_screenshot_api():
    try:
        screenshot_png = take_screenshot(driver)
        logging.info("✅ Screenshot served as PNG.")
        return send_file(
            BytesIO(screenshot_png),
            mimetype="image/png",
            as_attachment=False,
            download_name="screenshot.png"
        )
    except Exception as e:
        logging.error("❌ Failed to serve screenshot", exc_info=True)
        return jsonify({"error": str(e)}), 500
@app.route("/")
def index():
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    return jsonify({"hello":"test"})



if __name__ == '__main__':
    chrome_version = binary_version(chrome_bin)
    chromedriver_version = binary_version(chromedriver_bin)
    logging.info(f"🧪 Chromium version: {chrome_version}")
    logging.info(f"🧪 Chromedriver version: {chromedriver_version}")
    logging.info("🚀 Starting Flask app on port 10000")
    main()
    app.run(host='0.0.0.0', port=10000, debug=False)
