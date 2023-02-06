import os
import random
import base64
import typing as tp

from dmp_suite.py_env.files import get_secret_file, settings


def _encode(content: tp.Text) -> tp.Text:
    return base64.encodebytes(content.encode('utf-8')).decode('ascii')

def _file_mode(path: tp.Text) -> tp.Text:
    """Возвращает строку с восмиричным представлением прав на файл."""
    return oct(os.stat(path).st_mode & 0o777)


def test_secret_file_creation():
    real_filename = f'/tmp/secret-file{random.randint(0, 10000)}'
    base64_content: tp.Text = _encode('hello world')

    try:
        with settings.patch({
            'files': {
                'secret-file': {
                    'name': real_filename,
                    'content': base64_content,
                }
            }
        }):
            resulting_filename = get_secret_file('secret-file')
            assert resulting_filename == real_filename
            assert os.path.exists(resulting_filename)
            assert _file_mode(resulting_filename) == '0o600'
    finally:
        if os.path.exists(real_filename):
            os.remove(real_filename)


def test_secret_file_update():
    real_filename = f'/tmp/secret-file{random.randint(0, 10000)}'
    base64_initial_content: tp.Text = _encode('hello world')
    base64_new_content: tp.Text = _encode('new data')

    try:
        with settings.patch({
            'files': {
                'secret-file': {
                    'name': real_filename,
                    'content': base64_initial_content,
                }
            }
        }):
            get_secret_file('secret-file')

        with settings.patch({
            'files': {
                'secret-file': {
                    'name': real_filename,
                    'content': base64_new_content,
                }
            }
        }):
            path = get_secret_file('secret-file')
            with open(path, 'r') as f:
                assert f.read() == 'new data'
    finally:
        if os.path.exists(real_filename):
            os.remove(real_filename)
