import tempfile
import typing as tp

from core.errors import LockedError
from core.utils import encrypt, decrypt, get_random_iv, file_lock
from multiprocessing import Process, Value


def test_encrypt_decrypt():
    data = {
        'aaa': 'bb',
        'bbb': 'cc'
    }
    key = '0lmxvuhu7jongagnzqqvv9u00d5cigkr'
    iv = get_random_iv()

    encrypted = encrypt(data, key, iv)
    decrypted = decrypt(encrypted, key, iv)

    assert data == decrypted


def test_file_lock_success():
    def is_locked(name, folder) -> bool:
        def _check(_locked_flg: Value):
            try:
                with file_lock(name, folder):
                    _locked_flg.value = False
            except LockedError:
                _locked_flg.value = True

        # вызываем в отельном процессе, что бы сработал Lock
        locked_flg = Value('i', False)
        process = Process(target=_check, args=(locked_flg,))
        process.start()
        process.join()

        return locked_flg.value

    with tempfile.TemporaryDirectory() as tmp_folder:
        with file_lock('test', tmp_folder):
            assert is_locked('test', tmp_folder)

        assert not is_locked('test', tmp_folder)
