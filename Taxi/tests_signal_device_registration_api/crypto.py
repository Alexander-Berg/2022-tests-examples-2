import base64

from Crypto.Cipher import AES
from Crypto.Util import Padding

PASSWORDS_AES256_KEY = base64.b64decode(
    b'emFpMW5haDN0aGFlQ2hhaXNoMG9oanVrZWk4cGF3YWg=',
)


def decode_password(db_password):
    raw = base64.b64decode(db_password)
    assert AES.block_size == 16
    chiper = AES.new(PASSWORDS_AES256_KEY, AES.MODE_CBC, raw[:16])
    return Padding.unpad(chiper.decrypt(raw[16:]), 16).decode('utf-8')
