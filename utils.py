import hashlib

def hash_long(x):
    if len(x) < 100: return x

    prefix = x[:100].strip()
    hashed = hashlib.sha256(x.encode()).hexdigest()[:16]
    return f"{prefix}_{hashed}"
