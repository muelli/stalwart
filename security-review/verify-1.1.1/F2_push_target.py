#!/usr/bin/env python3
"""Lab push target for F2. Answers every POST with HTTP 500 and a large body.
Usage: push_target.py <bind_ip> <port> <cert> <key> [size_mib]
Logs each request's path, Content-Length and bytes sent. Run only on your own host."""
import http.server, ssl, sys, time
bind, port, cert, key = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
size = int(sys.argv[5]) * 1024 * 1024 if len(sys.argv) > 5 else 256 * 1024 * 1024
chunk = b"E" * (1024 * 1024)
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(n) if n else b""
        print(f"{time.strftime('%H:%M:%S')} POST {self.path} from {self.client_address[0]} req_len={n} -> 500 with {size} bytes", flush=True)
        self.send_response(500)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(size))
        self.end_headers()
        sent = 0
        try:
            while sent < size:
                self.wfile.write(chunk[: min(len(chunk), size - sent)])
                sent += min(len(chunk), size - sent)
        except (BrokenPipeError, ConnectionResetError):
            pass
        print(f"{time.strftime('%H:%M:%S')} sent {sent} bytes", flush=True)
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer((bind, port), H)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(cert, key)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
print(f"listening https://{bind}:{port}", flush=True)
srv.serve_forever()
