import copy

import pytest

URL = '4.0/persuggest/v1/drive-promos-on-summary'
USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'FLAGS',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
    'X-AppMetrica-UUID': 'UUID',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-Request-Application': 'app_name=iphone',
    'X-Request-Language': 'ru',
}

BASIC_REQUEST = {
    'summary_state': {
        'offer_id': 'some_offer_id',
        'tariff_classes': [
            'drive',
            'econom',
            'comfortplus',
            'vip',
            'business',
            'ultima',
        ],
    },
    'state': {
        'location': [37.615, 55.758],
        'fields': [
            {'type': 'a', 'position': [37.1, 55.2], 'log': 'log1'},
            {
                'type': 'b',
                'position': [37.2, 55.3],
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

GEO_OBJECT = {
    'business': {
        'address': {
            'formatted_address': 'Россия, Москва',
            'country': 'Россия',
            'locality': 'Москва',
        },
        'name': 'Яндекс',
        'id': '123456',
    },
    'uri': 'ymapsbm1://org?oid=1211722324',
    'name': 'Яндекс',
    'description': 'Сходненская ул., 56, Москва, Россия',
    'geometry': [37.444372, 55.850481],
}


def _customize_response(
        resp, numbers, icon_image_tag, offer_count_limit, previous_offer_ids,
):
    for preferred_car_number, item in zip(
            numbers, resp['offers']['promoblocks']['items'],
    ):
        if 'drive_arrow_button' in item['widgets']:
            if preferred_car_number:
                item['widgets']['drive_arrow_button']['layers_context'][
                    'preferred_car_number'
                ] = preferred_car_number
            else:
                del item['widgets']['drive_arrow_button']['layers_context'][
                    'preferred_car_number'
                ]

            if previous_offer_ids:
                item['widgets']['drive_arrow_button']['layers_context'][
                    'previous_offer_ids'
                ] = previous_offer_ids
            else:
                del item['widgets']['drive_arrow_button']['layers_context'][
                    'previous_offer_ids'
                ]

            item['widgets']['drive_arrow_button']['layers_context'][
                'offer_count_limit'
            ] = offer_count_limit

        item['icon']['image_tag'] = icon_image_tag


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
        'drive_promo.title': {'ru': 'На Драйве от %(min_price)s'},
        'drive_promo.text': {'ru': '%(car_model)s идти %(walking_duration)s'},
        'drive_promo.widget_text': {'ru': 'Виджет'},
    },
)
@pytest.mark.parametrize(
    'uuid,yandex_drive_response,persuggest_response,'
    'numbers,flags,icon_image_tag,offer_count_limit,'
    'previous_offer_ids,redirect',
    [
        pytest.param(
            'UUID_simple',
            'response_yandex_drive.json',
            'default_persuggest_response.json',
            ['т576нх799'],
            'portal,ya-plus',
            'tag',
            0,
            ['3e29f7f7-8a7d26c2-4359f132-d6e0ee73'],
            False,
            id='simple_test',
        ),
        pytest.param(
            'UUID_redirect',
            'response_yandex_drive.json',
            'persuggest_response_redirect_promoblock.json',
            ['т578нх799', 'т576нх799'],
            'portal,ya-plus',
            'redirect_tag',
            0,
            None,
            True,
            id='test_redirect_promoblock',
        ),
        pytest.param(
            'UUID',
            'response_yandex_drive.json',
            'default_persuggest_response.json',
            ['т576нх799'],
            'portal,ya-plus',
            'tag',
            0,
            ['3e29f7f7-8a7d26c2-4359f132-d6e0ee73'],
            False,
            id='test_simple_ranging_and_tariffs_unavailability',
        ),
        pytest.param(
            'UUID_2',
            'response_yandex_drive_high_price.json',
            'persuggest_response_high_price.json',
            ['т577нх799', 'т577нх799', 'т578нх799'],
            'portal,ya-plus',
            'tag',
            0,
            [
                '3e29f7f7-8a7d26c2-4359f132-d6e0ee71',
                '3e29f7f7-8a7d26c2-4359f132-d6e0ee72',
            ],
            False,
            id='test_different_promoblocks_and_ranging_thresholds',
        ),
        pytest.param(
            'UUID_noreg',
            'response_yandex_drive.json',
            'default_persuggest_response.json',
            ['т576нх799'],
            'portal,ya-plus',
            'noreg_tag',
            5,
            None,
            False,
            id='test_noreg',
        ),
        pytest.param(
            'UUID_phonish',
            'response_yandex_drive.json',
            'default_persuggest_response.json',
            ['т576нх799'],
            'phonish,ya-plus',
            'phonish_tag',
            5,
            None,
            False,
            id='test_phonish',
        ),
    ],
)
@pytest.mark.parametrize(
    'drive_allowed',
    [
        pytest.param(
            True,
            id='drive_allowed',
            marks=[
                pytest.mark.config(
                    APPLICATION_BRAND_CATEGORIES_SETS={
                        '__default__': ['econom', 'uberx', 'drive'],
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            id='drive_forbidden',
            marks=[
                pytest.mark.config(
                    APPLICATION_BRAND_CATEGORIES_SETS={
                        '__default__': ['econom', 'uberx'],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.experiments3(filename='exp3_add_drive_cars.json')
@pytest.mark.experiments3(filename='exp3_drive_promo_block.json')
@pytest.mark.experiments3(filename='exp3_drive_promo_block_style.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_drive_promos_on_summary(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        uuid,
        yandex_drive_response,
        persuggest_response,
        numbers,
        flags,
        icon_image_tag,
        offer_count_limit,
        previous_offer_ids,
        redirect,
        drive_allowed,
):
    class OrderOffersCallsCounter:
        calls = 0

    headers = copy.deepcopy(PA_HEADERS)
    headers['X-AppMetrica-UUID'] = uuid
    headers['X-YaTaxi-Pass-Flags'] = flags

    yamaps.add_fmt_geo_object(GEO_OBJECT)

    @mockserver.json_handler('/order-offers/v1/offer-fields')
    def _mock_search(request):
        OrderOffersCallsCounter.calls += 1
        return load_json('order_offers_response.json')

    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        previous_offer_ids = request.json.pop('previous_offer_ids', [])
        if redirect:
            assert previous_offer_ids == [
                '3e29f7f7-8a7d26c2-4359f132-d6e0ee73',
            ]
        else:
            assert not previous_offer_ids
        assert not request.json
        if 'phonish' not in flags:
            assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        assert request.headers['UUID'] == uuid
        assert request.headers['Lon'] == '37.615000'
        assert request.headers['Lat'] == '55.758000'
        assert request.headers['DeviceId'] == 'DeviceId'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.args == {
            'src': '37.1 55.2',
            'dst': '37.2 55.3',
            'destination_name': 'Яндекс',
            'lang': 'ru',
            'offer_count_limit': ('0' if redirect else '5'),
        }

        if not yandex_drive_response:
            return mockserver.make_response('fail', status=500)

        resp = load_json(yandex_drive_response)
        resp['is_registred'] = uuid not in ['UUID_noreg', 'UUID_phonish']
        return mockserver.make_response(json=resp, headers={'X-Req-Id': '123'})

    request = copy.deepcopy(BASIC_REQUEST)
    if redirect:
        request['summary_state'].update(
            {
                'promo_context': {
                    'drive': {
                        'promo_offer_id': (
                            '3e29f7f7-8a7d26c2-4359f132-d6e0ee73'
                        ),
                    },
                },
            },
        )
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    if not drive_allowed:
        assert not response.json()['offers']['promoblocks']['items']
    else:
        resp = load_json(persuggest_response)
        _customize_response(
            resp,
            numbers,
            icon_image_tag,
            offer_count_limit,
            previous_offer_ids,
        )
        compare_responses(response.json(), resp)

        assert OrderOffersCallsCounter.calls == (1 if uuid == 'UUID_2' else 0)
