#!/usr/bin/env python3
"""
Simple User Authentication Server
Just username/password login - no API keys
"""

import http.server
import json
import threading
import os
from urllib.parse import urlparse
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import base64

# ==================== DATABASE ====================
class Database:
    def __init__(self):
        self.users = {
            "admin": {
                "id": "usr_001",
                "username": "admin",
                "email": "admin@keyauth.local",
                "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
                "created_at": datetime.now().isoformat()
            }
        }
        self.sessions = {}
        self.token_counter = 1000
    
    def generate_token(self):
        """Generate a simple token"""
        self.token_counter += 1
        payload = {
            "sub": self.token_counter,
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400  # 24 hours
        }
        return base64.b64encode(json.dumps(payload).encode()).decode()

db = Database()

# ==================== UTILITIES ====================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_val):
    return hash_password(password) == hash_val

# ==================== REQUEST HANDLER ====================
class AuthHandler(http.server.BaseHTTPRequestHandler):
    
    def check_bearer_token(self):
        """Verify Bearer token from Authorization header"""
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        # Find session with this token
        for session_id, session_data in db.sessions.items():
            if session_data["token"] == token:
                # Check if session expired
                expires_at = datetime.fromisoformat(session_data["expires_at"])
                if datetime.now() < expires_at:
                    return session_data["user_id"]
        
        return None
    
    def send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_html(self, html, status=200):
        """Send HTML response"""
        self.send_response(status)
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
        
        # Serve index.html
        if path in ['/', '/index', '/index.html']:
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    html = f.read()
            except:
                html = "<h1>KeyAuth Server</h1><p>index.html not found</p>"
            self.send_html(html)
            return
        
        # Get user profile
        if path == '/api/user/profile':
            user_id = self.check_bearer_token()
            if not user_id:
                self.send_json({"error": "Unauthorized"}, 401)
                return
            
            # Find user by ID
            for username, user in db.users.items():
                if user["id"] == user_id:
                    self.send_json({
                        "success": True,
                        "user": {
                            "id": user["id"],
                            "username": user["username"],
                            "email": user["email"],
                            "created_at": user["created_at"]
                        }
                    })
                    return
            
            self.send_json({"error": "User not found"}, 404)
            return
        
        self.send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        body = self.read_body()
        
        # ========== REGISTER NEW USER ==========
        if path == '/api/auth/register':
            username = body.get('username')
            email = body.get('email')
            password = body.get('password')
            
            # Validation
            if not all([username, email, password]):
                self.send_json({"error": "Missing fields"}, 400)
                return
            
            if username in db.users:
                self.send_json({"error": "Username already exists"}, 409)
                return
            
            # Create new user
            user_id = f"usr_{len(db.users) + 1:03d}"
            db.users[username] = {
                "id": user_id,
                "username": username,
                "email": email,
                "password_hash": hash_password(password),
                "created_at": datetime.now().isoformat()
            }
            
            self.send_json({
                "success": True,
                "message": "User registered successfully"
            }, 201)
            print(f"[+] New user registered: {username}")
            return
        
        # ========== LOGIN ==========
        if path == '/api/auth/login':
            username = body.get('username')
            password = body.get('password')
            
            if username not in db.users:
                self.send_json({"error": "Invalid username or password"}, 401)
                return
            
            user = db.users[username]
            if not verify_password(password, user["password_hash"]):
                self.send_json({"error": "Invalid username or password"}, 401)
                return
            
            # Generate token and session
            token = db.generate_token()
            session_id = secrets.token_hex(16)
            db.sessions[session_id] = {
                "user_id": user["id"],
                "username": username,
                "token": token,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            self.send_json({
                "success": True,
                "token": token,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"]
                },
                "expires_in": 86400
            })
            print(f"[+] User logged in: {username}")
            return
        
        self.send_json({"error": "Not Found"}, 404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default logging

# ==================== START SERVER ====================
def run_server():
    try:
        server = http.server.HTTPServer(('0.0.0.0', 80), AuthHandler)
        print("\n" + "="*60)
        print("  🔐 Simple User Authentication Server")
        print("="*60)
        print("\n📚 Default Login:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🌐 Access:")
        print("   http://localhost/")
        print("\n📝 API Endpoints:")
        print("   POST /api/auth/register  - Create new user")
        print("   POST /api/auth/login     - Login user")
        print("   GET  /api/user/profile   - Get user info (needs token)")
        print("\n" + "="*60)
        print("   Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        server.serve_forever()
    except PermissionError:
        print("[!] Error: Need admin privileges for port 80")
        print("   Run as administrator or use a different port")
    except OSError as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    run_server()
