# pylint: disable=redefined-outer-name
import pytest

from taxi.clients import http_client

BASE_URL = '$mockserver/corp-suggest'


@pytest.fixture
async def client(loop, db, simple_secdist):
    from taxi import config
    from taxi.clients import tvm
    from taxi_corp.clients import corp_suggest

    async with http_client.HTTPClient(loop=loop) as session:
        config_ = config.Config(db)
        yield corp_suggest.CorpSuggestClient(
            session=session,
            tvm_client=tvm.TVMClient(
                service_name='developers',
                secdist=simple_secdist,
                config=config_,
                session=session,
            ),
        )


async def test_get_cities(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        from taxi.clients.helpers import base_client
        return base_client.Response(body={}, headers={})

    data = {'query': 'Балаха', 'country': 'rus'}
    locale = 'ru'

    await client.get_cities(data, locale)
    assert _request.calls == [
        {
            'kwargs': {'json': data, 'headers': {'Accept-Language': locale}},
            'log_extra': None,
            'return_binary': False,
            'method': 'POST',
            'url': f'{BASE_URL}/corp-suggest/v1/cities',
        },
    ]
