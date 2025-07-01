@app.route("/api/screenshot")
def serve_screenshot_api():
    try:
        screenshot_png = take_screenshot_in_memory(driver)
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
    return render_template("index.html", render_url=RENDER_URL)



if __name__ == '__main__':
    chrome_version = get_binary_version(chrome_bin)
    chromedriver_version = get_binary_version(chromedriver_bin)
    logging.info(f"🧪 Chromium version: {chrome_version}")
    logging.info(f"🧪 Chromedriver version: {chromedriver_version}")
    setup_chatgpt_session()
    logging.info("🚀 Starting Flask app on port 10000")
    app.run(host='0.0.0.0', port=10000, debug=False)
