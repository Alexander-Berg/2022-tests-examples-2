from typing import Dict
from typing import Optional

import aiohttp
import pytest


PARAMS = [
    'format_,url',
    [
        ('swagger', '/multipart-form-data/swagger'),
        ('openapi', '/multipart-form-data/openapi'),
    ],
]


def get_content_type(name: str, format_: str) -> Optional[str]:
    if name == 'file':
        return 'application/octet-stream'
    if name == 'string':
        return None
    if format_ == 'swagger':
        return 'text/plain'
    if name == 'int-required':
        return 'application/rare'
    return 'text/plain'


def make_extra(args: dict, format_: str) -> Dict[str, object]:
    with aiohttp.MultipartWriter('form-data') as data:
        for name, value in args.items():
            if not isinstance(value, bytes):
                value = str(value).encode('utf-8')

            content_type = get_content_type(name, format_)
            payload = aiohttp.payload.BytesPayload(
                value, content_type=content_type,
            )
            payload.set_content_disposition('form-data', name=name)
            # aiohttp defaults to octet-stream, we need none
            if content_type is None:
                del payload.headers['Content-Type']
            data.append_payload(payload)
    return {
        'data': data,
        'headers': {
            'Content-type': 'multipart/form-data; boundary=' + data.boundary,
        },
    }


@pytest.mark.parametrize(*PARAMS)
async def test_happy_path(taxi_userver_sample, url, format_):
    data = {
        'int': 1,
        'int-required': 2,
        'string': 'some string',
        'file': 'file data',
    }
    response = await taxi_userver_sample.post(url, **make_extra(data, format_))
    assert response.status_code == 200
    assert response.json() == data


@pytest.mark.parametrize(*PARAMS)
async def test_some_args(taxi_userver_sample, url, format_):
    data = {'int-required': 2, 'file': 'file data'}
    response = await taxi_userver_sample.post(url, **make_extra(data, format_))
    assert response.status_code == 200
    assert response.json() == data


@pytest.mark.parametrize(*PARAMS)
async def test_missing_arg(taxi_userver_sample, url, format_):
    response = await taxi_userver_sample.post(
        url, **make_extra({'tmp': 1}, format_),
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'
