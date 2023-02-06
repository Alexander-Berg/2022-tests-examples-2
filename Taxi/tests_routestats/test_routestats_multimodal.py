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


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:multimodal',
        'top_level:brandings',
        'brandings:proxy',
        'brandings:plus',
    ],
)
async def test_basic(
        taxi_routestats, mockserver, load_json, load_binary, testpoint,
):
    service_request = load_json('request.json')
    protocol_response = {
        'internal_data': load_json('internal_data.json'),
        **load_json('protocol_response.json'),
    }

    @mockserver.json_handler(
        '/masstransit/internal/masstransit/v1/multimodal_route_stats',
    )
    def _check_masstransit_multimodal_request(request):
        assert request.json == {
            'offer_data': {
                'currency_code': protocol_response['internal_data'][
                    'currency_rules'
                ]['code'],
                'duration_seconds': int(
                    protocol_response['internal_data']['route_info']['time'],
                ),
                'offer_id': protocol_response['offer'],
                'price': protocol_response['internal_data'][
                    'service_levels_data'
                ][0]['original_price'],
            },
            'route': service_request['route'],
            'zone': 'moscow',
        }
        return {}

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return protocol_response

    @testpoint('send_order_data_for_multimodal_calc')
    def data_posted(data):
        pass

    response = await taxi_routestats.post(
        'v1/routestats', service_request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    await data_posted.wait_call()
    assert _check_masstransit_multimodal_request.times_called == 1
