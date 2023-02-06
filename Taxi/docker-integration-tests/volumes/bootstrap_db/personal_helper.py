# pylint: disable=C0103
import base64
import binascii

from Crypto.Cipher import AES
from Crypto.Util import Counter


class AESCipher:
    def __init__(self, key, iv=''):
        # bytes format
        self.key = key
        self.iv = iv

    def encrypt(self, data, custom_crypto_iv=None):
        crypto_iv = (
            custom_crypto_iv if custom_crypto_iv is not None else self.iv
        )
        counter = Counter.new(
            128, initial_value=int(binascii.hexlify(crypto_iv), 16),
        )
        cipher = AES.new(self.key, AES.MODE_CTR, counter=counter)
        return base64.b64encode(cipher.encrypt(data.encode('utf-8')))

    def decode(self, data, custom_crypto_iv=None):
        crypto_iv = (
            custom_crypto_iv if custom_crypto_iv is not None else self.iv
        )
        counter = Counter.new(
            128, initial_value=int(binascii.hexlify(crypto_iv), 16),
        )
        cipher = AES.new(self.key, AES.MODE_CTR, counter=counter)
        return cipher.decrypt(base64.b64decode(data))
