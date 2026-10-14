
import os
import hashlib
from Crypto.Cipher import AES

DH_PRIME_P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF", 16
)
DH_GENERATOR_G = 2

class DiffieHellmanParticipant:
    def __init__(self, name: str, p: int = DH_PRIME_P, g: int = DH_GENERATOR_G):
        self.name = name
        self.p = p
        self.g = g
        self.private_key = int.from_bytes(os.urandom(32), 'big') % (self.p - 2) + 2
        self.public_key = pow(self.g, self.private_key, self.p)
        self.shared_key_int = None
        self.symmetric_key = None

    def compute_pairwise_secret(self, peer_public_key: int) -> int:
        self.shared_key_int = pow(peer_public_key, self.private_key, self.p)
        self.symmetric_key = hashlib.sha256(self.shared_key_int.to_bytes((self.shared_key_int.bit_length() + 7) // 8, 'big')).digest()
        return self.shared_key_int

    def set_group_secret(self, group_secret_int: int):
        self.shared_key_int = group_secret_int
        self.symmetric_key = hashlib.sha256(group_secret_int.to_bytes((group_secret_int.bit_length() + 7) // 8, 'big')).digest()


def pad_pkcs7(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def unpad_pkcs7(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16 or data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Помилка PKCS7 доповнення")
    return data[:-pad_len]

def aes_encrypt(key: bytes, plaintext: str) -> dict:
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad_pkcs7(plaintext.encode('utf-8'))
    ciphertext = cipher.encrypt(padded)
    return {
        "iv_hex": iv.hex(),
        "ciphertext_hex": ciphertext.hex()
    }

def aes_decrypt(key: bytes, iv_hex: str, ciphertext_hex: str) -> str:
    iv = bytes.fromhex(iv_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = cipher.decrypt(ciphertext)
    return unpad_pkcs7(padded).decode('utf-8')
