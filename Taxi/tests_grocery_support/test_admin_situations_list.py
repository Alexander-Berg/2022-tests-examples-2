async def test_v3_handler(
        taxi_grocery_support, grocery_orders, mockserver, passport,
):
    order_id = 'TEST_ID'
    personal_phone_id = 'test_ppid'
    country_iso2 = 'ru'
    yandex_uid = 'test_uid'
    user_ip = 'test_ip'

    grocery_orders.add_order(
        order_id=order_id,
        user_info={
            'personal_phone_id': personal_phone_id,
            'yandex_uid': yandex_uid,
            'user_ip': user_ip,
        },
        country_iso2=country_iso2,
    )

    eats_request_json = {
        'order_type': 'lavka',
        'order_delivery_type': 'our_delivery',
        'personal_phone_id': personal_phone_id,
        'country_code': country_iso2,
        'is_grocery_flow': True,
        'has_ya_plus': True,
    }

    response_json = {
        'situations': [],
        'matrix_id': 1,
        'matrix_code': 'some_code',
    }

    @mockserver.json_handler(
        '/eats-compensations-matrix'
        '/eats-compensations-matrix/v1/api/compensation/list',
    )
    def mock_eats_compensations_list(request):
        assert eats_request_json == request.json
        return response_json

    response = await taxi_grocery_support.post(
        '/v3/api/compensation/list',
        json={'order_id': order_id},
        headers={'X-Yandex-Login': 'superSupport'},
    )

    assert response.status_code == 200
    assert response.json() == response_json
    assert mock_eats_compensations_list.times_called == 1
    assert passport.times_mock_blackbox_called() == 1
