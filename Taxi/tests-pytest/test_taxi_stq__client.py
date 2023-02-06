import datetime
import functools
import json

import bson
import pytest

from taxi.conf import settings
from taxi.core import arequests
from taxi.core import async
from taxi.external import stq_agent
from taxi_stq import _client


@pytest.mark.parametrize(
    'response_status_code,expected_num_requests,'
    'expected_error', [
        (200, 1, None),
        (500, 3, stq_agent.RemoteError),
        (400, 1, stq_agent.RequestError),
        (None, 3, stq_agent.RemoteError),
    ],
)
@pytest.mark.noputmock
@pytest.inline_callbacks
def test_put(response_status_code,
             expected_num_requests, expected_error, patch, monkeypatch):
    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        yield
        request.num_calls += 1
        assert method == 'POST'
        assert url == '{}/{}'.format(settings.STQ_AGENT_BASE_URL, 'queues/api/add/processing')
        assert kwargs.get('headers') == {
            'X-YaRequestId': 'request_id',
        }
        body = json.loads(kwargs.get('data'))
        body['kwargs'].pop('log_extra')
        assert body == {
            'eta': '2018-12-27T13:12:36.446295Z',
            'args': [
                'foo',
                {'bar': {'$date': 1545829956446}},
            ],
            'task_id': '822c8f4dbcb9451697636a583336ba60',
            'kwargs': {
                'quux': {
                    '$oid': '5c24d070820f9e89326109c3'
                },
            },
        }
        if response_status_code is None:
            raise arequests.TimeoutError('timeout')
        async.return_value(
            arequests.Response(status_code=response_status_code, content='{}')
        )

    request.num_calls = 0

    monkeypatch.setattr(
        settings,
        'CLIENT_APIKEYS',
        {'stq_agent': {'stq_agent': 'stq_agent_token'}},
    )

    test_func = functools.partial(
        _client.put,
        queue='processing',
        eta=datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
        task_id='822c8f4dbcb9451697636a583336ba60',
        args=(
            'foo',
            {'bar': datetime.datetime(2018, 12, 26, 13, 12, 36, 446295)}
        ),
        kwargs={
            'quux': bson.ObjectId('5c24d070820f9e89326109c3'),
            'log_extra': {'_link': 'request_id'},
        },
    )

    if expected_error:
        with pytest.raises(expected_error):
            yield test_func()
    else:
        yield test_func()

    assert request.num_calls == expected_num_requests
