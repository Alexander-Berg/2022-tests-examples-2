import datetime

import pytest


BASIC_ORDER_INFO = {
    'currency_rules': {'code': 'RUB', 'sign': '', 'template': '', 'text': ''},
    'dont_call': True,
    'calc': {'time': 2254.0},
    'dont_sms': True,
    'driver': {
        'color': 'white',
        'color_code': 'FAFBFB',
        'plates': 'Н832ТР750',
        'model': 'Kia Optima',
        'phone_personal_id': 'e06756a1756a42368827165a39cd76b9',
    },
    'final_cost_as_str': '1,365 RUB',
    'payment': {
        'type': 'corp',
        'payment_method_id': 'corp-89c43fa2faab4518849ae29fdc25926d',
    },
    'tariff': {'class': 'comfortplus'},
    'request': {
        'comment': 'hello, world',
        'due': '2019-09-10T03:30:00+0000',
        'requirements': {'childchair': [3, 7], 'yellowcarnumber': True},
        'route': [
            {
                'city': 'Москва',
                'country': 'Россия',
                'description': 'Москва, Россия',
                'full_text': 'Россия, Москва, Варшавское шоссе, 141Ак3',
                'fullname': 'Россия, Москва, Варшавское шоссе, 141Ак3',
                'geopoint': [37.6033129823981, 55.58462105024274],
                'house': '141Ак3',
                'locality': 'Москва',
                'metrica_action': 'auto',
                'metrica_method': 'suggest',
                'object_type': 'другое',
                'point': [37.6033129823981, 55.58462105024274],
                'premisenumber': '141Ак3',
                'short_text': 'Варшавское шоссе, 141Ак3',
                'short_text_from': 'Варшавское шоссе, 141Ак3',
                'short_text_to': 'Варшавское шоссе, 141Ак3',
                'street': 'Варшавское шоссе',
                'thoroughfare': 'Варшавское шоссе',
                'type': 'address',
                'uris': [
                    'ymapsbm1://geo?ll=37.603%2C55.585&spn=0.001%2C0.001&'
                    'text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C'
                    '%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%92%D0%B0%D1'
                    '%80%D1%88%D0%B0%D0%B2%D1%81%D0%BA%D0%BE%D0%B5%20'
                    '%D1%88%D0%BE%D1%81%D1%81%D0%B5%2C%20141%D0%90%D0%BA3',
                ],
            },
            {
                'city': 'Москва',
                'country': 'Россия',
                'description': 'Ратная ул., 10, корп. 2, Москва, Россия',
                'full_text': (
                    'Россия, Москва, Ратная улица, 10к2, Гостевой дом АБ'
                ),
                'fullname': (
                    'Россия, Москва, Ратная улица, 10к2, Гостевой дом АБ'
                ),
                'geopoint': [37.577488, 55.57581],
                'house': '10, корп. 2',
                'locality': 'Москва',
                'metrica_method': 'expecteddestinations',
                'object_type': 'организация',
                'oid': '27619391639',
                'point': [37.577488, 55.57581],
                'premisenumber': '10, корп. 2',
                'short_text': 'Ратная улица, 10к2',
                'short_text_from': 'Ратная улица, 10к2',
                'short_text_to': 'Ратная улица, 10к2',
                'street': 'Ратная улица',
                'thoroughfare': 'Ратная улица',
                'title': 'Гостевой дом АБ',
                'type': 'organization',
                'uris': ['ymapsbm1://org?oid=27619391639'],
            },
            {
                'city': 'городской округ Домодедово',
                'country': 'Россия',
                'description': (
                    'городской округ Домодедово, ' 'Московская область, Россия'
                ),
                'full_text': (
                    'Россия, городской округ Домодедово, '
                    'аэропорт Домодедово, A1'
                ),
                'fullname': (
                    'Россия, городской округ Домодедово, '
                    'аэропорт Домодедово, A1'
                ),
                'geopoint': [37.90122349909804, 55.41550288485747],
                'house': '1',
                'locality': 'городской округ Домодедово',
                'metrica_action': 'addressCorrection',
                'metrica_method': 'suggest',
                'object_type': 'аэропорт',
                'point': [37.90122349909804, 55.41550288485747],
                'premisenumber': '1',
                'short_text': 'аэропорт Домодедово, A1',
                'short_text_from': 'аэропорт Домодедово, A1',
                'short_text_to': 'аэропорт Домодедово, A1',
                'street': '',
                'thoroughfare': '',
                'type': 'address',
                'uris': ['ytpp://Москва Домодедово/Столб А1'],
            },
        ],
    },
    'status': 'complete',
    'version': 'DAAAAAAABgAMAAQABgAAAApngRltAQAA',
    'private_data': {
        'user_phone_id': '57112ed0a8e87ce2f540d5b9',
        'extra_user_phone_id': '539e9a23e7e5b1f5397aefb0',
        'driver_id': (
            '5c94a6e5cb04454ba554670101982f72_'
            'ac933fe4a9ba4c138689756108d0c922'
        ),
        'cargo_ref_id': 'cargo_claims_entity_1',
        'order_route_info': {'distance': 40566, 'time': 2254},
        'sp': 1.0,
        'nz': 'moscow',
        'classes': ['comfortplus'],
        'fixed_price': 1365.0,
        'status_updates': [
            {
                'created': '2019-09-10T03:23:36.251+0000',
                'reason': 'create',
                'status': 'pending',
            },
            {
                'created': '2019-09-10T03:23:37.733+0000',
                'reason': 'new_driver_found',
            },
            {'created': '2019-09-10T03:23:39.575+0000', 'reason': 'seen'},
            {
                'created': '2019-09-10T03:23:41.679+0000',
                'reason': 'requestconfirm_assigned',
                'status': 'assigned',
            },
            {
                'created': '2019-09-10T03:23:41.679+0000',
                'reason': 'requestconfirm_driving',
            },
            {
                'created': '2019-09-10T03:26:59.385+0000',
                'reason': 'requestconfirm_waiting',
            },
            {
                'created': '2019-09-10T03:28:30.165+0000',
                'reason': 'requestconfirm_transporting',
            },
            {
                'created': '2019-09-10T04:12:21.55+0000',
                'reason': 'requestconfirm_complete',
                'status': 'finished',
            },
        ],
    },
    'rsk': '8dc3ecf12b2948653cc8d056a2b6b18c',
}


@pytest.mark.translations(color={'FAFBFB': {'en': 'white'}})
async def test_order_info_basic(taxi_order_core, mongodb):
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    user_id = '10d258597b033d1b0560056b4a42b930'
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=60'
    response = response.json()
    assert response == BASIC_ORDER_INFO


@pytest.mark.translations(color={'FAFBFB': {'en': 'white'}})
async def test_order_info_alternative_type(taxi_order_core, mongodb):
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    user_id = '10d258597b033d1b0560056b4a42b930'
    mongodb.order_proc.update(
        {'_id': order_id},
        {'$set': {'order.calc.alternative_type': 'combo_inner'}},
    )
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=60'
    response = response.json()
    calc = response.get('calc')
    assert calc
    assert calc.get('alternative_type', '') == 'combo_inner'


@pytest.mark.translations(color={'FAFBFB': {'en': 'white'}})
async def test_order_info_user_fraud(taxi_order_core, mongodb):
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    user_id = '10d258597b033d1b0560056b4a42b930'
    mongodb.order_proc.update(
        {'_id': order_id}, {'$set': {'order.user_fraud': True}},
    )
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=60'
    response = response.json()
    assert 'private_data' in response
    assert 'user_fraud' in response['private_data']
    assert response['private_data']['user_fraud']


@pytest.mark.translations(color={'FAFBFB': {'en': 'white'}})
async def test_order_info_early_hold(taxi_order_core, mongodb):
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    user_id = '10d258597b033d1b0560056b4a42b930'
    mongodb.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'payment_tech.early_hold': True,
                'payment_tech.cancelled_by_early_hold': True,
            },
        },
    )
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=60'
    response = response.json()
    assert 'private_data' in response
    assert response['private_data']['early_hold']
    assert response['private_data']['cancelled_by_early_hold']


async def test_order_info_missing_color_localization(taxi_order_core, mongodb):
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    user_id = '10d258597b033d1b0560056b4a42b930'
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['driver'] == {
        'color_code': 'FAFBFB',
        'plates': 'Н832ТР750',
        'model': 'Kia Optima',
        'phone_personal_id': 'e06756a1756a42368827165a39cd76b9',
    }


@pytest.mark.parametrize('locale,color', [('en', 'white'), ('ru', 'белый')])
@pytest.mark.translations(color={'FAFBFB': {'en': 'white', 'ru': 'белый'}})
async def test_order_info_request_language(
        taxi_order_core, mongodb, locale, color,
):
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    user_id = '10d258597b033d1b0560056b4a42b930'
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': locale},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['driver'] == {
        'color': color,
        'color_code': 'FAFBFB',
        'plates': 'Н832ТР750',
        'model': 'Kia Optima',
        'phone_personal_id': 'e06756a1756a42368827165a39cd76b9',
    }


async def test_order_info_missing_source_and_destination(
        taxi_order_core, mongodb,
):
    order_id = 'ce15bd13051c1f058e23f5be666dd513'
    user_id = 'f9f4550333261a5c23ef991379da14cb'
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['request']['route'] == [
        {
            'city': 'Московская область',
            'country': 'Россия',
            'description': 'Московская область, Россия',
            'full_text': (
                'Россия, Московская область, аэропорт Шереметьево имени А.С. '
                'Пушкина'
            ),
            'fullname': (
                'Россия, Московская область, аэропорт Шереметьево имени А.С. '
                'Пушкина'
            ),
            'geopoint': [37.41014180510618, 55.9616344873503],
            'house': '',
            'locality': 'Московская область',
            'metrica_action': 'manual',
            'metrica_method': 'suggest.pin_drop',
            'object_type': 'аэропорт',
            'point': [37.41014180510618, 55.9616344873503],
            'premisenumber': '',
            'short_text': 'аэропорт Шереметьево имени А.С. Пушкина',
            'short_text_from': 'аэропорт Шереметьево имени А.С. Пушкина',
            'short_text_to': 'аэропорт Шереметьево имени А.С. Пушкина',
            'street': 'аэропорт Шереметьево имени А.С. Пушкина',
            'thoroughfare': 'аэропорт Шереметьево имени А.С. Пушкина',
            'type': 'address',
            'uris': [],
        },
        {
            'city': 'Москва',
            'country': 'Россия',
            'description': 'Москва, Россия',
            'full_text': 'Россия, Москва, Кочновский проезд, 4к1',
            'fullname': 'Россия, Москва, Кочновский проезд, 4к1',
            'geopoint': [37.542994, 55.806616],
            'house': '4к1',
            'locality': 'Москва',
            'metrica_action': 'addressCorrection',
            'metrica_method': 'suggest.finalize',
            'object_type': 'другое',
            'point': [37.542994, 55.806616],
            'premisenumber': '4к1',
            'short_text': 'Кочновский проезд, 4к1',
            'short_text_from': 'Кочновский проезд, 4к1',
            'short_text_to': 'Кочновский проезд, 4к1',
            'street': 'Кочновский проезд',
            'thoroughfare': 'Кочновский проезд',
            'type': 'address',
            'uris': [],
        },
    ]


async def test_order_info_missing_optional_candidate_fields(
        taxi_order_core, mongodb,
):
    order_id = '0b0ef3c5398b3e07b59f03110563479d'
    user_id = '20d258597b033d1b0560056b4a42b930'
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['driver'] == {'plates': 'Н832ТР751', 'model': ''}


async def test_expired_no_performer(taxi_order_core):
    order_id = 'bfda5489e2215d599abc840fd8f56a76'
    user_id = '26de812c570b5c6260b9320a4707c769'
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['status'] == 'expired'


@pytest.mark.parametrize(
    'user_id,yandex_uid,enabled,expected_code',
    [
        ('26de812c570b5c6260b9320a4707c769', '4030364364', True, 200),
        ('26de812c570b5c6260b9320a4707c769', '4000000000', True, 404),
        ('26de812c570b5c6260b9320a4707c769', '4030364364', False, 200),
        ('26de812c570b5c6260b9320a4707c769', '4000000000', False, 200),
        ('26de812c570b5c6260b9320a4707c769', '4030364364', False, 200),
        ('00000000000000000000000000000009', '4030364364', True, 200),
        ('00000000000000000000000000000009', '4030364364', False, 404),
        ('00000000000000000000000000000009', '4000000000', True, 404),
        ('26de812c570b5c6260b9320a4707c769', None, True, 200),
        ('26de812c570b5c6260b9320a4707c769', None, False, 200),
        ('00000000000000000000000000000009', None, True, 404),
        ('00000000000000000000000000000009', None, False, 404),
    ],
)
async def test_multidevice(
        taxi_order_core,
        user_id,
        yandex_uid,
        enabled,
        expected_code,
        taxi_config,
        order_archive_mock,
):
    order_id = 'bfda5489e2215d599abc840fd8f56a76'
    taxi_config.set(CROSSDEVICE_ENABLED=enabled)
    headers = {'X-Request-Language': 'en'}
    if yandex_uid is not None:
        headers['X-Yandex-Uid'] = yandex_uid
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers=headers,
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'version, fetch_result_tag, mongo_requests_count',
    [
        (None, 'no_version', 1),
        ('blah', 'no_version', 1),
        # version taken from order_proc
        ('DAAAAAAABgAMAAQABgAAAApngRltAQAA', 'ok', 1),
        # version taken from prod for 2019-10-29
        ('DAAAAAAABgAMAAQABgAAAEIvXBduAQAA', 'laggy_secondary', 2),
    ],
)
async def test_secondary(
        taxi_order_core,
        testpoint,
        version,
        fetch_result_tag,
        mongo_requests_count,
):
    order_id = 'bfda5489e2215d599abc840fd8f56a76'
    user_id = '26de812c570b5c6260b9320a4707c769'

    @testpoint('proc-fetch-result')
    def _testpoint_fetch_result(data):
        assert data == fetch_result_tag

    @testpoint('proc-fetch')
    def testpoint_mongo_call(data):
        pass

    params = {'orderid': order_id, 'userid': user_id}
    if version is not None:
        params['version'] = version
    result = await taxi_order_core.get(
        '/v1/tc/order-info',
        params=params,
        headers={'X-Request-Language': 'en'},
    )
    assert result.status_code == 200

    assert testpoint_mongo_call.times_called == mongo_requests_count


@pytest.mark.parametrize(
    'with_current_prices, kind, with_coupon, expected_price',
    [
        (False, '', False, '1,365 RUB'),
        (False, '', True, '1,365 RUB without coupon'),
        (True, 'fixed', False, '1,365 RUB'),  # wrong kind
        (True, 'fixed', True, '1,365 RUB without coupon'),  # wrong kind
        (True, 'final_cost', False, '2,000 RUB'),
        (
            True,
            'final_cost',
            True,
            '2,000 RUB',
        ),  # current prices include coupon
    ],
    ids=(
        'order.cost, no coupon',
        'order.cost, with coupon',
        'current prices, wrong kind, no coupon',
        'current prices, wrong kind, with coupon',
        'current prices, no coupon',
        'current prices, with coupon',
    ),
)
async def test_order_info_final_cost(
        taxi_order_core,
        mongodb,
        with_current_prices,
        kind,
        with_coupon,
        expected_price,
):
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    user_id = '10d258597b033d1b0560056b4a42b930'
    mongodb.order_proc.update(
        {'_id': order_id, 'order_info.with_coupon': False},
        {'$set': {'order_info.with_coupon': with_coupon}},
    )
    if with_current_prices:
        current_prices_upd = {
            'kind': kind,
            'user_ride_display_price': 777,
            'user_total_display_price': 2000,
            'user_total_price': 100500,
        }
        mongodb.order_proc.update(
            {'_id': order_id},
            {'$set': {'order.current_prices': current_prices_upd}},
        )

    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response.get('final_cost_as_str') == expected_price


def currency_formatting_rules_rub(precision: int) -> dict:
    return {'RUB': {'__default__': precision}}


@pytest.mark.parametrize(
    'formatting_config, expected_price',
    [
        (currency_formatting_rules_rub(0), '1,001 RUB'),
        (currency_formatting_rules_rub(2), '1,000.99 RUB'),
        (currency_formatting_rules_rub(3), '1,000.987 RUB'),
        (currency_formatting_rules_rub(2 ** 31 - 1), '1,000.987 RUB'),
        # fallback to precision 2 for an invalid config
        ({}, '1,000.99 RUB'),
        ({'RUB': {}}, '1,000.99 RUB'),
    ],
)
async def test_order_info_final_cost_formatting(
        taxi_order_core, taxi_config, formatting_config, expected_price,
):
    taxi_config.set(CURRENCY_FORMATTING_RULES=formatting_config)
    order_id = 'order_for_testing_final_cost_as_str'
    user_id = '10d258597b033d1b0560056b4a42b930'

    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response.get('final_cost_as_str') == expected_price


async def test_order_info_with_complements(taxi_order_core):
    order_id = 'order_with_complements'
    user_id = '10d258597b033d1b0560056b4a42b930'

    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response['private_data']['complements']) == 1
    assert response['private_data']['complements'][0] == {
        'type': 'personal_wallet',
        'payment_method_id': 'w/5670-27987af-8346ca95-349b',
    }
    assert response['private_data']['current_prices'] == {
        'user_total_price': 1001,
        'user_total_display_price': 1001,
        'user_ride_display_price': 1001,
        'kind': 'final_cost',
        'cost_breakdown': [
            {'type': 'personal_wallet', 'amount': 100},
            {'type': 'card', 'amount': 901},
        ],
    }


async def test_order_info_with_cashback(taxi_order_core):
    order_id = 'order_with_cashback'
    user_id = '10d258597b033d1b0560056b4a42b930'

    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert 'complements' not in response['private_data']
    assert response['private_data']['current_prices'] == {
        'user_total_price': 1001,
        'user_total_display_price': 1001,
        'user_ride_display_price': 777,
        'cashback_price': 100,
        'discount_cashback': 12,
        'possible_cashback': 20,
        'kind': 'final_cost',
        'cashback_by_sponsor': {'sponsor': '0.01'},
        'alt_offer_final_discount': 40,
        'currency': 'RUB',
        'current_cost_meta': {'user': {'waiting_price': 35}},
    }
    assert response['extra_data']['is_possible_cashback'] is True


async def test_order_info_with_extra_data_without_field_cashback(
        taxi_order_core,
):
    order_id = 'order_with_complements'
    user_id = '10d258597b033d1b0560056b4a42b930'

    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json()['extra_data'] == {}


@pytest.mark.parametrize(
    'order_archived,archive_called', [(True, 1), (False, 0)],
)
@pytest.mark.translations(color={'FAFBFB': {'en': 'white'}})
async def test_archive(
        taxi_order_core,
        testpoint,
        mongodb,
        order_archive_mock,
        order_archived,
        archive_called,
):
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    user_id = '10d258597b033d1b0560056b4a42b930'

    @testpoint('archive-fetch')
    def testpoint_archive_call(data):
        pass

    if order_archived:
        proc = mongodb.order_proc.find_one({'_id': order_id})
        order_archive_mock.set_order_proc(proc)
        mongodb.order_proc.delete_one({'_id': order_id})

    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response == BASIC_ORDER_INFO

    assert testpoint_archive_call.times_called == archive_called


@pytest.mark.parametrize(
    'check_in_state, dispatch_check_in_etalon',
    [
        ({'dispatch_check_in.check_in_time': None}, {}),
        (
            {
                'dispatch_check_in.check_in_time': datetime.datetime(
                    2020, 7, 7, 0, 0, 0,
                ),
                'dispatch_check_in.pickup_line': 'svo_d_line1',
            },
            {
                'check_in_time': '2020-07-07T00:00:00+0000',
                'pickup_line': 'svo_d_line1',
            },
        ),
        (None, None),
    ],
)
@pytest.mark.translations(color={'FAFBFB': {'en': 'white'}})
async def test_order_info_dispatch_check_in(
        taxi_order_core, mongodb, check_in_state, dispatch_check_in_etalon,
):
    user_id = '10d258597b033d1b0560056b4a42b930'
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    if check_in_state is not None:
        mongodb.order_proc.update({'_id': order_id}, {'$set': check_in_state})
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()

    etalon_source_uris = [
        'ymapsbm1://geo?ll=37.603%2C55.585&spn=0.001%2C0.001&'
        'text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C'
        '%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%92%D0%B0%D1'
        '%80%D1%88%D0%B0%D0%B2%D1%81%D0%BA%D0%BE%D0%B5%20'
        '%D1%88%D0%BE%D1%81%D1%81%D0%B5%2C%20141%D0%90%D0%BA3',
    ]

    assert response.get('dispatch_check_in') == dispatch_check_in_etalon
    assert response['request']['route'][0]['uris'] == etalon_source_uris


@pytest.mark.translations(color={'FAFBFB': {'en': 'white'}})
@pytest.mark.parametrize(
    'proc_update, etalon',
    [
        # Case 1: auction active, price change allowed, fixed price
        (
            {
                'auction.iteration': 1,
                'auction.prepared': True,
                'auction.price.current': 100,
                'auction.price.base': 50,
                'auction.allowed_price_change.fixed_steps.step': 10,
                'auction.allowed_price_change.fixed_steps.max_steps': 3,
                'driver_bids': {
                    'min_price': 10.50,
                    'max_price': 100.00,
                    'price_options': [20.00, 30.00],
                },
            },
            {
                'is_fixed_price': True,
                'current_price': 100.0,
                'prepared': True,
                'iteration': 1,
                'allowed_price_change': {
                    'fixed_steps': {'max_steps': 3, 'step': 10.0},
                },
            },
        ),
        # Case 2: auction active, price change not allowed, fixed price
        (
            {
                'auction.iteration': 1,
                'auction.prepared': True,
                'auction.price.current': 100,
                'auction.price.base': 50,
            },
            {
                'is_fixed_price': True,
                'current_price': 100.0,
                'iteration': 1,
                'prepared': True,
            },
        ),
        # Case 3: auction active, price change not allowed, not fixed price
        (
            {
                'auction.iteration': 1,
                'auction.prepared': True,
                'auction.price.current': 100,
                'auction.price.base': 50,
                'order.fixed_price.price': None,
            },
            {
                'is_fixed_price': False,
                'current_price': 50.0,
                'iteration': 1,
                'prepared': True,
            },
        ),
        # Case 4: auction enabled, but not active yet
        (
            {'auction.iteration': 1, 'auction.prepared': False},
            {'is_fixed_price': True, 'iteration': 1, 'prepared': False},
        ),
        # Case 5: auction disabled
        (None, None),
    ],
)
async def test_order_info_auction(
        taxi_order_core, mongodb, proc_update, etalon,
):
    user_id = '10d258597b033d1b0560056b4a42b930'
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    if proc_update is not None:
        mongodb.order_proc.update({'_id': order_id}, {'$set': proc_update})
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()

    assert response.get('auction') == etalon
    if proc_update and 'driver_bids' in proc_update:
        assert response['driver_bids'] == {'enabled': True}


@pytest.mark.parametrize(
    'autoreorder_reason,etalon',
    [
        # Case 1: one autoreorder
        (
            {
                'autoreorder.decisions': {
                    'created': datetime.datetime(2020, 1, 1, 1, 1, 1),
                    'reason': 'eta-autoreorder',
                },
            },
            'eta-autoreorder',
        ),
        # Case 2: two autoreorders
        (
            {
                'autoreorder.decisions': {
                    '$each': [
                        {
                            'created': datetime.datetime(2020, 1, 1, 1, 1, 1),
                            'reason': 'wrong reason',
                        },
                        {
                            'created': datetime.datetime(2020, 1, 1, 1, 2, 1),
                            'reason': 'eta-autoreorder',
                        },
                    ],
                },
            },
            'eta-autoreorder',
        ),
        # Case 3: no autoreorder
        (None, None),
    ],
)
async def test_order_info_autoreorder_reason(
        taxi_order_core, mongodb, autoreorder_reason, etalon,
):
    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    user_id = '10d258597b033d1b0560056b4a42b930'
    if autoreorder_reason is not None:
        mongodb.order_proc.update(
            {'_id': order_id}, {'$push': autoreorder_reason},
        )
    response = await taxi_order_core.get(
        '/v1/tc/order-info',
        params={'orderid': order_id, 'userid': user_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response.get('autoreorder_reason') == etalon
