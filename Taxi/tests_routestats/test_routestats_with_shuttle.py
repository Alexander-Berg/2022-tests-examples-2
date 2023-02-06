import pytest


PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
}


def _sorted_tariff_requirements(tariff_requirements: list) -> list:
    return sorted(
        tariff_requirements,
        key=lambda tariff_requirement: tariff_requirement['class'],
    )


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.unsupported_payment_method': {
            'ru': 'Payment method is not supported',
        },
        'summary.shuttle.name': {'ru': 'Шаттл'},
        'summary.shuttle.button.title': {'ru': 'Забронировать место'},
        'summary.shuttle.button.subtitle': {'ru': 'а можно и два'},
        'summary.shuttle.estimated_waiting.message': {
            'ru': '%(shuttle_eta)s минут',
        },
        'shuttle_tariff_card_route_title': {
            'ru': 'У каждого шаттла свой маршрут',
        },
        'shuttle_tariff_card_route_text': {
            'ru': 'С 07:00 до 22:00, интервал около 15 минут',
        },
    },
    tariff={'currency_with_sign.rub': {'ru': '$VALUE$TEST$SIGN$$CURRENCY$'}},
)
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:shuttle_order_flow',
        'top_level:hide_ride_price',
    ],
)
@pytest.mark.experiments3(filename='shuttle_in_routestats.json')
@pytest.mark.parametrize(
    'request_file, shuttle_control_response, expected_routetats_response',
    [
        (
            'request_with_shuttle.json',
            'response_shuttle_control.json',
            'expected_response_with_shuttle.json',
        ),
        (
            'hide_price/request_with_shuttle.json',
            'response_shuttle_control.json',
            'hide_price/expected_response_with_shuttle.json',
        ),
    ],
)
async def test_routestats_with_shuttle(
        request_file,
        shuttle_control_response,
        expected_routetats_response,
        taxi_routestats,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response_with_shuttle.json'),
        }

    req = load_json(request_file)

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/match_shuttles',
    )
    def _mock_shuttle_control(request):
        assert all(
            request.headers.get(key, None) == val
            for key, val in PA_HEADERS.items()
        )

        assert request.json == {
            'route': [[37.587569, 55.733393], [37.687569, 55.633393]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 300,
                    'max_walk_distance': 1000,
                },
                'dropoff_limits': {
                    'max_walk_time': 300,
                    'max_walk_distance': 1000,
                },
                'max_wait_time': 300,
            },
            'payment': req['payment'],
        }

        return mockserver.make_response(
            json=load_json(shuttle_control_response),
        )

    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_routetats_response)


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.unsupported_payment_method': {
            'ru': 'Payment method is not supported',
        },
        'summary.shuttle.name': {'ru': 'Шаттл'},
        'summary.shuttle.button.title': {'ru': 'Забронировать место'},
        'summary.shuttle.button.subtitle': {'ru': 'а можно и два'},
        'summary.shuttle.estimated_waiting.message': {
            'ru': '%(shuttle_eta)s минут',
        },
        'shuttle_tariff_card_route_title': {
            'ru': 'У каждого шаттла свой маршрут',
        },
        'shuttle_tariff_card_route_text': {
            'ru': 'С 07:00 до 22:00, интервал около 15 минут',
        },
    },
    tariff={'currency_with_sign.rub': {'ru': '$VALUE$TEST$SIGN$$CURRENCY$'}},
)
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:shuttle_order_flow',
        'top_level:hide_ride_price',
    ],
)
@pytest.mark.experiments3(filename='shuttle_in_routestats_tp.json')
@pytest.mark.parametrize(
    'request_file, shuttle_control_response, expected_routetats_response',
    [
        (
            'request_with_shuttle.json',
            'response_shuttle_control_tp.json',
            'expected_response_with_shuttle.json',
        ),
        (
            'hide_price/request_with_shuttle.json',
            'response_shuttle_control_tp.json',
            'hide_price/expected_response_with_shuttle.json',
        ),
    ],
)
async def test_routestats_with_shuttle_tp(
        request_file,
        shuttle_control_response,
        expected_routetats_response,
        taxi_routestats,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response_with_shuttle.json'),
        }

    req = load_json(request_file)

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/trip-planner/search',
    )
    def _mock_shuttle_control_tp(request):
        assert all(
            request.headers.get(key, None) == val
            for key, val in PA_HEADERS.items()
        )

        assert request.json == {
            'route': [[37.587569, 55.733393], [37.687569, 55.633393]],
            'passengers_count': 1,
            'payment': req['payment'],
        }

        return mockserver.make_response(
            json=load_json(shuttle_control_response),
        )

    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_routetats_response)


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:shuttle_order_flow',
        'top_level:hide_ride_price',
    ],
)
@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.unsupported_payment_method': {
            'ru': 'Payment method is not supported',
        },
        'summary.shuttle.name': {'ru': 'Шаттл'},
        'summary.shuttle.button.title': {'ru': 'Забронировать место'},
        'summary.shuttle.button.subtitle': {'ru': 'а можно и два'},
        'summary.shuttle.estimated_waiting.message': {
            'ru': '%(shuttle_eta)s мин',
        },
    },
)
@pytest.mark.experiments3(filename='shuttle_in_routestats.json')
@pytest.mark.parametrize(
    'eta,response_eta,seconds', [(30, '1 мин', 60), (125, '2 мин', 120)],
)
async def test_shuttle_eta_response(
        eta, response_eta, seconds, taxi_routestats, mockserver, load_json,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response_with_shuttle.json'),
        }

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/match_shuttles',
    )
    def _mock_shuttle_control(request):
        response = load_json('response_shuttle_control.json')
        for shuttle in response['matched_shuttles']:
            shuttle['shuttle']['eta'] = eta
        return mockserver.make_response(json=response)

    req = load_json('request_with_shuttle.json')
    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    service_level = next(
        (
            level
            for level in response.json()['service_levels']
            if level['class'] == 'shuttle'
        ),
    )
    shuttle_extra = service_level['shuttle_extra']['offers'][0]
    estimated_waiting = shuttle_extra['service_level_override'][
        'estimated_waiting'
    ]
    assert estimated_waiting['message'] == response_eta
    assert estimated_waiting['seconds'] == seconds


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.unsupported_payment_method': {
            'ru': 'Payment method is not supported',
        },
        'summary.shuttle.name': {'ru': 'Шаттл'},
        'summary.shuttle.button.title': {'ru': 'Забронировать место'},
        'summary.shuttle.button.subtitle': {'ru': 'а можно и два'},
        'summary.shuttle.estimated_waiting.message': {
            'ru': '%(shuttle_eta)s минут',
        },
    },
)
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:shuttle_order_flow',
        'top_level:hide_ride_price',
    ],
)
@pytest.mark.parametrize(
    'expected_response_shuttle_ids',
    [
        pytest.param(
            ['gkZxnYQ73QGqrKyz', 'Pmp80rQ23L4wZYxd', '80vm7DQm7Ml24ZdO'],
            marks=pytest.mark.experiments3(
                filename='shuttle_in_routestats.json',
            ),
        ),
        pytest.param(
            ['gkZxnYQ73QGqrKyz', 'Pmp80rQ23L4wZYxd'],
            marks=pytest.mark.experiments3(
                filename='shuttle_in_routestats_filtered_routes.json',
            ),
        ),
    ],
)
async def test_routestats_hidding_shuttles_by_exp(
        expected_response_shuttle_ids,
        taxi_routestats,
        mockserver,
        load_json,
        experiments3,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response_with_shuttle.json'),
        }

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/match_shuttles',
    )
    def _mock_shuttle_control(request):
        return mockserver.make_response(
            json=load_json('response_shuttle_multiplie_shuttles.json'),
        )

    response = await taxi_routestats.post(
        'v1/routestats',
        load_json('request_with_shuttle.json'),
        headers=PA_HEADERS,
    )
    assert response.status_code == 200
    shuttle_service_levels = next(
        service_level
        for service_level in response.json()['service_levels']
        if service_level['class'] == 'shuttle'
    )
    shuttle_ids = [
        shuttle_offer['shuttle_id']
        for shuttle_offer in shuttle_service_levels['shuttle_extra']['offers']
    ]
    assert shuttle_ids == expected_response_shuttle_ids
