import os
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

def start_web_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hunter Bot ONLINE")
        def log_message(self, format, *args):
            return
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

Thread(target=start_web_server, daemon=True).start()
print("Hunter no ar!")
while True:
    time.sleep(60)
