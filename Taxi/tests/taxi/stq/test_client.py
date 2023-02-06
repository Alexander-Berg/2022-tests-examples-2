import asyncio
import copy
import datetime
import functools
import json

import aiohttp
import bson
import pytest

from taxi import config
from taxi.clients import stq_agent
from taxi.pytest_plugins import fixtures_content as conftest
from taxi.stq import client as stq_client


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    'response_status, expected_tries_count, ' 'expected_error',
    [
        (200, 1, None),
        (500, 3, stq_agent.RemoteError),
        (400, 1, stq_agent.RequestError),
        (None, 3, stq_agent.RemoteError),
    ],
)
async def test_put(
        response_status,
        expected_tries_count,
        expected_error,
        monkeypatch,
        patch,
        unittest_settings,
        mongo_settings,
        patch_aiohttp_session,
        response_mock,
        loop,
):
    monkeypatch.setattr(unittest_settings, 'STQ_AGENT_BASE_URL', 'patched_url')

    @patch_aiohttp_session(unittest_settings.STQ_AGENT_BASE_URL, 'POST')
    def patch_request(method, url, **kwargs):
        assert url == '{}/{}'.format(
            unittest_settings.STQ_AGENT_BASE_URL, 'queues/api/add/processing',
        )
        assert method == 'post'
        assert kwargs.get('headers') == {
            'X-YaTaxi-API-Key': 'stq-agent-apikey',
        }
        assert json.loads(kwargs.get('data')) == {
            'task_id': '822c8f4dbcb9451697636a583336ba60',
            'args': ['foo', {'bar': {'$date': 1545829956446}}],
            'kwargs': {'quux': {'$oid': '5c24d070820f9e89326109c3'}},
            'eta': '2018-12-27T13:12:36.446295Z',
        }

        if response_status is None:
            raise asyncio.TimeoutError('timeout')

        return response_mock(status=response_status, json={})

    secdist = {
        'mongo_settings': mongo_settings,
        'client_apikeys': copy.deepcopy(conftest.CLIENT_APIKEYS),
    }

    stq_clients = {'processing'}

    session = aiohttp.ClientSession()
    stq_client.init(
        secdist, stq_clients, session, config.Config(), unittest_settings,
    )

    test_func = functools.partial(
        stq_client.put,
        queue='processing',
        eta=datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
        task_id='822c8f4dbcb9451697636a583336ba60',
        args=(
            'foo',
            {'bar': datetime.datetime(2018, 12, 26, 13, 12, 36, 446295)},
        ),
        kwargs={'quux': bson.ObjectId('5c24d070820f9e89326109c3')},
        loop=loop,
    )

    if expected_error:
        with pytest.raises(expected_error):
            await test_func()
    else:
        await test_func()

    await session.close()

    assert len(patch_request.calls) == expected_tries_count
