from s3_json.crypt import CryptClient
from pytest import raises


class TestCryptClient:
    """
    Integration test: using DNS API call in runtime.
    """

    def setup(self):
        key = "test-key"
        key += "\f" * (CryptClient.AES_BLOCKSIZE - len(key) % CryptClient.AES_BLOCKSIZE)

        self.client = CryptClient(key)

    def test_exception_key_len(self):
        with raises(ValueError):
            CryptClient("test-key")

    def test_crypt_methods(self):
        sec_body = "random secure text"
        encrypted_text = self.client.encrypt(sec_body)
        assert len(encrypted_text) > 0
        assert sec_body == self.client.decrypt(encrypted_text)
