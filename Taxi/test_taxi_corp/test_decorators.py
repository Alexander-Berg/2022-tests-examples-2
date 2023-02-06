import aiohttp
import pytest

from taxi.util import decorators as taxi_decorators

from taxi_corp.internal import decorators


async def test_save_history_requests_db(
        patch,
        db,
        aiohttp_client,
        taxi_corp_mock_auth,  # order is important
        taxi_corp_auth_app,
):
    """Tests a request to db while @decorators.save_to_history was called"""
    from taxi_corp.api.handlers.base import base

    mock_ip = '231.233.42.2'
    mock_client_id = 'some_client_id_hash'

    class DummyView(base.ACLBaseView):
        db_collection_name = 'dummy'

        allowed_methods = {'PUT'}

        async def put(self):
            await self.update_doc(
                {'doc': 'this is a doc', 'client_id': mock_client_id},
            )
            return aiohttp.web.json_response({})

        @decorators.save_to_history
        async def update_doc(self, parsed):
            return parsed

    @patch('taxi.util.helpers.get_user_ip')
    def _get_user_ip(request):
        return mock_ip

    taxi_corp_auth_app.router.add_put('/dummy', DummyView)
    client = await aiohttp_client(taxi_corp_auth_app)
    result = await client.put('/dummy')
    assert result.status == 200

    received = await db.corp_history.find_one({'c': 'dummy'})

    assert received['c'] == 'dummy'
    assert received['p'] == 'login'
    assert received['p_uid'] == 0
    assert received['a'] == 'PUT'
    assert received['e'] == {
        'doc': 'this is a doc',
        'client_id': mock_client_id,
    }
    assert received['ip'] == mock_ip
    assert received['cl'] == mock_client_id


async def test_cache():
    from taxi_corp import corp_web

    class Cache(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.increment = 0

        @corp_web.cacheproperty('get_next')
        def get_next(self):
            self.increment += 1
            return self.increment

        @corp_web.cachemethod('sum_and_next')
        def sum_and_next(self, value):
            self.increment += 1
            return value + self.increment

        @corp_web.cacheproperty('get_anext')
        async def get_anext(self):
            self.increment += 1
            return self.increment

        @corp_web.cachemethod('sum_and_anext')
        async def sum_and_anext(self, value):
            self.increment += 1
            return value + self.increment

    cache = Cache()
    assert cache.get_next == 1  # pylint: disable=comparison-with-callable
    assert cache.get_next == 1  # pylint: disable=comparison-with-callable
    assert cache.sum_and_next(1) == 3
    assert cache.sum_and_next(1) == 3
    assert cache.sum_and_next(2) == 5
    assert cache.sum_and_next(2) == 5
    assert cache.sum_and_next(1) == 3
    assert await cache.get_anext == 4
    assert await cache.get_anext == 4
    assert await cache.sum_and_anext(3) == 8
    assert await cache.sum_and_anext(3) == 8


@pytest.mark.parametrize(
    ['errors'],
    [
        ([aiohttp.client_exceptions.ClientError],),
        (
            [
                aiohttp.client_exceptions.ClientError,
                aiohttp.client_exceptions.ClientError,
            ],
        ),
    ],
)
async def test_retry_decorator(errors):
    retries_cnt = len(errors) + 1
    tried = 0

    @taxi_decorators.retry_with_intervals([0.1, 0.2, 0.3], errors[:])
    async def _to_catch():
        nonlocal tried
        tried += 1
        if errors:
            raise errors.pop()
        else:
            return aiohttp.web.json_response({})

    await _to_catch()
    assert tried == retries_cnt


@pytest.mark.parametrize(['error'], [(aiohttp.client_exceptions.ClientError,)])
async def test_retry_decorator_fail(error):
    tried = 0

    @taxi_decorators.retry_with_intervals([0.1, 0.2, 0.3], [error])
    async def _to_catch():
        nonlocal tried
        tried += 1
        raise error

    try:
        await _to_catch()
    except error:
        pass
    assert tried == 4
