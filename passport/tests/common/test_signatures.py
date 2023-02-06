# -*- coding: utf-8 -*-
from passport.backend.takeout.common import (
    exceptions,
    signatures,
)
import pytest


@pytest.mark.parametrize(
    'data_to_sign',
    [
        ('foo',),
        (['foo', 'bar']),
        None,
        u'привет',
    ],
)
def test_signatures(data_to_sign):
    keys = {'0': b'key'}
    signature = signatures.sign(data_to_sign, '0', keys, salt='salt')

    assert type(signature) is str

    signature_bits = signature.split(signatures.DELIMITER)
    assert len(signature_bits) == 3
    salt, key_no, signature_wo_salt = signature_bits
    assert salt == 'salt'
    assert key_no == '0'
    assert signature_wo_salt

    signatures.check_signature(data_to_sign, signature, keys)

    with pytest.raises(exceptions.MissingKeyByVersion):
        signatures.check_signature(data_to_sign, signature, {'1': b'key'})

    with pytest.raises(exceptions.SignatureMismatch):
        signatures.check_signature(data_to_sign, signature, {'0': b'another key'})

    # подпись не является строкой
    with pytest.raises(exceptions.MalformedSignature):
        signatures.check_signature(data_to_sign, None, keys)


@pytest.mark.parametrize(
    'key_version', ['a', 'b', 'c'],
)
def test_signature_key_no(key_version):
    keys = {
        'a': b'key1',
        'b': b'key2',
        'c': b'key3',
    }
    signature = signatures.sign('data_to_sign', key_version, keys, salt='salt')

    signature_bits = signature.split(signatures.DELIMITER)
    assert len(signature_bits) == 3
    salt, parsed_key_version, signature_wo_salt = signature_bits

    assert parsed_key_version == key_version

    signatures.check_signature('data_to_sign', signature, keys)
