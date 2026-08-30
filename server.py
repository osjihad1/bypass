import http.server
import ssl
import json
import threading

# ------------------ HTTP সার্ভার (পোর্ট 80) ------------------
class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        # যেকোনো রিকোয়েস্টে সফল রেসপন্স
        response = {
            "success": True,
            "message": "Login successful",
            "token": "FAKE_TOKEN_FOR_TEST",
            "expires": 1788077395
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        response = {"success": True, "data": {}}
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]} {args[1]}")

# ------------------ HTTPS সার্ভার (পোর্ট 2040) ------------------
class HTTPSHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        response = {
            "success": True,
            "message": "Login successful",
            "token": "FAKE_TOKEN_FOR_TEST",
            "expires": 1788077395
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        response = {"success": True, "data": {}}
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        print(f"[HTTPS] {args[0]} {args[1]}")

# ------------------ SSL সার্টিফিকেট তৈরি (self-signed) ------------------
def generate_self_signed_cert():
    import subprocess, os
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        print("[*] Generating self-signed certificate...")
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", "key.pem", "-out", "cert.pem",
            "-days", "365", "-nodes",
            "-subj", "/CN=new.sensix.shop"
        ], check=True)
        print("[*] Certificate generated.")

# ------------------ মেইন ফাংশন ------------------
def run_http():
    server = http.server.HTTPServer(('0.0.0.0', 80), HTTPHandler)
    print("[*] HTTP server listening on port 80")
    server.serve_forever()

def run_https():
    server = http.server.HTTPServer(('0.0.0.0', 2040), HTTPSHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    server.socket = context.wrap_socket(server.socket, server_side=True)
    print("[*] HTTPS server listening on port 2040")
    server.serve_forever()

if __name__ == "__main__":
    generate_self_signed_cert()   # প্রথমে সার্টিফিকেট তৈরি করবে
    t1 = threading.Thread(target=run_http, daemon=True)
    t2 = threading.Thread(target=run_https, daemon=True)
    t1.start()
    t2.start()
    print("[*] Fake server started. Press Ctrl+C to stop.")
    threading.Event().wait()
