from flask import Flask, jsonify, send_file, render_template
from wapy import get_driver, take_screenshot, main, #copy_qr
from io import BytesIO
import threading

app = Flask(__name__)
driver = get_driver()

# Start WhatsApp automation as a background task
automation_thread = threading.Thread(target=main, daemon=True)
automation_thread.start()

@app.route("/api/screenshot")
def serve_screenshot_api():
    try:
        screenshot_png = take_screenshot(driver,filename)
        return send_file(
            BytesIO(screenshot_png),
            mimetype="image/png",
            as_attachment=False,
            download_name="screenshot.png"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

'''@app.route("/")
def index():
    qr_base64 = copy_qr(driver)
    return render_template('index.html', qr_base64=qr_base64)'''

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
