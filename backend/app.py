# app.py
import sqlite3
import time
import json
from datetime import datetime, timezone
from threading import Lock
from queue import Queue, Empty
from flask import Flask, request, jsonify, stream_with_context, Response
from flask_cors import CORS

DB_PATH = "hogwarts.db"
HOUSES = ["Gryff", "Slyth", "Raven", "Huff"]

app = Flask(__name__)
CORS(app)
db_lock = Lock()

clients = []
clients_lock = Lock()


def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                category TEXT,
                points INTEGER,
                ts INTEGER
            )
        ''')
        conn.commit()
        conn.close()


def insert_event(ev: dict):
    ts_iso = ev.get("timestamp")
    dt = datetime.fromisoformat(ts_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    epoch = int(dt.timestamp())
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO events (id, category, points, ts) VALUES (?, ?, ?, ?)',
                      (ev["id"], ev["category"], int(ev["points"]), epoch))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()


def totals_since(epoch_from: int):
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if epoch_from is None:
            c.execute('SELECT category, SUM(points) FROM events GROUP BY category')
        else:
            c.execute('SELECT category, SUM(points) FROM events WHERE ts >= ? GROUP BY category', (epoch_from,))
        rows = c.fetchall()
        conn.close()
    res = {h: 0 for h in HOUSES}
    for cat, s in rows:
        if cat in res:
            res[cat] = s or 0
    return res


@app.route("/api/ingest", methods=["POST"])
def ingest():
    data = request.get_json(force=True)
    if not data or "id" not in data or "category" not in data or "points" not in data or "timestamp" not in data:
        return jsonify({"error": "invalid payload"}), 400

    insert_event(data)

    payload = json.dumps(data)
    with clients_lock:
        for q in list(clients):
            try:
                q.put(payload, block=False)
            except Exception:
                pass

    return jsonify({"status": "ok"}), 201


@app.route("/api/totals")
def api_totals():
    window = request.args.get("window", "all")
    now = int(datetime.now(timezone.utc).timestamp())
    epoch_from = None
    if window == "5m":
        epoch_from = now - 5 * 60
    elif window == "1h":
        epoch_from = now - 60 * 60
    elif window == "all":
        epoch_from = None
    else:
        return jsonify({"error": "window must be one of 5m|1h|all"}), 400

    res = totals_since(epoch_from)
    return jsonify({"totals": res})


def sse_format(event_str: str):
    return f"data: {event_str}\n\n"


@app.route("/stream")
def stream():
    def gen():
        q = Queue()
        with clients_lock:
            clients.append(q)
        try:
            last_keep = time.time()
            while True:
                try:
                    payload = q.get(timeout=1.0)
                    yield sse_format(payload)
                except Empty:
                    if time.time() - last_keep > 15:
                        last_keep = time.time()
                        yield ": keep-alive\n\n"
        finally:
            with clients_lock:
                try:
                    clients.remove(q)
                except ValueError:
                    pass

    return Response(stream_with_context(gen()), mimetype="text/event-stream")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
