# pylint: disable=C0103
import base64
import binascii

from Crypto.Cipher import AES
from Crypto.Util import Counter


class AESCipher:
    def __init__(self, key, iv):
        self.key = base64.b64decode(key)
        self.iv = base64.b64decode(iv)

    def encrypt(self, data):
        counter = Counter.new(
            128, initial_value=int(binascii.hexlify(self.iv), 16),
        )
        cipher = AES.new(self.key, AES.MODE_CTR, counter=counter)
        return base64.b64encode(cipher.encrypt(data.encode('utf-8')))

    def decode(self, data):
        counter = Counter.new(
            128, initial_value=int(binascii.hexlify(self.iv), 16),
        )
        cipher = AES.new(self.key, AES.MODE_CTR, counter=counter)
        return cipher.decrypt(base64.b64decode(data)).decode('utf-8')
