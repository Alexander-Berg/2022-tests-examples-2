# pylint: disable=unused-variable,protected-access
import datetime
import json

import aiohttp.web
import pytest

from taxi import config
from taxi.clients import localizations
from taxi.clients.helpers import errors

GET_KEYSET_URL = 'http://localizations-replica.taxi.dev.yandex.net/v1/keyset'


@pytest.mark.parametrize(
    'response,result',
    [
        (
            {'keyset_name': 'keyset', 'keys': []},
            {'name': 'keyset', 'keys': []},
        ),
        (
            {
                'keyset_name': 'keyset',
                'keys': [{'key_id': 'ID', 'values': []}],
            },
            {'name': 'keyset', 'keys': [{'_id': 'ID', 'values': []}]},
        ),
        (
            {
                'keyset_name': 'keyset',
                'keys': [],
                'last_update': '2019-06-28T13:18:33.0Z',
            },
            {
                'name': 'keyset',
                'keys': [],
                'last_update': '2019-06-28T13:18:33.0Z',
            },
        ),
    ],
)
async def test_get_keyset(
        patch_aiohttp_session, response_mock, response, result,
):
    now = datetime.datetime.utcnow()

    @patch_aiohttp_session(GET_KEYSET_URL, 'GET')
    def patch_request(*args, **kwargs):
        params = kwargs['params']
        assert params['name'] == 'keyset'
        assert params['last_update'] == now.isoformat()
        return response_mock(read=json.dumps(response))

    async with aiohttp.ClientSession() as session:
        client = localizations.Localizations(
            session=session,
            service_url='http://localizations-replica.taxi.dev.yandex.net',
        )
        data = await client.get_keyset(
            'keyset', now.isoformat(), config.Config.LOCALIZATIONS_PY3_CLIENT,
        )
    assert data == result


@pytest.mark.parametrize(
    'keyset_name,expected_keys',
    [
        ('keyset1', []),
        (
            'keyset2',
            [
                {
                    '_id': 'some.key',
                    'values': [
                        {
                            'conditions': {
                                'form': 1,
                                'locale': {'language': 'en'},
                            },
                            'value': 'some key',
                        },
                        {
                            'conditions': {
                                'form': 1,
                                'locale': {'language': 'ru'},
                            },
                            'value': 'какой то ключ',
                        },
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.translations(
    keyset1={},
    keyset2={'some.key': {'en': 'some key', 'ru': 'какой то ключ'}},
)
async def test_get_keyset_mockserver(keyset_name, expected_keys):
    async with aiohttp.ClientSession() as session:
        client = localizations.Localizations(
            session=session, service_url='$mockserver/localizations-replica',
        )
        data = await client.get_keyset(
            keyset_name, None, config.Config.LOCALIZATIONS_PY3_CLIENT,
        )
    assert data['keys'] == expected_keys


async def test_get_keyset_retries(patch, patch_aiohttp_session, response_mock):

    conf = config.Config.LOCALIZATIONS_PY3_CLIENT
    conf['retries_count'] = 2
    conf['retries_delay'] = 0.1

    @patch_aiohttp_session(GET_KEYSET_URL, 'GET')
    def patch_request(*args, **kwargs):
        return response_mock(status=500)

    orig = localizations.Localizations._request

    @patch('taxi.clients.localizations.Localizations._request')
    async def _request(*args, **kwargs):
        return await orig(client, *args, **kwargs)

    async with aiohttp.ClientSession() as session:
        client = localizations.Localizations(
            session=session,
            service_url='http://localizations-replica.taxi.dev.yandex.net',
        )
        with pytest.raises(errors.BaseError):
            await client.get_keyset('keyset', None, conf)

    assert len(_request.calls) == conf['retries_count']
