import json
import base64
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256

print("[СЕРВЕР] Генерація пари ключів RSA 2048 біт (PyCryptodome)...")
t0 = time.time()
SERVER_RSA_KEY = RSA.generate(2048)
t1 = time.time()
print(f"[СЕРВЕР] Ключі успішно згенеровано за {round(t1 - t0, 3)} сек.")

SERVER_PUBLIC_DER = SERVER_RSA_KEY.publickey().export_key(format='DER')
SERVER_PUBLIC_B64 = base64.b64encode(SERVER_PUBLIC_DER).decode('ascii')
SERVER_PUBLIC_PEM = SERVER_RSA_KEY.publickey().export_key(format='PEM').decode('ascii')

USER_DATABASE = {
    "student": "lab2_password_2026",
    "admin": "super_secret_admin_pass"
}

HTML_PAGE = """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Лабораторна робота №2: Несиметричний алгоритм RSA</title>
    <style>
        :root {
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --secondary: #059669;
            --secondary-hover: #047857;
            --code-bg: #f8fafc;
            --success: #15803d;
            --success-bg: #dcfce7;
            --danger: #b91c1c;
            --danger-bg: #fee2e2;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 24px 16px;
            line-height: 1.5;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        header {
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }
        h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 6px; color: var(--text); }
        .subtitle { color: var(--text-muted); font-size: 0.9rem; }
        .info-pill {
            background: var(--card-bg);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 0.85rem;
            margin-bottom: 20px;
        }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
        @media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 18px;
        }
        .card h2 {
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 14px;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        label { display: block; font-size: 0.85rem; font-weight: 500; color: var(--text-muted); margin-bottom: 6px; }
        input, textarea {
            width: 100%;
            padding: 8px 12px;
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-family: 'Consolas', monospace;
            font-size: 0.88rem;
            margin-bottom: 12px;
        }
        button {
            width: 100%;
            padding: 9px 14px;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.9rem;
            cursor: pointer;
            background: var(--primary);
            color: #ffffff;
            margin-bottom: 10px;
        }
        button:hover { background: var(--primary-hover); }
        button.btn-green { background: var(--secondary); }
        button.btn-green:hover { background: var(--secondary-hover); }
        .traffic-box {
            background: var(--code-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px;
            font-family: 'Consolas', monospace;
            font-size: 0.82rem;
            color: var(--text);
            max-height: 240px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-all;
            margin-top: 8px;
        }
        .badge {
            display: inline-block;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-py { background: #e0f2fe; color: #0369a1; }
        .badge-js { background: #fef9c3; color: #854d0e; }
        .badge-success { background: var(--success-bg); color: var(--success); }
        .badge-fail { background: var(--danger-bg); color: var(--danger); }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Лабораторна робота №2: Несиметричний шифр RSA (2048 біт)</h1>
    </header>

    <div class="grid">
        <div class="card client-side">
            <h2>Клієнтська сторона <span class="badge badge-js">JavaScript / WebCrypto</span></h2>
            
            <button class="btn-green" onclick="generateClientKeys()">1. Згенерувати клієнтську пару ключів RSA (2048 біт)</button>
            <div id="clientKeyStatus" style="margin-bottom: 8px;"></div>

            <label>Відкритий ключ Клієнта (SPKI Base64):</label>
            <textarea id="clientPubArea" rows="3" readonly placeholder="Клієнтський публічний ключ з'явиться тут..."></textarea>

            <label>Логін для входу:</label>
            <input type="text" id="loginInput" value="student">

            <label>Пароль:</label>
            <input type="text" id="passwordInput" value="lab2_password_2026">

            <button onclick="sendEncryptedAuth()">2. Зашифрувати ключем сервера та відправити</button>

            <label>Розшифрована відповідь сервера (розшифровано приватним ключем клієнта):</label>
            <textarea id="clientDecryptedArea" rows="4" readonly placeholder="Розшифрована секретна відповідь від сервера..."></textarea>
        </div>

        <div class="card server-side">
            <h2>Серверна сторона <span class="badge badge-py">Python / PyCryptodome</span></h2>
            
            <label>Відкритий ключ Сервера (DER/SPKI Base64, RSA 2048 біт):</label>
            <textarea id="serverPubArea" rows="3" readonly></textarea>

            <label>Останній статус автентифікації на сервері:</label>
            <div id="authStatusBadge" style="margin-bottom: 12px;"><span class="badge">Очікування запиту...</span></div>

            <label>Інспектор незахищеного каналу зв'язку (Мережевий трафік):</label>
            <div class="traffic-box" id="trafficLog">Трафік поки що порожній. Зробіть запит для інспекції перехоплення.</div>
        </div>
    </div>
</div>

<script>
let clientKeyPair = null;
let serverPublicKey = null;

async function fetchServerKey() {
    const res = await fetch('/api/server-key');
    const data = await res.json();
    document.getElementById('serverPubArea').value = data.public_key_b64;
    
    const binaryDer = Uint8Array.from(atob(data.public_key_b64), c => c.charCodeAt(0));
    serverPublicKey = await window.crypto.subtle.importKey(
        'spki',
        binaryDer.buffer,
        { name: 'RSA-OAEP', hash: 'SHA-256' },
        true,
        ['encrypt']
    );
    logTraffic("[КЛІЄНТ] Отримано та успішно імпортовано публічний ключ сервера (RSA-2048)");
}

async function generateClientKeys() {
    document.getElementById('clientKeyStatus').innerHTML = "<span style='color: var(--primary);'>Генерація RSA-2048...</span>";
    const t0 = performance.now();
    clientKeyPair = await window.crypto.subtle.generateKey(
        {
            name: 'RSA-OAEP',
            modulusLength: 2048,
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: 'SHA-256'
        },
        true,
        ['encrypt', 'decrypt']
    );
    const t1 = performance.now();
    const pubDer = await window.crypto.subtle.exportKey('spki', clientKeyPair.publicKey);
    const pubB64 = btoa(String.fromCharCode(...new Uint8Array(pubDer)));
    document.getElementById('clientPubArea').value = pubB64;
    document.getElementById('clientKeyStatus').innerHTML = `<span class="badge badge-success">Ключі клієнта згенеровано за ${Math.round(t1 - t0)} мс</span>`;
    logTraffic("[КЛІЄНТ] Згенеровано власну пару ключів RSA 2048 біт через WebCrypto API");
}

function logTraffic(msg) {
    const box = document.getElementById('trafficLog');
    const now = new Date().toLocaleTimeString();
    box.innerHTML += `[${now}] ${msg}\n\n`;
    box.scrollTop = box.scrollHeight;
}

async function sendEncryptedAuth() {
    if (!clientKeyPair) {
        alert("Спочатку згенеруйте ключі клієнта (кнопка 1)!");
        return;
    }
    if (!serverPublicKey) {
        await fetchServerKey();
    }

    const login = document.getElementById('loginInput').value;
    const password = document.getElementById('passwordInput').value;

    const payload = JSON.stringify({
        login: login,
        password: password,
        timestamp: Date.now()
    });

    logTraffic(`[КЛІЄНТ -> КАНАЛ] Відкриті дані перед шифруванням: ${payload}`);

    const encBuffer = await window.crypto.subtle.encrypt(
        { name: 'RSA-OAEP' },
        serverPublicKey,
        new TextEncoder().encode(payload)
    );
    const encB64 = btoa(String.fromCharCode(...new Uint8Array(encBuffer)));
    const clientPubB64 = document.getElementById('clientPubArea').value;

    logTraffic(`[КАНАЛ ЗВ'ЯЗКУ] Передається зашифрований пакет клієнта (Ciphertext Base64):\n${encB64}`);

    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            client_public_key: clientPubB64,
            encrypted_payload: encB64
        })
    });

    const data = await res.json();
    logTraffic(`[КАНАЛ ЗВ'ЯЗКУ] Отримано зашифровану відповідь від сервера:\n${data.encrypted_response}`);

    const badge = document.getElementById('authStatusBadge');
    if (data.status === 'SUCCESS') {
        badge.innerHTML = '<span class="badge badge-success">АВТЕНТИФІКАЦІЯ УСПІШНА (200 OK)</span>';
    } else {
        badge.innerHTML = '<span class="badge badge-fail">ПОМИЛКА АВТЕНТИФІКАЦІЇ</span>';
    }

    const encRespBuf = Uint8Array.from(atob(data.encrypted_response), c => c.charCodeAt(0));
    try {
        const decRespBuf = await window.crypto.subtle.decrypt(
            { name: 'RSA-OAEP' },
            clientKeyPair.privateKey,
            encRespBuf
        );
        const decText = new TextDecoder().decode(decRespBuf);
        document.getElementById('clientDecryptedArea').value = decText;
        logTraffic(`[КЛІЄНТ] Успішно розшифровано відповідь сервера власним приватним ключем:\n${decText}`);
    } catch (e) {
        document.getElementById('clientDecryptedArea').value = "Помилка розшифрування: " + e.message;
        logTraffic(`[КЛІЄНТ] Помилка розшифрування: ${e.message}`);
    }
}

fetchServerKey();
</script>
</body>
</html>
"""

class RSAServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/index'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/api/server-key':
            payload = {
                "key_type": "RSA-OAEP",
                "key_size_bits": 2048,
                "public_key_b64": SERVER_PUBLIC_B64,
                "public_key_pem": SERVER_PUBLIC_PEM
            }
            self._send_json(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/login':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                req = json.loads(body)
                client_pub_b64 = req.get('client_public_key')
                encrypted_payload_b64 = req.get('encrypted_payload')

                enc_data = base64.b64decode(encrypted_payload_b64)
                cipher_server = PKCS1_OAEP.new(SERVER_RSA_KEY, hashAlgo=SHA256)
                decrypted_bytes = cipher_server.decrypt(enc_data)
                auth_data = json.loads(decrypted_bytes.decode('utf-8'))

                login = auth_data.get('login', '')
                password = auth_data.get('password', '')

                if login in USER_DATABASE and USER_DATABASE[login] == password:
                    status = "SUCCESS"
                    resp_obj = {
                        "status": "AUTHORIZED",
                        "user": login,
                        "token": f"TOKEN_RSA_{int(time.time())}",
                        "msg": "Успішна автентифікація RSA-2048",
                        "time": int(time.time())
                    }
                else:
                    status = "FAILED"
                    resp_obj = {
                        "status": "UNAUTHORIZED",
                        "user": login,
                        "error": "Невірний пароль",
                        "time": int(time.time())
                    }

                client_pub_bytes = base64.b64decode(client_pub_b64)
                client_rsa = RSA.import_key(client_pub_bytes)
                cipher_client = PKCS1_OAEP.new(client_rsa, hashAlgo=SHA256)

                resp_json_bytes = json.dumps(resp_obj, ensure_ascii=False).encode('utf-8')
                enc_resp_bytes = cipher_client.encrypt(resp_json_bytes)
                enc_resp_b64 = base64.b64encode(enc_resp_bytes).decode('ascii')

                self._send_json({
                    "status": status,
                    "encrypted_response": enc_resp_b64
                })
            except Exception as e:
                import traceback
                traceback.print_exc()
                self._send_json({"status": "ERROR", "error": str(e)}, status=400)
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

def run_server(port=8002):
    server = HTTPServer(('127.0.0.1', port), RSAServerHandler)
    print(f"[СЕРВЕР] RSA Server запущено на http://127.0.0.1:{port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
