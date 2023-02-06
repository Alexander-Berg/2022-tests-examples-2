import datetime

import pytest

from taxi.util import dates

NOW = datetime.datetime(2021, 7, 20, 0, 19, tzinfo=datetime.timezone.utc)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['params', 'expected_status', 'expected_response_data'],
    [
        ({}, 400, None),
        ({'action_name': 'beliberda'}, 400, None),
        (
            {
                'action_name': 'first_answer_in_line',
                'filter_by': 'waiting_time',
            },
            400,
            None,
        ),
        ({'action_name': 'first_answer_in_line', 'lower_limit': 0}, 400, None),
        (
            {'action_name': 'first_answer_in_line'},
            200,
            {
                'interval_start': '2021-07-18 00:19:00+00:00',
                'interval_finish': '2021-07-20 00:19:00+00:00',
                'values_by_line': [
                    {
                        'line': 'first',
                        'counters': [
                            {
                                'name': 'timely first answers',
                                'result': [
                                    {'variable': 'count', 'value': 1},
                                    {'variable': 'count (%)', 'value': 100},
                                ],
                            },
                        ],
                    },
                    {
                        'line': 'second',
                        'counters': [
                            {
                                'name': 'timely first answers',
                                'result': [
                                    {'variable': 'count', 'value': 2},
                                    {'variable': 'count (%)', 'value': 100},
                                ],
                            },
                        ],
                    },
                    {
                        'line': 'third',
                        'counters': [
                            {
                                'name': 'timely first answers',
                                'result': [
                                    {'variable': 'count', 'value': 1},
                                    {'variable': 'count (%)', 'value': 100},
                                ],
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'action_name': 'first_answer_in_line',
                'start': '2021-07-18 23:08:30+00:00',
                'finish': '2021-07-19 23:12:05+00:00',
            },
            200,
            {
                'interval_start': '2021-07-18 23:08:30+00:00',
                'interval_finish': '2021-07-19 23:12:05+00:00',
                'values_by_line': [
                    {
                        'line': 'second',
                        'counters': [
                            {
                                'name': 'timely first answers',
                                'result': [
                                    {'variable': 'count', 'value': 1},
                                    {'variable': 'count (%)', 'value': 100},
                                ],
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'action_name': 'first_answer_in_line',
                'lines': ['first', 'second'],
            },
            200,
            {
                'interval_start': '2021-07-18 00:19:00+00:00',
                'interval_finish': '2021-07-20 00:19:00+00:00',
                'values_by_line': [
                    {
                        'line': 'first',
                        'counters': [
                            {
                                'name': 'timely first answers',
                                'result': [
                                    {'variable': 'count', 'value': 1},
                                    {'variable': 'count (%)', 'value': 100},
                                ],
                            },
                        ],
                    },
                    {
                        'line': 'second',
                        'counters': [
                            {
                                'name': 'timely first answers',
                                'result': [
                                    {'variable': 'count', 'value': 2},
                                    {'variable': 'count (%)', 'value': 100},
                                ],
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'action_name': 'first_answer_in_line',
                'filter_by': 'waiting_time',
                'upper_limit': 60,
            },
            200,
            {
                'filter': 'waiting_time <= 60.0',
                'interval_start': '2021-07-18 00:19:00+00:00',
                'interval_finish': '2021-07-20 00:19:00+00:00',
                'values_by_line': [
                    {
                        'line': 'first',
                        'counters': [
                            {
                                'name': 'timely first answers',
                                'result': [
                                    {'variable': 'count', 'value': 1},
                                    {'variable': 'count (%)', 'value': 100},
                                ],
                            },
                        ],
                    },
                    {
                        'line': 'second',
                        'counters': [
                            {
                                'name': 'timely first answers',
                                'result': [
                                    {'variable': 'count', 'value': 1},
                                    {'variable': 'count (%)', 'value': 50},
                                ],
                            },
                        ],
                    },
                    {
                        'line': 'third',
                        'counters': [
                            {
                                'name': 'timely first answers',
                                'result': [
                                    {'variable': 'count', 'value': 0},
                                    {'variable': 'count (%)', 'value': 0},
                                ],
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {'action_name': 'success_call'},
            200,
            {
                'interval_finish': '2021-07-20 00:19:00+00:00',
                'interval_start': '2021-07-18 00:19:00+00:00',
                'values_by_line': [
                    {
                        'counters': [
                            {
                                'name': 'success_calls_count',
                                'result': {'count': 3, 'total': 4},
                            },
                        ],
                        'line': 'first',
                    },
                    {
                        'counters': [
                            {
                                'name': 'success_calls_count',
                                'result': {'count': 1, 'total': 2},
                            },
                        ],
                        'line': 'second',
                    },
                ],
            },
        ),
        (
            {'action_name': 'missed_call'},
            200,
            {
                'interval_finish': '2021-07-20 00:19:00+00:00',
                'interval_start': '2021-07-18 00:19:00+00:00',
                'values_by_line': [
                    {
                        'counters': [
                            {
                                'name': 'missed_calls_count',
                                'result': {'count': 1, 'total': 4},
                            },
                        ],
                        'line': 'first',
                    },
                    {
                        'counters': [
                            {
                                'name': 'missed_calls_count',
                                'result': {'count': 1, 'total': 2},
                            },
                        ],
                        'line': 'second',
                    },
                ],
            },
        ),
        (
            {
                'action_name': 'success_call',
                'start': '2021-07-18 23:08:30+00:00',
                'finish': '2021-07-19 23:12:05+00:00',
            },
            200,
            {
                'interval_finish': '2021-07-19 23:12:05+00:00',
                'interval_start': '2021-07-18 23:08:30+00:00',
                'values_by_line': [
                    {
                        'counters': [
                            {
                                'name': 'success_calls_count',
                                'result': {'count': 1, 'total': 2},
                            },
                        ],
                        'line': 'first',
                    },
                    {
                        'counters': [
                            {
                                'name': 'success_calls_count',
                                'result': {'count': 1, 'total': 1},
                            },
                        ],
                        'line': 'second',
                    },
                ],
            },
        ),
        (
            {'action_name': 'missed_call', 'lines': ['first', 'second']},
            200,
            {
                'interval_finish': '2021-07-20 00:19:00+00:00',
                'interval_start': '2021-07-18 00:19:00+00:00',
                'values_by_line': [
                    {
                        'counters': [
                            {
                                'name': 'missed_calls_count',
                                'result': {'count': 1, 'total': 4},
                            },
                        ],
                        'line': 'first',
                    },
                    {
                        'counters': [
                            {
                                'name': 'missed_calls_count',
                                'result': {'count': 1, 'total': 2},
                            },
                        ],
                        'line': 'second',
                    },
                ],
            },
        ),
        (
            {
                'action_name': 'success_call',
                'filter_by': 'waiting_time',
                'upper_limit': 30,
            },
            200,
            {
                'filter': 'waiting_time <= 30.0',
                'interval_finish': '2021-07-20 00:19:00+00:00',
                'interval_start': '2021-07-18 00:19:00+00:00',
                'values_by_line': [
                    {
                        'counters': [
                            {
                                'name': 'success_calls_count',
                                'result': {'count': 1, 'total': 4},
                            },
                        ],
                        'line': 'first',
                    },
                    {
                        'counters': [
                            {
                                'name': 'success_calls_count',
                                'result': {'count': 1, 'total': 2},
                            },
                        ],
                        'line': 'second',
                    },
                ],
            },
        ),
        (
            {
                'action_name': 'missed_call',
                'filter_by': 'waiting_time',
                'lower_limit': 10,
                'upper_limit': 60,
            },
            200,
            {
                'filter': '10.0 <= waiting_time <= 60.0',
                'interval_finish': '2021-07-20 00:19:00+00:00',
                'interval_start': '2021-07-18 00:19:00+00:00',
                'values_by_line': [
                    {
                        'counters': [
                            {
                                'name': 'missed_calls_count',
                                'result': {'count': 1, 'total': 4},
                            },
                        ],
                        'line': 'first',
                    },
                    {
                        'counters': [
                            {
                                'name': 'missed_calls_count',
                                'result': {'count': 0, 'total': 2},
                            },
                        ],
                        'line': 'second',
                    },
                ],
            },
        ),
    ],
)
async def test_chatterbox_stats(
        web_app_client, params, expected_status, expected_response_data,
):
    params_to_send = {}
    for key, value in params.items():
        if isinstance(value, list):
            value = '|'.join(value)
        if isinstance(value, datetime.datetime):
            value = dates.timestring(value, timezone='UTC')
        params_to_send[key] = value
    response = await web_app_client.get(
        '/v1/chatterbox/non-aggregated-stat/actions/count-by-line',
        params=params_to_send,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    data = await response.json()
    assert data == expected_response_data
