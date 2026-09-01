import http.server
import ssl
import json
import threading
import os
from urllib.parse import urlparse, parse_qs
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import base64

# ==================== DATABASE (In-Memory) ====================
class Database:
    def __init__(self):
        self.users = {
            "admin": {
                "id": "usr_001",
                "username": "admin",
                "email": "admin@keyauth.local",
                "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
                "created_at": datetime.now().isoformat(),
                "role": "admin",
                "active": True,
                "verified": True
            }
        }
        self.api_keys = {
            "test_key_12345": {
                "id": "key_001",
                "user_id": "usr_001",
                "key": "test_key_12345",
                "name": "Test Key",
                "active": True,
                "created_at": datetime.now().isoformat(),
                "last_used": None,
                "rate_limit": 1000,
                "usage_count": 0,
                "permissions": ["read", "write"]
            },
            "demo_key_67890": {
                "id": "key_002",
                "user_id": "usr_001",
                "key": "demo_key_67890",
                "name": "Demo Key",
                "active": True,
                "created_at": datetime.now().isoformat(),
                "last_used": None,
                "rate_limit": 500,
                "usage_count": 0,
                "permissions": ["read"]
            }
        }
        self.sessions = {}
        self.request_logs = []
        self.request_counter = 0
        self.token_counter = 1000
    
    def log_request(self, api_key, endpoint, method, status, ip):
        self.request_counter += 1
        log_entry = {
            "id": f"req_{self.request_counter:06d}",
            "api_key": api_key[:8] + "***" if api_key else "NO_KEY",
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "ip": ip,
            "timestamp": datetime.now().isoformat()
        }
        self.request_logs.append(log_entry)
        if len(self.request_logs) > 10000:
            self.request_logs = self.request_logs[-10000:]
        return log_entry
    
    def get_user_stats(self, user_id):
        keys = [k for k in self.api_keys.values() if k["user_id"] == user_id]
        total_requests = sum([k["usage_count"] for k in keys])
        return {
            "total_keys": len(keys),
            "active_keys": sum([1 for k in keys if k["active"]]),
            "total_requests": total_requests,
            "request_logs_count": len(self.request_logs)
        }

db = Database()

# ==================== AUTH & UTILITIES ====================
def generate_api_key():
    """Generate a random API key"""
    return "key_" + secrets.token_hex(16)

def generate_token():
    """Generate JWT-like token"""
    db.token_counter += 1
    payload = {
        "sub": db.token_counter,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_val):
    return hash_password(password) == hash_val

# ==================== REQUEST HANDLER ====================
class KeyAuthHandler(http.server.BaseHTTPRequestHandler):
    
    def check_api_key(self):
        """Verify API key from header"""
        api_key = self.headers.get('X-API-Key')
        if not api_key:
            return None
        
        key_data = db.api_keys.get(api_key)
        if not key_data or not key_data["active"]:
            return None
        
        # Check rate limit
        if key_data["usage_count"] >= key_data["rate_limit"]:
            return None
        
        # Update usage
        key_data["usage_count"] += 1
        key_data["last_used"] = datetime.now().isoformat()
        
        return key_data
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_html_response(self, html, status_code=200):
        """Send HTML response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def read_body(self):
        """Read JSON request body"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            return json.loads(body) if body else {}
        except:
            return {}

    def do_GET(self):
        path = urlparse(self.path).path
        
        # Index page
        if path in ['/', '/index', '/index.html']:
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    html = f.read()
            except:
                html = "<h1>KeyAuth Server</h1><p>index.html not found</p>"
            self.send_html_response(html)
            db.log_request(None, path, 'GET', 200, self.client_address[0])
            return
        
        # API: Get stats
        if path == '/api/stats':
            key_data = self.check_api_key()
            if not key_data:
                db.log_request(None, path, 'GET', 401, self.client_address[0])
                self.send_json_response({"error": "Unauthorized"}, 401)
                return
            
            stats = db.get_user_stats(key_data["user_id"])
            response = {
                "success": True,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
            db.log_request(key_data["key"], path, 'GET', 200, self.client_address[0])
            self.send_json_response(response)
            return
        
        # API: Get request logs
        if path == '/api/logs':
            key_data = self.check_api_key()
            if not key_data:
                db.log_request(None, path, 'GET', 401, self.client_address[0])
                self.send_json_response({"error": "Unauthorized"}, 401)
                return
            
            limit = 100
            logs = db.request_logs[-limit:]
            response = {
                "success": True,
                "logs": logs,
                "total": len(db.request_logs)
            }
            db.log_request(key_data["key"], path, 'GET', 200, self.client_address[0])
            self.send_json_response(response)
            return
        
        # API: Get API keys
        if path == '/api/keys':
            key_data = self.check_api_key()
            if not key_data:
                db.log_request(None, path, 'GET', 401, self.client_address[0])
                self.send_json_response({"error": "Unauthorized"}, 401)
                return
            
            user_keys = [k for k in db.api_keys.values() if k["user_id"] == key_data["user_id"]]
            # Hide full key in response
            for k in user_keys:
                k["key"] = k["key"][:8] + "***" + k["key"][-4:]
            
            response = {
                "success": True,
                "keys": user_keys
            }
            db.log_request(key_data["key"], path, 'GET', 200, self.client_address[0])
            self.send_json_response(response)
            return
        
        # Protected GET endpoints
        if path == '/api/data':
            key_data = self.check_api_key()
            if not key_data:
                db.log_request(None, path, 'GET', 401, self.client_address[0])
                self.send_json_response({"error": "Unauthorized"}, 401)
                return
            
            response = {
                "success": True,
                "data": {
                    "users": 15420,
                    "posts": 234890,
                    "comments": 892340,
                    "active_sessions": 1203
                },
                "timestamp": datetime.now().isoformat()
            }
            db.log_request(key_data["key"], path, 'GET', 200, self.client_address[0])
            self.send_json_response(response)
            return
        
        if path == '/api/user/profile':
            key_data = self.check_api_key()
            if not key_data:
                db.log_request(None, path, 'GET', 401, self.client_address[0])
                self.send_json_response({"error": "Unauthorized"}, 401)
                return
            
            user = db.users[next(u for u, v in db.users.items() if v["id"] == key_data["user_id"])]
            response = {
                "success": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "created_at": user["created_at"]
                }
            }
            db.log_request(key_data["key"], path, 'GET', 200, self.client_address[0])
            self.send_json_response(response)
            return
        
        db.log_request(None, path, 'GET', 404, self.client_address[0])
        self.send_json_response({"error": "Not Found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        body = self.read_body()
        
        # User registration
        if path == '/api/auth/register':
            username = body.get('username')
            email = body.get('email')
            password = body.get('password')
            
            if not all([username, email, password]):
                db.log_request(None, path, 'POST', 400, self.client_address[0])
                self.send_json_response({"error": "Missing fields"}, 400)
                return
            
            if username in db.users:
                db.log_request(None, path, 'POST', 409, self.client_address[0])
                self.send_json_response({"error": "User already exists"}, 409)
                return
            
            user_id = f"usr_{len(db.users) + 1:03d}"
            db.users[username] = {
                "id": user_id,
                "username": username,
                "email": email,
                "password_hash": hash_password(password),
                "created_at": datetime.now().isoformat(),
                "role": "user",
                "active": True,
                "verified": False
            }
            
            response = {
                "success": True,
                "message": "User registered successfully",
                "user_id": user_id
            }
            db.log_request(None, path, 'POST', 201, self.client_address[0])
            self.send_json_response(response, 201)
            return
        
        # User login
        if path == '/api/auth/login':
            username = body.get('username')
            password = body.get('password')
            
            if username not in db.users:
                db.log_request(None, path, 'POST', 401, self.client_address[0])
                self.send_json_response({"error": "Invalid credentials"}, 401)
                return
            
            user = db.users[username]
            if not verify_password(password, user["password_hash"]):
                db.log_request(None, path, 'POST', 401, self.client_address[0])
                self.send_json_response({"error": "Invalid credentials"}, 401)
                return
            
            token = generate_token()
            session_id = secrets.token_hex(16)
            db.sessions[session_id] = {
                "user_id": user["id"],
                "token": token,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            response = {
                "success": True,
                "token": token,
                "session_id": session_id,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"]
                },
                "expires_in": 86400
            }
            db.log_request(None, path, 'POST', 200, self.client_address[0])
            self.send_json_response(response)
            return
        
        # Create new API key
        if path == '/api/keys/create':
            key_data = self.check_api_key()
            if not key_data:
                db.log_request(None, path, 'POST', 401, self.client_address[0])
                self.send_json_response({"error": "Unauthorized"}, 401)
                return
            
            key_name = body.get('name', 'New Key')
            rate_limit = body.get('rate_limit', 1000)
            
            new_key = generate_api_key()
            key_id = f"key_{len(db.api_keys) + 1:03d}"
            db.api_keys[new_key] = {
                "id": key_id,
                "user_id": key_data["user_id"],
                "key": new_key,
                "name": key_name,
                "active": True,
                "created_at": datetime.now().isoformat(),
                "last_used": None,
                "rate_limit": rate_limit,
                "usage_count": 0,
                "permissions": ["read", "write"]
            }
            
            response = {
                "success": True,
                "message": "API key created",
                "key": new_key,
                "key_id": key_id
            }
            db.log_request(key_data["key"], path, 'POST', 201, self.client_address[0])
            self.send_json_response(response, 201)
            return
        
        # Revoke API key
        if path == '/api/keys/revoke':
            key_data = self.check_api_key()
            if not key_data:
                db.log_request(None, path, 'POST', 401, self.client_address[0])
                self.send_json_response({"error": "Unauthorized"}, 401)
                return
            
            key_to_revoke = body.get('key')
            if key_to_revoke not in db.api_keys:
                db.log_request(None, path, 'POST', 404, self.client_address[0])
                self.send_json_response({"error": "Key not found"}, 404)
                return
            
            db.api_keys[key_to_revoke]["active"] = False
            response = {
                "success": True,
                "message": "API key revoked"
            }
            db.log_request(key_data["key"], path, 'POST', 200, self.client_address[0])
            self.send_json_response(response)
            return
        
        # Generic API endpoint
        if path == '/api/data':
            key_data = self.check_api_key()
            if not key_data:
                db.log_request(None, path, 'POST', 401, self.client_address[0])
                self.send_json_response({"error": "Unauthorized"}, 401)
                return
            
            response = {
                "success": True,
                "message": "Data processed",
                "request_id": secrets.token_hex(8),
                "timestamp": datetime.now().isoformat()
            }
            db.log_request(key_data["key"], path, 'POST', 200, self.client_address[0])
            self.send_json_response(response)
            return
        
        db.log_request(None, path, 'POST', 404, self.client_address[0])
        self.send_json_response({"error": "Not Found"}, 404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Authorization')
        self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass

# ==================== HTTPS HANDLER ====================
class HTTPSKeyAuthHandler(KeyAuthHandler):
    pass

# ==================== SSL CERTIFICATE ====================
def generate_self_signed_cert():
    import subprocess
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        print("[*] Generating self-signed certificate...")
        try:
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:2048",
                "-keyout", "key.pem", "-out", "cert.pem",
                "-days", "365", "-nodes",
                "-subj", "/CN=keyauth.local"
            ], check=True)
            print("[✓] Certificate generated")
        except FileNotFoundError:
            print("[!] OpenSSL not found")
            return False
        except Exception as e:
            print(f"[!] Error: {e}")
            return False
    return True

# ==================== SERVER THREADS ====================
def run_http():
    try:
        server = http.server.HTTPServer(('0.0.0.0', 80), KeyAuthHandler)
        print("[✓] HTTP Server listening on port 80")
        server.serve_forever()
    except PermissionError:
        print("[!] Error: Admin privileges required for port 80")
    except Exception as e:
        print(f"[!] HTTP Error: {e}")

def run_https():
    try:
        if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
            print("[!] SSL certificates not found. Skipping HTTPS...")
            return
        
        server = http.server.HTTPServer(('0.0.0.0', 2040), HTTPSKeyAuthHandler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('cert.pem', 'key.pem')
        server.socket = context.wrap_socket(server.socket, server_side=True)
        print("[✓] HTTPS Server listening on port 2040")
        server.serve_forever()
    except Exception as e:
        print(f"[!] HTTPS Error: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🔐 KeyAuth Server - Professional API Management")
    print("=" * 60 + "\n")
    
    generate_self_signed_cert()
    
    t1 = threading.Thread(target=run_http, daemon=True)
    t2 = threading.Thread(target=run_https, daemon=True)
    t1.start()
    t2.start()
    
    print("\n📚 Default Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    
    print("\n🔑 Test API Keys:")
    for key_id, key_data in list(db.api_keys.items())[:2]:
        print(f"   • {key_id} ({key_data['name']})")
    
    print("\n🌐 Access Points:")
    print("   • HTTP:  http://localhost/")
    print("   • HTTPS: https://localhost:2040/")
    
    print("\n" + "=" * 60)
    print("  Press Ctrl+C to stop\n")
    
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")

