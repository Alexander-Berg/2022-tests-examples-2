# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest


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

MAAS_ROUTE_RESTRICTIONS = {
    'point_a_max_distance_to_metro': 200,
    'point_b_max_distance_to_metro': 200,
    'max_route_length': 20000,
    'parametrized_router_restrictions': [
        {
            'id': 'bee_line_route_length',
            'router_params': {'type': 'bee_line'},
            'threshold': {'distance_meters': 20000},
        },
    ],
}


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.experiments3(filename='exp_maas_tariff_unavailable.json')
@pytest.mark.experiments3(
    filename='exp_routestats_tariff_unavailable_brandings.json',
)
@pytest.mark.config(ROUTESTATS_HIDE_SURGE_FOR_ZERO_PRICE=True)
@pytest.mark.translations(
    client_messages={
        'maas.check_trip_requirements.tariff_unavailable_message': {
            'ru': 'Поездка по абонементу невозможна',
        },
        'maas.check_trip_requirements.route_without_point_b_error_key': {
            'ru': 'В поездке должна быть указана точка назначения',
        },
        'maas.check_trip_requirements.route_too_long': {
            'ru': 'Слишком длинный маршрут',
        },
    },
)
@pytest.mark.config(
    MAAS_PAYMENT_METHODS_CHECKS={
        'allowed_payment_methods': ['card'],
        'forbidden_payment_methods_to_check_id': {
            '__default__': 'unsupported_payment_method',
            'cash': 'cash_payment_method',
        },
    },
    MAAS_ROUTE_RESTRICTIONS=MAAS_ROUTE_RESTRICTIONS,
)
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:maas',
        'top_level:hide_ride_price',
        'top_level:brandings:tariff_unavailable_branding',
        'top_level:surge',
    ],
)
@pytest.mark.parametrize(
    'request_override, maas_check_response, '
    'expected_response_file, metric_labels',
    [
        (
            {},
            {'valid': True},
            'expected_response_ok.json',
            {
                'sensor': 'maas_routestats_metrics',
                'maas_checks_status': 'success',
                'failed_check_id': 'none',
            },
        ),
        (
            {},
            {'valid': False, 'failed_check_id': 'route_without_point_b'},
            'expected_response_tariff_unavailable.json',
            {
                'sensor': 'maas_routestats_metrics',
                'maas_checks_status': 'fail',
                'failed_check_id': 'route_without_point_b',
            },
        ),
        (
            {'route': [[37.0, 55.0], [37.687569, 55.633393]]},
            {'valid': True},
            'expected_response_route_too_long.json',
            {
                'sensor': 'maas_routestats_metrics',
                'maas_checks_status': 'fail',
                'failed_check_id': 'route_too_long',
            },
        ),
    ],
)
async def test_routestats_maas_flow(
        request_override,
        maas_check_response,
        expected_response_file,
        metric_labels,
        taxi_routestats,
        taxi_routestats_monitor,
        mockserver,
        load_json,
):
    rs_request = load_json('request_with_coupon.json')
    rs_request.update(request_override)

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        assert 'suggest_alternatives' in request.json
        assert request.json['suggest_alternatives'] is False
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response_with_coupon.json'),
        }

    @mockserver.json_handler('/maas/internal/maas/v1/check-trip-requirements')
    def _mock_maas(request):
        assert request.json == {
            'waypoints': rs_request['route'],
            'coupon': 'maascoupon',
        }

        return mockserver.make_response(json=maas_check_response)

    async with metrics_helpers.MetricsCollector(
            taxi_routestats_monitor, sensor='maas_routestats_metrics',
    ) as collector:
        response = await taxi_routestats.post(
            'v1/routestats', rs_request, headers=PA_HEADERS,
        )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response_file)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == metric_labels
