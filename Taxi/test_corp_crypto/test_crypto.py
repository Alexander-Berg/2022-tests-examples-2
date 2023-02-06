# pylint: disable=redefined-outer-name

import random
import string

import cryptography.fernet
import pytest


@pytest.fixture
def key(library_context):
    secdist = library_context.secdist['settings_override']
    return secdist['CORP_FERNET_SECRET_KEYS'].split(';')[0]


def test_crypto(library_context, key):
    corp_crypto = library_context.corp_crypto
    fernet = cryptography.fernet.Fernet(key)

    rnd = random.choices(string.printable, k=random.randint(0, 100))
    payload = ''.join(rnd)
    token = corp_crypto.encrypt(payload)

    assert payload == fernet.decrypt(token.encode()).decode()
    assert payload == corp_crypto.decrypt(token)
