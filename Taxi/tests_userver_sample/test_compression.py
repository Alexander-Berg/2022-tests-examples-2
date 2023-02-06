import gzip

import pytest


BODY = (
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod '
    'tempor incididunt ut labore et dolore magna aliqua.'
)

ARG_BODY = 'arg=123'


async def test_decompress_gzip_plain(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'compression/gzip',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=BODY,
    )
    assert response.status_code == 200
    assert response.json() == {'raw': BODY}
    assert response.headers['Accept-Encoding'] == 'gzip, identity'


async def test_decompress_gzip_parse_args_from_body(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'compression/gzip',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=ARG_BODY,
    )
    assert response.status_code == 200
    assert response.json() == {'raw': ARG_BODY, 'arg': '123'}
    assert response.headers['Accept-Encoding'] == 'gzip, identity'


@pytest.mark.parametrize('encoding', (None, 'identity'))
async def test_decompress_identity_parse_args_from_body(
        taxi_userver_sample, encoding,
):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    if encoding:
        headers['Content-Encoding'] = encoding
    response = await taxi_userver_sample.post(
        'compression/gzip', headers=headers, data=ARG_BODY,
    )
    assert response.status_code == 200
    assert response.json() == {'raw': ARG_BODY, 'arg': '123'}
    assert response.headers['Accept-Encoding'] == 'gzip, identity'


async def test_decompress_gzip(taxi_userver_sample):
    compressed = gzip.compress(BODY.encode())
    response = await taxi_userver_sample.post(
        'compression/gzip',
        data=compressed,
        headers={
            'Content-Encoding': 'gzip',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'raw': BODY}
    assert response.headers['Accept-Encoding'] == 'gzip, identity'


async def test_decompress_gzip_too_big(taxi_userver_sample):
    compressed = gzip.compress(('0' * (1024 * 1024 + 1)).encode())
    assert len(compressed) < 1024 * 1024

    response = await taxi_userver_sample.post(
        'compression/gzip',
        data=compressed,
        headers={
            'Content-Encoding': 'gzip',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    )
    assert response.status_code == 413


async def test_decompress_gzip_invalid(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'compression/gzip',
        data='text',
        headers={
            'Content-Encoding': 'gzip',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    )
    assert response.status_code == 400
    assert response.headers['Accept-Encoding'] == 'gzip, identity'


async def test_decompress_unsupported(taxi_userver_sample):
    compressed = gzip.compress(BODY.encode())
    response = await taxi_userver_sample.post(
        'compression/gzip',
        data=compressed,
        headers={
            'Content-Encoding': 'zstd',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    )
    assert response.status_code == 415
    assert response.headers['Accept-Encoding'] == 'gzip, identity'
