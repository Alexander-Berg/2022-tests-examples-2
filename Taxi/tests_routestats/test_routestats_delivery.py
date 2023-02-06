import pytest

from testsuite.utils import matching

PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
    'X-AppMetrica-DeviceId': 'DeviceId',
}


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:delivery_order_flow',
    ],
)
@pytest.mark.experiments3(filename='delivery_experiments.json')
async def test_routestats_with_delivery(
        taxi_routestats, mockserver, load_json, taxi_routestats_monitor,
):
    await taxi_routestats.tests_control(reset_metrics=True)

    delivery_classes = ['cargo', 'courier', 'express']

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    @mockserver.json_handler('/cargo-c2c/v1/delivery/estimate')
    def _cargo_c2c(request):
        assert request.json == {
            'delivery_description': {
                'payment_info': {
                    'id': 'card-eeeeeeeeeeeeeeeeeeeeeeeee',
                    'type': 'card',
                    'coupon': 'some_coupon_code',
                },
                'route_points': [
                    {
                        'coordinates': [37.587569, 55.733393],
                        'type': 'source',
                        'uri': 'point_a_uri',
                    },
                    {
                        'coordinates': [37.687569, 55.833393],
                        'type': 'destination',
                    },
                ],
                'zone_name': 'moscow',
                'due': '2020-01-01T00:00:00+00:00',
            },
            'taxi_tariffs': [
                {
                    'taxi_requirements': {
                        'a': 1,
                        'b': 'abacaba',
                        'c': [1, 2, 3],
                    },
                    'taxi_tariff': 'cargo',
                },
                {'taxi_requirements': {}, 'taxi_tariff': 'courier'},
                {
                    'taxi_requirements': {},
                    'taxi_tariff': 'express',
                    'alternative_option': {'type': 'combo'},
                },
            ],
        }
        return {
            'estimations': [
                {
                    'type': 'succeed',
                    'offer_id': 'offer_id_1',
                    'taxi_tariff': 'cargo',
                    'price': '403.0000',
                    'currency': 'RUB',
                    'paid_supply_price': '150',
                    'paid_cancel_in_driving': {
                        'free_cancel_timeout': 300,
                        'cancel_price': '150',
                    },
                    'decision': 'paid_supply_enabled',
                },
                {
                    'type': 'succeed',
                    'offer_id': 'offer_id_2',
                    'taxi_tariff': 'express',
                    'price': '203.0000',
                    'currency': 'RUB',
                    'decision': 'order_allowed',
                },
                {
                    'type': 'succeed',
                    'offer_id': 'offer_id_combo',
                    'taxi_tariff': 'express',
                    'price': '100.0000',
                    'currency': 'RUB',
                    'decision': 'order_allowed',
                    'alternative_option': {'type': 'combo'},
                },
                {
                    'type': 'succeed',
                    'offer_id': 'offer_id_3',
                    'taxi_tariff': 'courier',
                    'price': '199.0000',
                    'currency': 'RUB',
                    'original_price': '299.0000',
                    'decision': 'no_cars_order_enabled',
                },
            ],
        }

    req = load_json('request.json')
    req['requirements'] = {'coupon': 'some_coupon_code'}
    req['supported'] = [
        {
            'type': 'order_flow_delivery',
            'payload': {'classes': delivery_classes},
        },
    ]
    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    delivery_service_levels = []
    for service_level in response.json()['service_levels']:
        if service_level['class'] in delivery_classes:
            if service_level['class'] == 'courier':
                assert (
                    service_level['delivery_extra']['order_select_settings'][
                        'header'
                    ]
                    == {
                        'image_tag': 'delivery_clock',
                        'image_tag_dark': 'delivery_clock_dark',
                        'text': matching.AnyString(),
                    }
                )
                assert (
                    service_level['delivery_extra']['order_select_settings'][
                        'selector_overrides'
                    ]
                    == {
                        'order_eta_subtitle': matching.AnyString(),
                        'tooltip': {'text': matching.AnyString()},
                    }
                )

                del service_level['delivery_extra']['order_select_settings']

            delivery_service_levels.append(service_level)

    assert _cargo_c2c.times_called == 1
    assert delivery_service_levels == load_json(
        'expected_delivery_levels.json',
    )

    stats = await taxi_routestats_monitor.get_metric(
        'delivery_order_flow_routestats_metrics',
    )
    assert stats == {
        'cargo': {
            'order_allowed': 0,
            'order_prohibited': 0,
            'paid_supply_enabled': 1,
        },
        'courier': {
            'order_allowed': 1,
            'order_prohibited': 0,
            'paid_supply_enabled': 0,
        },
        'express': {
            'order_allowed': 1,
            'order_prohibited': 0,
            'paid_supply_enabled': 0,
        },
    }

    expected_alternatives = load_json('expected_alternatives.json')
    assert (
        response.json()['alternatives']['options'][0]
        == expected_alternatives['options'][0]
    )


# TODO: remove when lightweight handler will be enabled
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:delivery_order_flow',
    ],
)
@pytest.mark.config(DISABLE_ORDER_FLOW_DELIVERY_PLUGIN_IN_LIGHTWEIGHT=True)
@pytest.mark.experiments3(filename='delivery_experiments.json')
async def test_lightweight_routestats_with_delivery(
        taxi_routestats, mockserver, load_json,
):
    delivery_classes = ['cargo', 'courier', 'express']

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    @mockserver.json_handler('/cargo-c2c/v1/delivery/estimate')
    def _cargo_c2c(request):
        return {}

    req = load_json('request.json')
    req['requirements'] = {'coupon': 'some_coupon_code'}
    req['supported'] = [
        {
            'type': 'order_flow_delivery',
            'payload': {'classes': delivery_classes},
        },
    ]
    req['is_lightweight'] = True
    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    assert _cargo_c2c.times_called == 0


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:delivery_order_flow',
    ],
)
@pytest.mark.experiments3(filename='delivery_experiments.json')
async def test_routestats_with_delivery_unsupported(
        taxi_routestats, mockserver, load_json, taxi_routestats_monitor,
):
    await taxi_routestats.tests_control(reset_metrics=True)

    delivery_classes = ['cargo', 'courier', 'express']

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    @mockserver.json_handler('/cargo-c2c/v1/delivery/estimate')
    def _cargo_c2c(request):
        return {
            'estimations': [
                {
                    'type': 'succeed',
                    'offer_id': 'offer_id_1',
                    'taxi_tariff': 'econom',
                    'price': '403.0000',
                    'currency': 'RUB',
                },
            ],
        }

    req = load_json('request.json')
    req['supported'] = [
        {
            'type': 'order_flow_delivery',
            'payload': {'classes': delivery_classes},
        },
    ]
    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    econom_level = []
    for service_level in response.json()['service_levels']:
        if service_level['class'] == 'econom':
            econom_level = service_level

    assert econom_level['description_parts']['value'] == '194 $SIGN$$CURRENCY$'

    stats = await taxi_routestats_monitor.get_metric(
        'delivery_order_flow_routestats_metrics',
    )
    assert stats == {
        'cargo': {
            'order_allowed': 0,
            'order_prohibited': 1,
            'paid_supply_enabled': 0,
        },
        'courier': {
            'order_allowed': 0,
            'order_prohibited': 1,
            'paid_supply_enabled': 0,
        },
        'express': {
            'order_allowed': 0,
            'order_prohibited': 1,
            'paid_supply_enabled': 0,
        },
    }


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:delivery_order_flow',
    ],
)
@pytest.mark.config(
    ORDER_FLOW_DELIVERY_ALLOW_WITHOUT_POINT_B=True,
    ORDER_FLOW_DELIVERY_ALLOW_TARIFF_UNAVALABLE_WITHOUT_POINT_B=False,
)
@pytest.mark.experiments3(filename='delivery_experiments.json')
async def test_routestats_with_delivery_without_point_b(
        taxi_routestats, mockserver, load_json, taxi_routestats_monitor,
):
    await taxi_routestats.tests_control(reset_metrics=True)

    delivery_classes = ['cargo', 'courier', 'express']

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    req = load_json('request.json')
    req['supported'] = [
        {
            'type': 'order_flow_delivery',
            'payload': {'classes': delivery_classes},
        },
    ]
    req['route'] = [[37.587569, 55.733393]]
    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    delivery_service_levels = []
    for service_level in response.json()['service_levels']:
        if service_level['class'] in delivery_classes:
            delivery_service_levels.append(service_level)

    assert len(delivery_service_levels) == 3
    for delivery_service_level in delivery_service_levels:
        if delivery_service_level['class'] == 'courier':
            assert 'estimated_waiting' not in delivery_service_level.keys()
        else:
            assert 'estimated_waiting' in delivery_service_level.keys()


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:delivery_order_flow',
    ],
)
@pytest.mark.experiments3(filename='delivery_experiments.json')
@pytest.mark.config(
    CARGO_C2C_ROUTESTATS_TARIFF_UNAVAILABLE_SETTINGS={
        '__default__': {
            'show_price': True,
            'subtitle': {
                'key': (
                    'c2c.client_message.routestats.tariff_unavailable.subtitle'
                ),
            },
        },
    },
)
async def test_routestats_with_delivery_tariff_unavailable_1(
        taxi_routestats, mockserver, load_json, taxi_routestats_monitor,
):
    await taxi_routestats.tests_control(reset_metrics=True)

    delivery_classes = ['cargo', 'courier', 'express']

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        internal_data = load_json('internal_data.json')
        internal_data['service_levels_data'].append(
            {
                'class': 'express',
                'final_price': '1405',
                'is_paid_supply': True,
            },
        )
        return {
            'internal_data': internal_data,
            **load_json('protocol_response.json'),
        }

    @mockserver.json_handler('/cargo-c2c/v1/delivery/estimate')
    def _cargo_c2c(request):
        return {
            'estimations': [
                {
                    'type': 'succeed',
                    'offer_id': 'offer_id_1',
                    'taxi_tariff': 'express',
                    'price': '403.0000',
                    'currency': 'RUB',
                    'decision': 'order_prohibited',
                },
                {
                    'type': 'failed',
                    'taxi_tariff': 'cargo',
                    'error': {'message': '100', 'code': '100'},
                },
                {
                    'type': 'failed',
                    'taxi_tariff': 'courier',
                    'error': {
                        'message': '100',
                        'code': 'pickup_point_not_selected',
                    },
                },
            ],
        }

    req = load_json('request.json')
    req['supported'] = [
        {
            'type': 'order_flow_delivery',
            'payload': {'classes': delivery_classes},
        },
    ]
    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    delivery_service_levels = []
    for service_level in response.json()['service_levels']:
        if service_level['class'] in delivery_classes:
            delivery_service_levels.append(service_level)

    assert len(delivery_service_levels) == 3
    assert delivery_service_levels[0]['tariff_unavailable'] == {
        'code': 'delivery_offer_error',
        'message': 'Что-то пошло не так',
        'subtitle': 'Какой-то subtitle',
        'show_price': True,
    }
    assert delivery_service_levels[1]['tariff_unavailable'] == {
        'code': 'no_available_couriers',
        'message': 'Нет свободных курьеров!!!',
        'subtitle': 'Какой-то subtitle',
        'show_price': True,
    }
    assert delivery_service_levels[2]['tariff_unavailable'] == {
        'code': 'pickup_point_not_selected',
        'message': 'Выбери ПВЗ отправления',
        'subtitle': 'Какой-то subtitle',
        'show_price': True,
        'order_button_action': {
            'focus_field': 'destination',
            'type': 'open_summary_address',
        },
    }

    stats = await taxi_routestats_monitor.get_metric(
        'delivery_order_flow_routestats_metrics',
    )
    assert stats == {
        'cargo': {
            'order_allowed': 0,
            'order_prohibited': 1,
            'paid_supply_enabled': 0,
        },
        'courier': {
            'order_allowed': 0,
            'order_prohibited': 1,
            'paid_supply_enabled': 0,
        },
        'express': {
            'order_allowed': 0,
            'order_prohibited': 1,
            'paid_supply_enabled': 0,
        },
    }


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:delivery_order_flow',
    ],
)
@pytest.mark.experiments3(filename='delivery_experiments.json')
async def test_routestats_with_delivery_tariff_unavailable_2(
        taxi_routestats, mockserver, load_json, taxi_routestats_monitor,
):
    await taxi_routestats.tests_control(reset_metrics=True)

    delivery_classes = ['cargo', 'courier', 'express']
    tariff_unavalable = {'code': 'some_code', 'message': 'some_message'}

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        protocol_response = load_json('protocol_response.json')
        for service_level in protocol_response['service_levels']:
            service_level['tariff_unavailable'] = tariff_unavalable
            service_level.pop('description_parts', None)
        return {
            'internal_data': load_json('internal_data.json'),
            **protocol_response,
        }

    @mockserver.json_handler('/cargo-c2c/v1/delivery/estimate')
    def _cargo_c2c(request):
        return {
            'estimations': [
                {
                    'type': 'succeed',
                    'offer_id': 'offer_id_1',
                    'taxi_tariff': 'cargo',
                    'price': '403.0000',
                    'currency': 'RUB',
                    'paid_supply_price': '150',
                    'paid_cancel_in_driving': {
                        'free_cancel_timeout': 300,
                        'cancel_price': '150',
                    },
                    'decision': 'paid_supply_enabled',
                },
                {
                    'type': 'succeed',
                    'offer_id': 'offer_id_2',
                    'taxi_tariff': 'express',
                    'price': '203.0000',
                    'currency': 'RUB',
                    'decision': 'order_allowed',
                },
                {
                    'type': 'succeed',
                    'offer_id': 'offer_id_3',
                    'taxi_tariff': 'courier',
                    'price': '199.0000',
                    'currency': 'RUB',
                    'original_price': '299.0000',
                    'decision': 'no_cars_order_enabled',
                },
            ],
        }

    req = load_json('request.json')
    req['supported'] = [
        {
            'type': 'order_flow_delivery',
            'payload': {'classes': delivery_classes},
        },
    ]
    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    for service_level in response.json()['service_levels']:
        if service_level['class'] in delivery_classes:
            assert service_level['tariff_unavailable'] == tariff_unavalable

    stats = await taxi_routestats_monitor.get_metric(
        'delivery_order_flow_routestats_metrics',
    )
    assert stats == {
        'cargo': {
            'order_allowed': 0,
            'order_prohibited': 1,
            'paid_supply_enabled': 0,
        },
        'courier': {
            'order_allowed': 0,
            'order_prohibited': 1,
            'paid_supply_enabled': 0,
        },
        'express': {
            'order_allowed': 0,
            'order_prohibited': 1,
            'paid_supply_enabled': 0,
        },
    }


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:proxy',
        'top_level:brandings',
        'top_level:brandings',
        'brandings:proxy',
        'brandings:proxy',
        'top_level:delivery_order_flow',
        'top_level:delivery_order_flow',
    ],
)
@pytest.mark.experiments3(filename='delivery_experiments.json')
async def test_routestats_with_delivery_tariff_unavailable_3(
        taxi_routestats, mockserver, load_json, taxi_routestats_monitor,
):
    await taxi_routestats.tests_control(reset_metrics=True)

    delivery_classes = ['cargo', 'courier', 'express']
    tariff_unavalable = {
        'code': 'payment_method_unavailable',
        'message': 'Выберите другой способ оплаты',
    }

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    @mockserver.json_handler('/cargo-c2c/v1/delivery/estimate')
    def _cargo_c2c(request):
        return mockserver.make_response(
            json={'code': 'payment_method_unavailable'}, status=400,
        )

    req = load_json('request.json')
    req['supported'] = [
        {
            'type': 'order_flow_delivery',
            'payload': {'classes': delivery_classes},
        },
    ]
    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    for service_level in response.json()['service_levels']:
        if service_level['class'] in delivery_classes:
            assert service_level['tariff_unavailable'] == tariff_unavalable


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:delivery_order_flow',
    ],
)
@pytest.mark.experiments3(filename='delivery_experiments.json')
async def test_routestats_order_popup_properties(
        taxi_routestats, mockserver, load_json,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200

    popup = None
    for service_level in response.json()['service_levels']:
        if service_level['class'] == 'express':
            popup = service_level['paid_options']['order_popup_properties']

    assert popup == {
        'button_text': 'Вызвать такси',
        'description': 'Цена может вырасти',
        'reason': (
            'Не удалось построить маршрут, '
            'поэтому точная цена рассчитается по счётчику в конце поездки. '
            'Чтобы увидеть стоимость заранее, измените точку '
            'посадки или пункт назначения.'
        ),
        'type': 'default',
    }
