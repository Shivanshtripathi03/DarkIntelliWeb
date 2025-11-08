from flask import Flask, jsonify, request, g
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "darkintelliweb.db")

app = Flask(__name__)

def get_db():
    # open a new connection per request
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# Simple CORS for local dev (adjust for production)
@app.after_request
def add_cors_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

# Home page (same as before)
@app.route("/")
def home():
    return "<h2>DarkIntelliWeb Dashboard Running Successfully 🚀</h2>"

# Return all scans
@app.route("/api/scans", methods=["GET"])
def api_scans():
    db = get_db()
    cur = db.execute("SELECT id, url, status, threatLevel, timestamp FROM scans ORDER BY id DESC")
    rows = cur.fetchall()
    scans = [dict(r) for r in rows]
    return jsonify({"scans": scans})

# Return all AI queries
@app.route("/api/queries", methods=["GET"])
def api_queries():
    db = get_db()
    cur = db.execute("SELECT id, query, answer, timestamp FROM queries ORDER BY id DESC")
    rows = cur.fetchall()
    queries = [dict(r) for r in rows]
    return jsonify({"queries": queries})

# Insert a new scan (used by frontend when scanning)
@app.route("/api/scan", methods=["POST"])
def api_insert_scan():
    data = request.get_json(force=True)
    url = data.get("url")
    status = data.get("status", "")
    threatLevel = data.get("threatLevel", "")
    if not url:
        return jsonify({"error": "url is required"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO scans (url, status, threatLevel, timestamp) VALUES (?, ?, ?, datetime('now'))",
        (url, status, threatLevel),
    )
    db.commit()
    new_id = cur.lastrowid
    return jsonify({"id": new_id, "url": url, "status": status, "threatLevel": threatLevel}), 201

# Insert a new AI query/answer pair
@app.route("/api/query", methods=["POST"])
def api_insert_query():
    data = request.get_json(force=True)
    query_text = data.get("query")
    answer = data.get("answer", "")
    if not query_text:
        return jsonify({"error": "query is required"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO queries (query, answer, timestamp) VALUES (?, ?, datetime('now'))",
        (query_text, answer),
    )
    db.commit()
    new_id = cur.lastrowid
    return jsonify({"id": new_id, "query": query_text, "answer": answer}), 201

if __name__ == "__main__":
    # Run on all interfaces for local network testing (same as before)
    app.run(host="0.0.0.0", port=5000, debug=True)
