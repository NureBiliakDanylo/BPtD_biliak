const { subtle } = require('crypto');

const SERVER_URL = 'http://127.0.0.1:8002';

async function main() {
    console.log("==========================================================");
    console.log("  КЛІЄНТ RSA (Node.js / Web Crypto API, Ключ 2048 біт)   ");
    console.log("==========================================================");

    console.log("\n[1] Генерація власної пари RSA-2048 ключів клієнта...");
    const t0 = Date.now();
    const clientKeyPair = await subtle.generateKey(
        {
            name: 'RSA-OAEP',
            modulusLength: 2048,
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: 'SHA-256'
        },
        true,
        ['encrypt', 'decrypt']
    );
    console.log(`[+] Ключі клієнта успішно згенеровано за ${Date.now() - t0} мс.`);

    const clientPubDer = await subtle.exportKey('spki', clientKeyPair.publicKey);
    const clientPubB64 = Buffer.from(clientPubDer).toString('base64');
    console.log(`[+] Публічний ключ клієнта (SPKI Base64): ${clientPubB64}...`);

    console.log(`\n[2] Запит відкритого ключа сервера з ${SERVER_URL}/api/server-key ...`);
    const keyResp = await fetch(`${SERVER_URL}/api/server-key`);
    if (!keyResp.ok) {
        throw new Error(`Сервер недоступний: ${keyResp.statusText}`);
    }
    const keyData = await keyResp.json();
    console.log(`[+] Отримано публічний ключ сервера! Розмір: ${keyData.key_size_bits} біт.`);

    const serverPubDer = Buffer.from(keyData.public_key_b64, 'base64');
    const serverPubKey = await subtle.importKey(
        'spki',
        serverPubDer,
        { name: 'RSA-OAEP', hash: 'SHA-256' },
        false,
        ['encrypt']
    );

    const credentials = {
        login: "student",
        password: "lab2_password_202622",
        client_timestamp: new Date().toISOString()
    };
    const plainText = JSON.stringify(credentials);
    console.log(`\n[3] Відкриті дані для відправки: ${plainText}`);

    const encBuffer = await subtle.encrypt(
        { name: 'RSA-OAEP' },
        serverPubKey,
        Buffer.from(plainText, 'utf-8')
    );
    const encPayloadB64 = Buffer.from(encBuffer).toString('base64');
    console.log(`[+] Дані зашифровано публічним ключем сервера!`);
    console.log(`[+] Зашифрований пакет (Ciphertext Base64): ${encPayloadB64}...`);

    console.log(`\n[4] Відправка зашифрованого запиту на ${SERVER_URL}/api/login ...`);
    const authResp = await fetch(`${SERVER_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            client_public_key: clientPubB64,
            encrypted_payload: encPayloadB64
        })
    });
    const authResult = await authResp.json();
    console.log(`[+] Відповідь сервера отримана. Статус: ${authResult.status}`);
    console.log(`[+] Зашифрована відповідь сервера: ${authResult.encrypted_response}...`);

    console.log(`\n[5] Розшифрування відповіді власним закритим ключем клієнта...`);
    const encRespBuf = Buffer.from(authResult.encrypted_response, 'base64');
    const decRespBuf = await subtle.decrypt(
        { name: 'RSA-OAEP' },
        clientKeyPair.privateKey,
        encRespBuf
    );
    const decryptedJson = Buffer.from(decRespBuf).toString('utf-8');
    const responseObj = JSON.parse(decryptedJson);

    console.log("\n==========================================================");
    console.log("   УСПІШНО РОЗШИФРОВАНА СЕКРЕТНА ВІДПОВІДЬ СЕРВЕРА:       ");
    console.log("==========================================================");
    console.dir(responseObj, { depth: null, colors: true });
    console.log("==========================================================\n");
}

main().catch(err => {
    console.error("[!] Помилка виконання клієнта:", err.message);
    process.exit(1);
});
