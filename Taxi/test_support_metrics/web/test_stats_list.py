import datetime

import pytest

from taxi.util import dates

NOW = datetime.datetime(2019, 7, 2, 12, 34, tzinfo=datetime.timezone.utc)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['params', 'expected_status', 'expected_values'],
    [
        ({'instances': ['login']}, 200, [5.0]),
        (
            {
                'instances': ['line'],
                'keys': ['first_line'],
                'intervals': ['1min'],
            },
            200,
            [2],
        ),
        ({'instances': ['line'], 'keys': ['first_line']}, 200, [3, 2]),
        (
            {
                'instances': ['line'],
                'keys': ['first_line'],
                'start': NOW - datetime.timedelta(days=1),
                'finish': '2019-07-02T21:00:00',
            },
            200,
            [3, 2, 6],
        ),
        (
            {
                'instances': ['line'],
                'keys': ['first_line'],
                'start': NOW - datetime.timedelta(days=1),
                'finish': '2019-07-03T00:00:00+03',
            },
            200,
            [3, 2, 6],
        ),
        (
            {
                'instances': ['line'],
                'keys': ['first_line'],
                'start': NOW - datetime.timedelta(days=2),
                'finish': NOW - datetime.timedelta(days=1),
            },
            200,
            [],
        ),
        (
            {
                'instances': ['line'],
                'keys': ['first_line'],
                'start': NOW - datetime.timedelta(days=7),
            },
            400,
            [],
        ),
        ({'instances': ['asd']}, 400, []),
        (
            {
                'instances': ['line'],
                'keys': ['telephony'],
                'start': NOW - datetime.timedelta(days=1),
                'finish': NOW,
            },
            200,
            [8, 9, 11],
        ),
        (
            {
                'instances': ['line'],
                'keys': ['telephony', 'telephony2'],
                'start': NOW - datetime.timedelta(days=1),
                'finish': NOW,
            },
            200,
            [8, 9, 10, 11],
        ),
    ],
)
async def test_chatterbox_stats(
        web_app_client, params, expected_status, expected_values,
):
    params_to_send = {}
    for key, value in params.items():
        if isinstance(value, list):
            value = '|'.join(value)
        if isinstance(value, datetime.datetime):
            value = dates.timestring(value, timezone='UTC')
        params_to_send[key] = value
    response = await web_app_client.get(
        '/v1/chatterbox/stats/list', params=params_to_send,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    data = await response.json()

    if 'keys' in params:
        keys = []
        for date_interval in data:
            keys.extend([item['key'] for item in date_interval['items']])
        assert set(keys).issubset(params['keys'])
    if 'intervals' in params:
        intervals = [date_interval['interval'] for date_interval in data]
        assert set(intervals).issubset(params['intervals'])
    values = []
    for date_interval in data:
        for item in date_interval['items']:
            for stats in item['stats']:
                values.extend([value['value'] for value in stats['values']])

    assert sorted(values) == sorted(expected_values)
