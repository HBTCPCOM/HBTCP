#!/usr/bin/env python3
"""Local-only subscription + SOCKS fixture for an Android emulator VPN path check."""
import base64
import json
import socketserver
import struct
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote

records = []
lock = threading.Lock()

def receive(sock, count):
    result = b""
    while len(result) < count:
        chunk = sock.recv(count - len(result))
        if not chunk:
            raise EOFError()
        result += chunk
    return result

class Socks(socketserver.BaseRequestHandler):
    def handle(self):
        sock = self.request
        sock.settimeout(15)
        try:
            version, count = receive(sock, 2)
            if version != 5:
                return
            receive(sock, count)
            sock.sendall(b"\x05\x00")
            version, command, _, kind = receive(sock, 4)
            if kind == 1:
                host = ".".join(str(value) for value in receive(sock, 4))
            elif kind == 3:
                host = receive(sock, receive(sock, 1)[0]).decode()
            elif kind == 4:
                host = receive(sock, 16).hex()
            else:
                return
            port = struct.unpack("!H", receive(sock, 2))[0]
            if command != 1 or host != "1.1.1.1" or port != 80:
                sock.sendall(b"\x05\x02\x00\x01\x00\x00\x00\x00\x00\x00")
                return
            sock.sendall(b"\x05\x00\x00\x01\x7f\x00\x00\x01\x00\x00")
            request = b""
            while b"\r\n\r\n" not in request and len(request) < 8192:
                chunk = sock.recv(1024)
                if not chunk:
                    return
                request += chunk
            marker = f"HUBAN_VPN_OK_NODE_{self.server.marker}\n".encode()
            sock.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\nContent-Length: " + str(len(marker)).encode() + b"\r\n\r\n" + marker)
            with lock:
                records.append({"node": self.server.marker, "host": host, "port": port})
            print(json.dumps({"verified_vpn_request": self.server.marker}), flush=True)
        except (EOFError, TimeoutError, OSError):
            pass

class ThreadingSocks(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

class Subscription(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/subscription":
            nodes = "\n".join(f"socks://10.0.2.2:{port}#{quote('虎斑验证节点-' + name)}" for port, name in [(19080, "A"), (19081, "B")])
            payload = base64.b64encode(nodes.encode())
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("profile-title", "Huban QA")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif self.path == "/results":
            with lock:
                payload = json.dumps(records).encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_error(404)

    def log_message(self, *_):
        pass

if __name__ == "__main__":
    for port, marker in [(19080, "A"), (19081, "B")]:
        server = ThreadingSocks(("127.0.0.1", port), Socks)
        server.marker = marker
        threading.Thread(target=server.serve_forever, daemon=True).start()
    print("Local QA fixture: HTTP 18765, SOCKS 19080 / 19081", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 18765), Subscription).serve_forever()
