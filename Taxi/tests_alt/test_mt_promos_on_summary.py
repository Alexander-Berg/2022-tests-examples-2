import json

import pytest

BASIC_REQUEST_PROMOS = {
    'summary_state': {
        'offer_id': 'some_offer_id',
        'tariff_classes': ['econom', 'vip'],
    },
    'state': {
        'location': [37.615, 55.758],
        'fields': [
            {'type': 'a', 'position': [37.642563, 55.734760], 'log': 'log1'},
            {
                'type': 'b',
                'position': [37.534248, 55.749920],
                'log': 'ymapsbm1://org?oid=126805074611',
            },
        ],
        'known_orders': [],
    },
    'client_info': {
        'supported_features': [
            {
                'type': 'promoblock',
                'widgets': ['deeplink_arrow_button', 'drive_arrow_button'],
            },
        ],
    },
}

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
    'X-AppMetrica-UUID': 'UUID',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-Request-Application': 'app_name=iphone',
    'X-Request-Language': 'ru',
}

TEXT = 'Станций %(num_stops)s до %(last_stop_name)s - %(time_on_metro)s'

TITLE = '%(route_time)s. %(time_on_taxi)s на такси до %(first_stop_name)s'


@pytest.mark.translations(
    client_messages={
        'mt_promo.text': {'ru': TEXT},
        'mt_promo.title': {'ru': TITLE},
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
        'shortcuts.route_eta.round.hours': {'ru': '%(value).0f ч'},
        'shortcuts.route_eta.round.tens_minutes': {'ru': '%(value).0f мин'},
    },
)
@pytest.mark.experiments3(filename='exp3_mtpin_promo_summary.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('no_points', [False, True])
async def test_mt_promo_simple(taxi_alt, load_json, mockserver, no_points):
    @mockserver.json_handler('/masstransit/masstransit/v1/routepoints')
    def _mock_pickup_points(request):
        data = json.loads(request.get_data())
        assert not data.get('metro_first', True)
        assert 'max_distance_to_point_b' in data
        assert data['max_distance_to_point_b'] == 50
        if no_points:
            return {'options': []}
        response = load_json('masstransit_routepoints.json')
        return response

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_bzf(request):
        request_data = json.loads(request.get_data())
        assert request_data == load_json('filter_points_request.json')
        return load_json('pp_bzf_response.json')

    response = await taxi_alt.post(
        'alt/v1/mt-promos-on-summary',
        BASIC_REQUEST_PROMOS,
        headers=PA_HEADERS,
    )
    assert response.status_code == 200
    if no_points:
        assert response.json() == {'offers': {'promoblocks': {'items': []}}}
    else:
        resp_data = response.json()
        assert 'offers' in resp_data
        assert 'promoblocks' in resp_data['offers']
        assert 'items' in resp_data['offers']['promoblocks']
        assert resp_data['offers']['promoblocks']['items']
        item = resp_data['offers']['promoblocks']['items'][0]
        assert 'id' in item
        assert item['id']
        item.pop('id')
        assert resp_data == load_json('expected_response_mt_promos.json')
