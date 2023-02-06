# pylint: disable=redefined-outer-name
import aiohttp
from aiohttp import web
import pytest

from taxi.clients import tracker


class MockTrackerApp(web.Application):
    def __init__(self, loop):
        super().__init__(loop=loop, debug=True)

        self.response = None
        self.request = None
        self.posted_json = None

        self.router.add_post(
            '/service/driver-categories', self._general_post_handler,
        )
        self.router.add_get('/position', self._general_get_handler)
        self.router.add_post('/kick', self._general_post_handler)

    async def _general_post_handler(self, request):
        self.request = request
        self.posted_json = await request.json()
        return self.response

    def _general_get_handler(self, request):
        self.request = request
        return self.response

    async def startup(self) -> None:
        # start from aiohttp 3.x app must be frozen before started up
        self.freeze()
        await super().startup()


class MockTrackerClient(tracker.TrackerClient):
    def __init__(self, session, settings, app):
        super().__init__(session, settings)
        self.app = app

    def kick(self):
        return self._request(location='kick', data='payload')


@pytest.yield_fixture()
async def mock_tracker(loop, unused_port, unittest_settings):
    app = MockTrackerApp(loop)
    session = aiohttp.ClientSession(loop=loop)

    host = '127.0.0.1'
    port = unused_port()

    unittest_settings.TRACKER_HOST = 'http://{host}:{port}'.format(**locals())

    client = MockTrackerClient(session, unittest_settings, app)
    handler = app.make_handler(loop=loop)
    server = await loop.create_server(
        host=host, port=port, protocol_factory=handler,
    )
    try:
        async with session:
            yield client
    finally:
        server.close()
        await handler.shutdown()


@pytest.mark.not_mock_request()
async def test_tracker_socket_error(mock_tracker, unittest_settings):
    unittest_settings.TRACKER_HOST = 'invalid'
    with pytest.raises(tracker.TrackerRequestError):
        await mock_tracker.kick()


async def test_tracker_http_error(
        mock_tracker, unittest_settings, unused_port,
):
    unittest_settings.TRACKER_HOST = 'http://localhost:{0}'.format(
        unused_port(),
    )
    with pytest.raises(tracker.TrackerRequestError) as ctx:
        await mock_tracker.kick()
    assert 'http client error' in str(ctx.value)


async def test_tracker_ivalid_json(mock_tracker):
    mock_tracker.app.response = web.Response(body='invalid_content')
    with pytest.raises(tracker.TrackerRequestError) as ctx:
        await mock_tracker.kick()
    assert 'invalid_content' in str(ctx.value)
    assert 'json' in str(ctx.value)


async def test_tracker_invalid_status(mock_tracker):
    mock_tracker.app.response = web.Response(status=500, body='')
    with pytest.raises(tracker.TrackerRequestError) as ctx:
        await mock_tracker.kick()
    assert '500' in str(ctx.value)


async def test_tracker_notfound(mock_tracker):
    mock_tracker.app.response = web.Response(status=404, body='')
    with pytest.raises(tracker.NotFoundError) as ctx:
        await mock_tracker.kick()
    assert 'kick' in str(ctx.value)


# pylint: disable=invalid-name
async def test_driver_categories_normal_work(mock_tracker):
    mock_tracker.app.response = web.json_response(data='response')
    res = await mock_tracker.driver_categories('driver1', [60.0, 30.0])
    assert mock_tracker.app.posted_json == {
        'driver_id': 'driver1',
        'point': [60.0, 30.0],
    }
    assert res == 'response'


async def test_driver_categories_by_uuid(mock_tracker):
    mock_tracker.app.response = web.json_response(data='response')
    res = await mock_tracker.driver_categories_by_uuid(
        'dbid1', 'uuid1', [60.0, 30.0],
    )
    assert mock_tracker.app.posted_json == {
        'db_id': 'dbid1',
        'uuid': 'uuid1',
        'point': [60.0, 30.0],
    }
    assert res == 'response'


async def test_driver_position(mock_tracker):
    mock_tracker.app.response = web.json_response(data='response')
    res = await mock_tracker.driver_position('dbid1', 'uuid1')

    assert res == 'response'
