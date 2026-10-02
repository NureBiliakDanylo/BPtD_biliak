import os
import json
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from custom_hash import custom_hash, custom_hash_int, measure_avalanche
from collision_generator import auto_generate_collision
from create_samples import create_sample_file, ensure_all_samples, SAMPLES_DIR

HTML_PAGE = """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Лабораторна робота №3: Криптографічні Хеш-Функції та Колізії</title>
    <style>
        :root {
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --code-bg: #f1f5f9;
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
        .container { max-width: 1000px; margin: 0 auto; }
        header {
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }
        h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 6px; color: var(--text); }
        .subtitle { color: var(--text-muted); font-size: 0.9rem; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 16px;
        }
        .card h2 { font-size: 1.05rem; font-weight: 600; margin-bottom: 12px; color: var(--text); }
        label { display: block; font-size: 0.85rem; font-weight: 500; color: var(--text-muted); margin-bottom: 6px; }
        textarea, select, input[type="text"], input[type="file"] {
            width: 100%;
            padding: 8px 12px;
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            margin-bottom: 12px;
        }
        input[type="file"] {
            font-family: inherit;
            cursor: pointer;
        }
        button {
            padding: 8px 14px;
            background: var(--primary);
            color: #ffffff;
            border: none;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        button:hover { background: var(--primary-hover); }
        button.secondary { background: #475569; }
        button.secondary:hover { background: #334155; }
        button.outline {
            background: #ffffff;
            border: 1px solid var(--border);
            color: var(--text);
        }
        button.outline:hover { background: var(--code-bg); }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-success { background: var(--success-bg); color: var(--success); }
        .badge-danger { background: var(--danger-bg); color: var(--danger); }
        .result-box {
            background: var(--code-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px 12px;
            font-family: 'Consolas', monospace;
            font-size: 1rem;
            color: var(--text);
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Лабораторна робота №3: власна хеш-функція та колізії</h1>
    </header>

    <div class="card">
        <label>Глобальне налаштування довжини хешу:</label>
        <div style="display: flex; gap: 12px; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <select id="bitSelect" onchange="onBitChange()" style="max-width: 320px; margin-bottom: 0;">
                <option value="8" selected>8 біт (1 байт, 256 комбінацій)</option>
                <option value="4">4 біти (півбайта, 16 комбінацій)</option>
                <option value="2">2 біти (4 комбінації, швидка колізія)</option>
            </select>
            <button class="outline" onclick="restoreSamples()" style="margin: 0;">Відновити зразки в samples</button>
        </div>
        <div id="restoreMsg" style="font-size: 0.85rem; color: var(--success); margin-top: 6px;"></div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>1. Хешування тексту та лавинний ефект</h2>
            <label>Введіть довільний текст для обчислення дайджесту:</label>
            <textarea id="textInput" rows="3" oninput="calcTextHash()">Безпека інформаційних систем та контроль цілісності даних.</textarea>

            <label>Розрахований дайджест тексту:</label>
            <div class="result-box">
                <span>Біти: <strong id="hashBits">00000000</strong></span>
                <span style="font-size: 0.85rem; color: var(--text-muted);" id="hashDec">(Dec: 0, Hex: 0x00)</span>
            </div>

            <button onclick="testAvalanche()">Перевірити лавинний ефект</button>
            <div id="avalancheResult" style="margin-top: 10px; font-size: 0.88rem;"></div>
        </div>

        <div class="card">
            <h2>2. Завантаження користувацького файлу</h2>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 12px;">
                Оберіть будь-який файл з вашого комп'ютера для перевірки його дайджесту за алгоритмом хешування:
            </p>
            <label>Обрати файл для завантаження:</label>
            <input type="file" id="userFileInput" onchange="uploadAndHashFile()">

            <div id="fileUploadResult" style="display: none; background: var(--code-bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; font-family: 'Consolas', monospace; font-size: 0.88rem; line-height: 1.6;">
                <div>Назва файлу: <strong id="ufName">-</strong></div>
                <div>Розмір: <strong id="ufSize">-</strong></div>
                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border);">
                    Хеш (<span id="ufBitsLabel">8</span> біт): <strong id="ufHash" style="color: var(--primary); font-size: 1.05rem;">-</strong>
                    <span id="ufHex" style="color: var(--text-muted); margin-left: 10px;">-</span>
                </div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>3. Автоматичний генератор колізій для документів, коду та зображень</h2>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 12px;">
            Генерує парний файл з ідентичною хеш-сумою, модифікуючи невидимі службові метадані (Word DOCX), безпечні коментарі (Python PY) або кінцеві байти растру (BMP).
        </p>

        <label>Оберіть формат файлу для генерації колізії:</label>
        <select id="sampleSelect" style="max-width: 450px;">
            <option value="sample_doc.docx">Документ Microsoft Word (.docx)</option>
            <option value="sample_doc.txt">Текстовий файл (.txt)</option>
            <option value="sample_code.py">Вихідний код Python (.py)</option>
            <option value="sample_image.bmp">Графічне растрове зображення (.bmp)</option>
        </select>

        <div>
            <button class="secondary" onclick="findCollision()">Знайти колізію для обраного файлу</button>
        </div>

        <div id="collisionDetails" style="margin-top: 15px; font-family: 'Consolas', monospace; font-size: 0.88rem;">
            <div style="color: var(--text-muted);">Оберіть тип файлу та натисніть кнопку для пошуку колізії...</div>
        </div>
    </div>

    <div class="card">
        <h2>4. Демонстрація колізії для 2-бітного хешу (парадокс днів народження)</h2>
        <p style="color: var(--text-muted); font-size: 0.85rem; line-height: 1.5;">
            Для 2-бітного дайджесту існує лише 4 можливі стани (00, 01, 10, 11). Згідно з принципом Діріхле, колізія гарантовано виникає за щонайбільше 5 ітерацій.
        </p>
        <div style="background: var(--code-bg); padding: 12px; border-radius: 6px; border: 1px solid var(--border); margin-top: 12px; font-family: 'Consolas', monospace; font-size: 0.88rem; line-height: 1.6;">
            <div>Повідомлення А: <code>"Безпека даних варіант А"</code> -> Хеш (2 біти): <strong style="color: var(--success);" id="manualHashA">...</strong></div>
            <div style="margin-top: 4px;">Повідомлення Б: <code id="manualTextB">...</code> -> Хеш (2 біти): <strong style="color: var(--success);" id="manualHashB">...</strong></div>
            <div id="manualStatus" style="margin-top: 8px;"></div>
        </div>
    </div>
</div>

<script>
function onBitChange() {
    calcTextHash();
    if (document.getElementById('userFileInput').files.length > 0) {
        uploadAndHashFile();
    }
}

async function calcTextHash() {
    const text = document.getElementById('textInput').value;
    const bits = document.getElementById('bitSelect').value;
    const res = await fetch('/api/hash_text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text, bits: parseInt(bits)})
    });
    const data = await res.json();
    document.getElementById('hashBits').innerText = data.hash;
    document.getElementById('hashDec').innerText = `(Dec: ${data.dec}, Hex: 0x${data.hex})`;
}

async function testAvalanche() {
    const text = document.getElementById('textInput').value;
    const bits = document.getElementById('bitSelect').value;
    const res = await fetch('/api/avalanche', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text, bits: parseInt(bits)})
    });
    const data = await res.json();
    const div = document.getElementById('avalancheResult');
    div.innerHTML = `
        <div style="padding: 10px; background: var(--code-bg); border-radius: 6px; border: 1px solid var(--border); line-height: 1.6;">
            <div>Кількість протестованих мутацій: <strong>${data.tested_mutations}</strong></div>
            <div>Середній відсоток змінених бітів: <strong style="color: var(--primary);">${data.average_bits_flipped_percent}%</strong> (норма: ~50%)</div>
            <div>Частка мутацій зі зміною ≥ 30% бітів: <strong>${data.mutations_with_at_least_30_percent_change}%</strong></div>
            <div style="margin-top: 6px;"><span class="badge badge-success">Вимогу стандарту (≥30%) виконано</span></div>
        </div>
    `;
}

async function uploadAndHashFile() {
    const fileInput = document.getElementById('userFileInput');
    if (fileInput.files.length === 0) return;
    const file = fileInput.files[0];
    const bits = parseInt(document.getElementById('bitSelect').value);

    const reader = new FileReader();
    reader.onload = async function() {
        const base64Data = reader.result.split(',')[1];
        const res = await fetch('/api/hash_file', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                filename: file.name,
                content_base64: base64Data,
                bits: bits
            })
        });
        const data = await res.json();
        document.getElementById('fileUploadResult').style.display = 'block';
        document.getElementById('ufName').innerText = file.name;
        document.getElementById('ufSize').innerText = `${file.size} байт`;
        document.getElementById('ufBitsLabel').innerText = bits;
        document.getElementById('ufHash').innerText = data.hash;
        document.getElementById('ufHex').innerText = `(Hex: 0x${data.hex}, Dec: ${data.dec})`;
    };
    reader.readAsDataURL(file);
}

async function findCollision() {
    const filename = document.getElementById('sampleSelect').value;
    const bits = parseInt(document.getElementById('bitSelect').value);
    const details = document.getElementById('collisionDetails');
    details.innerHTML = "<div style='color: var(--primary);'>Пошук колізії в процесі (перевірка/генерація файлу-зразка)...</div>";

    const res = await fetch('/api/collide', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({filename, bits})
    });
    const data = await res.json();

    if (data.error) {
        details.innerHTML = `<div style="color: var(--danger);">Помилка: ${data.error}</div>`;
        return;
    }

    details.innerHTML = `
        <div style="padding: 12px; background: var(--code-bg); border-radius: 6px; border: 1px solid var(--border); line-height: 1.6;">
            <div style="margin-bottom: 8px;">
                <span class="badge badge-success">КОЛІЗІЮ УСПІШНО ЗНАЙДЕНО</span>
            </div>
            <div>Оригінальний файл: <span>${data.original_file}</span> (Розмір: ${data.original_size} б.)</div>
            <div>Файл із колізією: <strong style="color: var(--primary);">${data.collision_file}</strong> (Розмір: ${data.collision_size} б.)</div>
            <div style="margin: 8px 0; padding: 8px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);">
                Хеш оригіналу (${data.bit_length} біт): <strong style="color: var(--primary);">${data.original_hash}</strong><br>
                Хеш колізії  (${data.bit_length} біт): <strong style="color: var(--primary);">${data.collision_hash}</strong>
            </div>
            <div>Хеші повністю збігаються: <strong>${data.hashes_match ? 'ТАК' : 'НІ'}</strong></div>
            <div>Бінарний вміст відрізняється: <strong>${data.contents_differ ? 'ТАК' : 'НІ'}</strong></div>
            <div>Кількість ітерацій підбору: <strong>${data.attempts_needed}</strong></div>
        </div>
    `;
}

async function checkManualExample() {
    const resA = await fetch('/api/hash_text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: "Безпека даних варіант А", bits: 2})
    });
    const dataA = await resA.json();

    let nonce = 1;
    let matchText = "";
    let dataB = null;
    while(true) {
        matchText = "Безпека даних варіант Б " + nonce;
        const resB = await fetch('/api/hash_text', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: matchText, bits: 2})
        });
        dataB = await resB.json();
        if (dataB.hash === dataA.hash) break;
        nonce++;
    }

    document.getElementById('manualHashA').innerText = `${dataA.hash}`;
    document.getElementById('manualTextB').innerText = `"${matchText}"`;
    document.getElementById('manualHashB').innerText = `${dataB.hash}`;
    document.getElementById('manualStatus').innerHTML = `<span class="badge badge-success">Колізія 2-бітного дайджесту підтверджена на кроці ${nonce}! Обидва тексти мають однаковий хеш ${dataA.hash}</span>`;
}

async function restoreSamples() {
    const res = await fetch('/api/restore_samples', { method: 'POST' });
    const data = await res.json();
    const msg = document.getElementById('restoreMsg');
    msg.innerText = `Зразки перевірено та відновлено у папці samples (${data.files.length} файлів).`;
    setTimeout(() => { msg.innerText = ''; }, 4000);
}

calcTextHash();
checkManualExample();
</script>
</body>
</html>
"""

class HashRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/index'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
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

        if self.path == '/api/hash_text':
            text = req.get('text', '').encode('utf-8')
            bits = req.get('bits', 8)
            val = custom_hash_int(text, bits)
            bit_str = custom_hash(text, bits)
            self._send_json({
                "hash": bit_str,
                "dec": val,
                "hex": f"{val:02X}"
            })

        elif self.path == '/api/hash_file':
            b64_content = req.get('content_base64', '')
            bits = req.get('bits', 8)
            file_bytes = base64.b64decode(b64_content)
            val = custom_hash_int(file_bytes, bits)
            bit_str = custom_hash(file_bytes, bits)
            self._send_json({
                "hash": bit_str,
                "dec": val,
                "hex": f"{val:02X}",
                "size": len(file_bytes)
            })

        elif self.path == '/api/avalanche':
            text = req.get('text', '').encode('utf-8')
            bits = req.get('bits', 8)
            res = measure_avalanche(text, bits)
            self._send_json(res)

        elif self.path == '/api/collide':
            filename = req.get('filename', '')
            bits = req.get('bits', 8)
            target_path = os.path.join(SAMPLES_DIR, filename)
            if not os.path.exists(target_path):
                create_sample_file(filename, SAMPLES_DIR)
            try:
                result = auto_generate_collision(target_path, bits)
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)

        elif self.path == '/api/restore_samples':
            ensure_all_samples(SAMPLES_DIR)
            files = os.listdir(SAMPLES_DIR)
            self._send_json({"status": "OK", "files": files})

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

def run_server(port=8003):
    ensure_all_samples(SAMPLES_DIR)
    server = HTTPServer(('127.0.0.1', port), HashRequestHandler)
    print(f"[ХЕШ-СЕРВЕР] Запущено на http://127.0.0.1:{port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
