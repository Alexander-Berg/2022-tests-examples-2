# pylint: disable=import-error,too-many-lines,import-only-modules
import copy

import pytest
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary


URL = '/internal/shuttle-control/v1/promotion/fetch_offers'

PA_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
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

BASIC_REQUEST = {
    'summary_state': {
        'promo_context': {
            'eta_seconds': 185,
            'offer_id': '7c76c53b-98bb-481c-ac21-0555c5e51d10',
        },
    },
    'application_state': {
        'fields': [
            {'type': 'b', 'position': [35.0, 65.0]},
            {'type': 'a', 'position': [30.01, 50.01]},
        ],
    },
}


TEXT = 'До остановки %(walk_time)s пешком'

TITLE_PRICE = 'Можно на Шаттле: %(price)s'
TITLE = '%(eta)s и рядом будет Шаттл'

ROUTER = {'30.000000,60.000000': 120}


def _proto_masstransit_summary(time, distance):
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


def validate(resp_data, expected_data):
    assert 'offers' in resp_data
    assert 'promoblocks' in resp_data['offers']
    assert 'items' in resp_data['offers']['promoblocks']
    assert resp_data['offers']['promoblocks']['items']
    item = resp_data['offers']['promoblocks']['items'][0]
    assert 'id' in item
    assert item['id']
    item.pop('id')
    assert resp_data == expected_data


@pytest.mark.translations(
    client_messages={
        'shuttle_promo.text': {'ru': TEXT},
        'shuttle_promo.title': {'ru': TITLE},
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
        'shortcuts.route_eta.round.hours': {'ru': '%(value).0f ч'},
        'shortcuts.route_eta.round.tens_minutes': {'ru': '%(value).0f мин'},
    },
)
@pytest.mark.experiments3(filename='shuttle_promo_exp.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize('reason', ['no_context', 'no_field_a', 'no_fields'])
async def test_promo_disabled_by_request(taxi_shuttle_control, reason):
    request = copy.deepcopy(BASIC_REQUEST)
    if reason == 'no_context':
        request['summary_state'].pop('promo_context')
    elif reason == 'no_field_a':
        fields = request['application_state']['fields']
        request['application_state']['fields'] = [
            field for field in fields if field['type'] != 'a'
        ]
    elif reason == 'no_fields':
        request['application_state'].pop('fields')

    response = await taxi_shuttle_control.post(
        URL, json=request, headers=PA_HEADERS,
    )

    assert response.status_code == 200
    assert not response.json()['offers']['promoblocks']['items']


@pytest.mark.translations(
    client_messages={
        'shuttle_promo.text': {'ru': TEXT},
        'shuttle_promo.title': {'ru': TITLE},
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
        'shortcuts.route_eta.round.hours': {'ru': '%(value).0f ч'},
        'shortcuts.route_eta.round.tens_minutes': {'ru': '%(value).0f мин'},
    },
)
@pytest.mark.experiments3(filename='shuttle_promo_exp.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_promo_simple(taxi_shuttle_control, mockserver, load_json):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(300, 400),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_shuttle_control.post(
        URL, BASIC_REQUEST, headers=PA_HEADERS,
    )

    assert response.status_code == 200
    validate(response.json(), load_json('expected_response_promo.json'))


@pytest.mark.translations(
    client_messages={
        'shuttle_promo.text': {'ru': TEXT},
        'shuttle_promo.title': {'ru': TITLE_PRICE},
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
        'shortcuts.route_eta.round.hours': {'ru': '%(value).0f ч'},
        'shortcuts.route_eta.round.tens_minutes': {'ru': '%(value).0f мин'},
    },
)
@pytest.mark.experiments3(filename='shuttle_promo_exp.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_promo_simple_with_price(
        taxi_shuttle_control, mockserver, load_json,
):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(300, 400),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_shuttle_control.post(
        URL, BASIC_REQUEST, headers=PA_HEADERS,
    )

    assert response.status_code == 200
    validate(
        response.json(), load_json('expected_response_promo_with_price.json'),
    )
