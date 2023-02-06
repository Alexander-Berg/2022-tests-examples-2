DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


async def test_simple(
        taxi_cargo_orders, my_waybill_info, default_order_id, mockserver,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/get-update-diff')
    def mock_dispatch(request):
        assert request.json['waybill_ref'] == 'new_waybill_1'
        return {
            'new_points': [
                my_waybill_info['execution']['points'][0],
                my_waybill_info['execution']['points'][1],
            ],
            'revision': 3,
            'extra_time_min': 10,
        }

    @mockserver.json_handler(
        '/driver-orders-builder/v1/cargo/build-update-offer-screen',
    )
    def mock_dob(request):
        assert request.json == {
            'route_points': [
                {'title': 'Получение', 'subtitle': 'БЦ Аврора'},
                {'title': 'Выдача', 'subtitle': 'Ураина'},
            ],
        }
        return {
            'constructor_items': [
                {
                    'horizontal_divider_type': 'bottom_gap',
                    'reverse': True,
                    'subtitle': 'Получение',
                    'title': 'БЦ Аврора',
                    'type': 'default',
                },
                {
                    'horizontal_divider_type': 'bottom_gap',
                    'reverse': True,
                    'subtitle': 'Вручение',
                    'title': 'Ураина',
                    'type': 'default',
                },
            ],
        }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/get-update-offer-ui',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'offer_id': 'new_waybill_1',
            'offer_revision': 3,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'rejection_button_params': {'title': 'Пропустить. Танкер'},
        'title': '+2 точки к текущему заказу. Танкер',
        'subtitle': 'Займет около 10 минут. Танкер',
        'constructor_items': [
            {
                'horizontal_divider_type': 'bottom_gap',
                'reverse': True,
                'subtitle': 'Получение',
                'title': 'БЦ Аврора',
                'type': 'default',
            },
            {
                'horizontal_divider_type': 'bottom_gap',
                'reverse': True,
                'subtitle': 'Вручение',
                'title': 'Ураина',
                'type': 'default',
            },
        ],
        'acceptance_button_params': {
            'button_color': '#fbe125',
            'timeout': 20,
            'title': 'Добавить к заказу. Танкер',
        },
    }

    assert mock_dispatch.times_called == 1
    assert mock_dob.times_called == 1


async def test_outdated_revision(
        taxi_cargo_orders, my_waybill_info, default_order_id, mockserver,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/get-update-diff')
    def mock_dispatch(request):
        assert request.json['waybill_ref'] == 'new_waybill_1'
        return {
            'new_points': [
                my_waybill_info['execution']['points'][0],
                my_waybill_info['execution']['points'][1],
            ],
            'revision': 100,
        }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/get-update-offer-ui',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'offer_id': 'new_waybill_1',
            'offer_revision': 3,
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'conflict',
        'message': 'revision is outdated',
    }

    assert mock_dispatch.times_called == 1
