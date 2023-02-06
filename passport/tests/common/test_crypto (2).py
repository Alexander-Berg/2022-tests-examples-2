# -*- coding: utf-8 -*-
from io import BytesIO
import os

from passport.backend.takeout.common.crypto import (
    decrypt_stream,
    encrypt_stream,
    LazyFileLikeObject,
)
import pytest


@pytest.fixture()
def keys():
    return {'1': 'P4ssw0rd'}


@pytest.fixture()
def key_version():
    return 1


@pytest.fixture()
def buffer_size():
    return 16


class TestCountableIterator(object):
    def __init__(self, sequence):
        self.iter_count = 0
        self.sequence = iter(sequence)

    def __iter__(self):
        return self

    def __next__(self):
        data = next(self.sequence)
        self.iter_count += 1
        return data


@pytest.mark.parametrize(
    'input_stream',
    [
        BytesIO(),
        BytesIO(os.urandom(4)),
        BytesIO(os.urandom(16)),
        BytesIO(os.urandom(4096)),
        BytesIO(os.urandom(4096))
    ],
)
def test_encrypt_and_decrypt(input_stream, keys, key_version, buffer_size):
    output_file = encrypt_stream(
        input_stream,
        keys,
        key_version,
        buffer_size,
    )

    raw_data = input_stream.getvalue()
    encrypted_data = output_file.read()

    assert raw_data != encrypted_data

    new_output_stream = decrypt_stream(
        BytesIO(encrypted_data),
        keys,
        key_version,
        len(encrypted_data),
        buffer_size,
    )

    assert raw_data == new_output_stream.read()


def test_lazy_file_like_object():
    sequence = TestCountableIterator([b'foo', b'bar', b'zar'])

    lazy_io = LazyFileLikeObject(sequence)
    assert lazy_io.read(3) == b'foo'
    assert lazy_io.tell() == 3
    assert sequence.iter_count == 1

    assert lazy_io.read(3) == b'bar'
    assert sequence.iter_count == 2
    assert lazy_io.tell() == 6

    assert lazy_io.read(3) == b'zar'
    assert sequence.iter_count == 3
    assert lazy_io.tell() == 9

    assert lazy_io.read(3) == b''
    assert sequence.iter_count == 3
    assert lazy_io.tell() == 9


def test_lazy_file_like_object_2():
    sequence = TestCountableIterator([b'foo', b'bar', b'zar'])

    lazy_io = LazyFileLikeObject(sequence)

    expected = b'foobarzar'

    i = 0  # noqa
    for i, c in enumerate(expected, start=1):
        assert lazy_io.read(1) == bytes([c])
        assert lazy_io.tell() == i
        assert sequence.iter_count == i / 3 if i % 3 == 0 else i / 3 + 1

    assert lazy_io.read(1) == b''
    assert sequence.iter_count == 3


def test_lazy_file_like_object_3():
    sequence = TestCountableIterator([b'foo', b'bar', b'zar'])

    lazy_io = LazyFileLikeObject(sequence)

    assert lazy_io.read() == b'foobarzar'
    assert lazy_io.tell() == 9
    assert sequence.iter_count == 3


def test_lazy_file_like_object_4():
    sequence = TestCountableIterator([b'foo', b'bar', b'zar'])

    lazy_io = LazyFileLikeObject(sequence)

    assert lazy_io.read(9000) == b'foobarzar'
    assert lazy_io.tell() == 9
    assert sequence.iter_count == 3
