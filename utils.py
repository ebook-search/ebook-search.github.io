import hashlib

def hash_long(x):
    if len(x) < 40: return x

    prefix = x[:40].strip()
    hashed = hashlib.sha256(x.encode()).hexdigest()[:16]
    return f"{prefix}_{hashed}"
