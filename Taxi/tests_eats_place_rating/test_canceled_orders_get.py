def response_ordershistory(order_id, place_id, status, reason):
    return {
        'order_id': order_id,
        'place_id': place_id,
        'status': status,
        'cancel_reason': reason,
        'source': 'eda',
        'delivery_location': {'lat': 1.0, 'lon': 1.0},
        'total_amount': '123.45',
        'is_asap': True,
        'created_at': '2021-07-25T12:01:00+00:00',
    }


async def test_get(taxi_eats_place_rating, mockserver, pgsql):
    @mockserver.json_handler('/eats-ordershistory/internal/v1/get-orders/list')
    def _ordershistory_orders(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': [
                    response_ordershistory(
                        '111-111', 123456, 'cancelled', 'cancel_reason1',
                    ),
                    response_ordershistory(
                        '444-444', 123456, 'cancelled', 'cancel_reason4',
                    ),
                ],
            },
        )

    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'INSERT INTO'
        ' eats_place_rating.excluded_canceled_orders'
        '(order_nr,place_id,user_context,reason,is_deleted) '
        'VALUES (\'111-111\', 123456, \'user\', \'because1\', true),'
        '(\'222-222\', 123456, \'user\', \'because2\', false);',
    )

    cursor.execute(
        'INSERT INTO'
        ' eats_place_rating.place_cancels'
        '(order_nr,place_id,canceled_by_place_reason,'
        'canceled_by_place,updated_at) '
        'VALUES (\'222-222\', 123456, \'cancel_reason2\','
        ' true, current_timestamp)',
    )

    response = await taxi_eats_place_rating.get(
        '/eats/v1/eats-place-rating/v1/canceled-orders?'
        'order_nrs=111-111,222-222,333-333,444-444',
    )
    assert response.status_code == 200
    assert response.json() == {
        'cancels': [
            {
                'canceled_by_reason': 'cancel_reason1',
                'modified_by_reason': 'because1',
                'order_nr': '111-111',
                'place_id': 123456,
                'status': 'excluded',
                'user_context': 'user',
            },
            {
                'canceled_by_reason': 'cancel_reason2',
                'modified_by_reason': 'because2',
                'order_nr': '222-222',
                'place_id': 123456,
                'status': 'restored',
                'user_context': 'user',
            },
            {'order_nr': '333-333'},
            {
                'canceled_by_reason': 'cancel_reason4',
                'order_nr': '444-444',
                'place_id': 123456,
                'status': 'unmodified',
            },
        ],
    }
