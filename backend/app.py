from flask import Flask, jsonify, send_from_directory

from config import BASE_DIR
from database import init_db
from routes.access_event_routes import access_event_bp
from routes.auth_routes import auth_bp
from routes.collaborator_routes import collaborator_bp
from routes.device_routes import device_bp
from routes.monitoring_routes import monitoring_bp
from routes.report_routes import report_bp
import os

frontend_dist_dir = os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist")
app = Flask(__name__, static_folder=frontend_dist_dir, static_url_path="/")

init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(collaborator_bp)
app.register_blueprint(access_event_bp)
app.register_blueprint(device_bp)
app.register_blueprint(monitoring_bp)
app.register_blueprint(report_bp)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
