import pytest

URL = '/internal/eats-orders-tracking/v1/get-claim-by-order-nr'


@pytest.mark.parametrize(
    'query, expected_response, expected_status_code',
    [
        (
            {'order_nr': '100000-100000'},
            {
                'order_nr': '100000-100000',
                'claim_id': 'id1',
                'claim_alias': 'default',
            },
            200,
        ),  # exist_claim_id
        (
            {'order_nr': '100011-100000'},
            {
                'code': 'NOT_FOUND_COURIER_DATA',
                'message': (
                    'Not found courier_data for order_nr: 100011-100000'
                ),
            },
            400,
        ),  # not_exist_courier_data
        (
            {'order_nr': '100001-100000'},
            {
                'code': 'NOT_FOUND_CLAIM_ID',
                'message': 'Not found claim_id for order_nr: 100001-100000',
            },
            400,
        ),  # not_exist_claim_id
        (
            {'order_nr': '100111-100000'},
            {
                'code': 'NOT_FOUND_CLAIM_ALIAS',
                'message': 'Not found claim_alias for order_nr: 100111-100000',
            },
            400,
        ),  # not_exist_claim_alias
        (
            {'order_nr': ''},
            {
                'code': 'EMPTY_ORDER_NR',
                'message': (
                    'Accepted empty order_nr on handler '
                    '/internal/eats-orders-tracking/v1/get-claim-by-order-nr'
                ),
            },
            400,
        ),  # empty_order_nr
        (
            {},
            {'code': '400', 'message': 'Missing order_nr in query'},
            400,
        ),  # empty_query
    ],
    ids=[
        'exist_claim_id',
        'not_exist_courier_data',
        'not_exist_claim_id',
        'not_exist_claim_alias',
        'empty_order_nr',
        'empty_query',
    ],
)
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_couriers.sql'])
async def test_get_problem(
        taxi_eats_orders_tracking,
        query,
        expected_response,
        expected_status_code,
):
    response = await taxi_eats_orders_tracking.get(URL, params=query)

    assert response.status_code == expected_status_code
    assert response.json() == expected_response
