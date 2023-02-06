import base64
import hashlib
import urllib.parse

import pytest


def encode_query_params(*pairs):
    def _tobytes(value):
        if isinstance(value, bytes):
            return value
        return str(value).encode()

    return b'&'.join(
        b'='.join(
            base64.urlsafe_b64encode(_tobytes(part)).rstrip(b'=')
            for part in pair
        )
        for pair in pairs
    )


async def test_empty(taxi_userver_sample):
    response = await taxi_userver_sample.post('autogen/hash')

    assert response.status_code == 200
    assert response.json() == {
        'query-hash': hashlib.sha256(b'autogen/hash').hexdigest(),
        'body-hash': hashlib.sha256().hexdigest(),
    }


async def test_binary(taxi_userver_sample):
    data = b'\x89PNG\r\n'

    response = await taxi_userver_sample.post(
        'autogen/hash?q=' + urllib.parse.quote_from_bytes(data), data=data,
    )

    assert response.status_code == 200
    assert response.json() == {
        'query-hash': hashlib.sha256(
            b'autogen/hash?' + encode_query_params(('q', data)),
        ).hexdigest(),
        'body-hash': hashlib.sha256(data).hexdigest(),
    }


@pytest.mark.parametrize(
    'query_string, is_ok',
    [
        ('autogen/hash?a=1&b=2&b=3', True),
        ('autogen/hash/?a=1&b=2&b=3', True),
        ('/autogen/hash?a=1&b=2&b=3', True),
        ('/autogen/hash/?a=1&b=2&b=3', True),
        ('autogen/hash?b=2&b=3&a=1', True),
        ('autogen/hash?a=1&b=3&b=2', False),
    ],
)
async def test_canonicalization(taxi_userver_sample, query_string, is_ok):
    expected = {
        'query-hash': hashlib.sha256(
            b'autogen/hash?'
            + encode_query_params(('a', '1'), ('b', '2'), ('b', '3')),
        ).hexdigest(),
        'body-hash': hashlib.sha256().hexdigest(),
    }

    response = await taxi_userver_sample.post(query_string)

    assert response.status_code == 200
    if is_ok:
        assert response.json() == expected
    else:
        assert response.json() != expected
