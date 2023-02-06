import pytest


@pytest.mark.parametrize(
    'data, expected_status',
    [
        (
            {
                'data': [
                    {'login': 'test', 'payday_uid': 'payda_test'},
                    {'login': 'test_1', 'payday_uid': 'payda_test_1'},
                    {'login': 'test_2', 'payday_uid': 'payda_test_2'},
                ],
            },
            200,
        ),
        ({'data': []}, 200),
    ],
)
async def test_insert_payday_mapping(
        web_context, web_app_client, data, expected_status,
):
    response = await web_app_client.post(
        '/v1/payday/mapping-logins', json=data,
    )
    assert response.status == expected_status
    async with web_context.pg.slave_pool.acquire() as conn:
        db_results = await conn.fetch(
            'SELECT login, payday_uid '
            'FROM piecework.mapping_payday_uid_login '
            'ORDER BY login',
        )
        db_results = [dict(item) for item in db_results]

    assert data['data'] == db_results
