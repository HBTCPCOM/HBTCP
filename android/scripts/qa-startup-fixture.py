#!/usr/bin/env python3
"""Mutable local subscription for startup refresh and active-node replacement checks."""
from pathlib import Path
import base64
import importlib.util
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote

spec = importlib.util.spec_from_file_location("network_fixture", Path(__file__).with_name("qa-network-fixture.py"))
network = importlib.util.module_from_spec(spec)
spec.loader.exec_module(network)
phase = "initial"
requests = []

class Subscription(BaseHTTPRequestHandler):
    def do_POST(self):
        global phase
        phase = json.loads(self.rfile.read(int(self.headers["Content-Length"])))['phase']
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == "/results":
            payload = json.dumps({"phase": phase, "requests": requests, "socks": network.records}).encode()
        elif self.path == "/subscription":
            requests.append({"phase": phase})
            print("subscription requested: " + phase, flush=True)
            if phase == "failure":
                self.send_error(503)
                return
            if phase == "invalid":
                payload = b"not a valid subscription"
            else:
                nodes = [(19080, "A"), (19081, "B")] if phase == "initial" else [(19081, "A"), (19080, "C")]
                payload = base64.b64encode("\n".join(f"socks://10.0.2.2:{port}#{quote('虎斑验证节点-' + name)}" for port, name in nodes).encode())
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_):
        pass

if __name__ == "__main__":
    for port, marker in [(19080, "A"), (19081, "B")]:
        server = network.ThreadingSocks(("127.0.0.1", port), network.Socks)
        server.marker = marker
        threading.Thread(target=server.serve_forever, daemon=True).start()
    print("Mutable startup QA fixture ready", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 18765), Subscription).serve_forever()
