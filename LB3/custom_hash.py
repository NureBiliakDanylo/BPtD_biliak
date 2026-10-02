
def mix64(x: int) -> int:
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9 & 0xFFFFFFFFFFFFFFFF
    x = (x ^ (x >> 27)) * 0x94d049bb133111eb & 0xFFFFFFFFFFFFFFFF
    x = (x ^ (x >> 31)) & 0xFFFFFFFFFFFFFFFF
    return x

def custom_hash_int(data: bytes, bit_length: int = 8) -> int:
    if bit_length not in (2, 4, 8):
        raise ValueError("Довжина хешу повинна бути 2, 4 або 8 біт!")

    h = 0xCBF29CE484222325
    prime = 0x100000001B3

    for b in data:
        h = (h ^ b) * prime & 0xFFFFFFFFFFFFFFFF
        h = mix64(h)

    h ^= len(data)
    h = mix64(h)

    h8 = ((h >> 56) ^ (h >> 48) ^ (h >> 40) ^ (h >> 32) ^
          (h >> 24) ^ (h >> 16) ^ (h >> 8) ^ h) & 0xFF

    if bit_length == 8:
        return h8
    elif bit_length == 4:
        return ((h8 >> 4) ^ (h8 & 0x0F)) & 0x0F
    elif bit_length == 2:
        h4 = ((h8 >> 4) ^ (h8 & 0x0F)) & 0x0F
        return ((h4 >> 2) ^ (h4 & 0x03)) & 0x03

def custom_hash(data: bytes, bit_length: int = 8) -> str:
    val = custom_hash_int(data, bit_length)
    return format(val, f'0{bit_length}b')

def hash_file(filepath: str, bit_length: int = 8) -> str:
    with open(filepath, 'rb') as f:
        data = f.read()
    return custom_hash(data, bit_length)

def measure_avalanche(data: bytes, bit_length: int = 8) -> dict:
    if not data:
        data = b"Default testing payload"
    orig_val = custom_hash_int(data, bit_length)
    diff_percentages = []

    sample_len = min(len(data), 100)
    for i in range(sample_len):
        for bit_idx in range(8):
            mutated = bytearray(data)
            mutated[i] ^= (1 << bit_idx)
            mut_val = custom_hash_int(bytes(mutated), bit_length)
            diff_bits = bin(orig_val ^ mut_val).count('1')
            diff_percentages.append(diff_bits / bit_length)

    avg_pct = sum(diff_percentages) / len(diff_percentages) * 100.0
    over_30_pct = sum(1 for p in diff_percentages if p >= 0.3) / len(diff_percentages) * 100.0

    return {
        "bit_length": bit_length,
        "tested_mutations": len(diff_percentages),
        "average_bits_flipped_percent": round(avg_pct, 2),
        "mutations_with_at_least_30_percent_change": round(over_30_pct, 2),
        "meets_30_percent_criterion": avg_pct >= 30.0
    }
