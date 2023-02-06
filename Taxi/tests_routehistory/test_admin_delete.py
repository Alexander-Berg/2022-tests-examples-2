import pytest

from . import utils


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(ROUTEHISTORY_ADMIN_DELETE_LIMIT=limit),
            id=f'limit-{limit}',
        )
        for limit in [1, 2, 3, 4, 5, 100]
    ],
)
@pytest.mark.parametrize(
    'request_obj, orders_to_delete, expected_uapi_calls',
    [
        ({'phone_id': '123456789abcdef123456789', 'order_ids': []}, [], 0),
        (
            {
                'phone_id': '123456789abcdef123456789',
                'order_ids': ['11111111000000000000000000000007'],
            },
            ['11111111-0000-0000-0000-000000000007'],
            0,
        ),
        (
            {'order_ids': ['11111111000000000000000000000008']},
            ['11111111-0000-0000-0000-000000000008'],
            0,
        ),
        (
            {'phone_id': '123456789abcdef123456789'},
            [
                '11111111-0000-0000-0000-000000000007',
                '11111111-0000-0000-0000-000000000008',
            ],
            0,
        ),
        (
            {'phone_id': '1dcf5804abae14bb0d31d02d'},
            [
                '11111111-0000-0000-0000-000000000003',
                '11111111-0000-0000-0000-000000000002',
                '11111111-0000-0000-0000-000000000001',
                '11111111-0000-0000-0000-000000000004',
            ],
            0,
        ),
        (
            {'phone': '+79001234567'},
            [
                '11111111-0000-0000-0000-000000000007',
                '11111111-0000-0000-0000-000000000008',
            ],
            1,
        ),
    ],
)
async def test_admin_delete(
        taxi_routehistory,
        pgsql,
        load_json,
        request_obj,
        orders_to_delete,
        expected_uapi_calls,
        mockserver,
):
    cursor = pgsql['routehistory_ph'].cursor()
    utils.fill_db(cursor, load_json('db_ph.json'))
    cursor.execute(
        'SELECT order_id FROM routehistory_ph.phone_history2 '
        'ORDER BY order_id',
    )
    all_orders = utils.convert_pg_result(cursor.fetchall())

    # Test that to-be-deleted orders are present initially:
    assert all(order in all_orders for order in orders_to_delete)

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _uapi_mock(request):
        return load_json('uapi_response.json')

    response = await taxi_routehistory.post(
        'routehistory/admin/delete', request_obj, headers={},
    )

    assert response.status_code == 200
    assert _uapi_mock.times_called == expected_uapi_calls

    cursor.execute(
        'SELECT order_id FROM routehistory_ph.phone_history2 '
        'ORDER BY order_id',
    )
    remaining_orders = utils.convert_pg_result(cursor.fetchall())
    for order in orders_to_delete:
        all_orders.remove(order)
    assert all_orders == remaining_orders
