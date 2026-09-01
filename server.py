<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KeyAuth Server - User Authentication System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 28px; color: #667eea; }
        .user-info {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .user-name {
            font-weight: 600;
            color: #333;
            padding: 10px 15px;
            background: #f0f0f0;
            border-radius: 5px;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .btn-small {
            padding: 6px 12px;
            font-size: 11px;
            margin: 0;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h2 {
            font-size: 18px;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 13px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .alert {
            padding: 12px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 12px;
        }
        .alert-success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .alert-error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .section { display: none; }
        .section.active { display: block; }
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            background: #d4edda;
            color: #155724;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        .table th {
            background: #f5f5f5;
            padding: 10px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            color: #666;
            border-bottom: 2px solid #ddd;
        }
        .table td {
            padding: 10px;
            border-bottom: 1px solid #eee;
            font-size: 12px;
        }
        .table tr:hover { background: #f9f9f9; }
        .stat {
            font-size: 28px;
            font-weight: bold;
            color: #764ba2;
            margin: 10px 0;
        }
        .key-box {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 5px;
            margin: 8px 0;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            word-break: break-all;
            border-left: 4px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Login/Register Section -->
        <div id="authSection" class="section active">
            <div class="grid">
                <div class="card">
                    <h2>🔐 User Login</h2>
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="loginUsername" placeholder="Enter username">
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" id="loginPassword" placeholder="Enter password">
                    </div>
                    <button class="btn" onclick="login()" style="width: 100%;">Login</button>
                    <div id="loginResponse"></div>
                    <div style="margin-top: 15px; padding: 12px; background: #f0f0f0; border-radius: 5px; font-size: 12px;">
                        <strong>Demo Login:</strong><br>
                        Username: <code>admin</code><br>
                        Password: <code>admin123</code>
                    </div>
                </div>

                <div class="card">
                    <h2>📝 Create New User</h2>
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="regUsername" placeholder="Choose username">
                    </div>
                    <div class="form-group">
                        <label>Email:</label>
                        <input type="email" id="regEmail" placeholder="user@example.com">
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" id="regPassword" placeholder="Enter password">
                    </div>
                    <button class="btn" onclick="register()" style="width: 100%;">Create User</button>
                    <div id="registerResponse"></div>
                </div>
            </div>
        </div>

        <!-- Dashboard Section (After Login) -->
        <div id="dashboardSection" class="section">
            <div class="header">
                <h1>🔐 KeyAuth Server</h1>
                <div class="user-info">
                    <span class="user-name" id="currentUsername">User</span>
                    <button class="btn" onclick="logout()">Logout</button>
                </div>
            </div>

            <div class="grid">
                <div class="card">
                    <h2>📊 Account Info</h2>
                    <p><strong>Username:</strong> <span id="displayUsername"></span></p>
                    <p><strong>Email:</strong> <span id="displayEmail"></span></p>
                    <p><strong>Status:</strong> <span class="status-badge">✓ Active</span></p>
                </div>

                <div class="card">
                    <h2>📈 API Statistics</h2>
                    <p><strong>Total API Keys:</strong></p>
                    <div class="stat" id="statKeys">0</div>
                    <p><strong>Active Keys:</strong></p>
                    <div class="stat" id="statActiveKeys">0</div>
                </div>

                <div class="card">
                    <h2>📋 Recent Activity</h2>
                    <p><strong>Total API Requests:</strong></p>
                    <div class="stat" id="statRequests">0</div>
                </div>
            </div>

            <!-- API Keys Management -->
            <div class="card">
                <h2>🔑 API Key Management</h2>
                <h3 style="font-size: 14px; color: #666; margin-top: 15px; margin-bottom: 10px;">Generate New API Key</h3>
                <div class="form-group">
                    <label>Key Name:</label>
                    <input type="text" id="keyName" placeholder="e.g., Mobile App, Web API">
                </div>
                <div class="form-group">
                    <label>Rate Limit (requests/hour):</label>
                    <input type="number" id="keyRateLimit" value="1000" min="100" max="10000">
                </div>
                <button class="btn" onclick="createAPIKey()">Generate Key</button>
                <div id="keyResponse"></div>

                <h3 style="font-size: 14px; color: #666; margin-top: 20px; margin-bottom: 10px;">Your API Keys</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Key ID</th>
                            <th>Key Value</th>
                            <th>Status</th>
                            <th>Usage</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="keysTable">
                        <tr><td colspan="5" style="text-align: center; color: #999;">Loading keys...</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- Request Logs -->
            <div class="card">
                <h2>📊 Request Logs</h2>
                <p style="color: #666; font-size: 12px; margin-bottom: 15px;">Last 50 API requests</p>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Request ID</th>
                            <th>Endpoint</th>
                            <th>Method</th>
                            <th>Status</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody id="logsTable">
                        <tr><td colspan="5" style="text-align: center; color: #999;">Loading logs...</td></tr>
                    </tbody>
                </table>
                <button class="btn" onclick="loadLogs()" style="margin-top: 15px;">Refresh Logs</button>
            </div>
        </div>
    </div>

    <script>
        const BASE_URL = window.location.origin;
        let currentUser = null;
        let currentToken = null;

        // Check if already logged in
        window.addEventListener('load', () => {
            const savedUser = localStorage.getItem('currentUser');
            const savedToken = localStorage.getItem('currentToken');
            if (savedUser && savedToken) {
                currentUser = JSON.parse(savedUser);
                currentToken = savedToken;
                showDashboard();
            }
        });

        // ==================== AUTH ====================
        async function login() {
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;

            if (!username || !password) {
                showAlert('loginResponse', '⚠️ Please enter username and password', 'error');
                return;
            }

            try {
                const response = await fetch(`${BASE_URL}/api/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await response.json();

                if (data.success) {
                    currentUser = data.user;
                    currentToken = data.token;
                    localStorage.setItem('currentUser', JSON.stringify(currentUser));
                    localStorage.setItem('currentToken', currentToken);
                    showAlert('loginResponse', '✓ Login successful!', 'success');
                    setTimeout(showDashboard, 800);
                } else {
                    showAlert('loginResponse', '❌ Invalid username or password', 'error');
                }
            } catch (error) {
                showAlert('loginResponse', '❌ Error: ' + error.message, 'error');
            }
        }

        async function register() {
            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;

            if (!username || !email || !password) {
                showAlert('registerResponse', '⚠️ Please fill all fields', 'error');
                return;
            }

            try {
                const response = await fetch(`${BASE_URL}/api/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await response.json();

                if (data.success) {
                    showAlert('registerResponse', `✓ User "${username}" created! Now login.`, 'success');
                    document.getElementById('regUsername').value = '';
                    document.getElementById('regEmail').value = '';
                    document.getElementById('regPassword').value = '';
                    document.getElementById('loginUsername').value = username;
                    document.getElementById('loginPassword').value = password;
                } else {
                    showAlert('registerResponse', `❌ ${data.error}`, 'error');
                }
            } catch (error) {
                showAlert('registerResponse', '❌ Error: ' + error.message, 'error');
            }
        }

        function logout() {
            localStorage.removeItem('currentUser');
            localStorage.removeItem('currentToken');
            currentUser = null;
            currentToken = null;
            document.getElementById('authSection').classList.add('active');
            document.getElementById('dashboardSection').classList.remove('active');
            document.getElementById('loginUsername').value = '';
            document.getElementById('loginPassword').value = '';
        }

        function showDashboard() {
            document.getElementById('authSection').classList.remove('active');
            document.getElementById('dashboardSection').classList.add('active');
            document.getElementById('currentUsername').textContent = currentUser.username;
            document.getElementById('displayUsername').textContent = currentUser.username;
            document.getElementById('displayEmail').textContent = currentUser.email;
            loadStats();
            loadAPIKeys();
            loadLogs();
        }

        // ==================== API CALLS ====================
        async function loadStats() {
            try {
                const response = await fetch(`${BASE_URL}/api/stats`, {
                    headers: { 'Authorization': `Bearer ${currentToken}` }
                });
                const data = await response.json();
                if (data.success) {
                    document.getElementById('statKeys').textContent = data.stats.total_keys;
                    document.getElementById('statActiveKeys').textContent = data.stats.active_keys;
                    document.getElementById('statRequests').textContent = data.stats.total_requests;
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function loadAPIKeys() {
            try {
                const response = await fetch(`${BASE_URL}/api/keys`, {
                    headers: { 'Authorization': `Bearer ${currentToken}` }
                });
                const data = await response.json();
                
                if (data.success && data.keys) {
                    const table = document.getElementById('keysTable');
                    table.innerHTML = data.keys.map(key => `
                        <tr>
                            <td>${key.id}</td>
                            <td><code style="background: #f0f0f0; padding: 3px 6px; border-radius: 3px; font-size: 11px;">${key.key}</code></td>
                            <td><span style="background: #d4edda; color: #155724; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: 600;">${key.active ? 'Active' : 'Revoked'}</span></td>
                            <td>${key.usage_count} / ${key.rate_limit}</td>
                            <td>${key.active ? `<button class="btn btn-small" onclick="revokeKey('${key.key}')">Revoke</button>` : 'Revoked'}</td>
                        </tr>
                    `).join('');
                } else {
                    document.getElementById('keysTable').innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">No keys yet</td></tr>';
                }
            } catch (error) {
                console.error('Error loading keys:', error);
            }
        }

        async function loadLogs() {
            try {
                const response = await fetch(`${BASE_URL}/api/logs`, {
                    headers: { 'Authorization': `Bearer ${currentToken}` }
                });
                const data = await response.json();
                
                if (data.success && data.logs) {
                    const table = document.getElementById('logsTable');
                    table.innerHTML = data.logs.slice().reverse().slice(0, 50).map(log => {
                        let statusColor = log.status === 200 ? '#2ecc71' : log.status < 500 ? '#f39c12' : '#e74c3c';
                        return `
                            <tr>
                                <td><code style="font-size: 11px;">${log.id}</code></td>
                                <td>${log.endpoint}</td>
                                <td><strong>${log.method}</strong></td>
                                <td><span style="color: ${statusColor}; font-weight: 600;">${log.status}</span></td>
                                <td>${new Date(log.timestamp).toLocaleTimeString()}</td>
                            </tr>
                        `;
                    }).join('');
                }
            } catch (error) {
                console.error('Error loading logs:', error);
            }
        }

        async function createAPIKey() {
            const name = document.getElementById('keyName').value;
            const rateLimit = document.getElementById('keyRateLimit').value;
            
            if (!name) {
                showAlert('keyResponse', '⚠️ Please enter a key name', 'error');
                return;
            }

            try {
                const response = await fetch(`${BASE_URL}/api/keys/create`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${currentToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, rate_limit: parseInt(rateLimit) })
                });
                const data = await response.json();
                
                if (data.success) {
                    showAlert('keyResponse', `✓ Key generated: ${data.key}`, 'success');
                    document.getElementById('keyName').value = '';
                    setTimeout(loadAPIKeys, 1000);
                } else {
                    showAlert('keyResponse', '❌ Failed to create key', 'error');
                }
            } catch (error) {
                showAlert('keyResponse', '❌ Error: ' + error.message, 'error');
            }
        }

        async function revokeKey(key) {
            if (confirm('Are you sure you want to revoke this API key?')) {
                try {
                    const response = await fetch(`${BASE_URL}/api/keys/revoke`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${currentToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ key })
                    });
                    const data = await response.json();
                    
                    if (data.success) {
                        showAlert('keyResponse', '✓ Key revoked successfully', 'success');
                        setTimeout(loadAPIKeys, 500);
                    }
                } catch (error) {
                    showAlert('keyResponse', '❌ Error: ' + error.message, 'error');
                }
            }
        }

        function showAlert(containerId, message, type) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type}`;
            alertDiv.textContent = message;
            container.insertBefore(alertDiv, container.firstChild);
            
            setTimeout(() => alertDiv.remove(), 4000);
        }
    </script>
</body>
</html>
