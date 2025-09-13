# data_forwarder.py
import requests
import time
import argparse
from data_gen import record_stream

def forward(url="http://localhost:5000/api/ingest", delay_range=(0.5,2)):
    for rec in record_stream(delay_range=delay_range):
        try:
            r = requests.post(url, json=rec, timeout=5)
            print("sent", rec["category"], rec["points"], "->", r.status_code)
        except Exception as e:
            print("failed to send:", e)
            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:5000/api/ingest")
    args = parser.parse_args()
    forward(args.url)
