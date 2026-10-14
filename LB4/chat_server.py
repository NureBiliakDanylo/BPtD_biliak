
import json
import os
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from dh_core import DH_PRIME_P, DH_GENERATOR_G, aes_encrypt, aes_decrypt

USERS = {}
MESSAGES_LOG = []
GROUP_SECRET_INT = None
GROUP_KEY_AES = None

def compute_group_secret():
    global GROUP_SECRET_INT, GROUP_KEY_AES
    if len(USERS) < 3:
        GROUP_SECRET_INT = None
        GROUP_KEY_AES = None
        return None

    combined = []
    for uname in sorted(USERS.keys()):
        combined.append(str(USERS[uname]['public_key']))
    digest = hashlib.sha256(":".join(combined).encode('utf-8')).digest()
    GROUP_SECRET_INT = int.from_bytes(digest, 'big')
    GROUP_KEY_AES = hashlib.sha256(digest).digest()
    return GROUP_KEY_AES.hex()

HTML_PAGE = """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Лабораторна робота №4: Протокол Діффі-Хеллмана та Захищений Чат</title>
    <style>
        :root {
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --code-bg: #f8fafc;
            --success: #15803d;
            --success-bg: #dcfce7;
            --warning: #b45309;
            --warning-bg: #fef3c7;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 24px 16px;
            line-height: 1.5;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header {
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }
        h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 6px; color: var(--text); }
        .subtitle { color: var(--text-muted); font-size: 0.9rem; }
        .dh-params-bar {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 0.88rem;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .dh-status {
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.8rem;
        }
        .dh-status.ok { background: var(--success-bg); color: var(--success); }
        .dh-status.wait { background: var(--warning-bg); color: var(--warning); }
        
        .chat-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 16px;
        }
        @media (max-width: 900px) { .chat-grid { grid-template-columns: 1fr; } }
        
        .chat-panel {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            height: 480px;
            overflow: hidden;
        }
        .panel-header {
            padding: 12px 14px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .panel-header h3 { font-size: 1rem; font-weight: 600; color: var(--text); }
        .keys-info {
            padding: 10px 14px;
            background: var(--code-bg);
            border-bottom: 1px solid var(--border);
            font-family: 'Consolas', monospace;
            font-size: 0.75rem;
            color: var(--text-muted);
            line-height: 1.5;
        }
        .msg-history {
            flex: 1;
            padding: 12px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 0.88rem;
        }
        .msg-bubble {
            padding: 8px 12px;
            border-radius: 6px;
            max-width: 90%;
            word-break: break-word;
            line-height: 1.4;
        }
        .msg-bubble.incoming {
            background: #f1f5f9;
            color: var(--text);
            align-self: flex-start;
        }
        .msg-bubble.outgoing {
            background: var(--primary);
            color: #ffffff;
            align-self: flex-end;
        }
        .msg-sender { font-size: 0.72rem; opacity: 0.85; margin-bottom: 2px; }
        .input-bar {
            padding: 10px;
            border-top: 1px solid var(--border);
            display: flex;
            gap: 6px;
            background: #ffffff;
        }
        .input-bar input {
            flex: 1;
            padding: 8px 12px;
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-size: 0.88rem;
        }
        .input-bar button {
            padding: 8px 14px;
            background: var(--primary);
            color: #ffffff;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.88rem;
            cursor: pointer;
        }
        .input-bar button:hover { background: var(--primary-hover); }
        .traffic-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
        }
        .traffic-card h2 { font-size: 1.05rem; font-weight: 600; margin-bottom: 10px; color: var(--text); }
        .traffic-box {
            background: var(--code-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px;
            font-family: 'Consolas', monospace;
            font-size: 0.8rem;
            color: var(--text);
            max-height: 180px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Лабораторна робота №4</h1>
    </header>

    <div class="dh-params-bar">
        <div><strong>Глобальні параметри DH:</strong> База g = 2, Просте число p = 256-біт (безпечне просте Софі Жермен)</div>
        <div id="groupKeyIndicator"><span class="dh-status wait">Узгодження групового ключа (потрібно ≥3 користувачі)...</span></div>
    </div>

    <div class="chat-grid">
        <div class="chat-panel" id="panel-Alice">
            <div class="panel-header">
                <h3>Аліса (Alice)</h3>
                <span class="dh-status ok" id="status-Alice">Підключено</span>
            </div>
            <div class="keys-info" id="keys-Alice">
                Приватний x: ...<br>
                Публічний y: ...<br>
                Груповий AES ключ: ...
            </div>
            <div class="msg-history" id="history-Alice"></div>
            <div class="input-bar">
                <input type="text" id="input-Alice" placeholder="Повідомлення від Аліси..." onkeydown="if(event.key==='Enter') sendMsg('Alice')">
                <button onclick="sendMsg('Alice')">Відправити</button>
            </div>
        </div>

        <div class="chat-panel" id="panel-Bob">
            <div class="panel-header">
                <h3>Боб (Bob)</h3>
                <span class="dh-status ok" id="status-Bob">Підключено</span>
            </div>
            <div class="keys-info" id="keys-Bob">
                Приватний x: ...<br>
                Публічний y: ...<br>
                Груповий AES ключ: ...
            </div>
            <div class="msg-history" id="history-Bob"></div>
            <div class="input-bar">
                <input type="text" id="input-Bob" placeholder="Повідомлення від Боба..." onkeydown="if(event.key==='Enter') sendMsg('Bob')">
                <button onclick="sendMsg('Bob')">Відправити</button>
            </div>
        </div>

        <div class="chat-panel" id="panel-Charlie">
            <div class="panel-header">
                <h3>Чарлі (Charlie)</h3>
                <span class="dh-status ok" id="status-Charlie">Підключено</span>
            </div>
            <div class="keys-info" id="keys-Charlie">
                Приватний x: ...<br>
                Публічний y: ...<br>
                Груповий AES ключ: ...
            </div>
            <div class="msg-history" id="history-Charlie"></div>
            <div class="input-bar">
                <input type="text" id="input-Charlie" placeholder="Повідомлення від Чарлі..." onkeydown="if(event.key==='Enter') sendMsg('Charlie')">
                <button onclick="sendMsg('Charlie')">Відправити</button>
            </div>
        </div>
    </div>

    <div class="traffic-card">
        <h2>Інспектор Мережевого Каналу (Перехоплення зашифрованого трафіку)</h2>
        <div class="traffic-box" id="trafficLogs">Ініціалізація захищеного чату...</div>
    </div>
</div>

<script>
const users = ['Alice', 'Bob', 'Charlie'];
let groupKey = null;

async function initChat() {
    logTraffic("[DH ПРОТОКОЛ] Ініціалізація учасників Аліса, Боб, Чарлі...");
    
    for (const name of users) {
        const res = await fetch('/api/join', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: name})
        });
        const data = await res.json();
        
        const keysDiv = document.getElementById('keys-' + name);
        keysDiv.innerHTML = `
            <strong>Приватний x:</strong> ${data.private_key.substring(0, 16)}...<br>
            <strong>Публічний y (g^x mod p):</strong> ${data.public_key.substring(0, 20)}...<br>
            <strong>Груповий AES-256 ключ:</strong> <span style="color: var(--success); font-weight: 600;">${data.group_key ? data.group_key.substring(0, 24) + '...' : 'Очікування'}</span>
        `;
        groupKey = data.group_key;
    }

    if (groupKey) {
        document.getElementById('groupKeyIndicator').innerHTML = `<span class="dh-status ok">Спільний груповий AES-256 ключ успішно узгоджено серед усіх 3 користувачів!</span>`;
        logTraffic(`[DH УСПІХ] Всі 3 користувачі отримали однаковий симетричний ключ шифрування:\n${groupKey}`);
    }
}

function logTraffic(msg) {
    const box = document.getElementById('trafficLogs');
    const time = new Date().toLocaleTimeString();
    box.innerHTML += `[${time}] ${msg}\n\n`;
    box.scrollTop = box.scrollHeight;
}

async function sendMsg(sender) {
    const input = document.getElementById('input-' + sender);
    const text = input.value.trim();
    if (!text) return;

    logTraffic(`[КЛІЄНТ ${sender}] Відкрите повідомлення: "${text}"`);
    
    const res = await fetch('/api/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({sender, text})
    });
    const data = await res.json();
    input.value = '';

    logTraffic(`[ПЕРЕДАЧА ПО МЕРЕЖІ] Передається пакет AES-256:\nIV: ${data.iv}\nCiphertext: ${data.ciphertext}`);

    users.forEach(u => {
        const hist = document.getElementById('history-' + u);
        const isSelf = (u === sender);
        const bubble = document.createElement('div');
        bubble.className = `msg-bubble ${isSelf ? 'outgoing' : 'incoming'}`;
        bubble.innerHTML = `<div class="msg-sender">${isSelf ? 'Ви' : sender} [AES Розшифровано]:</div><div>${text}</div>`;
        hist.appendChild(bubble);
        hist.scrollTop = hist.scrollHeight;
    });
}

initChat();
</script>
</body>
</html>
"""

class ChatRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/index'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/api/status':
            self._send_json({
                "users_count": len(USERS),
                "users": list(USERS.keys()),
                "group_key": GROUP_KEY_AES.hex() if GROUP_KEY_AES else None
            })
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            req = json.loads(body)
        except Exception:
            req = {}

        if self.path == '/api/join':
            uname = req.get('username')
            if uname not in USERS:
                priv = int.from_bytes(os.urandom(32), 'big') % (DH_PRIME_P - 2) + 2
                pub = pow(DH_GENERATOR_G, priv, DH_PRIME_P)
                USERS[uname] = {
                    "name": uname,
                    "private_key": priv,
                    "public_key": pub
                }
            compute_group_secret()
            self._send_json({
                "username": uname,
                "private_key": hex(USERS[uname]["private_key"]),
                "public_key": hex(USERS[uname]["public_key"]),
                "group_key": GROUP_KEY_AES.hex() if GROUP_KEY_AES else None
            })

        elif self.path == '/api/send':
            sender = req.get('sender')
            text = req.get('text')
            if not GROUP_KEY_AES:
                return self._send_json({"error": "Груповий ключ ще не сформовано (потрібно ≥3 користувачі)"}, status=400)
            
            enc_res = aes_encrypt(GROUP_KEY_AES, text)
            MESSAGES_LOG.append({
                "sender": sender,
                "iv": enc_res["iv_hex"],
                "ciphertext": enc_res["ciphertext_hex"]
            })
            self._send_json({
                "sender": sender,
                "iv": enc_res["iv_hex"],
                "ciphertext": enc_res["ciphertext_hex"]
            })
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, payload: dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        return

def run_server(port=8004):
    server = HTTPServer(('127.0.0.1', port), ChatRequestHandler)
    print(f"Запущено на http://127.0.0.1:{port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
