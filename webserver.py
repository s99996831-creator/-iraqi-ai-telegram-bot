import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/health'):
            body = b'OK'
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

def start_health_server():
    port = int(os.getenv('PORT', '10000'))
    server = ThreadingHTTPServer(('0.0.0.0', port), HealthHandler)
    print(f'Health server listening on port {port}')
    server.serve_forever()
