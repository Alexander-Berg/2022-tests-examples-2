import copy

import pytest

from taxi.clickhouse import clickhouse


BASE_ANSWER = {
    'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
    'meta': [],
    'data': [],
    'rows': 1,
}


@pytest.mark.parametrize(
    'response_data, meta_info',
    [
        (
            [{'field1': 1, 'field2': 'asd'}],
            [
                {'name': 'field1', 'type': 'Int16'},
                {'name': 'field2', 'type': 'String'},
            ],
        ),
        (
            [{'field1': 1, 'field2': 'asd'}, {'field1': 2, 'field2': 'dsa'}],
            [
                {'name': 'field1', 'type': 'String'},
                {'name': 'field2', 'type': 'String'},
            ],
        ),
        (
            [],
            [
                {'name': 'field1', 'type': 'Int16'},
                {'name': 'field2', 'type': 'String'},
            ],
        ),
    ],
)
async def test_base(
        mock_clickhouse_host,
        clickhouse_connection,
        policy,
        response_mock,
        response_data,
        meta_info,
):
    def response(*args, **kwargs):
        response = copy.deepcopy(BASE_ANSWER)
        response['data'].extend(response_data)
        response['meta'].extend(meta_info)
        return response_mock(json=response)

    mock_clickhouse_host(
        clickhouse_response=response,
        request_url='http://less_awesome_db.db.yandex.net:8443'
        '/?database=test_db',
    )

    param_settings = clickhouse.settings.ParametersSettings()
    conn = clickhouse_connection()
    pol = policy(conn=conn)
    client = clickhouse.Clickhouse(
        conn=conn, ch_policy=pol, param_settings=param_settings,
    )

    res, _ = await client.select('SELECT * FROM test_db.table1')

    assert len(res) == len(response_data)
    if res:
        row = res[0]
        meta_info = sorted(
            meta_info, key=lambda x: list(row.keys()).index(x['name']),
        )
    for row in res:
        for column_name, column_meta in zip(row.keys(), meta_info):
            expected_type = column_meta['type']
            if expected_type == 'String':
                assert isinstance(row[column_name], str)
            elif 'Int' in expected_type:
                assert isinstance(row[column_name], int)
