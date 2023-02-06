import pytest

URL_LIST_BY_ID = (
    '/internal/logistic-platform-replica/request-compilations/list-by-id'
)
URL_LIST_BY_CODE = (
    '/internal/logistic-platform-replica/request-compilations/list-by-code'
)
URL_SEARCH = '/internal/logistic-platform-replica/request-compilations/search'


DATA_SUFFIX_TO_ITEMS = {
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
    'PG1': {
        'created_at': 1643399569,
        'data': 'PG_DATA_STRING_PG1',
        'request_id': '13aad1ae-c205-42e8-94e1-e7c96728d738',
    },
    'PG2': {
        'created_at': 1641694841,
        'request_id': '07243441-785b-4a70-a2c2-bf48348f4225',
        'data': 'PG_DATA_STRING_PG2',
    },
    'PG3': {
        'created_at': 1671161946,
        'data': 'PG_DATA_STRING_PG3',
        'request_id': '09c7720b-8e6c-4d30-bd73-5d52916be754',
    },
    'PG4': {
        'created_at': 1670766632,
        'request_id': '288affa0-50e8-458e-8ab7-5bdb8938de7a',
        'data': 'PG_DATA_STRING_PG4',
    },
    'PG5': {
        'created_at': 1670017115,
        'request_id': '5d04acd2-aee3-4058-a194-57b6ddc635f5',
        'data': 'PG_DATA_STRING_PG5',
    },
    'PG6': {
        'created_at': 1670017115,
        'request_id': '0000acd2-aee3-4058-a194-57b6ddc635f5',
        'data': 'PG_DATA_STRING_PG6',
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


@pytest.mark.pgsql(
    'logistic_platform', files=['pg/request_compilations_merge_test.sql'],
)
@pytest.mark.ydb(
    files=['ydb/request_compilations_index_by_request_id_merge_test.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_struct_merge_test.sql'])
async def test_merge_in_list_by_id(taxi_logistic_platform_replica):
    json_body = {
        'request_ids': [
            '13aad1ae-c205-42e8-94e1-e7c96728d738',
            'b90b5b11-2b83-40fc-9920-957f43e602b6',
            '07243441-785b-4a70-a2c2-bf48348f4225',
            '0000acd2-aee3-4058-a194-57b6ddc635f5',
        ],
    }
    expected_items = _get_items(['PG1', 'PG2', 'PG6', 'B6'])
    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_ID, params={'cluster': 'main'}, json=json_body,
    )

    assert response.status_code == 200
    response_items = response.json()['items']
    assert _sort_items_by_request_id(
        response_items,
    ) == _sort_items_by_request_id(expected_items)


@pytest.mark.pgsql(
    'logistic_platform', files=['pg/request_compilations_merge_test.sql'],
)
@pytest.mark.ydb(
    files=['ydb/request_compilations_index_by_request_code_merge_test.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_struct_merge_test.sql'])
async def test_merge_in_list_by_code_without_truncating(
        taxi_logistic_platform_replica,
):
    json_body = {
        'request_codes': [
            'request_code1',
            'request_code2',
            'request_code5',
            'request_code8',
            'request_code9',
        ],
    }
    expected_items = _get_items(['PG1', 'PG2', 'A4', 'PG3', 'B4', 'B5', 'PG6'])
    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_CODE, params={'cluster': 'main'}, json=json_body,
    )

    assert response.status_code == 200
    response_items = response.json()['items']
    assert _sort_items_by_request_id(
        response_items,
    ) == _sort_items_by_request_id(expected_items)
    assert response.json()['is_result_truncated'] is False


@pytest.mark.config(YDB_QUERY_RESULT_MAX_ROWS_COUNT=4)
@pytest.mark.pgsql(
    'logistic_platform', files=['pg/request_compilations_merge_test.sql'],
)
@pytest.mark.ydb(
    files=['ydb/request_compilations_index_by_request_code_merge_test.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_struct_merge_test.sql'])
async def test_merge_in_list_by_code_with_truncating(
        taxi_logistic_platform_replica,
):
    json_body = {
        'request_codes': [
            'request_code1',
            'request_code2',
            'request_code5',
            'request_code8',
            'request_code9',
        ],
    }
    response = await taxi_logistic_platform_replica.post(
        URL_LIST_BY_CODE, params={'cluster': 'main'}, json=json_body,
    )

    assert response.status_code == 200
    response_items = response.json()['items']
    assert len(response_items) == 3
    assert response.json()['is_result_truncated'] is True


@pytest.mark.pgsql(
    'logistic_platform', files=['pg/request_compilations_merge_test.sql'],
)
@pytest.mark.ydb(
    files=['ydb/request_compilations_cursor_with_filters_merge_test.sql'],
)
@pytest.mark.ydb(files=['ydb/request_compilations_struct_merge_test.sql'])
async def test_merge_in_search(taxi_logistic_platform_replica):
    json_body = {
        'page_size': 100,
        'filter': {'delivery_policy': ['min_by_request', 'another_policy']},
    }
    expected_items = _get_items(
        ['PG1', 'A5', 'PG4', 'PG6', 'PG5', 'B6', 'B7', 'B3'],
        sort_function=_sort_items_by_cursor,
    )

    response = await taxi_logistic_platform_replica.post(
        URL_SEARCH, params={'cluster': 'main'}, json=json_body,
    )

    assert response.status_code == 200
    response_items = response.json()['items']
    assert response_items == expected_items
