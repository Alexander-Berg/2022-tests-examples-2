import hashlib


def make_sha1(key):
    return hashlib.sha1(key.encode('utf-8')).hexdigest()
