class CaesarCipher:
    ALPHABET = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    N = len(ALPHABET)
    CHAR_TO_INDEX = {c: i for i, c in enumerate(ALPHABET)}

    @classmethod
    def encrypt(cls, text: str, shift: int) -> str:
        res = []
        for ch in text:
            is_upper = ch.isupper()
            cu = ch.upper()
            if cu in cls.CHAR_TO_INDEX:
                new_idx = (cls.CHAR_TO_INDEX[cu] + shift) % cls.N
                res_char = cls.ALPHABET[new_idx]
                res.append(res_char if is_upper else res_char.lower())
            else:
                res.append(ch)
        return "".join(res)

    @classmethod
    def decrypt(cls, text: str, shift: int) -> str:
        return cls.encrypt(text, -shift)

class VigenereCipher:
    ALPHABET = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    N = len(ALPHABET)
    CHAR_TO_INDEX = {c: i for i, c in enumerate(ALPHABET)}

    @classmethod
    def _clean_key(cls, key: str) -> str:
        k = [c.upper() for c in key if c.upper() in cls.CHAR_TO_INDEX]
        if not k:
            return "А"
        return "".join(k)

    @classmethod
    def encrypt(cls, text: str, key: str) -> str:
        key_clean = cls._clean_key(key)
        res = []
        k_len = len(key_clean)
        k_idx = 0
        for ch in text:
            is_upper = ch.isupper()
            cu = ch.upper()
            if cu in cls.CHAR_TO_INDEX:
                shift = cls.CHAR_TO_INDEX[key_clean[k_idx % k_len]]
                new_idx = (cls.CHAR_TO_INDEX[cu] + shift) % cls.N
                res_char = cls.ALPHABET[new_idx]
                res.append(res_char if is_upper else res_char.lower())
                k_idx += 1
            else:
                res.append(ch)
        return "".join(res)

    @classmethod
    def decrypt(cls, text: str, key: str) -> str:
        key_clean = cls._clean_key(key)
        res = []
        k_len = len(key_clean)
        k_idx = 0
        for ch in text:
            is_upper = ch.isupper()
            cu = ch.upper()
            if cu in cls.CHAR_TO_INDEX:
                shift = cls.CHAR_TO_INDEX[key_clean[k_idx % k_len]]
                new_idx = (cls.CHAR_TO_INDEX[cu] - shift) % cls.N
                res_char = cls.ALPHABET[new_idx]
                res.append(res_char if is_upper else res_char.lower())
                k_idx += 1
            else:
                res.append(ch)
        return "".join(res)

class OneTimePadManual:
    ROW0 = {1: 'А', 2: 'И', 3: 'Т', 4: 'Е', 5: 'С', 6: 'Н', 7: 'О'}
    ROW8 = {1: 'Б', 2: 'В', 3: 'Г', 4: 'Ґ', 5: 'Д', 6: 'Є', 7: 'Ж', 8: 'З', 9: 'І', 0: 'Ї'}
    ROW9 = {1: 'Й', 2: 'К', 3: 'Л', 4: 'М', 5: 'П', 6: 'Р', 7: 'У', 8: 'Ф', 9: 'Х', 0: 'Ц'}
    ROW0_EXTRA = {1: 'Ч', 2: 'Ш', 3: 'Щ', 4: 'Ь', 5: 'Ю', 6: 'Я', 7: ' '}

    CHAR_TO_CODE = {}
    CODE_TO_CHAR = {}

    for k, v in ROW0.items():
        CHAR_TO_CODE[v] = str(k)
        CODE_TO_CHAR[str(k)] = v
    for k, v in ROW8.items():
        code = '8' + str(k)
        CHAR_TO_CODE[v] = code
        CODE_TO_CHAR[code] = v
    for k, v in ROW9.items():
        code = '9' + str(k)
        CHAR_TO_CODE[v] = code
        CODE_TO_CHAR[code] = v
    for k, v in ROW0_EXTRA.items():
        code = '0' + str(k)
        CHAR_TO_CODE[v] = code
        CODE_TO_CHAR[code] = v

    @classmethod
    def encode_straddling(cls, text: str) -> str:
        digits = []
        for ch in text.upper():
            if ch in cls.CHAR_TO_CODE:
                digits.append(cls.CHAR_TO_CODE[ch])
            elif ch == ' ':
                digits.append(cls.CHAR_TO_CODE[' '])
        return "".join(digits)

    @classmethod
    def decode_straddling(cls, digits: str) -> str:
        res = []
        i = 0
        n = len(digits)
        while i < n:
            d = digits[i]
            if d in "1234567":
                res.append(cls.CODE_TO_CHAR.get(d, '?'))
                i += 1
            elif d in "890":
                if i + 1 < n:
                    code = digits[i:i+2]
                    res.append(cls.CODE_TO_CHAR.get(code, '?'))
                    i += 2
                else:
                    break
            else:
                i += 1
        return "".join(res)

    @classmethod
    def encrypt(cls, text: str, key_text_or_digits: str) -> dict:
        m_digits = cls.encode_straddling(text)
        if any(c.isalpha() for c in key_text_or_digits):
            k_base = cls.encode_straddling(key_text_or_digits)
        else:
            k_base = "".join(c for c in key_text_or_digits if c.isdigit())
        if not k_base:
            k_base = "1"
        
        full_k = (k_base * (len(m_digits) // len(k_base) + 1))[:len(m_digits)]
        c_digits = "".join(str((int(m) + int(k)) % 10) for m, k in zip(m_digits, full_k))

        return {
            "plain_text": text,
            "plain_digits": m_digits,
            "key_base": k_base,
            "full_key_digits": full_k,
            "cipher_digits": c_digits
        }

    @classmethod
    def decrypt(cls, cipher_digits: str, key_text_or_digits: str) -> dict:
        c_clean = "".join(c for c in cipher_digits if c.isdigit())
        if any(c.isalpha() for c in key_text_or_digits):
            k_base = cls.encode_straddling(key_text_or_digits)
        else:
            k_base = "".join(c for c in key_text_or_digits if c.isdigit())
        if not k_base:
            k_base = "1"

        full_k = (k_base * (len(c_clean) // len(k_base) + 1))[:len(c_clean)]
        p_digits = "".join(str((int(c) - int(k)) % 10) for c, k in zip(c_clean, full_k))
        decoded_text = cls.decode_straddling(p_digits)

        return {
            "cipher_digits": c_clean,
            "key_base": k_base,
            "full_key_digits": full_k,
            "plain_digits": p_digits,
            "decoded_text": decoded_text
        }
