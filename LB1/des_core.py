import math

IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9,  1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

IP_INV = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9,  49, 17, 57, 25
]

E = [
    32,  1,  2,  3,  4,  5,
     4,  5,  6,  7,  8,  9,
     8,  9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32,  1
]

P = [
    16,  7, 20, 21,
    29, 12, 28, 17,
     1, 15, 23, 26,
     5, 18, 31, 10,
     2,  8, 24, 14,
    32, 27,  3,  9,
    19, 13, 30,  6,
    22, 11,  4, 25
]

S_BOXES = [
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
    ],
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
    ],
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
    ],
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    ],
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    ],
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    ],
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    ]
]

PC1 = [
    57, 49, 41, 33, 25, 17,  9,
     1, 58, 50, 42, 34, 26, 18,
    10,  2, 59, 51, 43, 35, 27,
    19, 11,  3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
     7, 62, 54, 46, 38, 30, 22,
    14,  6, 61, 53, 45, 37, 29,
    21, 13,  5, 28, 20, 12,  4
]

SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

PC2 = [
    14, 17, 11, 24,  1,  5,
     3, 28, 15,  6, 21, 10,
    23, 19, 12,  4, 26,  8,
    16,  7, 27, 20, 13,  2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

WEAK_KEYS = {
    0x0101010101010101: "Слабкий ключ (всі 0 після паритету)",
    0xFEFEFEFEFEFEFEFE: "Слабкий ключ (всі 1 після паритету)",
    0x1F1F1F1F1F1F1F1F: "Слабкий ключ (C0=0, D0=1)",
    0xE0E0E0E0E0E0E0E0: "Слабкий ключ (C0=1, D0=0)"
}

SEMI_WEAK_KEYS = {
    0x01FE01FE01FE01FE: "Напівслабкий ключ",
    0xFE01FE01FE01FE01: "Напівслабкий ключ",
    0x1FE01FE01FE01FE0: "Напівслабкий ключ",
    0xE01FE01FE01FE01F: "Напівслабкий ключ",
    0x01E001E001E001E0: "Напівслабкий ключ",
    0xE001E001E001E001: "Напівслабкий ключ",
    0x1FFE1FFE1FFE1FFE: "Напівслабкий ключ",
    0xFE1FFE1FFE1FFE1F: "Напівслабкий ключ",
    0x011F011F011F011F: "Напівслабкий ключ",
    0x1F011F011F011F01: "Напівслабкий ключ",
    0xE0FEE0FEE0FEE0FE: "Напівслабкий ключ",
    0xFEE0FEE0FEE0FEE0: "Напівслабкий ключ"
}

def check_weak_key(key_bytes: bytes) -> tuple[bool, str]:
    if len(key_bytes) != 8:
        raise ValueError("Розмір ключа DES повинен бути рівно 8 байтів (64 біти)")
    val = int.from_bytes(key_bytes, byteorder='big')
    if val in WEAK_KEYS:
        return True, WEAK_KEYS[val]
    if val in SEMI_WEAK_KEYS:
        return True, SEMI_WEAK_KEYS[val]
    return False, "Ключ коректний (не є слабким)"

def bytes_to_bits(data: bytes) -> list[int]:
    bits = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits

def bits_to_bytes(bits: list[int]) -> bytes:
    res = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i:i+8]:
            byte = (byte << 1) | bit
        res.append(byte)
    return bytes(res)

def permute(bits: list[int], table: list[int]) -> list[int]:
    return [bits[pos - 1] for pos in table]

def left_rotate(bits: list[int], n: int) -> list[int]:
    return bits[n:] + bits[:n]

def xor_bits(a: list[int], b: list[int]) -> list[int]:
    return [x ^ y for x, y in zip(a, b)]

def generate_round_keys(key_bytes: bytes) -> list[list[int]]:
    key_bits = bytes_to_bits(key_bytes)
    pc1_bits = permute(key_bits, PC1)
    c = pc1_bits[:28]
    d = pc1_bits[28:]

    round_keys = []
    for shift in SHIFTS:
        c = left_rotate(c, shift)
        d = left_rotate(d, shift)
        cd = c + d
        round_key = permute(cd, PC2)
        round_keys.append(round_key)
    return round_keys

def feistel_function(r_bits: list[int], round_key: list[int]) -> list[int]:
    expanded = permute(r_bits, E)
    xored = xor_bits(expanded, round_key)
    s_output = []
    for i in range(8):
        block = xored[i * 6:(i + 1) * 6]
        row = (block[0] << 1) | block[5]
        col = (block[1] << 3) | (block[2] << 2) | (block[3] << 1) | block[4]
        val = S_BOXES[i][row][col]
        for bit_idx in range(3, -1, -1):
            s_output.append((val >> bit_idx) & 1)
    return permute(s_output, P)

def calculate_entropy(bits: list[int]) -> float:
    total = len(bits)
    if total == 0:
        return 0.0
    ones = sum(bits)
    p = ones / total
    if p == 0.0 or p == 1.0:
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)

def des_process_block(block_bytes: bytes, round_keys: list[list[int]]) -> tuple[bytes, list[dict]]:
    bits = bytes_to_bits(block_bytes)
    ip_bits = permute(bits, IP)
    l = ip_bits[:32]
    r = ip_bits[32:]

    round_info = []

    for round_num, k in enumerate(round_keys, start=1):
        f_res = feistel_function(r, k)
        new_r = xor_bits(l, f_res)
        new_l = r
        l, r = new_l, new_r

        current_state = l + r
        entropy_val = calculate_entropy(current_state)
        ones_count = sum(current_state)

        round_info.append({
            "round": round_num,
            "ones_count": ones_count,
            "zeros_count": 64 - ones_count,
            "probability_one": round(ones_count / 64.0, 4),
            "entropy": round(entropy_val, 5),
            "state_hex": f"{int(''.join(map(str, current_state)), 2):016X}"
        })

    pre_output = r + l
    final_bits = permute(pre_output, IP_INV)
    return bits_to_bytes(final_bits), round_info

def pad_pkcs7(data: bytes) -> bytes:
    pad_len = 8 - (len(data) % 8)
    return data + bytes([pad_len] * pad_len)

def unpad_pkcs7(data: bytes) -> bytes:
    if not data:
        raise ValueError("Порожні дані для зняття PKCS7")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 8:
        raise ValueError("Невірне заповнення PKCS7")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Помилка валідації PKCS7")
    return data[:-pad_len]

class DESCipher:
    def __init__(self, key: bytes):
        if len(key) != 8:
            raise ValueError("Ключ DES повинен мати довжину 8 байт (64 біти)!")
        self.key = key
        is_weak, msg = check_weak_key(key)
        self.is_weak = is_weak
        self.key_status = msg
        self.encrypt_subkeys = generate_round_keys(key)
        self.decrypt_subkeys = list(reversed(self.encrypt_subkeys))

    def encrypt(self, data: bytes) -> tuple[bytes, list[dict]]:
        padded = pad_pkcs7(data)
        ciphertext = bytearray()
        all_rounds = []
        for i in range(0, len(padded), 8):
            block = padded[i:i+8]
            enc_block, rounds = des_process_block(block, self.encrypt_subkeys)
            ciphertext.extend(enc_block)
            if not all_rounds:
                all_rounds = rounds
        return bytes(ciphertext), all_rounds

    def decrypt(self, data: bytes) -> tuple[bytes, list[dict]]:
        if len(data) % 8 != 0 or len(data) == 0:
            raise ValueError("Довжина шифротексту повинна бути кратна 8 байтам")
        plaintext = bytearray()
        all_rounds = []
        for i in range(0, len(data), 8):
            block = data[i:i+8]
            dec_block, rounds = des_process_block(block, self.decrypt_subkeys)
            plaintext.extend(dec_block)
            if not all_rounds:
                all_rounds = rounds
        unpadded = unpad_pkcs7(bytes(plaintext))
        return unpadded, all_rounds
