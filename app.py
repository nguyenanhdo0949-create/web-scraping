"""
app.py — Flask dashboard cho Web Scraping Project
  - Hiển thị dữ liệu sách (Playwright) & quotes (Selenium + Scrapy)
  - REST API: /api/data, /api/stats, /api/run-scraper
  - Export: CSV, JSON
"""
from flask import Flask, render_template, request, jsonify, Response
import csv
import io
import sys
import os
import threading
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database.db import query_unified, count_unified, get_stats, create_db

app = Flask(__name__)

# Ensure DB exists on startup
create_db()

PAGE_SIZE = 20
_scraper_running = False
_scraper_log = []


@app.route("/")
def home():
    keyword    = request.args.get("keyword", "")
    data_type  = request.args.get("data_type", "")
    scraped_by = request.args.get("scraped_by", "")
    page       = int(request.args.get("page", 1))
    offset     = (page - 1) * PAGE_SIZE

    data = query_unified(
        keyword    = keyword    or None,
        data_type  = data_type  or None,
        scraped_by = scraped_by or None,
        limit      = PAGE_SIZE,
        offset     = offset
    )
    total = count_unified(
        keyword    = keyword    or None,
        data_type  = data_type  or None,
        scraped_by = scraped_by or None,
    )
    stats       = get_stats()
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

    return render_template(
        "index.html",
        products    = data,
        stats       = stats,
        keyword     = keyword,
        data_type   = data_type,
        scraped_by  = scraped_by,
        page        = page,
        total_pages = total_pages,
        total       = total,
        scraper_running = _scraper_running,
    )


# ─── API: data ────────────────────────────────────────────────────────────────

@app.route("/api/data")
def api_data():
    keyword    = request.args.get("keyword", "")
    data_type  = request.args.get("data_type", "")
    scraped_by = request.args.get("scraped_by", "")
    page       = int(request.args.get("page", 1))
    offset     = (page - 1) * PAGE_SIZE

    data = query_unified(
        keyword    = keyword    or None,
        data_type  = data_type  or None,
        scraped_by = scraped_by or None,
        limit      = PAGE_SIZE,
        offset     = offset
    )
    total = count_unified(
        keyword    = keyword    or None,
        data_type  = data_type  or None,
        scraped_by = scraped_by or None,
    )

    return jsonify({
        "data":        data,
        "total":       total,
        "page":        page,
        "total_pages": (total + PAGE_SIZE - 1) // PAGE_SIZE
    })


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


# ─── API: trigger scraper ─────────────────────────────────────────────────────

@app.route("/api/run-scraper", methods=["POST"])
def run_scraper():
    """Chạy main.py trong background thread — không block Flask."""
    global _scraper_running, _scraper_log
    if _scraper_running:
        return jsonify({"status": "already_running", "message": "Scraper đang chạy..."}), 409

    _scraper_running = True
    _scraper_log     = []

    def _run():
        global _scraper_running, _scraper_log
        try:
            python_exe = sys.executable
            root       = os.path.dirname(os.path.abspath(__file__))
            proc = subprocess.run(
                [python_exe, "main.py"],
                cwd     = root,
                capture_output = True,
                text    = True,
                timeout = 600
            )
            _scraper_log = (proc.stdout + proc.stderr).splitlines()
        except Exception as e:
            _scraper_log = [f"ERROR: {e}"]
        finally:
            _scraper_running = False

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"status": "started", "message": "Scraper đã được khởi động!"})


@app.route("/api/scraper-status")
def scraper_status():
    return jsonify({
        "running": _scraper_running,
        "log":     _scraper_log[-50:],   # 50 dòng log cuối
    })


# ─── EXPORT ───────────────────────────────────────────────────────────────────

@app.route("/export/csv")
def export_csv():
    keyword    = request.args.get("keyword", "")
    data_type  = request.args.get("data_type", "")
    scraped_by = request.args.get("scraped_by", "")

    data = query_unified(
        keyword    = keyword    or None,
        data_type  = data_type  or None,
        scraped_by = scraped_by or None,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title/Text", "Price/Author", "Rating", "Availability/Tags",
                     "Data Type", "Scraped By", "Created At"])
    for row in data:
        writer.writerow([
            row["id"],
            row["title"],
            row["secondary"],
            row["rating"],
            row["extra"],
            row["data_type"],
            row["scraped_by"],
            row["created_at"],
        ])

    return Response(
        output.getvalue(),
        mimetype = "text/csv",
        headers  = {"Content-Disposition": "attachment; filename=scraped_data.csv"}
    )


@app.route("/export/json")
def export_json():
    keyword    = request.args.get("keyword", "")
    data_type  = request.args.get("data_type", "")
    scraped_by = request.args.get("scraped_by", "")
    data = query_unified(
        keyword    = keyword    or None,
        data_type  = data_type  or None,
        scraped_by = scraped_by or None,
    )
    return jsonify(data)


# ─── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)