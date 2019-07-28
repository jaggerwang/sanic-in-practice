import random
import string
import hashlib


def random_string(length=8, letters=None):
    if letters is None:
        letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def sha256_hash(s, salt=''):
    return hashlib.sha256((s + salt).encode()).hexdigest()
