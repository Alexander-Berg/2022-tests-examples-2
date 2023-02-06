import datetime

import pytest

from taxi.util import dates

NOW = datetime.datetime(2019, 7, 2, 12, 34, tzinfo=datetime.timezone.utc)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['params', 'expected_status', 'expected_sum'],
    [
        ({'instances': ['login']}, 200, 0),
        ({'instances': ['line'], 'keys': ['first_line']}, 200, 2),
        (
            {
                'instances': ['line'],
                'keys': ['first_line'],
                'start': NOW - datetime.timedelta(days=1),
                'finish': '2019-07-02T21:00:00',
            },
            200,
            34,
        ),
        (
            {
                'instances': ['line'],
                'keys': ['first_line'],
                'start': NOW - datetime.timedelta(days=1),
                'finish': '2019-07-03T00:00:00+03',
            },
            200,
            34,
        ),
        (
            {
                'instances': ['line'],
                'keys': ['first_line'],
                'start': NOW - datetime.timedelta(days=2),
                'finish': NOW - datetime.timedelta(days=1),
            },
            200,
            0,
        ),
        (
            {
                'instances': ['line'],
                'keys': ['first_line'],
                'start': NOW - datetime.timedelta(days=7),
            },
            400,
            0,
        ),
        ({'instances': ['asd']}, 400, 0),
    ],
)
async def test_chatterbox_stats(
        web_app_client, params, expected_status, expected_sum,
):
    params_to_send = {}
    for key, value in params.items():
        if isinstance(value, list):
            value = '|'.join(value)
        if isinstance(value, datetime.datetime):
            value = dates.timestring(value, timezone='UTC')
        params_to_send[key] = value
    response = await web_app_client.get(
        '/v1/chatterbox/actions/count', params=params_to_send,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    data = await response.json()

    if 'keys' in params:
        keys = [item['key'] for item in data]
        assert set(keys).issubset(params['keys'])

    values = []
    for key_stat in data:
        values.extend([value['count'] for value in key_stat['actions']])

    assert sum(values) == expected_sum
