import copy
from typing import Union

import pytest

DEFAULT_HEADERS = {
    'X-Request-Application': (
        'app_name=android,app_ver1=1,app_ver2=2,app_ver3=4'
    ),
    'X-Request-Language': 'ru',
    'X-YaTaxi-UserId': 'user_id_1',
    'X-Yandex-UID': 'yauid',
    'X-Ya-User-Ticket': 'user-ticket',
    'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
    'X-YaTaxi-PhoneId': 'phone_id_1',
    'X-AppMetrica-UUID': 'appmetrica_uid',
    'X-AppMetrica-DeviceId': 'device_id',
}


def default_request():
    return {
        'summary_state': {
            'tariff_classes': ['econom', 'comfort', 'vip', 'ultima', 'drive'],
            'promo_context': {
                'offer_id': 'some_offer_id',
                'drive': {'promo_offer_id': 'drive_offer_1'},
                'shuttle': {
                    'offer_id': 'shuttle_offer_id',
                    'eta_seconds': 300,
                },
                'people_combo': {
                    'promoblock': {
                        'id': 'promo_on_summary_id_combo',
                        'substitutions': [
                            {'key': 'good', 'value': '👍'},
                            {'key': 'bad', 'value': '👎'},
                        ],
                    },
                },
            },
            'service_levels_offers': [
                {
                    'class': 'drive',
                    'offer_ids': ['drive_offer_1', 'drive_offer_2'],
                },
            ],
            'alternative_offers': [
                {'offer_id': 'alt_offer_id_1', 'type': 'explicit_antisurge'},
                {'offer_id': 'alt_offer_id_2', 'type': 'plus_promo'},
                {'offer_id': 'alt_offer_id_3', 'type': 'combo_outer'},
            ],
        },
        'state': {
            'location': [37.211375, 55.477065],
            'accuracy': 12,
            'bbox': [37.615, 55.753, 37.619, 55.758],
            'known_orders': [
                'taxi:taxi_order_id:revision',
                'eats:eats_order_id',
                'grocery:grocery_order_id',
            ],
            'fields': [
                {
                    'type': 'a',
                    'position': [37.211375, 55.477065],
                    'uri': 'uri',
                    'entrance': '6',
                },
                {
                    'type': 'b',
                    'position': [37.211375, 55.477065],
                    'uri': 'uri',
                    'entrance': '6',
                },
            ],
            'nz': 'moscow',
        },
        'client_info': {
            'supported_configurations': ['dialogue'],
            'supported_features': [
                {
                    'type': 'promoblock',
                    'widgets': ['arrow_button', 'deeplink_arrow_button'],
                },
            ],
            'mdash_width': 20.0,
            'ndash_width': 9.0,
        },
        'media_size_info': {
            'screen_height': 1920,
            'screen_width': 1080,
            'scale': 2.5,
        },
    }


BLENDER_PRIORITY = [
    {
        'class': 'econom',
        'promoblocks_order': [
            'promoblock1',
            'scooters_promoblock1',
            'promo_on_summary_id',
            'promo_on_summary_id_combo',
            'shuttle_promo:1a9f6b7e98b830a2e6b777eaaa88ede1',
        ],
    },
    {'class': 'comfort', 'promoblocks_order': ['promoblock1']},
    {'class': 'vip', 'promoblocks_order': ['promoblock1']},
    {'class': 'ultima', 'promoblocks_order': []},
    {'class': 'drive', 'promoblocks_order': []},
]


def _check_headers(request):
    for header, value in DEFAULT_HEADERS.items():
        if header in ['X-Request-Application', 'X-YaTaxi-Pass-Flags']:
            listed_headers_req = sorted(request.headers[header].split(','))
            listed_headers_original = sorted(value.split(','))
            assert listed_headers_original == listed_headers_req
        else:
            assert request.headers[header] == value


def _get_sorted_priorities(priorities):
    return sorted(priorities, key=lambda item: item['class'])


def remove_related_promoblocks(promoblocks):
    related_promo_ids = set()
    for item in promoblocks['items']:
        if 'related_promo' in item:
            related_promo_ids.add(item['id'])
            related_promo_ids.add(item['related_promo']['promo_id'])
    promoblocks['items'] = [
        item
        for item in promoblocks['items']
        if item['id'] not in related_promo_ids
    ]
    for priority in promoblocks['priority']:
        priority['promoblocks_order'] = [
            promo_id
            for promo_id in priority['promoblocks_order']
            if promo_id not in related_promo_ids
        ]


def _stats_fetching_exp(enabled: bool):
    return pytest.mark.experiments3(
        is_config=True,
        name='user_stats_fetching_settings',
        consumers=['inapp_communications/promos_on_summary'],
        default_value={'enabled': enabled},
        clauses=[],
    )


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
)
@pytest.mark.experiments3(filename='exp3_newbie_promo.json')
@pytest.mark.parametrize(
    'is_fetching_enabled',
    [
        pytest.param(False, marks=_stats_fetching_exp(False)),
        pytest.param(True, marks=_stats_fetching_exp(True)),
    ],
)
@pytest.mark.parametrize(
    'stats_response, is_authorized, should_see_promo',
    [
        ('empty_data', True, False),
        ('empty_counters', True, True),
        ('500_response', True, False),
        (0, True, True),
        (1, True, True),
        (3, True, False),
        (0, False, False),
        pytest.param(
            0,
            False,
            True,
            marks=pytest.mark.config(
                INAPP_PROMOS_ON_SUMMARY_ALLOW_UNAUTHORIZED=True,
            ),
        ),
    ],
)
async def test_number_of_trips_kwarg(
        taxi_inapp_communications,
        mockserver,
        load_json,
        stats_response: Union[int, str],
        should_see_promo: bool,
        is_authorized: bool,
        is_fetching_enabled: bool,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    @mockserver.json_handler('/user-statistics/v1/orders')
    def _mock_stats(request):
        if stats_response == '500_response':
            return mockserver.make_response(status=500)
        data = [
            {
                'identity': {'type': 'phone_id', 'value': ''},
                'counters': [
                    {
                        'counted_from': '2019-12-11T09:00:00+0000',
                        'counted_to': '2019-12-11T09:00:00+0000',
                        'value': stats_response,
                        'properties': [],
                    },
                ],
            },
        ]
        if stats_response == 'empty_data':
            data = []
        if stats_response == 'empty_counters':
            data[0]['counters'] = []
        return mockserver.make_response(status=200, json={'data': data})

    headers = copy.deepcopy(DEFAULT_HEADERS)
    if not is_authorized:
        del headers['X-Yandex-UID'], headers['X-YaTaxi-PhoneId']
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        json=default_request(),
        headers=headers,
    )

    assert response.status_code == 200

    if is_authorized and is_fetching_enabled:
        assert _mock_stats.has_calls
        request = _mock_stats.next_call()['request'].json

        assert request == {
            'identities': [{'type': 'phone_id', 'value': 'phone_id_1'}],
            'group_by': [],
        }

    body = response.json()
    if should_see_promo and (is_fetching_enabled or not is_authorized):
        assert len(body['offers']['promoblocks']['items']) == 1
    else:
        assert not body['offers']['promoblocks']['items']


@pytest.mark.config(
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {
            'source_name': 'drive',
            'enabled': True,
            'summary_modes': [{'type': 'maas', 'enabled': False}],
        },
        {'source_name': 'shuttle', 'enabled': True},
        {'source_name': 'inapp-communications', 'enabled': True},
        {'source_name': 'price-promotions', 'enabled': True},
        {'source_name': 'people_combo', 'enabled': True},
        {'source_name': 'scooters', 'enabled': True},
    ],
)
@pytest.mark.parametrize(
    'use_blender, resp_json',
    [
        pytest.param(
            True,
            'promos_on_summary_default_response.json',
            id='using blender',
            marks=[
                pytest.mark.config(
                    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=True,
                ),
            ],
        ),
        pytest.param(
            False,
            'promos_on_summary_default_response.json',
            id='no using blender',
            marks=[
                pytest.mark.config(
                    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
                ),
            ],
        ),
        pytest.param(
            False,
            'promos_on_summary_stub_response.json',
            id='no using blender (stub)',
            marks=[
                pytest.mark.config(
                    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
                    INAPP_PROMOBLOCKS_STUB_SETTINGS={
                        'enabled': True,
                        'meta_types_allowed': [
                            'tariff_upgrade_promo',
                            'drive_promo_block',
                            'shuttle_promo',
                            'people_combo',
                            'scooters_promo_block',
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            'promos_on_summary_default_response.json',
            id='no using blender (stub, metatypes not provided)',
            marks=[
                pytest.mark.config(
                    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
                    INAPP_PROMOBLOCKS_STUB_SETTINGS={'enabled': True},
                ),
            ],
        ),
    ],
)
@pytest.mark.translations(
    backend_promotions={
        'combo_promo_title': {
            'ru': 'промки %(bad)s!',
            'en': 'promoblocks are %(bad)s!',
        },
        'combo_promo_text': {
            'ru': 'комбо %(good)s!',
            'en': 'combo is %(good)s!',
        },
    },
)
@pytest.mark.experiments3(filename='exp3_tariff_matches.json')
@pytest.mark.experiments3(filename='exp3_inapp_scooters_promos_source.json')
async def test_ok(
        taxi_inapp_communications,
        mockserver,
        load_json,
        use_blender,
        resp_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    @mockserver.json_handler('/blender/blender/v1/internal/summary/priority')
    def _mock_blender(request):
        _check_headers(request)
        assert request.json == load_json('blender_default_request.json')

        return {'priority': copy.deepcopy(BLENDER_PRIORITY)}

    @mockserver.json_handler(
        '/persuggest/4.0/persuggest/v1/drive-promos-on-summary',
    )
    def _mock_persuggest(request):
        _check_headers(request)
        assert request.json == load_json('persuggest_default_request.json')

        return load_json('persuggest_service_response.json')

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/promotion/fetch_offers',
    )
    def _mock_shuttle_control(request):
        assert request.json == load_json('shuttle_default_request.json')

        return load_json('shuttle_service_response.json')

    @mockserver.json_handler('/tariffs-promotions/v1/price-promotions')
    def _mock_price_promotions(request):
        _check_headers(request)
        assert request.json == load_json(
            'tariffs_price_promotions_request.json',
        )
        return load_json('tariffs_price_promotions_response.json')

    @mockserver.json_handler(
        '/scooters-misc/scooters-misc/v1/promos-on-summary',
    )
    def _mock_scooters_misc(request):
        _check_headers(request)
        assert request.json == load_json('scooters_misc_default_request.json')

        return load_json('scooters_misc_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        default_request(),
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    resp = copy.deepcopy(load_json(resp_json))
    if use_blender:
        resp['offers']['promoblocks']['priority'] = copy.deepcopy(
            BLENDER_PRIORITY,
        )
    else:
        remove_related_promoblocks(resp['offers']['promoblocks'])

    body = response.json()

    del resp['layout']['grid_id']
    resp_priority = resp['offers']['promoblocks']['priority']
    print(resp_priority)
    del resp['offers']['promoblocks']['priority']

    del body['layout']['grid_id']
    body_priority = body['offers']['promoblocks']['priority']
    del body['offers']['promoblocks']['priority']

    assert body == resp
    assert _get_sorted_priorities(body_priority) == _get_sorted_priorities(
        resp_priority,
    )


@pytest.mark.experiments3(filename='exp3_tariff_matches.json')
@pytest.mark.parametrize(
    'modes',
    [
        pytest.param(
            [],
            id='all_disabled',
            marks=pytest.mark.config(
                INAPP_SOURCES_OF_PROMOBLOCKS=[
                    {'source_name': 'drive', 'enabled': False},
                    {'source_name': 'shuttle', 'enabled': False},
                    {'source_name': 'inapp-communications', 'enabled': False},
                    {'source_name': 'price-promotions', 'enabled': False},
                    {'source_name': 'scooters', 'enabled': False},
                ],
                INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
            ),
        ),
        pytest.param(
            [{'type': 'maas'}],
            id='disabled_by_summary_mode',
            marks=pytest.mark.config(
                INAPP_SOURCES_OF_PROMOBLOCKS=[
                    {
                        'source_name': 'drive',
                        'enabled': True,
                        'summary_modes': [
                            {'type': 'maas', 'enabled': False},
                            {'type': 'other', 'enabled': True},
                        ],
                    },
                    {'source_name': 'shuttle', 'enabled': False},
                    {
                        'source_name': 'price-promotions',
                        'enabled': False,
                        'summary_modes': [{'type': 'maas', 'enabled': True}],
                    },
                ],
                INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
            ),
        ),
    ],
)
async def test_sources_disabled(taxi_inapp_communications, mockserver, modes):
    @mockserver.json_handler('/card-filter/v1/filteredcards')
    def _mock_card_filter(request):
        assert False

    @mockserver.json_handler(
        '/persuggest/4.0/persuggest/v1/drive-promos-on-summary',
    )
    def _mock_drive_persuggest(request):
        assert False

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/promo_on_summary',
    )
    def _mock_shuttle_control(request):
        assert False

    @mockserver.json_handler('/tariffs-promotions/v1/price-promotions')
    def _mock_price_promotions(request):
        assert False

    @mockserver.json_handler(
        '/scooters-misc/scooters-misc/v1/promos-on-summary',
    )
    def _mock_scooters_misc(request):
        assert False

    request = default_request()
    request['summary_state']['modes'] = modes

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        json=request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
)
@pytest.mark.translations(
    backend_promotions={'text to translate': {'ru': 'текст', 'en': 'text'}},
)
@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_translations(taxi_inapp_communications, mockserver, load_json):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_promo_on_summary_tanker_key.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        default_request(),
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()
    assert len(body['offers']['promoblocks']['items']) == 1
    item = body['offers']['promoblocks']['items'][0]
    assert item['text']['items'][1]['text'] == 'текст'
    assert item['title']['items'][1]['text'] == 'текст'
    assert item['widgets']['attributed_text']['items'][1]['text'] == 'текст'


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
    INAPP_PROMOBLOCKS_CARD_PLUS_FEATURES=[
        {
            'feature_name': 'mastercard_plus',
            'conditions': {'bin_one_of': ['123456']},
        },
    ],
)
@pytest.mark.experiments3(filename='exp3_promos_on_summary_mastercard.json')
@pytest.mark.parametrize(
    'mastercard_selected,has_point_b',
    [(True, True), (False, True), (True, False)],
)
@pytest.mark.parametrize('ios_hack', [True, False])
async def test_mastercard_matching(
        taxi_inapp_communications,
        mockserver,
        load_json,
        mastercard_selected,
        has_point_b,
        ios_hack,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_promo_on_summary_mastercard.json')

    @mockserver.json_handler('/card-filter/v1/filteredcards')
    def _mock_card_filter(request):
        assert request.headers['X-Yandex-UID'] == 'yauid'
        assert request.json['cache_preferred'] is True
        return {
            'available_cards': [
                {
                    'type': 'card',
                    'name': 'MasterCard',
                    'id': 'card-aaaaaaaaaaaa',
                    'currency': 'RUB',
                    'system': 'MasterCard',
                    'number': '123456****0000',
                    'available': True,
                    'availability': {'available': True, 'disabled_reason': ''},
                    'bin': '123456',
                },
                {
                    'type': 'card',
                    'name': 'Visa',
                    'id': 'card-bbbbbbbbbbbb',
                    'currency': 'RUB',
                    'system': 'Visa',
                    'number': '111111****0000',
                    'available': True,
                    'availability': {'available': True, 'disabled_reason': ''},
                    'bin': '111111',
                },
            ],
            'wallets': [],
        }

    request = default_request()
    payment = {
        'type': 'card',
        'payment_method_id': (
            'card-aaaaaaaaaaaa' if mastercard_selected else 'card-bbbbbbbbbbbb'
        ),
    }
    if not ios_hack:
        request.update({'payment': payment})
    else:
        summary_state = request.get('summary_state', {})
        summary_state.update({'payments': payment})
        request['summary_state'] = summary_state

    if not has_point_b:
        request['state']['fields'] = request['state']['fields'][:1]
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()
    assert len(body['offers']['promoblocks']['items']) == (
        2 if has_point_b else 0
    )


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
)
@pytest.mark.experiments3(filename='exp3_promos_on_summary_mastercard.json')
@pytest.mark.parametrize('ios_hack', [True, False])
async def test_mastercard_card_filter_failure(
        taxi_inapp_communications, mockserver, load_json, ios_hack,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_promo_on_summary_mastercard.json')

    @mockserver.json_handler('/card-filter/v1/filteredcards')
    def _mock_card_filter(request):
        return mockserver.make_response(status=500)

    request = default_request()
    payment = {'type': 'card', 'payment_method_id': 'card-aaaaaaaaaaaa'}
    if not ios_hack:
        request.update({'payment': payment})
    else:
        summary_state = request.get('summary_state', {})
        summary_state.update({'payments': payment})
        request['summary_state'] = summary_state

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()
    assert not body['offers']['promoblocks']['items']


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
)
@pytest.mark.parametrize(
    'matches',
    [
        pytest.param(
            True,
            id='tariff matches',
            marks=[
                pytest.mark.experiments3(filename='exp3_tariff_matches.json'),
            ],
        ),
        pytest.param(
            False,
            id='tariff mismatches',
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_tariff_mismatches.json',
                ),
            ],
        ),
    ],
)
async def test_tariff_matching(
        taxi_inapp_communications, mockserver, load_json, matches,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        default_request(),
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()

    priorities = _get_sorted_priorities(
        body['offers']['promoblocks']['priority'],
    )
    if matches:
        assert priorities == [
            {'class': 'comfort', 'promoblocks_order': ['promo_on_summary_id']},
            {'class': 'drive', 'promoblocks_order': []},
            {'class': 'econom', 'promoblocks_order': ['promo_on_summary_id']},
            {'class': 'ultima', 'promoblocks_order': []},
            {'class': 'vip', 'promoblocks_order': []},
        ]
    else:
        assert len(priorities) == 5
        for i in range(5):
            assert not priorities[i]['promoblocks_order']


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=True,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
)
@pytest.mark.experiments3(filename='exp3_tariff_matches.json')
async def test_check_firewall(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    @mockserver.json_handler('/blender/blender/v1/internal/summary/priority')
    def _mock_blender(request):
        prior = copy.deepcopy(BLENDER_PRIORITY)
        prior[1]['class'] = 'comfort+'
        return {'priority': prior}

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        default_request(),
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()

    resp_priority = copy.deepcopy(BLENDER_PRIORITY)
    resp_priority[1]['promoblocks_order'] = []

    body_priority = body['offers']['promoblocks']['priority']
    assert _get_sorted_priorities(body_priority) == _get_sorted_priorities(
        resp_priority,
    )


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
)
@pytest.mark.parametrize(
    'phone_id, is_in_test',
    [('phone_id_1', True), ('phone_id_not_in_test_publish', False)],
)
@pytest.mark.experiments3(filename='exp3_test_publish.json')
async def test_test_publish(
        taxi_inapp_communications, phone_id, is_in_test, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['X-YaTaxi-PhoneId'] = phone_id
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        json=default_request(),
        headers=headers,
    )

    assert response.status == 200, response.text
    offers = response.json()['offers']['promoblocks']['items']
    assert len(offers) == (1 if is_in_test else 0)


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
)
@pytest.mark.parametrize(
    'matches',
    [
        pytest.param(
            True,
            id='bin matches',
            marks=[pytest.mark.experiments3(filename='exp3_bin_matches.json')],
        ),
        pytest.param(
            False,
            id='bin mismatches',
            marks=[
                pytest.mark.experiments3(filename='exp3_bin_mismatches.json'),
            ],
        ),
    ],
)
async def test_bin_matching(
        taxi_inapp_communications, mockserver, load_json, matches,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_promo_on_summary_bin.json')

    @mockserver.json_handler('/card-filter/v1/filteredcards')
    def _mock_card_filter(request):
        assert request.headers['X-Yandex-UID'] == 'yauid'
        assert request.json['cache_preferred'] is True
        return {
            'available_cards': [
                {
                    'type': 'card',
                    'name': 'MasterCard',
                    'id': 'card-aaaaaaaaaaaa',
                    'currency': 'RUB',
                    'system': 'MasterCard',
                    'number': '123456****0000',
                    'available': True,
                    'availability': {'available': True, 'disabled_reason': ''},
                    'bin': '123456',
                },
                {
                    'type': 'card',
                    'name': 'Visa',
                    'id': 'card-bbbbbbbbbbbb',
                    'currency': 'RUB',
                    'system': 'Visa',
                    'number': '111111****0000',
                    'available': True,
                    'availability': {'available': True, 'disabled_reason': ''},
                    'bin': '111111',
                },
            ],
            'wallets': [],
        }

    request = default_request()
    payment = {'type': 'card', 'payment_method_id': 'card-aaaaaaaaaaaa'}
    request.update({'payment': payment})

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()
    if matches:
        assert len(body['offers']['promoblocks']['items']) == 1
    else:
        assert not body['offers']['promoblocks']['items']


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
)
@pytest.mark.parametrize('bank_account', [True, False])
@pytest.mark.experiments3(filename='exp3_bank_account.json')
async def test_bank_account(
        taxi_inapp_communications, bank_account, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    headers = copy.deepcopy(DEFAULT_HEADERS)
    if bank_account:
        headers['X-YaTaxi-Pass-Flags'] = 'bank-account'
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        json=default_request(),
        headers=headers,
    )

    assert response.status == 200, response.text
    promos = response.json()['offers']['promoblocks']['items']
    assert len(promos) == (1 if bank_account else 0)
