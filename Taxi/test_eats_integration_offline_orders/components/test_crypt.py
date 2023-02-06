import uuid


async def test_crypt(web_context):
    test_str = uuid.uuid4().hex
    dek = uuid.uuid4().hex

    encrypt_str = web_context.crypt.encrypt(test_str, dek)
    assert encrypt_str != test_str
    decrypt_str = web_context.crypt.decrypt(encrypt_str, dek)
    assert test_str == decrypt_str
