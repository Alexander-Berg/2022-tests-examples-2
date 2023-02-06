# pylint: disable=C0103
import base64

from Crypto.Cipher import AES

TEST_DEK = base64.b64decode(b'gDjNonVyRyaS/TuuQis0Sbm2zw9o/kcMn9aU9/clKq8=')
TEST_IV = base64.b64decode(b'28yjLr+bgEYXw6qe/6Q0KA==')

TAG_SIZE = 12
IV_SIZE = 16


def _decrypt_gcm_aes(key, data):
    assert AES.block_size == 16
    iv = data[:IV_SIZE]
    encrypted = data[IV_SIZE:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    return cipher.decrypt(encrypted)[:-TAG_SIZE]


def _encrypt_gcm_aes(key, data):
    cipher = AES.new(key, AES.MODE_GCM, nonce=TEST_IV, mac_len=TAG_SIZE)
    encrypted, digest = cipher.encrypt_and_digest(data)
    return TEST_IV + encrypted + digest


class GcmAesCipher:
    def __init__(self, kek):
        self.kek = kek

    def encrypt(self, data):
        encrypted_data = _encrypt_gcm_aes(TEST_DEK, data)
        dek_encrypted = _encrypt_gcm_aes(self.kek, TEST_DEK)
        return {'data': encrypted_data, 'dek': dek_encrypted}

    def decrypt(self, encrypted):
        dek = _decrypt_gcm_aes(self.kek, encrypted['dek'])
        return _decrypt_gcm_aes(dek, encrypted['data'])
