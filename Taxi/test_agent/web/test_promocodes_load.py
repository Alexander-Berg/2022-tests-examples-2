import datetime

import pytest


@pytest.mark.now('2022-01-01T10:00:00')
@pytest.mark.parametrize(
    'csv_file_name,goods_detail_id,status,promocodes_data,goods_detail_amount',
    [
        (
            'ok_file.csv',
            1,
            200,
            [
                {
                    'id': 1,
                    'hash': 'FIUH!@##',
                    'goods_detail_id': 1,
                    'expired_date': datetime.date(2022, 1, 1),
                },
                {
                    'id': 2,
                    'hash': 'FJWJKLEL@',
                    'goods_detail_id': 1,
                    'expired_date': datetime.date(2022, 1, 1),
                },
            ],
            [{'id': 1, 'amount': 54}],
        ),
        ('invalid_file.csv', 1, 400, [], [{'id': 1, 'amount': 52}]),
        ('invalid_fields_file.csv', 1, 400, [], [{'id': 1, 'amount': 52}]),
    ],
)
async def test_promocodes_load(
        web_app_client,
        web_context,
        load_binary,
        csv_file_name,
        goods_detail_id,
        status,
        promocodes_data,
        goods_detail_amount,
):

    csv_file = load_binary(csv_file_name)

    response = await web_app_client.post(
        '/shop/promocodes/load',
        params={'goods_detail_id': goods_detail_id},
        data=csv_file,
        headers={'X-Yandex-Login': 'admin', 'Accept-Language': 'ru-RU'},
    )
    assert response.status == status

    query = (
        'SELECT id, hash, goods_detail_id, expired_date FROM agent.promocodes'
    )
    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        assert [dict(row) for row in rows] == promocodes_data

    query = 'SELECT id, amount FROM agent.goods_detail'
    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        assert [dict(row) for row in rows] == goods_detail_amount
