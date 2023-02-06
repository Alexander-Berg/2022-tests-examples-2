import datetime

import pytest

URL_LIST_BY_ID = (
    '/internal/logistic-platform-replica/request-compilations/list-by-id'
)
URL_LIST_BY_CODE = (
    '/internal/logistic-platform-replica/request-compilations/list-by-code'
)
URL_SEARCH = '/internal/logistic-platform-replica/request-compilations/search'


DATA_SUFFIX_TO_ITEMS = {
    'A1': {
        'created_at': 1643399569,
        'data': 'STRING_VALUE_A1',
        'request_id': '13aad1ae-c205-42e8-94e1-e7c96728d738',
    },
    'A2': {
        'created_at': 1641694841,
        'request_id': '07243441-785b-4a70-a2c2-bf48348f4225',
        'data': 'STRING_VALUE_A2',
    },
    'A3': {
        'created_at': 1641490467,
        'data': 'STRING_VALUE_A3',
        'request_id': '2d6fb2df-15b9-4855-9cc1-e51f5f1bc674',
    },
    'A4': {
        'created_at': 1641966527,
        'request_id': '3121c950-1024-4be1-9ba5-33e6dae2da4a',
        'data': 'STRING_VALUE_A4',
    },
    'A5': {
        'created_at': 164273835,
        'data': 'STRING_VALUE_A5',
        'request_id': 'aadc50f7-5654-4f38-a669-de2aee65aeac',
    },
    'B1': {
        'created_at': 1671161946,
        'data': 'STRING_VALUE_B1',
        'request_id': '09c7720b-8e6c-4d30-bd73-5d52916be754',
    },
    'B2': {
        'created_at': 1670766632,
        'data': 'STRING_VALUE_B2',
        'request_id': '288affa0-50e8-458e-8ab7-5bdb8938de7a',
    },
    'B3': {
        'created_at': 1672017115,
        'request_id': '5d04acd2-aee3-4058-a194-57b6ddc635f5',
        'data': 'STRING_VALUE_B3',
    },
    'B4': {
        'created_at': 1670018124,
        'request_id': 'd81dec52-83e9-4175-93bb-0e913d6afbb9',
        'data': 'STRING_VALUE_B4',
    },
    'B5': {
        'created_at': 1670765326,
        'request_id': '1717dcb9-3767-4232-ac04-43b832006edd',
        'data': 'STRING_VALUE_B5',
    },
    'B6': {
        'created_at': 1670148072,
        'request_id': 'b90b5b11-2b83-40fc-9920-957f43e602b6',
        'data': 'STRING_VALUE_B6',
    },
    'B7': {
        'created_at': 1670090329,
        'request_id': '6d2b13a2-f55b-4063-a269-d91d545508ae',
        'data': 'STRING_VALUE_B7',
    },
}


def _get_items(data_suffix_list, sort_function=None):
    items_with_full_context = list()
    for data_suffix in data_suffix_list:
        items_with_full_context.append(DATA_SUFFIX_TO_ITEMS[data_suffix])
    if sort_function is not None:
        items_with_full_context = sort_function(items_with_full_context)

    result = list()
    for item in items_with_full_context:
        result.append({'request_id': item['request_id'], 'data': item['data']})
    return result


def _sort_items_by_cursor(items):
    return sorted(
        items,
        key=lambda item: (item['created_at'], item['request_id']),
        reverse=True,
    )


def _sort_items_by_request_id(items):
    return sorted(items, key=lambda item: item['request_id'])


@pytest.mark.ydb(
    files=['ydb/request_compilations_main_index_by_request_id.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.parametrize(
    'json_body, expected_response_code, expected_items,',
    [
        (
            {
                'request_ids': [
                    '2d6fb2df-15b9-4855-9cc1-e51f5f1bc674',
                    'aadc50f7-5654-4f38-a669-de2aee65aeac',
                    '13aad1ae-c205-42e8-94e1-e7c96728d738',
                ],
            },
            200,
            _get_items(['A1', 'A3', 'A5']),
        ),
        (
            {'request_ids': ['aadc50f7-5654-4f38-a669-de2aee65aeac']},
            200,
            _get_items(['A5']),
        ),
        (
            {
                'request_ids': [
                    '3121c950-1024-4be1-9ba5-33e6dae2da4a',
                    '288affa0-50e8-458e-8ab7-5bdb8938de7a',
                    'd81dec52-83e9-4175-93bb-0e913d6afbb9',
                    '6d2b13a2-f55b-4063-a269-d91d545508ae',
                ],
            },
            200,
            _get_items(['A4', 'B2', 'B4', 'B7']),
        ),
        ({}, 400, None),
        ({'request_ids': ['some_id' for i in range(1000)]}, 200, []),
        ({'request_ids': ['some_id' for i in range(1001)]}, 400, None),
    ],
)
async def test_list_by_id(
        taxi_logistic_platform_replica,
        json_body,
        expected_response_code,
        expected_items,
):
    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_ID, params={'cluster': 'main'}, json=json_body,
    )

    assert response.status_code == expected_response_code
    if expected_response_code == 200:
        response_items = response.json()['items']
        assert _sort_items_by_request_id(
            response_items,
        ) == _sort_items_by_request_id(expected_items)


@pytest.mark.parametrize(
    'params, expected_response_code, expected_items,',
    [
        pytest.param(
            {'cluster': 'market'},
            400,
            None,
            marks=pytest.mark.config(
                LOGISTIC_PLATFORM_REPLICA_SETTINGS={
                    'list_of_clusters': ['main', 'market'],
                },
            ),
        ),
        pytest.param({'cluster': 'market'}, 400, None),
        pytest.param({'cluster': 'other_cluster'}, 400, None),
        pytest.param({}, 400, None),
    ],
)
async def test_other_clusters(
        taxi_logistic_platform_replica,
        params,
        expected_response_code,
        expected_items,
):
    json_body = {
        'request_ids': [
            '23aad1ae-c205-42e8-94e1-e7c96728d738',
            '4d6fb2df-15b9-4855-9cc1-e51f5f1bc674',
        ],
    }
    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_ID, params=params, json=json_body,
    )

    assert response.status_code == expected_response_code
    if expected_response_code == 200:
        response_items = response.json()['items']
        assert _sort_items_by_request_id(
            response_items,
        ) == _sort_items_by_request_id(expected_items)


@pytest.mark.ydb(
    files=['ydb/request_compilations_main_index_by_request_id.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.parametrize(
    'expected_response_code, expected_items, timeout',
    [
        pytest.param(
            500,
            None,
            0,
            marks=pytest.mark.config(
                LOGISTIC_PLATFORM_REPLICA_SETTINGS={
                    'retrieve_degradation_immitation': {
                        'return_error_from_ydb': True,
                    },
                    'list_of_clusters': ['main'],
                },
            ),
        ),
        pytest.param(
            200,
            _get_items(['A4', 'B2', 'B4', 'B7']),
            0,
            marks=pytest.mark.config(
                LOGISTIC_PLATFORM_REPLICA_SETTINGS={
                    'retrieve_degradation_immitation': {
                        'return_error_from_ydb': False,
                    },
                    'list_of_clusters': ['main'],
                },
            ),
        ),
        pytest.param(
            200,
            _get_items(['A4', 'B2', 'B4', 'B7']),
            500,
            marks=pytest.mark.config(
                LOGISTIC_PLATFORM_REPLICA_SETTINGS={
                    'retrieve_degradation_immitation': {'timeout_ms': 500},
                    'list_of_clusters': ['main'],
                },
            ),
        ),
    ],
)
async def test_using_of_degradation_config(
        taxi_logistic_platform_replica,
        expected_response_code,
        expected_items,
        timeout,
):
    request_json = {
        'request_ids': [
            '3121c950-1024-4be1-9ba5-33e6dae2da4a',
            '288affa0-50e8-458e-8ab7-5bdb8938de7a',
            'd81dec52-83e9-4175-93bb-0e913d6afbb9',
            '6d2b13a2-f55b-4063-a269-d91d545508ae',
        ],
    }
    start = datetime.datetime.now()
    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_ID, params={'cluster': 'main'}, json=request_json,
    )
    assert (datetime.datetime.now() - start).total_seconds() * 1000 >= timeout

    assert response.status_code == expected_response_code
    if response.status_code == 200:
        response_items = response.json()['items']
        assert _sort_items_by_request_id(
            response_items,
        ) == _sort_items_by_request_id(expected_items)


@pytest.mark.ydb(
    files=['ydb/request_compilations_main_index_by_request_id.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.config(YDB_QUERY_RESULT_MAX_ROWS_COUNT=1)
async def test_ydb_max_row_count_work(taxi_logistic_platform_replica):
    request_json = {
        'request_ids': [
            '3121c950-1024-4be1-9ba5-33e6dae2da4a',
            '288affa0-50e8-458e-8ab7-5bdb8938de7a',
            'd81dec52-83e9-4175-93bb-0e913d6afbb9',
            '6d2b13a2-f55b-4063-a269-d91d545508ae',
        ],
    }
    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_ID, params={'cluster': 'main'}, json=request_json,
    )
    assert response.status_code == 200

    response_items = response.json()['items']
    expected_items = _get_items(['A4', 'B2', 'B4', 'B7'])
    assert _sort_items_by_request_id(
        response_items,
    ) == _sort_items_by_request_id(expected_items)


@pytest.mark.ydb(
    files=['ydb/request_compilations_main_index_by_request_code.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.parametrize(
    'json_body, expected_response_code, expected_items,',
    [
        (
            {
                'request_codes': [
                    'request_code1',
                    'request_code3',
                    'request_code4',
                ],
                'employer_code': 'third_employer',
            },
            200,
            _get_items(['A3', 'A4']),
        ),
        (
            {
                'request_codes': ['request_code3'],
                'employer_code': 'third_employer',
            },
            200,
            _get_items(['A3']),
        ),
        (
            {
                'request_codes': [
                    'request_code1',
                    'request_code2',
                    'request_code5',
                    'request_code8',
                    'request_code9',
                ],
                'employer_code': 'first_employer',
            },
            200,
            _get_items(['A1', 'B1', 'B4']),
        ),
        (
            {
                'request_codes': [
                    'request_code1',
                    'request_code3',
                    'request_code4',
                ],
            },
            200,
            _get_items(['A1', 'A3', 'A4', 'A5']),
        ),
        (
            {
                'request_codes': [
                    'request_code1',
                    'request_code2',
                    'request_code5',
                    'request_code8',
                    'request_code9',
                ],
            },
            200,
            _get_items(['A1', 'A2', 'A4', 'B1', 'B4', 'B5']),
        ),
        ({}, 400, None),
        (
            {
                'request_codes': ['some_id' for i in range(999)],
                'employer_code': 'some_employer',
            },
            200,
            [],
        ),
        (
            {
                'request_codes': ['some_id' for i in range(1000)],
                'employer_code': 'some_employer',
            },
            400,
            None,
        ),
    ],
)
async def test_list_by_code_without_truncating(
        taxi_logistic_platform_replica,
        json_body,
        expected_response_code,
        expected_items,
):
    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_CODE, params={'cluster': 'main'}, json=json_body,
    )

    assert response.status_code == expected_response_code
    if expected_response_code == 200:
        response_items = response.json()['items']
        assert _sort_items_by_request_id(
            response_items,
        ) == _sort_items_by_request_id(expected_items)
        assert response.json()['is_result_truncated'] is False


@pytest.mark.ydb(
    files=['ydb/request_compilations_main_index_by_request_code.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.parametrize(
    'expected_count_of_items,',
    [
        pytest.param(
            0, marks=pytest.mark.config(YDB_QUERY_RESULT_MAX_ROWS_COUNT=1),
        ),
        pytest.param(
            1, marks=pytest.mark.config(YDB_QUERY_RESULT_MAX_ROWS_COUNT=2),
        ),
        pytest.param(
            11, marks=pytest.mark.config(YDB_QUERY_RESULT_MAX_ROWS_COUNT=12),
        ),
    ],
)
async def test_list_by_code_with_truncating(
        taxi_logistic_platform_replica, expected_count_of_items,
):
    json_body = {'request_codes': ['request_code' + str(i) for i in range(12)]}

    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_CODE, params={'cluster': 'main'}, json=json_body,
    )

    assert response.status_code == 200
    assert len(response.json()['items']) == expected_count_of_items
    assert response.json()['is_result_truncated'] is True


@pytest.mark.ydb(
    files=['ydb/request_compilations_main_cursor_with_filters.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.parametrize(
    'json_body, expected_response_code, list_of_suffixes,',
    [
        (
            {'page_size': 100, 'filter': {'status': ['canceled', 'finished']}},
            200,
            ['A1', 'A4', 'B1', 'B2', 'B7'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'delivery_date': {
                        'begin': '2022-01-12T05:48:48Z',
                        'end': '2022-12-26T01:12:04Z',
                    },
                },
            },
            200,
            ['A1', 'A4', 'B2', 'B7'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'delivery_date': {'begin': '2022-01-12T05:48:48Z'},
                },
            },
            200,
            ['A1', 'A4', 'B1', 'B2', 'B7'],
        ),
        (
            {'page_size': 100, 'filter': {'delivery_date': {'begin': ''}}},
            400,
            None,
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'delivery_date': {'end': '2022-01-28T19:52:59Z'},
                },
            },
            200,
            ['A4', 'A1'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'created_at': {
                        'begin': '2022-01-28T19:52:49Z',
                        'end': '2022-12-16T03:39:05Z',
                    },
                },
            },
            200,
            ['A1', 'B2', 'B7'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'created_at': {'begin': '2022-01-28T19:52:49Z'},
                },
            },
            200,
            ['A1', 'B1', 'B2', 'B7'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'created_at': {'end': '2022-01-28T19:52:49Z'},
                },
            },
            200,
            ['A4', 'A1'],
        ),
        ({'page_size': 100, 'filter': {'created_at': {'end': ''}}}, 400, None),
    ],
)
async def test_search_by_status_and_date_range(
        taxi_logistic_platform_replica,
        json_body,
        expected_response_code,
        list_of_suffixes,
):
    response = await taxi_logistic_platform_replica.post(
        path=URL_SEARCH, params={'cluster': 'main'}, json=json_body,
    )
    assert response.status_code == expected_response_code
    if response.status_code == 200:
        response_items = response.json()['items']
        expected_items = _get_items(
            list_of_suffixes, sort_function=_sort_items_by_cursor,
        )
        assert response_items == expected_items


@pytest.mark.ydb(
    files=['ydb/request_compilations_main_cursor_with_filters.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.parametrize(
    'json_body, expected_response_code, list_of_suffixes,',
    [
        (
            {
                'page_size': 100,
                'filter': {
                    'delivery_policy': ['min_by_request', 'another_policy'],
                },
            },
            200,
            ['A1', 'A5', 'B2', 'B3', 'B6', 'B7'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'delivery_policy': ['min_by_request', 'another_policy'],
                    'operator_id': 'strizh',
                },
            },
            200,
            ['A1', 'B3'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'operator_id': 'lavka',
                    'recipient_phone_pd_id': 'qwerty',
                },
            },
            200,
            ['A2', 'B4'],
        ),
        ({'page_size': 100, 'filter': {'delivery_policy': []}}, 400, None),
    ],
)
async def test_search_by_delivery_policy_and_string_params(
        taxi_logistic_platform_replica,
        json_body,
        expected_response_code,
        list_of_suffixes,
):
    response = await taxi_logistic_platform_replica.post(
        path=URL_SEARCH, params={'cluster': 'main'}, json=json_body,
    )
    assert response.status_code == expected_response_code
    if response.status_code == 200:
        response_items = response.json()['items']
        expected_items = _get_items(
            list_of_suffixes, sort_function=_sort_items_by_cursor,
        )
        assert response_items == expected_items


@pytest.mark.ydb(
    files=[
        (
            'ydb/request_compilations_main_cursor'
            '_with_filters_by_employer_code.sql'
        ),
    ],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.parametrize(
    'json_body, list_of_suffixes,',
    [
        (
            {
                'page_size': 100,
                'filter': {
                    'delivery_policy': [
                        'min_by_request',
                        'interval_with_fees',
                    ],
                    'employer_code': 'third_employer',
                },
            },
            ['A3', 'A4'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'operator_id': 'lavka',
                    'recipient_phone_pd_id': 'qwerty',
                    'employer_code': 'first_employer',
                },
            },
            ['B4'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'processing'],
                    'created_at': {'begin': '2022-01-28T19:52:49Z'},
                    'delivery_date': {'end': '2030-01-01T00:00:00Z'},
                    'employer_code': 'first_employer',
                },
            },
            ['A1', 'B2', 'B4'],
        ),
    ],
)
async def test_search_with_employer_code(
        taxi_logistic_platform_replica, json_body, list_of_suffixes,
):
    response = await taxi_logistic_platform_replica.post(
        path=URL_SEARCH, params={'cluster': 'main'}, json=json_body,
    )
    assert response.status_code == 200
    response_items = response.json()['items']
    expected_items = _get_items(
        list_of_suffixes, sort_function=_sort_items_by_cursor,
    )
    assert response_items == expected_items


@pytest.mark.ydb(
    files=[
        (
            'ydb/request_compilations_main_cursor'
            '_with_filters_by_employer_code.sql'
        ),
    ],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.parametrize(
    'page_size, total_step_number', [(1, 4), (2, 2), (3, 2), (4, 1)],
)
async def test_cursor_by_search_with_employer_code(
        taxi_logistic_platform_replica, page_size, total_step_number,
):
    json_body = {
        'page_size': page_size,
        'filter': {'employer_code': 'first_employer'},
    }

    current_step_number = 0
    response_items = list()

    while current_step_number < 5:
        response = await taxi_logistic_platform_replica.post(
            path=URL_SEARCH, params={'cluster': 'main'}, json=json_body,
        )

        assert response.status_code == 200
        response_json = response.json()
        print(response_json['cursor'])
        if response_json['items'] == []:
            break

        response_items += response_json['items']
        current_step_number += 1
        json_body['cursor'] = response_json['cursor']

    expected_items = _get_items(
        ['A1', 'B1', 'B2', 'B4'], sort_function=_sort_items_by_cursor,
    )
    assert response_items == expected_items
    assert current_step_number == total_step_number


@pytest.mark.ydb(
    files=['ydb/request_compilations_main_cursor_with_filters.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
@pytest.mark.parametrize(
    'page_size, total_step_number', [(1, 4), (2, 2), (3, 2), (4, 1), (6, 1)],
)
async def test_cursor_by_search_without_employer_code(
        taxi_logistic_platform_replica, page_size, total_step_number,
):
    json_body = {
        'page_size': page_size,
        'filter': {
            'status': ['canceled', 'finished'],
            'created_at': {'begin': '2022-01-28T19:52:49Z'},
        },
    }

    current_step_number = 0
    response_items = list()

    while current_step_number < 5:
        response = await taxi_logistic_platform_replica.post(
            path=URL_SEARCH, params={'cluster': 'main'}, json=json_body,
        )

        assert response.status_code == 200
        response_json = response.json()
        print(response_json['cursor'])
        if response_json['items'] == []:
            break

        response_items += response_json['items']
        current_step_number += 1
        json_body['cursor'] = response_json['cursor']

    expected_items = _get_items(
        ['A1', 'B1', 'B2', 'B7'], sort_function=_sort_items_by_cursor,
    )
    assert response_items == expected_items
    assert current_step_number == total_step_number


async def test_cursor_format(taxi_logistic_platform_replica):
    cursor_format_list = [
        '1bc|bc|123',
        '|1|2',
        '1|1ab|request_id',
        '1||',
        '',
        'abcd',
        '1',
        '1|',
        '1|1',
        '2|2|3',
        '1|2|3|',
    ]
    json_body = {'page_size': 100, 'cursor': '2|2|3', 'filter': {}}
    for cursor_value in cursor_format_list:
        json_body['cursor'] = cursor_value
        response = await taxi_logistic_platform_replica.post(
            path=URL_SEARCH, params={'cluster': 'main'}, json=json_body,
        )
        assert response.status_code == 400


@pytest.mark.ydb(
    files=['ydb/request_compilations_main_cursor_with_filters.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_main_struct.sql'])
async def test_cursor_created_at_bigger_than_created_at_end(
        taxi_logistic_platform_replica,
):
    json_body = {
        'page_size': 100,
        'cursor': '1|1643399570|2d6fb2df-15b9-4855-9cc1-e51f5f1bc674',
        'filter': {
            'status': ['canceled', 'finished'],
            'created_at': {'end': '2022-01-28T19:52:49Z'},
        },
    }
    expected_items = _get_items(
        ['A1', 'A4'], sort_function=_sort_items_by_cursor,
    )

    response = await taxi_logistic_platform_replica.post(
        path=URL_SEARCH, params={'cluster': 'main'}, json=json_body,
    )
    assert response.status_code == 200
    assert response.json()['items'] == expected_items


@pytest.mark.parametrize(
    'json_body,',
    [
        (
            {
                'page_size': 100,
                'filter': {
                    'created_at': {
                        'begin': '2032-01-28T19:52:49Z',
                        'end': '2022-01-28T19:52:49Z',
                    },
                },
            }
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'delivery_date': {
                        'begin': '2032-01-28T19:52:49Z',
                        'end': '2022-01-28T19:52:49Z',
                    },
                },
            }
        ),
        (
            {
                'page_size': 100,
                'cursor': '1|1641490467|2d6fb2df-15b9-4855-9cc1-e51f5f1bc674',
                'filter': {'delivery_date': {'end': '2010-01-28T19:52:49Z'}},
            }
        ),
    ],
)
async def test_not_valid_request_filters(
        taxi_logistic_platform_replica, testpoint, json_body,
):
    @testpoint('ydb-query-kFetchRequestCompilationsDataFromPartition')
    async def ydb_query_from_partition(data):
        return {}

    response = await taxi_logistic_platform_replica.post(
        path=URL_SEARCH, params={'cluster': 'main'}, json=json_body,
    )
    assert response.status_code == 200
    assert response.json()['items'] == []
    assert response.json()['cursor'] == ''
    assert ydb_query_from_partition.times_called == 0
