from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

@app.post("/api/scan")
def scan():
    data = request.get_json(force=True) or {}
    url = data.get("url", "")
    status = data.get("status", "safe")
    threat = data.get("threatLevel", "Safe")
    return jsonify({
        "id": int(time.time()*1000),
        "url": url,
        "status": status,
        "threatLevel": threat
    })

@app.post("/api/query")
def query():
    q = (request.get_json(force=True) or {}).get("query", "")
    return jsonify({"answer": f"Stub: you asked '{q}'"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

