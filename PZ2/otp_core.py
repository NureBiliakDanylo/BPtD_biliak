import secrets

class MachineOTP:
    @staticmethod
    def generate_key(length: int) -> bytes:
        return secrets.token_bytes(length)

    @staticmethod
    def encrypt_bytes(data: bytes, key: bytes) -> bytes:
        if len(key) < len(data):
            raise ValueError("Ключ повинен бути не коротшим за дані!")
        return bytes(d ^ k for d, k in zip(data, key))

    @staticmethod
    def decrypt_bytes(cipher: bytes, key: bytes) -> bytes:
        return MachineOTP.encrypt_bytes(cipher, key)

    @classmethod
    def encrypt_text(cls, text: str, key_bytes: bytes = None) -> tuple[str, str, str]:
        data = text.encode('utf-8')
        if key_bytes is None:
            key_bytes = cls.generate_key(len(data))
        elif len(key_bytes) < len(data):
            key_bytes = (key_bytes * (len(data) // len(key_bytes) + 1))[:len(data)]
        
        cipher = cls.encrypt_bytes(data, key_bytes)
        return cipher.hex().upper(), key_bytes.hex().upper(), cipher.decode('latin-1')

    @classmethod
    def decrypt_text(cls, cipher_hex: str, key_hex: str) -> str:
        cipher = bytes.fromhex(cipher_hex)
        key = bytes.fromhex(key_hex)
        if len(key) < len(cipher):
            key = (key * (len(cipher) // len(key) + 1))[:len(cipher)]
        decrypted = cls.decrypt_bytes(cipher, key)
        return decrypted.decode('utf-8', errors='replace')

class CryptanalysisLab:
    UKR_ALPHABET = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    N = len(UKR_ALPHABET)
    CHAR_TO_IDX = {c: i for i, c in enumerate(UKR_ALPHABET)}

    UKR_FREQS = {
        'О': 0.0928, 'А': 0.0834, 'И': 0.0623, 'І': 0.0579, 'Н': 0.0532,
        'В': 0.0450, 'Е': 0.0449, 'Р': 0.0446, 'Т': 0.0444, 'С': 0.0387,
        'К': 0.0352, 'Д': 0.0305, 'У': 0.0302, 'Л': 0.0298, 'М': 0.0296,
        'П': 0.0267, 'З': 0.0217, 'Я': 0.0216, 'Ь': 0.0177, 'Б': 0.0174,
        'Г': 0.0149, 'Ч': 0.0139, 'Й': 0.0124, 'Х': 0.0117, 'Ж': 0.0090,
        'Ш': 0.0084, 'Ї': 0.0076, 'Ц': 0.0061, 'Ю': 0.0055, 'Є': 0.0049,
        'Щ': 0.0041, 'Ф': 0.0028, 'Ґ': 0.0003
    }

    @classmethod
    def break_caesar(cls, ciphertext: str) -> list[dict]:
        results = []
        for shift in range(cls.N):
            candidate = []
            for ch in ciphertext:
                cu = ch.upper()
                if cu in cls.CHAR_TO_IDX:
                    orig_idx = (cls.CHAR_TO_IDX[cu] - shift) % cls.N
                    res_c = cls.UKR_ALPHABET[orig_idx]
                    candidate.append(res_c if ch.isupper() else res_c.lower())
                else:
                    candidate.append(ch)
            cand_str = "".join(candidate)

            letters = [c.upper() for c in cand_str if c.upper() in cls.UKR_FREQS]
            score = 0.0
            if letters:
                total = len(letters)
                cand_counts = {}
                for l in letters:
                    cand_counts[l] = cand_counts.get(l, 0) + 1
                for l, count in cand_counts.items():
                    obs_p = count / total
                    exp_p = cls.UKR_FREQS.get(l, 0.0001)
                    score += obs_p * exp_p

            results.append({
                "shift": shift,
                "score": score,
                "text": cand_str
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    @staticmethod
    def two_time_pad_xor(cipher1_bytes: bytes, cipher2_bytes: bytes) -> bytes:
        min_len = min(len(cipher1_bytes), len(cipher2_bytes))
        return bytes(c1 ^ c2 for c1, c2 in zip(cipher1_bytes[:min_len], cipher2_bytes[:min_len]))

    @classmethod
    def crib_drag(cls, c1_xor_c2: bytes, crib_text: str) -> list[dict]:
        crib_bytes = crib_text.encode('utf-8')
        matches = []
        crib_len = len(crib_bytes)
        if crib_len > len(c1_xor_c2):
            return matches

        for pos in range(len(c1_xor_c2) - crib_len + 1):
            sub = c1_xor_c2[pos:pos+crib_len]
            revealed = bytes(s ^ c for s, c in zip(sub, crib_bytes))
            dec_str = revealed.decode('utf-8', errors='ignore')
            if len(dec_str) >= 2 and all(c.isprintable() or c.isspace() for c in dec_str):
                matches.append({
                    "position": pos,
                    "crib": crib_text,
                    "revealed_counterpart": dec_str
                })

        return matches
