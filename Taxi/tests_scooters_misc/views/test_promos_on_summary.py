import copy

import pytest

URL = 'scooters-misc/v1/promos-on-summary'
USER_ID = 'TAXI_USER_ID'

PA_HEADERS = {
    'X-Ya-User-Ticket': 'user-ticket',
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-UserId': USER_ID,
    'X-Request-Language': 'ru',
    'X-YaTaxi-Pass-Flags': 'ya-plus',
}

POSITION_NEAR_PARKING = [37.578652, 55.734492]
POSITION_FAR_FROM_PARKING = [37.606244, 55.743349]

BASIC_REQUEST = {
    'summary_state': {
        'offer_id': 'some_offer_id',
        'tariff_classes': [
            'econom',
            'business',
            'comfortplus',
            'vip',
            'ultima',
        ],
    },
    'state': {
        'location': [37.615, 55.758],
        'fields': [
            {'type': 'a', 'position': [37.612658, 55.759499], 'log': 'log1'},
            {
                'type': 'b',
                'position': [37.578652, 55.734492],
                'log': 'ymapsbm1://org?oid=126805074611',
            },
        ],
        'known_orders': [],
    },
    'client_info': {
        'supported_features': [
            {'type': 'promoblock', 'widgets': ['deeplink_arrow_button']},
        ],
    },
}


def compare_responses(service_resp, resp):
    assert len(service_resp['offers']['promoblocks']['items']) == len(
        resp['offers']['promoblocks']['items'],
    )
    for item_service, item_resp in zip(
            service_resp['offers']['promoblocks']['items'],
            resp['offers']['promoblocks']['items'],
    ):
        del item_service['id']
        del item_resp['id']
    assert service_resp == resp


@pytest.mark.translations(
    client_messages={
        'scooters_promo.title': {'ru': 'На самокате ~%(min_price)s₽'},
        'scooters_promo.text': {'ru': '%(riding_duration)s мин в пути'},
        'scooters_promo.widget_text': {'ru': 'Виджет'},
    },
)
@pytest.mark.parametrize(
    'scooters_misc_response, position_b, scooter_price_rub,'
    'scooter_walking_duration_min, scooter_riding_duration_min,'
    'multiple_offers, no_econom',
    [
        pytest.param(
            'scooters_misc_response_redirect_promoblock.json',
            POSITION_NEAR_PARKING,
            75,
            4,
            8,
            True,
            False,
            id='test_promoblock',
        ),
        pytest.param(
            'scooters_misc_response_no_promos.json',
            POSITION_FAR_FROM_PARKING,
            75,
            4,
            8,
            True,
            False,
            id='test_parking_too_far',
        ),
        pytest.param(
            'scooters_misc_response_no_promos.json',
            POSITION_NEAR_PARKING,
            75,
            11,
            8,
            False,
            False,
            id='test_walking_duration_too_long',
        ),
        pytest.param(
            'scooters_misc_response_no_promos.json',
            POSITION_NEAR_PARKING,
            75,
            4,
            31,
            False,
            False,
            id='test_riding_duration_too_long',
        ),
        pytest.param(
            'scooters_misc_response_no_promos.json',
            POSITION_NEAR_PARKING,
            75,
            4,
            1,
            False,
            False,
            id='test_riding_duration_too_short',
        ),
        pytest.param(
            'scooters_misc_response_no_promos.json',
            POSITION_NEAR_PARKING,
            501,
            4,
            8,
            False,
            False,
            id='test_scooter_too_expensive',
        ),
        pytest.param(
            'scooters_misc_response_no_promos.json',
            POSITION_NEAR_PARKING,
            75,
            4,
            8,
            True,
            True,
            id='test_no_econom_tariff',
        ),
    ],
)
@pytest.mark.now('2021-01-24T10:00:00+0300')
@pytest.mark.experiments3(filename='exp3_scooters_promo_block.json')
@pytest.mark.experiments3(filename='exp3_scooters_promo_block_style.json')
async def test_promos_on_summary(
        taxi_scooters_misc,
        mockserver,
        load_json,
        scooters_misc_response,
        position_b,
        scooter_price_rub,
        scooter_walking_duration_min,
        scooter_riding_duration_min,
        multiple_offers,
        no_econom,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/offers/fixpoint')
    def _mock_scooter_backend(request):
        assert not request.json
        assert request.args == {
            'src': '37.612658 55.759499',
            'dst': '37.588023534140355 55.733910887668294',
            'offer_count_limit': '10',
        }

        resp = load_json('response_scooter_backend.json')
        if not multiple_offers:
            resp['offers'] = resp['offers'][:1]

        resp['offers'][0]['price'] = scooter_price_rub * 100
        resp['offers'][0]['walking_duration'] = (
            scooter_walking_duration_min * 60
        )
        resp['offers'][0]['riding_duration'] = scooter_riding_duration_min * 60

        return mockserver.make_response(json=resp, headers={'X-Req-Id': '123'})

    request = copy.deepcopy(BASIC_REQUEST)

    request['state']['fields'][1]['position'] = position_b
    if no_econom:
        del request['summary_state']['tariff_classes'][0]

    response = await taxi_scooters_misc.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200

    resp = load_json(scooters_misc_response)
    compare_responses(response.json(), resp)
