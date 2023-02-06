# pylint: disable=protected-access
import pytest


async def test_insert_call_records(
        web_context, web_app_client, clickhouse_query_storage,
):
    response_empty = await web_app_client.post(
        '/supportai-statistics/v1/calls_statistics?project_slug=some_project',
        json={'records': []},
    )
    assert response_empty.status == 200

    response = await web_app_client.post(
        '/supportai-statistics/v1/calls_statistics?project_slug=some_project',
        json={
            'records': [
                {
                    'call_id': '1',
                    'chat_id': '123',
                    'direction': 'outgoing',
                    'call_service': 'ivr_framework',
                    'user_phone_number': '123',
                    'attempt_number': 2,
                    'initiated_at': '2020.01.01 00:00:00',
                    'call_connected': True,
                    'status': 'ended',
                },
                {
                    'call_id': '2',
                    'chat_id': '123',
                    'direction': 'outgoing',
                    'call_service': 'voximplant',
                    'user_phone_number': '123',
                    'attempt_number': 3,
                    'initiated_at': '2020.01.01 00:00:00',
                    'call_connected': True,
                    'user_was_silent': False,
                    'tags': ['first', 'second'],
                    'status': 'ended',
                },
                {
                    'call_id': '3',
                    'chat_id': '123',
                    'direction': 'outgoing',
                    'call_service': 'ya_telephony',
                    'user_phone_number': '123',
                    'attempt_number': 2,
                    'initiated_at': '2020.01.01 00:00:00',
                    'call_connected': True,
                    'status': 'error',
                    'error_code': 'SOME_ERROR',
                },
            ],
        },
    )
    assert response.status == 200
    assert len(clickhouse_query_storage) == 1


@pytest.mark.parametrize('with_borders', [True, False])
async def test_get_calls_general_statistics(
        web_context,
        web_app_client,
        mock_clickhouse_host,
        response_mock,
        with_borders,
):
    def mock_clickhouse(*args, **kwargs):
        return response_mock(
            json={
                'meta': [
                    {'name': 'sum(series_total)', 'type': 'UInt64'},
                    {'name': 'sum(dials_first_attempt)', 'type': 'UInt64'},
                    {'name': 'sum(series_dials)', 'type': 'UInt64'},
                    {'name': 'sum(unsuccessful_series)', 'type': 'UInt64'},
                    {'name': 'sum(calls_total)', 'type': 'UInt64'},
                    {'name': 'sum(calls_dials)', 'type': 'UInt64'},
                    {'name': 'sum(no_dial_calls)', 'type': 'UInt64'},
                    {'name': 'sum(successful_calls)', 'type': 'UInt64'},
                    {'name': 'sum(hangups)', 'type': 'UInt64'},
                    {'name': 'sum(silent_hangups)', 'type': 'UInt64'},
                    {'name': 'sum(forwarded_calls)', 'type': 'UInt64'},
                    {'name': 'sum(errors_during_call)', 'type': 'UInt64'},
                    {'name': 'sum(total_seconds)', 'type': 'UInt64'},
                ],
                'data': (
                    [
                        {
                            'sum(series_total)': '550',
                            'sum(dials_first_attempt)': '281',
                            'sum(series_dials)': '412',
                            'sum(unsuccessful_series)': '138',
                            'sum(calls_total)': '986',
                            'sum(calls_dials)': '412',
                            'sum(no_dial_calls)': '574',
                            'sum(successful_calls)': '191',
                            'sum(hangups)': '182',
                            'sum(silent_hangups)': '56',
                            'sum(forwarded_calls)': '1',
                            'sum(errors_during_call)': '39',
                            'sum(total_seconds)': '10616',
                        },
                    ]
                ),
                'rows': 1,
                'statistics': {
                    'elapsed': 0.002271832,
                    'rows_read': 38422,
                    'bytes_read': 430380,
                },
            },
        )

    host_list = web_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(
        clickhouse_response=mock_clickhouse, request_url=host_list[0],
    )

    params = {'project_slug': 'test_statistics', 'user_id': '34'}
    if with_borders:
        params['newer_than'] = 1
        params['older_than'] = 2

    response = await web_app_client.get(
        f'/supportai-statistics/v1/statistics/calls/general', params=params,
    )
    assert response.status == 200
    response_json = await response.json()

    expected_json = {
        'series_total': 550,
        'dials_first_attempt': 281,
        'series_dials': 412,
        'unsuccessful_series': 138,
        'calls_total': 986,
        'calls_dials': 412,
        'no_dial_calls': 574,
        'successful_calls': 191,
        'hangups': 182,
        'silent_hangups': 56,
        'forwarded_calls': 1,
        'errors_during_call': 39,
        'mean_talk_duration': 25,
    }

    assert response_json == expected_json
