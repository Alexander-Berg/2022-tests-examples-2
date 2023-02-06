import itertools as it

from sandbox.common import crypto
from sandbox.common import random as crandom


class TestEncryption(object):
    def test__data_extraction(self):
        data = crandom.random_string(27)
        aes = crypto.AES()

        for use_salt, use_base64 in it.product((False, True), (False, True)):
            enc = aes.encrypt(data, use_base64, use_salt)
            assert aes.decrypt(enc, use_base64) == data,\
                "Fail with use_salt={}, use_base64={}".format(use_salt, use_base64)
