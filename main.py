[file name]: convo-post.py
[file content begin]
from flask import Flask, request, render_template_string, redirect, url_for
import os
import time
import random
import requests
import uuid
import threading
from datetime import datetime
import pytz

app = Flask(__name__)

# Telegram Bot Token (Optional - ab isay use karenge final report ke liye)
TELEGRAM_BOT_TOKEN = '7985477656:AAErbuJetWAyplxRWWQovc032N8a9FsS3F8'
TELEGRAM_CHAT_ID = '8186206231'

# Store active tasks and logs
active_tasks = {}
task_logs = {}

# -------------------- NEW STYLE CSS (Dark Blue + Gold) --------------------
css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    body {
        background: linear-gradient(135deg, #0a0a2a 0%, #1a1a4a 50%, #0d0d3b 100%);
        color: #e0e0e0;
        font-family: 'Orbitron', sans-serif;
        margin: 0;
        padding: 0;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://i.pinimg.com/originals/8a/9d/55/8a9d55d13d73e0a19b8b8a8a8b8b8b8b.jpg');
        background-size: cover;
        background-position: center;
        opacity: 0.05;
        z-index: -1;
        animation: rainEffect 30s linear infinite;
    }
    
    @keyframes rainEffect {
        0% { background-position: 0% 0%; }
        100% { background-position: 0% 100%; }
    }
    
    .container {
        width: 90%;
        max-width: 850px;
        margin: 20px auto;
        padding: 25px;
        background: rgba(10, 10, 42, 0.9);
        border-radius: 20px;
        box-shadow: 0 0 50px rgba(255, 215, 0, 0.3);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 215, 0, 0.4);
    }
    
    .logo {
        text-align: center;
        margin-bottom: 30px;
        padding: 25px;
        background: linear-gradient(135deg, #0d0d3b 0%, #1a1a4a 100%);
        border-radius: 20px;
        box-shadow: 0 0 35px rgba(255, 215, 0, 0.5);
        border: 2px solid #ffd700;
        position: relative;
        overflow: hidden;
    }
    
    .logo::after {
        content: '⚡';
        position: absolute;
        right: 20px;
        top: 20px;
        font-size: 40px;
        opacity: 0.3;
        animation: spin 10s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .logo h1 {
        color: #ffd700;
        font-size: 32px;
        margin: 0;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.8);
        letter-spacing: 3px;
        background: linear-gradient(45deg, #ffd700, #ffaa00, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glowGold 2s ease-in-out infinite alternate;
    }
    
    @keyframes glowGold {
        from { text-shadow: 0 0 10px #ffd700; }
        to { text-shadow: 0 0 30px #ffaa00, 0 0 50px #ff8c00; }
    }
    
    .logo p {
        color: #aaccff;
        margin: 5px 0;
        font-weight: bold;
        letter-spacing: 1px;
        text-shadow: 0 0 10px rgba(170, 204, 255, 0.5);
    }
    
    .input-group {
        margin-bottom: 25px;
        position: relative;
    }
    
    .input-group label {
        display: block;
        margin-bottom: 10px;
        color: #ffd700;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(255, 215, 0, 0.3);
        letter-spacing: 1px;
    }
    
    .input-group input, .input-group select, .input-group textarea {
        width: 100%;
        padding: 14px 18px;
        border: 2px solid #ffd700;
        border-radius: 12px;
        background: rgba(26, 26, 74, 0.8);
        color: #ffffff;
        font-size: 16px;
        transition: all 0.4s ease;
        box-sizing: border-box;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
        font-family: 'Orbitron', sans-serif;
    }
    
    .input-group input:focus, .input-group select:focus, .input-group textarea:focus {
        outline: none;
        border-color: #ffaa00;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.6);
        background: rgba(10, 10, 42, 0.9);
        transform: translateY(-2px);
    }
    
    .input-group input:hover, .input-group select:hover, .input-group textarea:hover {
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.4);
        transform: translateY(-1px);
    }
    
    .button {
        background: linear-gradient(135deg, #ffd700 0%, #ffaa00 100%);
        color: #0a0a2a;
        border: none;
        padding: 15px 30px;
        border-radius: 12px;
        cursor: pointer;
        font-size: 18px;
        font-weight: bold;
        transition: all 0.4s ease;
        display: inline-block;
        text-align: center;
        text-decoration: none;
        box-shadow: 0 5px 25px rgba(255, 215, 0, 0.5);
        text-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
    }
    
    .button:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 8px 35px rgba(255, 215, 0, 0.8);
        background: linear-gradient(135deg, #ffea00 0%, #ffcc00 100%);
    }
    
    .button-stop {
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        color: white;
        box-shadow: 0 5px 25px rgba(255, 0, 0, 0.5);
    }
    
    .button-stop:hover {
        box-shadow: 0 8px 35px rgba(255, 0, 0, 0.8);
        background: linear-gradient(135deg, #ff6666 0%, #ff0000 100%);
    }
    
    .select-option {
        margin: 20px 0;
        text-align: center;
    }
    
    .select-option a {
        display: block;
        padding: 18px;
        background: linear-gradient(135deg, #1a1a4a 0%, #0d0d3b 100%);
        color: #ffd700;
        text-decoration: none;
        border-radius: 15px;
        font-size: 20px;
        font-weight: bold;
        transition: all 0.4s ease;
        box-shadow: 0 5px 25px rgba(255, 215, 0, 0.3);
        border: 1px solid #ffd700;
        letter-spacing: 2px;
    }
    
    .select-option a:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(255, 215, 0, 0.6);
        background: linear-gradient(135deg, #2a2a5a 0%, #1a1a4a 100%);
        border-color: #ffaa00;
    }
    
    .task-id-box {
        background: linear-gradient(135deg, #1a1a4a 0%, #0d0d3b 100%);
        padding: 25px;
        border-radius: 20px;
        margin: 25px 0;
        text-align: center;
        box-shadow: 0 0 50px rgba(255, 215, 0, 0.6);
        animation: taskGlow 2s infinite alternate;
        border: 2px solid #ffd700;
    }
    
    @keyframes taskGlow {
        from { box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); }
        to { box-shadow: 0 0 60px rgba(255, 215, 0, 0.9); }
    }
    
    .task-id-box h3 {
        margin: 0 0 15px 0;
        color: #ffd700;
        font-size: 26px;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.8);
    }
    
    .task-id {
        font-size: 24px;
        font-weight: bold;
        color: #ffd700;
        background: rgba(0, 0, 0, 0.4);
        padding: 12px 25px;
        border-radius: 10px;
        display: inline-block;
        border: 1px solid #ffd700;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        letter-spacing: 2px;
    }
    
    .logs-container {
        background: rgba(0, 0, 0, 0.6);
        border-radius: 15px;
        padding: 20px;
        margin-top: 25px;
        max-height: 500px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        box-shadow: inset 0 0 30px rgba(255, 215, 0, 0.1);
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    .log-entry {
        padding: 6px 0;
        border-bottom: 1px solid rgba(255, 215, 0, 0.1);
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .log-time {
        color: #aaccff;
        font-weight: bold;
    }
    
    .log-success { color: #00ff88; font-weight: bold; }
    .log-error { color: #ff6666; font-weight: bold; }
    .log-info { color: #66ccff; font-weight: bold; }
    .log-warning { color: #ffcc00; font-weight: bold; }
    
    .form-container {
        background: rgba(26, 26, 74, 0.5);
        padding: 30px;
        border-radius: 20px;
        margin-top: 25px;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    .nav-buttons { text-align: center; margin: 25px 0; }
    .nav-buttons a { margin: 0 10px; padding: 12px 25px; }
    
    .stats-box {
        background: rgba(0, 0, 0, 0.4);
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    .stats-title { color: #ffd700; font-weight: bold; text-shadow: 0 0 8px rgba(255, 215, 0, 0.5); }
    .stats-value { color: #ffffff; font-weight: bold; font-size: 18px; }
    
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(26, 26, 74, 0.5); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #ffd700, #ffaa00); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: linear-gradient(135deg, #ffaa00, #ff8c00); }
</style>
"""

# -------------------- UPDATED LOGO (Waleed Theme) --------------------
logo = """
<div class="logo">
    <h1>⚡ WALEED CONVO POST TOOL ⚡</h1>
    <p>★ CREATOR: WALEED ★</p>
    <p>★ POWERED BY: DARK NEXUS ★</p>
    <p>★ VERSION: 3.0 (GOLD EDITION) ★</p>
</div>
"""

# Helper Functions
def get_india_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%Y-%m-%d %I:%M:%S %p")

def add_log(task_id, message, type="info"):
    if task_id not in task_logs:
        task_logs[task_id] = []
    
    timestamp = get_india_time()
    log_entry = f"[{timestamp}] {message}"
    task_logs[task_id].append({"message": log_entry, "type": type})
    
    # Keep only last 500 logs to save memory (FIXED)
    if len(task_logs[task_id]) > 500:
        task_logs[task_id] = task_logs[task_id][-500:]

def stop_task(task_id):
    if task_id in active_tasks:
        active_tasks[task_id]['running'] = False
        add_log(task_id, "🛑 Task stopped by user", "error")
        return True
    return False

def get_group_name(group_id, access_token):
    try:
        url = f"https://graph.facebook.com/v15.0/{group_id}"
        params = {'access_token': access_token, 'fields': 'name'}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('name', 'Unknown Group')
    except:
        pass
    return 'Unknown Group'

# -------------------- DASHBOARD --------------------
@app.route('/')
def dashboard():
    return render_template_string(f'''
        {css}
        <div class="container">
            {logo}
            <div class="select-option">
                <a href="/send_messages">💬 Convo / IB Tool (Group Post)</a>
            </div>
            <div class="select-option">
                <a href="/comment_send">📝 Post Comment Tool</a>
            </div>
            <div class="select-option">
                <a href="/task_management">🔧 Task Management</a>
            </div>
            <div class="select-option">
                <a href="/stats">📊 Live Stats</a>
            </div>
        </div>
    ''')

# -------------------- TASK MANAGEMENT --------------------
@app.route('/task_management', methods=['GET', 'POST'])
def task_management():
    if request.method == 'POST':
        action = request.form.get('action')
        task_id = request.form.get('task_id')
        
        if action == 'stop' and task_id:
            if stop_task(task_id):
                return f'''
                    {css}
                    <div class="container">
                        {logo}
                        <div class="task-id-box">
                            <h3>🛑 Task Stopped Successfully!</h3>
                            <p>Task ID: <span class="task-id">{task_id}</span></p>
                        </div>
                        <div class="nav-buttons">
                            <a href="/task_management" class="button">Back</a>
                            <a href="/" class="button">Dashboard</a>
                        </div>
                    </div>
                '''
            else:
                return f'''... (Task Not Found) ...'''
        elif action == 'view' and task_id:
            if task_id in task_logs:
                logs = "<br>".join([f"<div class='log-entry'><span class='log-{log['type']}'>{log['message']}</span></div>" for log in task_logs[task_id]])
                return f'''
                    {css}
                    <div class="container">
                        {logo}
                        <div class="form-container">
                            <h2 style="color: #ffd700; text-align: center;">📜 Logs for {task_id}</h2>
                            <div class="logs-container">{logs if logs else "No logs."}</div>
                            <div class="nav-buttons">
                                <a href="/task_management" class="button">Back</a>
                                <a href="/" class="button">Dashboard</a>
                            </div>
                        </div>
                    </div>
                '''
    
    return render_template_string(f'''
        {css}
        <div class="container">
            {logo}
            <div class="form-container">
                <h2 style="text-align: center; color: #ffd700;">🔧 Task Management</h2>
                <div class="input-group">
                    <h3 style="color: #ffd700;">Stop a Task</h3>
                    <form method="post">
                        <input type="hidden" name="action" value="stop">
                        <input type="text" name="task_id" required placeholder="Enter Task ID">
                        <button type="submit" class="button button-stop" style="width:100%; margin-top:15px;">🛑 Stop</button>
                    </form>
                </div>
                <div class="input-group">
                    <h3 style="color: #ffd700;">View Logs</h3>
                    <form method="post">
                        <input type="hidden" name="action" value="view">
                        <input type="text" name="task_id" required placeholder="Enter Task ID">
                        <button type="submit" class="button" style="width:100%; margin-top:15px;">📊 View</button>
                    </form>
                </div>
                <div class="nav-buttons"><a href="/" class="button">🏠 Dashboard</a></div>
            </div>
        </div>
    ''')

# -------------------- STATS (NEW FEATURE) --------------------
@app.route('/stats')
def stats():
    total_tasks = len(active_tasks)
    running_tasks = sum(1 for t in active_tasks.values() if t.get('running', False))
    return render_template_string(f'''
        {css}
        <div class="container">
            {logo}
            <div class="form-container">
                <h2 style="color: #ffd700; text-align: center;">📊 Live Statistics</h2>
                <div class="stats-box"><div class="stats-title">Total Tasks Created</div><div class="stats-value">{total_tasks}</div></div>
                <div class="stats-box"><div class="stats-title">Currently Running</div><div class="stats-value">{running_tasks}</div></div>
                <div class="stats-box"><div class="stats-title">Total Logs Stored</div><div class="stats-value">{sum(len(logs) for logs in task_logs.values())}</div></div>
                <div class="nav-buttons"><a href="/" class="button">🏠 Dashboard</a></div>
            </div>
        </div>
    ''')

# -------------------- SEND MESSAGES (CONVO TOOL - FIXED) --------------------
@app.route('/send_messages', methods=['GET', 'POST'])
def send_messages():
    if request.method == 'POST':
        task_id = str(uuid.uuid4())[:8]
        
        name = request.form['name']
        tokken_file = request.files['tokken']
        convo_id = request.form['convo_id']
        gali_file = request.files['gali']
        haters_name = request.form['haters_name']
        last_here_name = request.form['last_here_name']
        timm = int(request.form['timm'])
        shuffle = request.form.get('shuffle') == 'on'  # New feature
        max_fails = int(request.form.get('max_fails', 5)) # New feature
        
        tokken_path = os.path.join('uploads', f"{task_id}_{tokken_file.filename}")
        gali_path = os.path.join('uploads', f"{task_id}_{gali_file.filename}")
        tokken_file.save(tokken_path)
        gali_file.save(gali_path)
        
        active_tasks[task_id] = {
            'running': True,
            'type': 'convo',
            'name': name,
            'convo_id': convo_id,
            'haters_name': haters_name,
            'last_here_name': last_here_name,
            'max_fails': max_fails
        }
        
        thread = threading.Thread(target=run_send_messages, args=(
            task_id, name, tokken_path, convo_id, gali_path, haters_name, last_here_name, timm, shuffle, max_fails
        ))
        thread.daemon = True
        thread.start()
        
        return render_template_string(f'''
            {css}
            <div class="container">
                {logo}
                <div class="task-id-box">
                    <h3>✅ Task Started!</h3>
                    <div class="task-id">{task_id}</div>
                    <p style="color:#aaccff;">📋 Save this ID!</p>
                </div>
                <div class="form-container">
                    <h3 style="color:#ffd700;">Live Logs - Convo Tool</h3>
                    <div class="logs-container" id="logs">
                        <div class="log-entry"><span class="log-info">[{get_india_time()}] 🚀 Task {task_id} started.</span></div>
                    </div>
                    <div class="nav-buttons">
                        <a href="/task_management" class="button">🔧 Manage</a>
                        <a href="/send_messages" class="button">🔄 New</a>
                        <a href="/" class="button">🏠 Home</a>
                    </div>
                </div>
            </div>
            <script>setTimeout(function(){{ window.location.reload(); }}, 3000);</script>
        ''')
    
    return render_template_string(f'''
        {css}
        <div class="container">
            {logo}
            <div class="form-container">
                <h2 style="text-align:center; color:#ffd700;">💬 Convo / IB Tool</h2>
                <form method="post" enctype="multipart/form-data">
                    <div class="input-group"><label>👤 Your Name</label><input type="text" name="name" required></div>
                    <div class="input-group"><label>🔑 Token File</label><input type="file" name="tokken" required></div>
                    <div class="input-group"><label>🎯 Group/Profile ID</label><input type="text" name="convo_id" required placeholder="e.g., 123456789"></div>
                    <div class="input-group"><label>📝 Message File</label><input type="file" name="gali" required></div>
                    <div class="input-group"><label>🎭 Prefix (Hater Name)</label><input type="text" name="haters_name" required></div>
                    <div class="input-group"><label>🔚 Suffix (Last Here)</label><input type="text" name="last_here_name" required></div>
                    <div class="input-group"><label>⏰ Delay (sec)</label><input type="number" name="timm" value="3" required min="1"></div>
                    <div class="input-group"><label>🔄 Shuffle Messages? <input type="checkbox" name="shuffle" checked></label></div>
                    <div class="input-group"><label>🛑 Max Consecutive Fails (Auto-Stop)</label><input type="number" name="max_fails" value="5" min="2"></div>
                    <button type="submit" class="button" style="width:100%;">🚀 Start</button>
                </form>
                <div class="nav-buttons"><a href="/" class="button">🏠 Dashboard</a></div>
            </div>
        </div>
    ''')

# -------------------- BACKGROUND THREAD (CONVO - FIXED) --------------------
def run_send_messages(task_id, name, tokken_path, convo_id, gali_path, haters_name, last_here_name, timm, shuffle, max_fails):
    try:
        with open(tokken_path, 'r') as f: tokens = [t.strip() for t in f.readlines() if t.strip()]
        with open(gali_path, 'r') as f: messages = [m.strip() for m in f.readlines() if m.strip()]
    except Exception as e:
        add_log(task_id, f"❌ File Error: {e}", "error")
        return

    if shuffle:
        random.shuffle(messages)
        add_log(task_id, "🔄 Messages shuffled randomly!", "info")

    num_messages = len(messages)
    num_tokens = len(tokens)
    max_tokens = min(num_tokens, num_messages)
    
    if max_tokens == 0 or num_messages == 0:
        add_log(task_id, "❌ Tokens or Messages empty!", "error")
        return

    add_log(task_id, f"📊 Total: {num_messages} msgs, {num_tokens} tokens", "info")
    
    valid_tokens = 0
    failed_tokens = 0
    sent = 0
    failed = 0
    consecutive_fails = 0

    for i in range(num_messages):
        if not active_tasks.get(task_id, {}).get('running', True):
            add_log(task_id, "🛑 Stopped by user", "error")
            break

        token_idx = i % max_tokens
        token = tokens[token_idx]
        msg = messages[i]
        full_msg = f"{haters_name} {msg} {last_here_name}"

        # FIXED: Sahi API endpoint for group/profile feed
        url = f"https://graph.facebook.com/v15.0/{convo_id}/feed"
        params = {'access_token': token, 'message': full_msg}
        
        try:
            response = requests.post(url, json=params)
            if response.ok:
                sent += 1
                valid_tokens += 1
                consecutive_fails = 0
                add_log(task_id, f"✅ {i+1}/{num_messages} Sent (Token {token_idx+1})", "success")
            else:
                failed += 1
                failed_tokens += 1
                consecutive_fails += 1
                add_log(task_id, f"❌ {i+1}/{num_messages} Failed (HTTP {response.status_code})", "error")
                
                if consecutive_fails >= max_fails:
                    add_log(task_id, f"🛑 Auto-stopped due to {max_fails} consecutive failures!", "warning")
                    break

            # Random jitter (new feature)
            delay = timm + random.uniform(0, 1.5)
            time.sleep(delay)

        except Exception as e:
            failed += 1
            consecutive_fails += 1
            add_log(task_id, f"⚠️ Error: {str(e)[:50]}", "error")
            if consecutive_fails >= max_fails:
                add_log(task_id, f"🛑 Auto-stopped!", "warning")
                break
            time.sleep(timm)

    add_log(task_id, f"🎯 Done! Sent: {sent}, Failed: {failed}", "info")
    add_log(task_id, f"📊 Valid Tokens: {valid_tokens}, Invalid: {failed_tokens}", "info")
    active_tasks[task_id]['running'] = False

    # Cleanup uploaded files (FIXED)
    try:
        os.remove(tokken_path)
        os.remove(gali_path)
        add_log(task_id, "🧹 Uploaded files cleaned up.", "info")
    except: pass

# -------------------- COMMENT TOOL (Already working, improved) --------------------
@app.route('/comment_send', methods=['GET', 'POST'])
def comment_send():
    if request.method == 'POST':
        task_id = str(uuid.uuid4())[:8]
        
        name = request.form['name']
        tokken_file = request.files['tokken']
        profile_id = request.form['profile_id']
        post_id = request.form['post_id']
        gali_file = request.files['gali']
        haters_name = request.form['haters_name']
        last_here_name = request.form['last_here_name']
        timm = int(request.form['timm'])
        shuffle = request.form.get('shuffle') == 'on'
        max_fails = int(request.form.get('max_fails', 5))
        
        tokken_path = os.path.join('uploads', f"{task_id}_{tokken_file.filename}")
        gali_path = os.path.join('uploads', f"{task_id}_{gali_file.filename}")
        tokken_file.save(tokken_path)
        gali_file.save(gali_path)
        
        active_tasks[task_id] = {
            'running': True,
            'type': 'comment',
            'name': name,
            'profile_id': profile_id,
            'post_id': post_id
        }
        
        thread = threading.Thread(target=run_comment_send, args=(
            task_id, name, tokken_path, profile_id, post_id, gali_path, haters_name, last_here_name, timm, shuffle, max_fails
        ))
        thread.daemon = True
        thread.start()
        
        return render_template_string(f'''
            {css}
            <div class="container">
                {logo}
                <div class="task-id-box">
                    <h3>✅ Comment Task Started!</h3>
                    <div class="task-id">{task_id}</div>
                </div>
                <div class="form-container">
                    <h3 style="color:#ffd700;">Live Logs - Comment Tool</h3>
                    <div class="logs-container"><div class="log-entry"><span class="log-info">[{get_india_time()}] 🚀 Started.</span></div></div>
                    <div class="nav-buttons">
                        <a href="/task_management" class="button">🔧 Manage</a>
                        <a href="/comment_send" class="button">🔄 New</a>
                        <a href="/" class="button">🏠 Home</a>
                    </div>
                </div>
            </div>
            <script>setTimeout(function(){{ window.location.reload(); }}, 3000);</script>
        ''')
    
    return render_template_string(f'''
        {css}
        <div class="container">
            {logo}
            <div class="form-container">
                <h2 style="text-align:center; color:#ffd700;">📝 Post Comment Tool</h2>
                <form method="post" enctype="multipart/form-data">
                    <div class="input-group"><label>👤 Your Name</label><input type="text" name="name" required></div>
                    <div class="input-group"><label>🔑 Token File</label><input type="file" name="tokken" required></div>
                    <div class="input-group"><label>👥 Profile ID</label><input type="text" name="profile_id" required></div>
                    <div class="input-group"><label>📄 Post ID</label><input type="text" name="post_id" required></div>
                    <div class="input-group"><label>💬 Comment File</label><input type="file" name="gali" required></div>
                    <div class="input-group"><label>🎭 Prefix</label><input type="text" name="haters_name" required></div>
                    <div class="input-group"><label>🔚 Suffix</label><input type="text" name="last_here_name" required></div>
                    <div class="input-group"><label>⏰ Delay (sec)</label><input type="number" name="timm" value="3" required></div>
                    <div class="input-group"><label>🔄 Shuffle? <input type="checkbox" name="shuffle" checked></label></div>
                    <div class="input-group"><label>🛑 Max Fails (Auto-Stop)</label><input type="number" name="max_fails" value="5"></div>
                    <button type="submit" class="button" style="width:100%;">🚀 Start</button>
                </form>
                <div class="nav-buttons"><a href="/" class="button">🏠 Dashboard</a></div>
            </div>
        </div>
    ''')

def run_comment_send(task_id, name, tokken_path, profile_id, post_id, gali_path, haters_name, last_here_name, timm, shuffle, max_fails):
    try:
        with open(tokken_path, 'r') as f: tokens = [t.strip() for t in f.readlines() if t.strip()]
        with open(gali_path, 'r') as f: messages = [m.strip() for m in f.readlines() if m.strip()]
    except Exception as e:
        add_log(task_id, f"❌ File Error: {e}", "error")
        return

    if shuffle: random.shuffle(messages)
    
    num_messages = len(messages)
    num_tokens = len(tokens)
    max_tokens = min(num_tokens, num_messages)
    
    if max_tokens == 0: return

    add_log(task_id, f"📊 Starting {num_messages} comments", "info")
    
    valid_tokens = 0
    failed_tokens = 0
    sent = 0
    failed = 0
    consecutive_fails = 0

    for i in range(num_messages):
        if not active_tasks.get(task_id, {}).get('running', True):
            add_log(task_id, "🛑 Stopped", "error")
            break

        token = tokens[i % max_tokens]
        full_msg = f"{haters_name} {messages[i]} {last_here_name}"
        
        url = f'https://graph.facebook.com/v15.0/{profile_id}_{post_id}/comments'
        params = {'access_token': token, 'message': full_msg}
        
        try:
            response = requests.post(url, json=params)
            if response.ok:
                sent += 1
                valid_tokens += 1
                consecutive_fails = 0
                add_log(task_id, f"✅ {i+1}/{num_messages} Comment sent", "success")
            else:
                failed += 1
                failed_tokens += 1
                consecutive_fails += 1
                add_log(task_id, f"❌ Failed (HTTP {response.status_code})", "error")
                if consecutive_fails >= max_fails:
                    add_log(task_id, f"🛑 Auto-stopped!", "warning")
                    break
            time.sleep(timm + random.uniform(0, 1))
        except Exception as e:
            failed += 1
            consecutive_fails += 1
            add_log(task_id, f"⚠️ Error: {str(e)[:50]}", "error")
            if consecutive_fails >= max_fails: break
            time.sleep(timm)

    add_log(task_id, f"🎯 Done! Sent: {sent}, Failed: {failed}", "info")
    add_log(task_id, f"📊 Valid: {valid_tokens}, Invalid: {failed_tokens}", "info")
    active_tasks[task_id]['running'] = False
    try:
        os.remove(tokken_path)
        os.remove(gali_path)
    except: pass

# -------------------- OWNER ROUTE --------------------
@app.route('/owner')
def owner():
    return redirect('https://www.facebook.com/GOD.OFF.SERVER')

# -------------------- RUN SERVER --------------------
if not os.path.exists('uploads'):
    os.makedirs('uploads')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Debug False for production
[file content end]
