import pytest

URL_LIST_BY_ID = (
    '/internal/logistic-platform-replica/request-compilations/list-by-id'
)
URL_LIST_BY_CODE = (
    '/internal/logistic-platform-replica/request-compilations/list-by-code'
)
URL_SEARCH = '/internal/logistic-platform-replica/request-compilations/search'


DATA_SUFFIX_TO_ITEMS = {
    '1': {
        'created_at': 1800000000,
        'data': 'PG_DATA_STRING_1',
        'request_id': 'PGaad1ae-c205-42e8-94e1-e7c96728d738',
    },
    '2': {
        'created_at': 1800000005,
        'request_id': 'PG243441-785b-4a70-a2c2-bf48348f4225',
        'data': 'PG_DATA_STRING_2',
    },
    '3': {
        'created_at': 1800001005,
        'data': 'PG_DATA_STRING_3',
        'request_id': 'PG6fb2df-15b9-4855-9cc1-e51f5f1bc674',
    },
    '4': {
        'created_at': 1800000005,
        'request_id': 'PG21c950-1024-4be1-9ba5-33e6dae2da4a',
        'data': 'PG_DATA_STRING_4',
    },
    '5': {
        'created_at': 1800000000,
        'data': 'PG_DATA_STRING_5',
        'request_id': 'PGdc50f7-5654-4f38-a669-de2aee65aeac',
    },
    '6': {
        'created_at': 1800001000,
        'data': 'PG_DATA_STRING_6',
        'request_id': 'PGc7720b-8e6c-4d30-bd73-5d52916be754',
    },
    '7': {
        'created_at': 1800002000,
        'data': 'PG_DATA_STRING_7',
        'request_id': 'PG8affa0-50e8-458e-8ab7-5bdb8938de7a',
    },
    '8': {
        'created_at': 1800000001,
        'request_id': 'PG04acd2-aee3-4058-a194-57b6ddc635f5',
        'data': 'PG_DATA_STRING_8',
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


@pytest.mark.pgsql('logistic_platform', files=['pg/request_compilations.sql'])
@pytest.mark.parametrize(
    'json_body, expected_response_code, expected_items,',
    [
        (
            {
                'request_ids': [
                    'PG6fb2df-15b9-4855-9cc1-e51f5f1bc674',
                    'PGdc50f7-5654-4f38-a669-de2aee65aeac',
                    'PGaad1ae-c205-42e8-94e1-e7c96728d738',
                ],
            },
            200,
            _get_items(['1', '3', '5']),
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


@pytest.mark.pgsql('logistic_platform', files=['pg/request_compilations.sql'])
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
            _get_items(['3', '4']),
        ),
        (
            {
                'request_codes': [
                    'request_code1',
                    'request_code2',
                    'request_code5',
                ],
                'employer_code': 'first_employer',
            },
            200,
            _get_items(['1', '6']),
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
            _get_items(['1', '3', '4', '5']),
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
async def test_list_by_code(
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


@pytest.mark.config(YDB_QUERY_RESULT_MAX_ROWS_COUNT=3)
@pytest.mark.pgsql('logistic_platform', files=['pg/request_compilations.sql'])
async def test_list_by_code_with_truncating(taxi_logistic_platform_replica):
    json_body = {
        'request_codes': ['request_code1', 'request_code3', 'request_code4'],
    }
    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_CODE, params={'cluster': 'main'}, json=json_body,
    )

    assert response.status_code == 200
    response_items = response.json()['items']
    assert len(response_items) == 2
    assert response.json()['is_result_truncated'] is True


@pytest.mark.pgsql('logistic_platform', files=['pg/request_compilations.sql'])
@pytest.mark.parametrize(
    'json_body, expected_response_code, list_of_suffixes,',
    [
        (
            {'page_size': 100, 'filter': {'status': ['canceled', 'finished']}},
            200,
            ['1', '4', '6', '7'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'delivery_date': {
                        'begin': '2027-01-15T08:00:10Z',
                        'end': '2027-01-15T09:23:31Z',
                    },
                },
            },
            200,
            ['1', '4'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'delivery_date': {'begin': '2027-01-15T09:23:31Z'},
                },
            },
            200,
            ['4', '6', '7'],
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
                    'delivery_date': {'end': '2027-01-15T09:23:31Z'},
                },
            },
            200,
            ['1', '4'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'created_at': {
                        'begin': '2027-01-15T07:00:00Z',
                        'end': '2027-01-15T08:33:19Z',
                    },
                },
            },
            200,
            ['1', '4', '6'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'created_at': {'begin': '2027-01-15T08:00:00Z'},
                },
            },
            200,
            ['1', '4', '6', '7'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'finished'],
                    'created_at': {'end': '2027-01-15T08:00:05Z'},
                },
            },
            200,
            ['1', '4'],
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


@pytest.mark.pgsql('logistic_platform', files=['pg/request_compilations.sql'])
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
            ['1', '5', '7', '8'],
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
            ['1', '8'],
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
            ['2'],
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


@pytest.mark.pgsql('logistic_platform', files=['pg/request_compilations.sql'])
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
            ['3', '4'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'operator_id': 'lavka',
                    'recipient_phone_pd_id': 'qwerty',
                    'employer_code': 'second_employer',
                },
            },
            ['2'],
        ),
        (
            {
                'page_size': 100,
                'filter': {
                    'status': ['canceled', 'processing'],
                    'created_at': {'begin': '2027-01-15T08:00:00Z'},
                    'delivery_date': {'end': '2027-01-15T09:23:31Z'},
                    'employer_code': 'first_employer',
                },
            },
            ['1'],
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


@pytest.mark.pgsql('logistic_platform', files=['pg/request_compilations.sql'])
@pytest.mark.parametrize(
    'page_size, total_step_number', [(1, 3), (2, 2), (3, 1), (4, 1)],
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
        ['1', '6', '7'], sort_function=_sort_items_by_cursor,
    )
    assert response_items == expected_items
    assert current_step_number == total_step_number


@pytest.mark.pgsql('logistic_platform', files=['pg/request_compilations.sql'])
@pytest.mark.parametrize(
    'page_size, total_step_number', [(1, 4), (2, 2), (3, 2), (4, 1), (6, 1)],
)
async def test_cursor_by_search_without_employer_code(
        taxi_logistic_platform_replica, page_size, total_step_number,
):
    json_body = {
        'page_size': page_size,
        'filter': {'status': ['canceled', 'finished']},
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
        ['1', '4', '6', '7'], sort_function=_sort_items_by_cursor,
    )
    assert response_items == expected_items
    assert current_step_number == total_step_number


@pytest.mark.pgsql('logistic_platform', files=['pg/request_compilations.sql'])
async def test_pg_archiving_emulation(taxi_logistic_platform_replica):
    json_body = {'request_codes': ['request_code8']}

    response = await taxi_logistic_platform_replica.post(
        path=URL_LIST_BY_CODE, params={'cluster': 'main'}, json=json_body,
    )
    assert response.status_code == 200
    assert len(response.json()['items']) == 1
    assert response.json()['items'][0]['data'] == 'PG_DATA_STRING_10'
