
import os
import docx
from custom_hash import custom_hash_int, custom_hash

def generate_text_collision(filepath: str, bit_length: int = 8, output_path: str = None) -> tuple[str, int, str]:
    with open(filepath, 'rb') as f:
        original_data = f.read()

    target_hash = custom_hash_int(original_data, bit_length)
    if not output_path:
        base, ext = os.path.splitext(filepath)
        output_path = f"{base}_collision{ext}"

    nonce = 1
    while True:
        padding = f"\n<!-- metadata-ref: {nonce} -->".encode('utf-8')
        candidate = original_data + padding
        if custom_hash_int(candidate, bit_length) == target_hash:
            with open(output_path, 'wb') as f:
                f.write(candidate)
            return output_path, nonce, custom_hash(candidate, bit_length)
        nonce += 1

def generate_docx_collision(filepath: str, bit_length: int = 8, output_path: str = None) -> tuple[str, int, str]:
    with open(filepath, 'rb') as f:
        orig_bytes = f.read()
    target_hash = custom_hash_int(orig_bytes, bit_length)

    if not output_path:
        base, ext = os.path.splitext(filepath)
        output_path = f"{base}_collision{ext}"

    doc = docx.Document(filepath)
    nonce = 1
    while True:
        doc.core_properties.comments = f"Verified digest id: {nonce}"
        doc.save(output_path)
        with open(output_path, 'rb') as f:
            candidate_bytes = f.read()
        if custom_hash_int(candidate_bytes, bit_length) == target_hash and candidate_bytes != orig_bytes:
            return output_path, nonce, custom_hash(candidate_bytes, bit_length)
        nonce += 1

def generate_code_collision(filepath: str, bit_length: int = 8, output_path: str = None) -> tuple[str, int, str]:
    with open(filepath, 'rb') as f:
        original_data = f.read()

    target_hash = custom_hash_int(original_data, bit_length)
    if not output_path:
        base, ext = os.path.splitext(filepath)
        output_path = f"{base}_collision{ext}"

    nonce = 1
    while True:
        comment = f"\n# [HashCollisionSalt: {nonce}]".encode('utf-8')
        candidate = original_data + comment
        if custom_hash_int(candidate, bit_length) == target_hash:
            with open(output_path, 'wb') as f:
                f.write(candidate)
            return output_path, nonce, custom_hash(candidate, bit_length)
        nonce += 1

def generate_image_collision(filepath: str, bit_length: int = 8, output_path: str = None) -> tuple[str, int, str]:
    with open(filepath, 'rb') as f:
        original_data = f.read()

    target_hash = custom_hash_int(original_data, bit_length)
    if not output_path:
        base, ext = os.path.splitext(filepath)
        output_path = f"{base}_collision{ext}"

    nonce = 1
    while True:
        padding = f"\x00/*img-salt:{nonce}*/".encode('latin-1')
        candidate = original_data + padding
        if custom_hash_int(candidate, bit_length) == target_hash:
            with open(output_path, 'wb') as f:
                f.write(candidate)
            return output_path, nonce, custom_hash(candidate, bit_length)
        nonce += 1

def auto_generate_collision(filepath: str, bit_length: int = 8, output_path: str = None) -> dict:
    ext = os.path.splitext(filepath)[1].lower()
    with open(filepath, 'rb') as f:
        orig_bytes = f.read()
    orig_hash = custom_hash(orig_bytes, bit_length)

    if ext == '.docx':
        out_f, attempts, coll_hash = generate_docx_collision(filepath, bit_length, output_path)
    elif ext in ('.py', '.js', '.c', '.cpp', '.java'):
        out_f, attempts, coll_hash = generate_code_collision(filepath, bit_length, output_path)
    elif ext in ('.bmp', '.png', '.jpg', '.jpeg'):
        out_f, attempts, coll_hash = generate_image_collision(filepath, bit_length, output_path)
    else:
        out_f, attempts, coll_hash = generate_text_collision(filepath, bit_length, output_path)

    with open(out_f, 'rb') as f:
        new_bytes = f.read()

    return {
        "original_file": filepath,
        "collision_file": out_f,
        "file_type": ext,
        "bit_length": bit_length,
        "original_hash": orig_hash,
        "collision_hash": coll_hash,
        "hashes_match": orig_hash == coll_hash,
        "contents_differ": orig_bytes != new_bytes,
        "attempts_needed": attempts,
        "original_size": len(orig_bytes),
        "collision_size": len(new_bytes)
    }
