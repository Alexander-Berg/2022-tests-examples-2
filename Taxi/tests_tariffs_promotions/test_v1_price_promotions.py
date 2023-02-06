import copy
import enum
import json
import urllib.parse as urlparse

import pytest


class PromoType(enum.Enum):
    EXPENSIVE = 1
    CHEAPER = 2
    FASTER = 3


# some tariffs have different names on backend and on client
# keys are backend tariff names, values - client names
TARIFFS_COMPLIANCE = {
    'business': 'comfort',
    'econom': 'econom',
    'vip': 'business',
}

CURRENCY_SIGN = {'USD': '$', 'RUB': '₽'}

CURRENCY_FORMATTING_RULES = {
    'USD': {'__default__': 2},
    'RUB': {'__default__': 2},
}
CURRENCY_ROUNDING_RULES = {
    'USD': {'__default__': 0.1},
    '__default__': {'__default__': 1},
}

PA_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '4003514353',
    'X-Request-Application': 'app_name=iphone',
    'X-Request-Language': 'en',
}

BASIC_REQUEST = {
    'client_info': {'supported_configurations': ['dialogue']},
    'summary_state': {
        'offer_id': 'offer_id',
        'tariff_classes': ['econom', 'business', 'vip', 'elite'],
        'alternative_offers': [
            {'offer_id': 'alt_offer_id_1', 'type': 'explicit_antisurge'},
            {'offer_id': 'alt_offer_id_2', 'type': 'plus_promo'},
            {'offer_id': 'alt_offer_id_3', 'type': 'perfect_chain'},
        ],
    },
    'state': {
        'location': [37.615, 55.758],
        'nz': 'moscow',
        'fields': [
            {'position': [37.53472388755793, 55.750507058344134], 'type': 'a'},
            {
                'position': [37.53360806644724, 55.8001525488165],
                'type': 'mid1',
            },
            {'position': [37.642563, 55.73476], 'type': 'b'},
        ],
    },
}

PROMO_CLIENT_MESSAGES = {
    'promo.tariff_upgrade_suggestion_text': {
        'en': '<bold>+%(price)s</bold> и приедет %(tariff)s',
    },
    'promo.cheaper_tariff_upgrade_suggestion_text': {
        'en': '%(tariff)s приедет дешевле <bold>на %(price)s</bold>',
    },
    'promo.faster_tariff_upgrade_suggestion_text': {
        'en': '%(tariff)s приедет быстрее <bold>на %(minutes)s мин.</bold>',
    },
    'promo.plus_promo_upgraded_tariff.tariff_from.title': {
        'en': '<bold>Комфорт</bold> на %(price)s дешевле',
    },
    'promo.plus_promo_upgraded_tariff.tariff_to.title': {
        'en': 'Уехать на %(price)s дешевле <bold>Эконома</bold>',
    },
    'promo.plus_promo_upgraded_tariff.text': {
        'en': [
            '<text_minor>Потратить </text_minor>'
            '<plus_minor>%(plus_amount)s балл</plus_minor>',
            '<text_minor>Потратить </text_minor>'
            '<plus_minor>%(plus_amount)s балла</plus_minor>',
            '<text_minor>Потратить </text_minor>'
            '<plus_minor>%(plus_amount)s баллов</plus_minor>',
        ],
    },
    'promo.surge_redirect_transport.title': {'en': 'Общественный транспорт'},
    'promo.surge_redirect_transport.text': {
        'en': '<text_minor>В такой снегопад будет быстрее</text_minor>',
    },
    'promo.surge_communications.popup_title': {
        'en': 'Мало машин. Повысили цену, чтобы вы ...',
    },
    'promo.surge_communications.popup_button_text': {
        'en': 'Как это работает?',
    },
    'promo.driver_funded_discount.title': {
        'en': '<text_minor>Попробуйте скидку в тарифе "Комфорт"</text_minor>',
    },
    'promo.driver_funded_discount.text': {
        'en': '<text_minor>Будет комфортно на халяву</text_minor>',
    },
    'promo.perfect_chain.title': {
        'en': 'Подождать и сэкономить %(price_delta)s',
    },
    'promo.perfect_chain.text': {'en': 'Ждать машину ~%(eta)s'},
}
TARIFF_TRANSLATIONS = {
    'name.econom': {'en': 'econom'},
    'name.comfort': {'en': 'comfort'},
    'name.business': {'en': 'business'},
    'currency_with_sign.default': {'en': '$VALUE$$SIGN$$CURRENCY$'},
    'currency_sign.rub': {'en': CURRENCY_SIGN['RUB']},
    'currency_sign.usd': {'en': CURRENCY_SIGN['USD']},
}
CHEAPER_TARIFF_META_TYPE = 'cheaper_tariff_promo'
EXPENSIVE_TARIFF_META_TYPE = 'tariff_upgrade_promo'
FASTER_TARIFF_META_TYPE = 'faster_tariff_promo'
CHEAPER_TARIFF_EXPERIMENT_NAME = 'upgraded_cheaper_tariff_promo'
EXPENSIVE_TARIFF_EXPERIMENT_NAME = 'upgraded_expensive_tariff_promo'
FASTER_TARIFF_EXPERIMENT_NAME = 'upgraded_faster_tariff_promo'

TARIFFS_TANKER_KEYS = {
    'business': 'name.' + TARIFFS_COMPLIANCE['business'],
    'econom': 'name.' + TARIFFS_COMPLIANCE['econom'],
    'vip': 'name.' + TARIFFS_COMPLIANCE['vip'],
}

BOLD_FONT = 'bold'
REGULAR_FONT = 'regular'


def check_tariff_upgrade_promo_base(promo, promo_type):
    if promo_type == PromoType.EXPENSIVE:
        assert promo['meta_type'] == EXPENSIVE_TARIFF_META_TYPE
        assert (
            promo['options']['experiment'] == EXPENSIVE_TARIFF_EXPERIMENT_NAME
        )
    elif promo_type == PromoType.CHEAPER:
        assert promo['meta_type'] == CHEAPER_TARIFF_META_TYPE
        assert promo['options']['experiment'] == CHEAPER_TARIFF_EXPERIMENT_NAME
    elif promo_type == PromoType.FASTER:
        assert promo['meta_type'] == FASTER_TARIFF_META_TYPE
        assert promo['options']['experiment'] == FASTER_TARIFF_EXPERIMENT_NAME
    assert promo['options']['priority'] == 3
    assert promo['show_policy']['max_show_count'] == 3
    assert promo['show_policy']['max_widget_usage_count'] == 5
    assert promo['widgets']['deeplink_arrow_button']['items'][0]['width'] == 50


def check_tariff_faster_upgrade(
        promo, base_tariff, promo_tariff, expected_delta,
):
    widget = promo['widgets']['deeplink_arrow_button']
    promo_title = promo['title']['items']
    deeplink = widget['deeplink']
    image_tag = widget['items'][0]['image_tag']
    client_tariff_name = TARIFFS_COMPLIANCE[promo_tariff]

    assert promo_title[0]['text'] == f'{client_tariff_name} приедет быстрее '

    assert promo_title[1]['text'] == f'на {expected_delta} мин.'
    assert promo_title[1]['font_weight'] == BOLD_FONT
    assert (
        promo['id'] == f'{FASTER_TARIFF_META_TYPE}:'
        f'{base_tariff}_{promo_tariff}_offer_id'
    )

    assert deeplink == f'yandextaxi://route?tariffClass={promo_tariff}'
    assert image_tag == f'class_{promo_tariff}_icon_7'
    assert promo['promoted_class'] == promo_tariff


def check_tariff_upgrade_promo(
        promo, base_tariff, promo_tariff, expected_delta, promo_type, currency,
):
    widget = promo['widgets']['deeplink_arrow_button']
    promo_title = promo['title']['items']
    deeplink = widget['deeplink']
    image_tag = widget['items'][0]['image_tag']

    client_tariff_name = TARIFFS_COMPLIANCE[promo_tariff]
    sign = CURRENCY_SIGN[currency]
    if promo_type == PromoType.EXPENSIVE:
        assert promo_title[0]['text'] == f'+{expected_delta}{sign}'
        assert promo_title[0]['font_weight'] == BOLD_FONT

        assert promo_title[1]['text'] == f' и приедет {client_tariff_name}'

        assert (
            promo['id'] == f'{EXPENSIVE_TARIFF_META_TYPE}:'
            f'{base_tariff}_{promo_tariff}_offer_id'
        )
    elif promo_type == PromoType.CHEAPER:
        assert (
            promo_title[0]['text'] == f'{client_tariff_name} приедет дешевле '
        )

        assert promo_title[1]['text'] == f'на {expected_delta}{sign}'
        assert promo_title[1]['font_weight'] == BOLD_FONT
        assert (
            promo['id'] == f'{CHEAPER_TARIFF_META_TYPE}:'
            f'{base_tariff}_{promo_tariff}_offer_id'
        )
    assert deeplink == f'yandextaxi://route?tariffClass={promo_tariff}'
    assert image_tag == f'class_{promo_tariff}_icon_7'
    assert promo['promoted_class'] == promo_tariff


def prepare_prices(base_resp, prices):
    for i, price in enumerate(prices.values()):
        base_resp['fields']['prices'][i]['pricing_data']['user']['price'][
            'total'
        ] = price

    for _ in prices.keys():
        for j, price in enumerate(base_resp['fields']['prices']):
            if price['cls'] not in prices:
                del base_resp['fields']['prices'][j]
                break

    return base_resp


def to_categories(prices):
    return [
        {'name': cls, 'final_price': str(price)}
        for cls, price in prices.items()
    ]


def seconds_to_categories(tariff_seconds):
    return [
        {'name': cls, 'final_price': '100', 'estimated_seconds': seconds}
        for cls, seconds in tariff_seconds.items()
    ]


@pytest.mark.translations(
    client_messages=PROMO_CLIENT_MESSAGES, tariff=TARIFF_TRANSLATIONS,
)
@pytest.mark.config(
    CURRENCY_FORMATTING_RULES=CURRENCY_FORMATTING_RULES,
    CURRENCY_ROUNDING_RULES=CURRENCY_ROUNDING_RULES,
)
@pytest.mark.parametrize(
    (
        'prices',
        'price_perc',
        'expected_promo_tariffs',
        'expected_supported_classes',
        'expected_price_deltas',
        'currency',
    ),
    (
        pytest.param(
            {'econom': 100, 'business': 106, 'vip': 207, 'elite': 400},
            5,
            [],
            [],
            None,
            'RUB',
            id='price_not_match',
        ),
        pytest.param(
            {'econom': 100, 'business': 200, 'vip': 300, 'elite': 101},
            5,
            [],
            [],
            None,
            'RUB',
            id='tariff_not_match',
        ),
        pytest.param({'econom': 100}, 20, [], [], None, 'RUB', id='one_price'),
        pytest.param(
            {'econom': 1000, 'business': 200, 'vip': 300, 'elite': 400},
            5,
            [],
            [],
            None,
            'RUB',
            id='small_price',
        ),
        pytest.param(
            {'econom': 1000, 'business': 200, 'vip': 210, 'elite': 400},
            5,
            ['vip'],
            ['business'],
            [10],
            'RUB',
            id='get_one_promo',
        ),
        pytest.param(
            {'econom': 100, 'business': 110, 'vip': 111, 'elite': 112},
            20,
            ['business', 'vip'],
            ['econom', 'business'],
            [10, 1],
            'RUB',
            id='get_two_promos',
        ),
        pytest.param(
            {'econom': 10.2, 'business': 10.3, 'vip': 12.5, 'elite': 15.9},
            10,
            ['business'],
            ['econom'],
            [0.1],
            'USD',
            id='get_one_promo_float',
        ),
        pytest.param({}, 20, [], [], [], 'RUB', id='no_prices'),
    ),
)
@pytest.mark.redis_store(file='redis')
async def test_upgraded_expensive_tariff_promotions(
        taxi_tariffs_promotions,
        redis_store,
        load_json,
        experiments3,
        prices,
        price_perc,
        expected_promo_tariffs,
        expected_supported_classes,
        expected_price_deltas,
        currency,
):
    exp = load_json('exp3_upgraded_expensive_tariff_promo.json')
    exp['experiments'][0]['clauses'][0]['value']['show_rulles'][0][
        'diff_price_percent'
    ] = price_perc
    experiments3.add_experiments_json(exp)
    await taxi_tariffs_promotions.invalidate_caches()

    redis_store.set(
        'offer:offer_id',
        json.dumps(
            {'currency': currency, 'categories': to_categories(prices)},
        ),
    )

    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=BASIC_REQUEST, headers=PA_HEADERS,
    )

    assert response.status_code == 200
    promos = response.json()['offers']['promoblocks']['items']

    assert len(promos) == len(expected_promo_tariffs)
    promo_map = {}
    for promo in promos:
        check_tariff_upgrade_promo_base(promo, PromoType.EXPENSIVE)
        promo_map[promo['supported_classes'][0]] = promo

    for i, tariff in enumerate(expected_supported_classes):
        check_tariff_upgrade_promo(
            promo_map[tariff],
            tariff,
            expected_promo_tariffs[i],
            expected_price_deltas[i],
            PromoType.EXPENSIVE,
            currency,
        )


@pytest.mark.translations(
    client_messages=PROMO_CLIENT_MESSAGES, tariff=TARIFF_TRANSLATIONS,
)
@pytest.mark.config(
    CURRENCY_FORMATTING_RULES=CURRENCY_FORMATTING_RULES,
    CURRENCY_ROUNDING_RULES=CURRENCY_ROUNDING_RULES,
)
@pytest.mark.parametrize(
    (
        'prices',
        'expected_promo_tariffs',
        'expected_supported_classes',
        'expected_price_deltas',
        'currency',
    ),
    (
        pytest.param(
            {'econom': 100, 'business': 106, 'vip': 207, 'elite': 400},
            [],
            [],
            None,
            'RUB',
            id='price_not_match',
        ),
        pytest.param({'econom': 100}, [], [], None, 'RUB', id='one_price'),
        pytest.param(
            {'econom': 100, 'business': 200, 'vip': 190, 'elite': 400},
            ['vip'],
            ['business'],
            [10],
            'RUB',
            id='get_one_promo',
        ),
        pytest.param(
            {'econom': 1.1, 'business': 2.0, 'vip': 1.9, 'elite': 4.2},
            ['vip'],
            ['business'],
            [0.1],
            'USD',
            id='get_one_promo_float',
        ),
        pytest.param(
            {'econom': 100, 'business': 200, 'vip': 90, 'elite': 300},
            ['vip', 'vip'],
            ['econom', 'business'],
            [10, 110],
            'RUB',
            id='get_two_promos',
        ),
        pytest.param({}, [], [], None, 'RUB', id='no_prices'),
    ),
)
@pytest.mark.redis_store(file='redis')
async def test_upgraded_cheaper_tariff_promotions(
        taxi_tariffs_promotions,
        redis_store,
        load_json,
        experiments3,
        prices,
        expected_promo_tariffs,
        expected_supported_classes,
        expected_price_deltas,
        currency,
):
    exp = load_json('exp3_upgraded_cheaper_tariff_promo.json')
    experiments3.add_experiments_json(exp)
    await taxi_tariffs_promotions.invalidate_caches()

    redis_store.set(
        'offer:offer_id',
        json.dumps(
            {'currency': currency, 'categories': to_categories(prices)},
        ),
    )

    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=BASIC_REQUEST, headers=PA_HEADERS,
    )

    assert response.status_code == 200
    promos = response.json()['offers']['promoblocks']['items']

    assert len(promos) == len(expected_promo_tariffs)
    promo_map = {}
    for promo in promos:
        check_tariff_upgrade_promo_base(promo, PromoType.CHEAPER)
        promo_map[promo['supported_classes'][0]] = promo

    for i, tariff in enumerate(expected_supported_classes):
        check_tariff_upgrade_promo(
            promo_map[tariff],
            tariff,
            expected_promo_tariffs[i],
            expected_price_deltas[i],
            PromoType.CHEAPER,
            currency,
        )


@pytest.mark.redis_store(file='redis')
@pytest.mark.translations(client_messages=PROMO_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'has_promo, params',
    (
        pytest.param(True, {}, id='success_promo'),
        pytest.param(False, {'without_alternatives'}, id='no_alternatives'),
        pytest.param(False, {'without_plus_promo'}, id='no_plus_alternative'),
        pytest.param(
            False, {'unavaibale_tariff_from'}, id='unavaibale_tariff_from',
        ),
        pytest.param(
            False, {'unavaibale_tariff_to'}, id='unavaibale_tariff_to',
        ),
        pytest.param(False, {'without_exp'}, id='no_plus_promo_exp'),
        pytest.param(False, {'without_db_offer'}, id='no_db_offer'),
        pytest.param(False, {'invalid_db_offer'}, id='invalid_db_offer'),
    ),
)
async def test_upgraded_tariff_by_plus_promotions(
        taxi_tariffs_promotions,
        mockserver,
        has_promo,
        params,
        redis_store,
        load_json,
        experiments3,
):
    request = copy.deepcopy(BASIC_REQUEST)

    if 'without_alternatives' in params:
        del request['summary_state']['alternative_offers']

    if 'without_plus_promo' in params:
        request['summary_state']['alternative_offers'] = [
            offer
            for offer in request['summary_state']['alternative_offers']
            if offer['type'] != 'plus_promo'
        ]
    elif 'unavaibale_tariff_from' in params:
        request['summary_state']['tariff_classes'].remove('econom')
    elif 'unavaibale_tariff_to' in params:
        request['summary_state']['tariff_classes'].remove('business')

    if 'without_exp' not in params:
        exp = load_json('exp3_upgraded_tariff_by_plus_promo.json')
        experiments3.add_experiments_json(exp)

    if 'without_db_offer' not in params:
        plus_promo = {
            'personal_wallet_withdraw_amount': '42',
            'tariff_from': 'econom',
            'tariff_to': 'business',
        }

        if 'invalid_db_offer' in params:
            del plus_promo['tariff_from']

        redis_store.set(
            'offer:alt_offer_id_2',
            json.dumps(
                {
                    'currency': 'RUB',
                    'categories': [{'final_price': '70', 'name': 'business'}],
                    'plus_promo': plus_promo,
                },
            ),
        )

    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=request, headers=PA_HEADERS,
    )
    promos = response.json()['offers']['promoblocks']['items']

    assert bool(promos) == has_promo

    if has_promo:
        expected_promos = load_json('expected_plus_promo.json')
        assert promos == expected_promos


@pytest.mark.now('2021-03-01T10:00:00.00000+0000')
@pytest.mark.redis_store(file='redis')
@pytest.mark.translations(client_messages=PROMO_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'has_promo, frequency_policy',
    (
        pytest.param(
            True,
            {'show_delay_hours': 1, 'show_threshold_minutes': 15},
            id='in_show_threshold',
        ),
        pytest.param(
            False,
            {'show_delay_hours': 1, 'show_threshold_minutes': 5},
            id='not_in_show_threshold_and_in_show_delay_hours',
        ),
        pytest.param(
            True,
            {'show_delay_hours': 0.1, 'show_threshold_minutes': 1},
            id='not_in_show_delay_hours',
        ),
        pytest.param(
            True,
            {'show_delay_hours': 0.1, 'show_threshold_minutes': 0},
            id='one_show_with_zero_show_threshold',
        ),
    ),
)
async def test_upgraded_tariff_by_plus_promotions_frequency_policy(
        taxi_tariffs_promotions,
        redis_store,
        load_json,
        experiments3,
        has_promo,
        frequency_policy,
):
    request = copy.deepcopy(BASIC_REQUEST)

    exp = load_json('exp3_upgraded_tariff_by_plus_promo.json')
    if frequency_policy:
        plus_promo_exp = exp['experiments'][0]
        plus_promo_exp['clauses'][0]['value']['widget_settings'][
            'frequency_policy'
        ] = frequency_policy
    experiments3.add_experiments_json(exp)

    redis_store.set(
        'offer:alt_offer_id_2',
        json.dumps(
            {
                'currency': 'RUB',
                'categories': [{'final_price': '70', 'name': 'business'}],
                'plus_promo': {
                    'personal_wallet_withdraw_amount': '42',
                    'tariff_from': 'econom',
                    'tariff_to': 'business',
                },
            },
        ),
    )

    ten_minutes_to_now = '2021-03-01T09:50:00.00000+0000'
    redis_store.set('yandex_uid:4003514353', ten_minutes_to_now)
    redis_store.set('phone_id:123456789012345678901234', ten_minutes_to_now)

    for _ in range(3):
        response = await taxi_tariffs_promotions.post(
            'v1/price-promotions', json=request, headers=PA_HEADERS,
        )
        promos = response.json()['offers']['promoblocks']['items']
        assert bool(promos) == has_promo

        if frequency_policy['show_threshold_minutes'] == 0:
            has_promo = False


@pytest.mark.redis_store(file='redis')
@pytest.mark.translations(client_messages=PROMO_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'surge_threshold, supported_classes',
    (
        ('3.5', []),
        ('2.0', ['econom']),
        ('1.5', ['vip', 'econom']),
        ('1.0', ['vip', 'elite', 'econom']),
    ),
)
async def test_surge_promotions(
        taxi_tariffs_promotions,
        mockserver,
        redis_store,
        load_json,
        experiments3,
        surge_threshold,
        supported_classes,
):
    def _normalize_deeplink(promos):
        widget = promos[0]['widgets']['deeplink_arrow_button']
        deeplink = urlparse.urlparse(widget['deeplink'])
        sorted_query = dict(sorted(urlparse.parse_qs(deeplink.query).items()))
        deeplink = deeplink._replace(query=urlparse.urlencode(sorted_query))
        widget['deeplink'] = deeplink.geturl()

    request = copy.deepcopy(BASIC_REQUEST)

    exp = load_json('exp3_surge_promotions.json')
    surge_promo_exp = exp['experiments'][0]
    surge_promo_exp['clauses'][0]['value']['surge_threshold'] = surge_threshold
    experiments3.add_experiments_json(exp)

    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=request, headers=PA_HEADERS,
    )
    promos = response.json()['offers']['promoblocks']['items']

    if supported_classes:
        expected_promos = load_json('expected_surge_promo.json')

        assert set(promos[0]['supported_classes']) == set(supported_classes)
        del promos[0]['supported_classes']

        # make same order for GET params
        _normalize_deeplink(promos)
        _normalize_deeplink(expected_promos)

        assert promos == expected_promos
    else:
        assert not promos


@pytest.mark.redis_store(file='redis')
@pytest.mark.translations(
    client_messages=PROMO_CLIENT_MESSAGES, tariff=TARIFF_TRANSLATIONS,
)
async def test_upgraded_tariff_promotions_two_experiments(
        taxi_tariffs_promotions, load_json, experiments3,
):
    expensive_exp = load_json('exp3_upgraded_expensive_tariff_promo.json')
    expensive_exp['experiments'][0]['clauses'][0]['value']['show_rulles'][0][
        'diff_price_percent'
    ] = 20
    experiments3.add_experiments_json(expensive_exp)

    cheaper_exp = load_json('exp3_upgraded_cheaper_tariff_promo.json')
    experiments3.add_experiments_json(cheaper_exp)
    await taxi_tariffs_promotions.invalidate_caches()

    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=BASIC_REQUEST, headers=PA_HEADERS,
    )

    assert response.status_code == 200
    promos = response.json()['offers']['promoblocks']['items']
    assert len(promos) == 2

    vip_promo = promos[0]
    check_tariff_upgrade_promo_base(vip_promo, PromoType.EXPENSIVE)
    check_tariff_upgrade_promo(
        vip_promo, 'econom', 'vip', 10, PromoType.EXPENSIVE, 'RUB',
    )

    comfort_promo = promos[1]
    check_tariff_upgrade_promo_base(comfort_promo, PromoType.CHEAPER)
    check_tariff_upgrade_promo(
        comfort_promo, 'econom', 'business', 10, PromoType.CHEAPER, 'RUB',
    )


@pytest.mark.translations(client_messages=PROMO_CLIENT_MESSAGES, tariff={})
async def test_upgraded_tariff_promotions_no_category_key(
        taxi_tariffs_promotions, load_json, experiments3,
):
    cheaper_exp = load_json('exp3_upgraded_cheaper_tariff_promo.json')
    experiments3.add_experiments_json(cheaper_exp)
    await taxi_tariffs_promotions.invalidate_caches()

    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=BASIC_REQUEST, headers=PA_HEADERS,
    )

    assert response.status_code == 200
    assert not response.json()['offers']['promoblocks']['items']


@pytest.mark.redis_store(file='redis')
@pytest.mark.translations(
    client_messages=PROMO_CLIENT_MESSAGES, tariff=TARIFF_TRANSLATIONS,
)
@pytest.mark.config(TARIFFS_TANKER_KEYS=TARIFFS_TANKER_KEYS)
async def test_category_name_fallback(
        taxi_tariffs_promotions, load_json, experiments3,
):
    cheaper_exp = load_json('exp3_upgraded_cheaper_tariff_promo.json')
    experiments3.add_experiments_json(cheaper_exp)
    await taxi_tariffs_promotions.invalidate_caches()

    request = BASIC_REQUEST.copy()
    del request['state']['nz']
    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=request, headers=PA_HEADERS,
    )

    assert response.status_code == 200
    promos = response.json()['offers']['promoblocks']['items']
    assert len(promos) == 1

    check_tariff_upgrade_promo(
        promos[0], 'econom', 'business', 10, PromoType.CHEAPER, 'RUB',
    )


@pytest.mark.redis_store(file='redis')
@pytest.mark.translations(client_messages=PROMO_CLIENT_MESSAGES)
@pytest.mark.experiments3(filename='exp3_surge_communications.json')
async def test_surge_dialogue(taxi_tariffs_promotions, redis_store, load_json):
    request = BASIC_REQUEST.copy()
    request['supported_configurations'] = ['dialogue']
    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=request, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    promos = response.json()['offers']['promoblocks']['items']
    expected_promos = load_json('expected_surge_dialogue.json')

    assert len(promos) == 2
    assert promos == expected_promos


@pytest.mark.redis_store(file='redis')
@pytest.mark.translations(client_messages=PROMO_CLIENT_MESSAGES)
@pytest.mark.experiments3(filename='exp3_driver_funded_discount_promo.json')
async def test_driver_funded_discount(
        taxi_tariffs_promotions, redis_store, load_json,
):
    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    promos = response.json()['offers']['promoblocks']['items']
    expected_promos = load_json('expected_driver_funded_discount_promo.json')

    assert len(promos) == 1
    assert promos == expected_promos


@pytest.mark.redis_store(file='redis')
@pytest.mark.translations(client_messages=PROMO_CLIENT_MESSAGES)
@pytest.mark.experiments3(filename='exp3_perfect_chain_promo.json')
async def test_perfect_chain_promo(
        taxi_tariffs_promotions, redis_store, load_json,
):
    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    promos = response.json()['offers']['promoblocks']['items']
    expected_promos = load_json('expected_perfect_chain_promo.json')

    assert len(promos) == 1
    assert promos == expected_promos


@pytest.mark.translations(
    client_messages=PROMO_CLIENT_MESSAGES, tariff=TARIFF_TRANSLATIONS,
)
@pytest.mark.parametrize(
    (
        'seconds',
        'min_diff_seconds',
        'expected_promo_tariffs',
        'expected_supported_classes',
        'expected_minutes_details',
    ),
    (
        pytest.param(
            {'econom': 120, 'business': 320},
            120,
            [],
            [],
            [],
            id='get_one_zero_promo',
        ),
        pytest.param(
            {'econom': 320, 'business': 120},
            120,
            ['business'],
            ['econom'],
            [3],
            id='get_one_faster_promo',
        ),
        pytest.param(
            {'econom': 360, 'business': 240, 'vip': 180},
            60,
            ['business', 'vip'],
            ['econom', 'business'],
            [2, 1],
            id='get_two_faster_promo',
        ),
    ),
)
async def test_upgraded_faster_tariff_promotions(
        taxi_tariffs_promotions,
        redis_store,
        load_json,
        experiments3,
        seconds,
        min_diff_seconds,
        expected_promo_tariffs,
        expected_supported_classes,
        expected_minutes_details,
):
    exp = load_json('exp3_upgraded_faster_tariff_promo.json')
    exp['experiments'][0]['clauses'][0]['value']['show_rules'][0][
        'min_diff_seconds'
    ] = min_diff_seconds
    experiments3.add_experiments_json(exp)
    await taxi_tariffs_promotions.invalidate_caches()

    redis_store.set(
        'offer:offer_id',
        json.dumps(
            {'currency': 'RUB', 'categories': seconds_to_categories(seconds)},
        ),
    )

    response = await taxi_tariffs_promotions.post(
        'v1/price-promotions', json=BASIC_REQUEST, headers=PA_HEADERS,
    )

    assert response.status_code == 200
    promos = response.json()['offers']['promoblocks']['items']

    assert len(promos) == len(expected_promo_tariffs)
    promo_map = {}
    for promo in promos:
        check_tariff_upgrade_promo_base(promo, PromoType.FASTER)
        promo_map[promo['supported_classes'][0]] = promo

    for i, tariff in enumerate(expected_supported_classes):
        check_tariff_faster_upgrade(
            promo_map[tariff],
            tariff,
            expected_promo_tariffs[i],
            expected_minutes_details[i],
        )
