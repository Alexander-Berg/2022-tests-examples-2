import datetime
import uuid

import aiohttp.web
import pytest

from fleet_support_chat.generated.stq3 import stq_context as context
from fleet_support_chat.stq import handle_event


@pytest.mark.pgsql('taxi_db_opteum', files=('taxi_db_opteum.sql',))
async def test_success(
        stq3_context: context.Context,
        mock_fleet_notifications,
        mock_fleet_parks,
        mock_support_chat,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @patch('uuid.uuid4')
    def _uuid4():
        token = uuid.UUID('ef1e796b7c7041cfa1dbc32fa920cd83')
        return token

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert request.json == stub['fleet_parks_request']
        return aiohttp.web.json_response(stub['fleet_parks_response'])

    @mock_fleet_notifications('/v1/notifications/create')
    async def _v1_notifications_create(request):
        assert request.json == stub['fleet_notifications_request']
        return aiohttp.web.json_response({})

    @mock_support_chat('/v1/chat/search')
    async def _v1_chat_search(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(stub['support_chat_response'])

    await handle_event.task(
        stq3_context,
        'a2e4822a98337283e39f7b60acf85ec9_all_4018047800',
        '5e9700d82ca830cb9fb1b493',
        'update',
        datetime.datetime(2020, 1, 1, 16, 14),
    )

    events = await stq3_context.pg.write_pool.fetch(
        'SELECT * FROM support_chat_events',
    )
    assert len(events) == 1


@pytest.mark.now('2020-01-01T16:14:00+03:00')
@pytest.mark.pgsql(
    'taxi_db_opteum', files=('taxi_db_opteum_event_already_exists.sql',),
)
async def test_success_failed_send_notify(
        stq3_context: context.Context,
        mock_fleet_notifications,
        mock_fleet_parks,
        mock_support_chat,
        mock_sticker,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @patch('uuid.uuid4')
    def _uuid4():
        token = uuid.UUID('ef1e796b7c7041cfa1dbc32fa920cd83')
        return token

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert request.json == stub['fleet_parks_request']
        return aiohttp.web.json_response(stub['fleet_parks_response'])

    @mock_fleet_notifications('/v1/notifications/create')
    async def _v1_notifications_create(request):
        assert request.json == stub['fleet_notifications_request']
        return aiohttp.web.json_response({}, status=503)

    @mock_sticker('/send/')
    async def _send(request):
        return aiohttp.web.json_response({}, status=503)

    @mock_support_chat('/v1/chat/search')
    async def _v1_chat_search(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(stub['support_chat_response'])

    await handle_event.task(
        stq3_context,
        'a2e4822a98337283e39f7b60acf85ec9_all_4018047800',
        '5e9700d82ca830cb9fb1b493',
        'reply',
        datetime.datetime(2020, 1, 1, 16, 14),
    )

    events = await stq3_context.pg.write_pool.fetch(
        'SELECT * FROM support_chat_events',
    )
    assert len(events) == 2
