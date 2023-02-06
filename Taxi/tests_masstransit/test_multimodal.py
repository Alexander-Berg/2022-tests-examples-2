import copy

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

DEFAULT_REQUEST = {
    'route': [[37.2, 55.4], [38.1, 56.0]],
    'zone': 'moscow',
    'offer_data': {
        'price': '123.45',
        'currency_code': 'BUB',
        'duration_seconds': 12345,
        'offer_id': 'original_offer_id',
    },
}

URI = 'internal/masstransit/v1/multimodal_route_stats'


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['linear-fallback']},
        {
            'routers': ['yamaps', 'linear-fallback'],
            'type': 'masstransit',
            'service': 'masstransit',
        },
    ],
    ROUTER_MASSTRANSIT_MAPS_ENABLED=True,
)
@pytest.mark.mtinfo(v2_stop='mtinfo_stop.json')
@pytest.mark.stops_file(filename='stops.json')
@pytest.mark.config(
    MASSTRANSIT_STOPS_IMAGE_TAGS={
        'tramway': 'tramway_tag',
        'stop': 'stop_tag',
        'metro': 'metro_tag',
    },
)
@pytest.mark.experiments3(filename='exp_multimodal_settings.json')
async def test_basic(taxi_masstransit, mockserver, load_json, load_binary):
    request = copy.deepcopy(DEFAULT_REQUEST)

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(request):
        return load_json('pricing_response.json')

    @mockserver.handler('/maps-pedestrian-router/masstransit/v2/route')
    def _mock_route(request):
        return mockserver.make_response(
            response=load_binary('masstransit-route.protobuf'),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_masstransit.post(URI, request, headers=PA_HEADERS)

    assert response.status_code == 200
