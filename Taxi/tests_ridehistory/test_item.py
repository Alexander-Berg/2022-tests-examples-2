# pylint: disable=too-many-lines

import copy

import pytest


DEFAULT_RECEIPT_SETTINGS = {
    'show_trust_receipt_countries': ['rus'],
    'show_fetched_receipt_countries': ['kaz'],
    'show_trust_receipt_payment_methods': [
        'card',
        'applepay',
        'googlepay',
        'coop_account',
    ],
    'trust_receipt_url_tmpl': (
        'https://trust.yandex.ru/receipts/{order_id}/'
        '#receipt_url_pdf='
        'https://trust.yandex.ru/receipts/{order_id}/?mode=pdf'
    ),
    'check_url_tmpl': (
        'https://check.yandex.ru/mobile/?n={n}&fn={fn}&fpd={fpd}'
        '#receipt_url_pdf='
        'https://check.yandex.ru/pdf/?n={n}&fn={fn}&fpd={fpd}'
    ),
    'show_partial_receipts': True,
}


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'order_id, request_extra, order_core_times_called, '
    'transactions_times_called, yt_times_called, admin_images_fname, '
    'expected_yt_request, expected_resp, expected_status_code',
    [
        ('1', {}, 1, 1, 0, None, None, 'expected_resp_simple_1.json', 200),
        (
            '1',
            {'settings': {'format_currency': False}},
            1,
            1,
            0,
            None,
            None,
            'expected_resp_format_currency.json',
            200,
        ),
        (
            '1',
            {'image_tags': {'skin_version': '4'}},
            1,
            1,
            0,
            'admin_images_list_4.json',
            None,
            'expected_resp_image_tags.json',
            200,
        ),
        (
            '1',
            {'image_tags': {'skin_version': '4'}},
            1,
            1,
            0,
            'admin_images_list_empty.json',
            None,
            'expected_resp_image_tags_empty.json',
            200,
        ),
        (
            '2',
            {},
            0,
            0,
            1,
            None,
            'expected_yt_request_simple_2',
            'expected_resp_simple_2.json',
            200,
        ),
        (
            '1',
            {'settings': {'include_hidden_orders': True}},
            1,
            1,
            0,
            None,
            None,
            'expected_resp_simple_1.json',
            200,
        ),
        (
            '2',
            {'settings': {'include_hidden_orders': True}},
            0,
            0,
            1,
            None,
            'expected_yt_request_simple_2_include_hidden',
            'expected_resp_simple_2.json',
            200,
        ),
        (
            '3',
            {'settings': {'include_hidden_orders': True}},
            1,
            1,
            0,
            None,
            None,
            'expected_resp_simple_3_pg.json',
            200,
        ),
        ('3', {}, 0, 0, 0, None, None, None, 404),
        ('4', {}, 0, 0, 0, None, None, None, 404),
        (
            '5',
            {'settings': {'include_hidden_orders': True}},
            0,
            0,
            1,
            None,
            'expected_yt_request_simple_5',
            None,
            404,
        ),
    ],
)
async def test_simple(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        mock_admin_images_custom,
        order_id,
        order_core_times_called,
        transactions_times_called,
        yt_times_called,
        admin_images_fname,
        expected_yt_request,
        expected_resp,
        expected_status_code,
        request_extra,
):
    if admin_images_fname is not None:
        mock_admin_images_custom(admin_images_fname)
        await taxi_ridehistory.invalidate_caches()

    yt_mock = mock_yt_queries(expected_yt_request)
    order_core_mock = mock_order_core_query(
        [order_id], 'order_core_resp_simple', True,
    )
    transactions_mock = mock_transactions_query(
        [order_id], 'transactions_resp_simple',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek', 'saratov'])
    driver_profiles_mock = mock_driver_profiles('driver_profiles.json')
    parks_replica_mock = mock_parks_replica('parks.json', True)
    personal_phones_mock = mock_personal_phones('personal_phones.json')
    mock_territories(True)

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    request_json = {'check_permissions': False, 'order_id': order_id}
    request_json.update(request_extra)

    response = await taxi_ridehistory.post(
        'v2/item',
        json=request_json,
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == expected_status_code

    if expected_resp is not None:
        assert response.json() == load_json(expected_resp)
        assert taxi_tariffs_mock.times_called == 1
        assert driver_profiles_mock.times_called == 1
        assert parks_replica_mock.times_called == 1
        assert personal_phones_mock.times_called == 1

    assert yt_mock.times_called == yt_times_called
    assert order_core_mock.times_called == order_core_times_called
    assert transactions_mock.times_called == transactions_times_called


@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    [
        'order_id',
        'request_uid',
        'request_phone_id',
        'should_pass',
        'expected_yt_request',
    ],
    [
        pytest.param(
            '1',
            'nonexistent',
            '777777777777777777777777',
            True,
            None,
            marks=pytest.mark.now('2017-09-09T00:00:00+0300'),
        ),
        pytest.param(
            '1',
            '12345',
            'nonexistent',
            True,
            None,
            marks=pytest.mark.now('2021-09-09T00:00:00+0300'),
        ),
        pytest.param(
            '1',
            'nonexistent',
            'nonexistent',
            False,
            None,
            marks=pytest.mark.now('2017-09-09T00:00:00+0300'),
        ),
        pytest.param(
            '1',
            'nonexistent',
            '777777777777777777777777',
            False,
            None,
            marks=pytest.mark.now('2021-09-09T00:00:00+0300'),
        ),
        pytest.param(
            '2',
            '12345',
            '777777777777777777777777',
            True,
            'expected_yt_request_permissions_no_uid',
            marks=pytest.mark.now('2017-09-09T00:00:00+0300'),
        ),
        pytest.param(
            '2',
            '12345',
            'nonexistent',
            True,
            'expected_yt_request_permissions',
            marks=pytest.mark.now('2021-09-09T00:00:00+0300'),
        ),
        pytest.param(
            '2',
            '12345',
            '777777777777777777777777',
            False,
            'expected_yt_request_permissions_no_uid',
            marks=pytest.mark.now('2021-09-09T00:00:00+0300'),
        ),
        pytest.param(
            '2',
            '12345',
            'nonexistent',
            False,
            'expected_yt_request_permissions_no_uid',
            marks=pytest.mark.now('2017-09-09T00:00:00+0300'),
        ),
    ],
)
@pytest.mark.parametrize('check_permissions', [True, False])
async def test_check_permissions(
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        order_id,
        request_uid,
        request_phone_id,
        should_pass,
        expected_yt_request,
        check_permissions,
):
    yt_mock = mock_yt_queries(expected_yt_request)
    mock_order_core_query(['1'], 'order_core_resp_simple', True)
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')
    mock_territories(True)

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': check_permissions, 'order_id': order_id},
        headers={
            'X-Yandex-UID': request_uid,
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': request_phone_id,
            'X-YaTaxi-Bound-Uids': 'uid4',
        },
    )

    if not check_permissions or should_pass:
        assert response.status == 200
    else:
        assert response.status == 404

    if expected_yt_request is None:
        assert yt_mock.times_called == 0
    elif not check_permissions:
        assert yt_mock.times_called == 1
    else:
        assert yt_mock.times_called == 2


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.translations(
    client_messages={
        'orderhistory.charged': {'ru': '%(CARD_NUMBER)s'},
        'orderhistory.paid_by_coop_account': {
            'ru': 'Семейный аккаунт напрямую из танкера',
        },
        'orderhistory.paid_by_corp': {
            'ru': 'Корпоративный счёт (оплачено с учётом НДС)',
        },
        'orderhistory.paid_by_cash': {'ru': 'Наличные'},
        'orderhistory.paid_by_business_account': {
            'ru': 'Бизнес-аккаунт напрямую из танкера',
        },
        'orderhistory.paid_by': {'ru': '%(PAYMENT_TYPE)s'},
        'orderhistory.paid_by_personal_wallet': {'ru': 'Плюс'},
        'orderhistory.paid_by_yandex_card': {'ru': 'Деньгами Плюса'},
    },
)
@pytest.mark.parametrize(
    [
        'payment_tech',
        'shared_payments_response',
        'cardstorage_down',
        'shared_payments_down',
        'cardstorage_times_called',
        'shared_payments_times_called',
        'expected_payment_method',
    ],
    [
        (
            {'type': 'applepay'},
            None,
            False,
            False,
            0,
            0,
            {'type': 'applepay', 'title': 'Apple Pay'},
        ),
        (
            {'type': 'googlepay'},
            None,
            False,
            False,
            0,
            0,
            {'type': 'googlepay', 'title': 'Google Pay'},
        ),
        (
            {'type': 'cash'},
            None,
            False,
            False,
            0,
            0,
            {'type': 'cash', 'title': 'Наличные'},
        ),
        (
            {'type': 'corp'},
            None,
            False,
            False,
            0,
            0,
            {
                'type': 'corp',
                'title': 'Корпоративный счёт (оплачено с учётом НДС)',
            },
        ),
        ({'type': 'prepaid'}, None, False, False, 0, 0, {'type': 'prepaid'}),
        (
            {'type': 'personal_wallet'},
            None,
            False,
            False,
            0,
            0,
            {'type': 'personal_wallet', 'title': 'Плюс'},
        ),
        (
            {'type': 'card', 'main_card_payment_id': 'card-1234'},
            None,
            False,
            False,
            1,
            0,
            {'type': 'card', 'title': 'VISA 546916****9285', 'system': 'VISA'},
        ),
        (
            {'type': 'card', 'main_card_payment_id': 'card-1234'},
            None,
            True,
            False,
            3,
            0,
            {'type': 'card'},
        ),
        ({'type': 'card'}, None, False, False, 0, 0, {'type': 'card'}),
        (
            {'type': 'coop_account', 'main_card_payment_id': 'family-1234'},
            {
                'type': 'family',
                'details': {'name': 'Семейный аккаунт из shared-payments'},
            },
            False,
            False,
            0,
            1,
            {
                'type': 'coop_account',
                'title': 'Семейный аккаунт из shared-payments',
                'system': 'family',
            },
        ),
        (
            {'type': 'coop_account', 'main_card_payment_id': 'family-1234'},
            {'type': 'family', 'details': {}},
            False,
            False,
            0,
            1,
            {
                'type': 'coop_account',
                'title': 'Семейный аккаунт напрямую из танкера',
                'system': 'family',
            },
        ),
        (
            {'type': 'coop_account', 'main_card_payment_id': 'family-1234'},
            None,
            False,
            True,
            0,
            2,
            {
                'type': 'coop_account',
                'title': 'Семейный аккаунт напрямую из танкера',
                'system': 'family',
            },
        ),
        (
            {'type': 'coop_account', 'main_card_payment_id': 'business-1234'},
            {
                'type': 'business',
                'details': {'name': 'Бизнес-аккаунт из shared-payments'},
            },
            False,
            False,
            0,
            1,
            {
                'type': 'coop_account',
                'title': 'Бизнес-аккаунт из shared-payments',
                'system': 'business',
            },
        ),
        (
            {'type': 'coop_account', 'main_card_payment_id': 'business-1234'},
            {'type': 'business', 'details': {}},
            False,
            False,
            0,
            1,
            {
                'type': 'coop_account',
                'title': 'Бизнес-аккаунт напрямую из танкера',
                'system': 'business',
            },
        ),
        (
            {'type': 'coop_account', 'main_card_payment_id': 'business-1234'},
            None,
            False,
            True,
            0,
            2,
            {
                'type': 'coop_account',
                'title': 'Бизнес-аккаунт напрямую из танкера',
                'system': 'business',
            },
        ),
        (
            {'type': 'coop_account', 'main_card_payment_id': 'other-1234'},
            {
                'type': 'other',
                'details': {'name': 'Ещё какой-то групповой аккаунт'},
            },
            False,
            False,
            0,
            1,
            {'type': 'coop_account'},
        ),
        (
            {'type': 'coop_account', 'main_card_payment_id': 'other-1234'},
            {'type': 'other', 'details': {}},
            False,
            False,
            0,
            1,
            {'type': 'coop_account'},
        ),
        (
            {'type': 'coop_account', 'main_card_payment_id': 'other-1234'},
            None,
            False,
            True,
            0,
            2,
            {'type': 'coop_account'},
        ),
        (
            {'type': 'coop_account'},
            None,
            False,
            False,
            0,
            0,
            {'type': 'coop_account'},
        ),
        (
            {'type': 'nonexistent'},
            None,
            False,
            False,
            0,
            0,
            {'type': 'nonexistent'},
        ),
        (
            {'type': 'yandex_card'},
            None,
            False,
            False,
            0,
            0,
            {'type': 'yandex_card', 'title': 'Деньгами Плюса'},
        ),
    ],
)
@pytest.mark.config(
    CARDSTORAGE_CLIENT_QOS={'__default__': {'attempts': 3, 'timeout-ms': 200}},
)
async def test_payment_method(
        taxi_ridehistory,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_cardstorage,
        mock_shared_payments,
        payment_tech,
        shared_payments_response,
        cardstorage_down,
        shared_payments_down,
        cardstorage_times_called,
        shared_payments_times_called,
        expected_payment_method,
):
    mock_order_core_query(
        ['1'],
        'order_core_resp_simple',
        True,
        {'1': {'payment_tech': payment_tech}},
    )
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')

    cardstorage_mock = mock_cardstorage(
        '12345',
        'card-1234',
        'cardstorage_resp_simple.json',
        error=cardstorage_down,
    )

    shared_payments_mock = mock_shared_payments(
        payment_tech.get('main_card_payment_id'),
        'ru',
        shared_payments_response,
        error=shared_payments_down,
    )

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': '1'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert (
        response.json()['data']['payment']['payment_method']
        == expected_payment_method
    )
    assert cardstorage_mock.times_called == cardstorage_times_called
    assert shared_payments_mock.times_called == shared_payments_times_called


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'order_id, expected_resp',
    [
        ('1', 'expected_resp_cashback_pg.json'),
        ('2', 'expected_resp_cashback_yt.json'),
        ('3', 'expected_resp_cashback_zero_pg.json'),
        ('4', 'expected_resp_cashback_zero_yt.json'),
        ('5', 'expected_resp_cashback_byn_pg.json'),
        ('6', 'expected_resp_cashback_byn_yt.json'),
        pytest.param(
            '1',
            'expected_resp_cashback_pg_current_prices.json',
            marks=[
                pytest.mark.config(
                    RIDEHISTORY_CASHBACK_FROM_CURRENT_PRICES_ENABLED=True,
                ),
            ],
        ),
        pytest.param(
            '2',
            'expected_resp_cashback_yt_current_prices.json',
            marks=[
                pytest.mark.config(
                    RIDEHISTORY_CASHBACK_FROM_CURRENT_PRICES_ENABLED=True,
                ),
            ],
        ),
    ],
)
async def test_cashback(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        order_id,
        expected_resp,
):
    mock_yt_queries('expected_yt_request_cashback')
    mock_order_core_query(['1', '3', '5'], 'order_core_resp_simple', True)
    mock_transactions_query(['1', '3', '5'], 'transactions_resp_cashback')
    mock_taxi_tariffs_query(['bishkek', 'saratov', 'minsk'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': order_id},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert response.json() == load_json(expected_resp)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'order_id, expected_resp', [('1', 'expected_resp_complements_pg.json')],
)
async def test_complements(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        order_id,
        expected_resp,
):
    mock_yt_queries('expected_yt_request_cashback')
    mock_order_core_query(['1'], 'order_core_resp_simple', True)
    mock_transactions_query(['1'], 'transactions_resp_complements')
    mock_taxi_tariffs_query(['bishkek', 'saratov', 'minsk'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': order_id},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert response.json() == load_json(expected_resp)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    [
        'order_id',
        'unique_drivers_resp',
        'driver_ratings_resp',
        'unique_drivers_down',
        'driver_ratings_down',
        'unique_drivers_times_called',
        'driver_ratings_times_called',
        'expected_park_driver_profile_id',
        'expected_unique_driver_id',
        'expected_rating',
        'expected_photo_url',
        'expected_tin',
    ],
    [
        (
            '1',
            {
                'uniques': [
                    {
                        'park_driver_profile_id': 'parkid_driver_uuid',
                        'data': {'unique_driver_id': 'unique_driver_id'},
                    },
                ],
            },
            '777.000',
            False,
            False,
            1,
            1,
            'parkid_driver_uuid',
            'unique_driver_id',
            '777',
            'avatar_url',
            '550012341234',
        ),
        (
            '1',
            {
                'uniques': [
                    {
                        'park_driver_profile_id': 'parkid_driver_uuid',
                        'data': {'unique_driver_id': 'unique_driver_id'},
                    },
                ],
            },
            '5.123',
            False,
            False,
            1,
            1,
            'parkid_driver_uuid',
            'unique_driver_id',
            '5,12',
            'avatar_url',
            '550012341234',
        ),
        (
            '1',
            None,
            None,
            True,
            False,
            3,
            0,
            None,
            None,
            None,
            'avatar_url',
            '550012341234',
        ),
        (
            '1',
            {
                'uniques': [
                    {
                        'park_driver_profile_id': 'parkid_driver_uuid',
                        'data': {'unique_driver_id': 'unique_driver_id'},
                    },
                ],
            },
            None,
            False,
            True,
            1,
            3,
            'parkid_driver_uuid',
            None,
            None,
            'avatar_url',
            '550012341234',
        ),
        (
            '1',
            {'uniques': [{'park_driver_profile_id': 'parkid_driver_uuid'}]},
            None,
            False,
            False,
            1,
            0,
            'parkid_driver_uuid',
            None,
            None,
            'avatar_url',
            '550012341234',
        ),
        (
            '1',
            {'uniques': []},
            None,
            False,
            False,
            1,
            0,
            'parkid_driver_uuid',
            None,
            None,
            'avatar_url',
            '550012341234',
        ),
        (
            'wo_db_id',
            None,
            None,
            False,
            False,
            0,
            0,
            None,
            None,
            None,
            None,
            None,
        ),
    ],
)
async def test_driver_rating_photo_url_tin(
        taxi_ridehistory,
        load_json,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_personal_tins,
        mock_selfemployed,
        mock_unique_drivers,
        mock_driver_ratings,
        mock_udriver_photos,
        order_id,
        unique_drivers_resp,
        driver_ratings_resp,
        unique_drivers_down,
        driver_ratings_down,
        unique_drivers_times_called,
        driver_ratings_times_called,
        expected_park_driver_profile_id,
        expected_unique_driver_id,
        expected_rating,
        expected_photo_url,
        expected_tin,
):
    mock_order_core_query([order_id], 'order_core_resp_driver_rating', True)
    mock_transactions_query([order_id], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')
    mock_udriver_photos([('parkid', 'driver_uuid')])

    unique_drivers_mock = mock_unique_drivers(
        expected_park_driver_profile_id,
        unique_drivers_resp,
        error=unique_drivers_down,
    )

    driver_ratings_mock = mock_driver_ratings(
        expected_unique_driver_id,
        driver_ratings_resp,
        error=driver_ratings_down,
    )

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': order_id},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    data = response.json()['data']
    assert data['driver'].get('rating') == expected_rating
    assert data['driver'].get('photo_url') == expected_photo_url
    assert data['driver'].get('tin') == expected_tin

    assert unique_drivers_mock.times_called == unique_drivers_times_called
    assert driver_ratings_mock.times_called == driver_ratings_times_called


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
async def test_corp(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
):
    mock_order_core_query(['corp'], 'order_core_resp_corp', True)
    mock_transactions_query(['corp'], 'transactions_resp_corp')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': 'corp'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert response.json()['data']['payment'] == {
        'cashback': '3',
        'cost': 6.543,
        'currency_code': 'KGS',
        'final_cost': '6,54\u2006$SIGN$$CURRENCY$',
        'ride_cost': '4,54\u2006$SIGN$$CURRENCY$',
        'tips': '2\u2006$SIGN$$CURRENCY$',
        'payment_method': {'type': 'corp'},
    }


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
async def test_format_cost_fallback(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
):
    mock_order_core_query(['1'], 'order_core_resp_simple', True)
    mock_transactions_query(['1'], 'transactions_resp_cost_fallback')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/item',
        json={
            'check_permissions': False,
            'order_id': '1',
            # causes exception due to nonexistent currency -> cost formatting
            # fallback is called
            'settings': {'format_currency': False},
        },
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    final_cost = response.json()['data']['payment']['final_cost']
    assert final_cost == '7.7 NONEXISTENT'


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize('order_id', ['1', 'some_order'])
async def test_no_destination(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        order_id,
):
    mock_order_core_query([order_id], 'order_core_resp_no_destination', True)
    mock_transactions_query([order_id], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': order_id},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    route = response.json()['data']['route']
    assert route == {
        'source': {
            'point': [37.64295455983948, 55.73485044101388],
            'short_text': 'Начало pg',
        },
        'map_image': (
            'https://tc.mobile.yandex.net/get-map/1.x/?l=map&size=800,400'
            '&cr=0&lg=0&scale=1.4&lang=ru&pt=37.642955,55.734850,'
            'comma_solid_red'
        ),
        'destinations': [],
    }


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_charity_tips.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'order_id, expected_yt_request, expected_pp_times_called',
    [
        ('charity_no_tips_transactions', None, 1),
        ('no_charity_tips_transactions', None, 1),
        ('charity_tips_transactions', None, 1),
        ('charity_no_tips_corp', None, 1),
        ('no_charity_tips_corp', None, 1),
        ('charity_tips_corp', None, 1),
        ('charity_no_tips_yt', 'expected_yt_request_charity_no_tips', 0),
        ('no_charity_tips_yt', 'expected_yt_request_no_charity_tips', 0),
        ('charity_tips_yt', 'expected_yt_request_charity_tips', 0),
    ],
)
async def test_charity_tips(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_persey_payments,
        order_id,
        expected_yt_request,
        expected_pp_times_called,
):
    mock_yt_queries(expected_yt_request)
    mock_order_core_query([order_id], 'order_core_resp_charity_tips', True)
    mock_transactions_query([order_id], 'transactions_resp_charity_tips')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    persey_payments_mock = mock_persey_payments(
        [order_id], 'persey_payments_resp_charity_tips.json',
    )

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': order_id},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert persey_payments_mock.times_called == expected_pp_times_called


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
async def test_map_image(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_trackstory,
):
    mock_order_core_query(['1'], 'order_core_resp_simple', True)
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    trackstory_mock = mock_driver_trackstory(
        'expected_trackstory_request.json', 'trackstory_response.json',
    )

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': '1'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert response.json()['data']['route']['map_image'] == (
        'https://tc.mobile.yandex.net/get-map/1.x/?l=map&size=800,400'
        '&cr=0&lg=0&scale=1.4&lang=ru&pt=37.642955,55.734850,'
        'comma_solid_red~37.666000,55.777000,trackpoint~37.642641,55.735877,'
        'comma_solid_blue&pl=c:3C3C3CFF,w:6,37.591126,55.732636,37.590900,'
        '55.731300,37.585900,55.729400&'
        'bbox=37.579492,55.727496~37.672408,55.786520'
    )
    assert response.json()['data']['route']['track'] == [
        [37.591126, 55.732636],
        [37.5909, 55.7313],
        [37.5859, 55.7294],
    ]

    assert trackstory_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'empty_carrier, oc_resp',
    [
        (False, 'order_core_resp_simple'),
        (True, 'order_core_resp_empty_carrier'),
    ],
)
@pytest.mark.parametrize(
    'empty_park, parks_replica_error', [(True, True), (False, False)],
)
@pytest.mark.parametrize(
    'legal_entities_enabled, legal_entities_flag, taxi_tariffs_error',
    [
        (True, True, False),
        (True, None, False),
        (True, None, True),
        (False, False, False),
    ],
)
@pytest.mark.parametrize(
    'carrier_enabled, carrier_flag, territories_error',
    [
        (True, True, False),
        (False, None, False),
        (False, None, True),
        (False, False, False),
    ],
)
async def test_legal_entities_parts(
        taxi_ridehistory,
        load_json,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_parks_replica,
        mock_territories,
        empty_carrier,
        oc_resp,
        empty_park,
        parks_replica_error,
        legal_entities_enabled,
        legal_entities_flag,
        taxi_tariffs_error,
        carrier_enabled,
        carrier_flag,
        territories_error,
):
    if taxi_tariffs_error:
        carrier_enabled = False

    mock_order_core_query(['1'], oc_resp, True)
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(
        ['bishkek', 'saratov'], legal_entities_flag, taxi_tariffs_error,
    )
    mock_parks_replica('parks.json', True, parks_replica_error)
    mock_territories(carrier_flag, territories_error)

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': '1'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    order = response.json()['data']
    exp_order = load_json('expected_resp_simple_1.json')['data']

    legal_entities = {le['type']: le for le in order['legal_entities']}
    exp_legal_entities = {le['type']: le for le in exp_order['legal_entities']}

    if legal_entities_enabled:
        if not empty_park:
            if carrier_enabled:
                assert (
                    legal_entities['partner'] == exp_legal_entities['partner']
                )

            if not carrier_enabled or (carrier_enabled and empty_carrier):
                partner_copy = copy.deepcopy(exp_legal_entities['partner'])
                partner_copy['type'] = 'carrier'
                partner_copy['title'] = 'Перевозчик'
                assert legal_entities['carrier'] == partner_copy
            else:
                assert (
                    legal_entities['carrier'] == exp_legal_entities['carrier']
                )
        else:
            for key, value in legal_entities.items():
                assert exp_legal_entities[key] == value

    legal_entities_types = set(legal_entities)
    if not legal_entities_enabled:
        exp_legal_entities_types = set()
    else:
        if empty_park:
            if carrier_enabled and not empty_carrier:
                exp_legal_entities_types = {'carrier'}
            else:
                exp_legal_entities_types = set()
        else:
            if carrier_enabled:
                exp_legal_entities_types = {'partner', 'carrier'}
            else:
                exp_legal_entities_types = {'carrier'}

    assert legal_entities_types == exp_legal_entities_types

    if not empty_park:
        assert (
            order['park']['long_name']
            == 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ЧИРИК"'
        )
    else:
        assert order['park'] == {}


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'parks_fname, no_legal_log',
    [('parks_legal_log.json', False), ('parks_no_legal_log.json', True)],
)
@pytest.mark.parametrize(
    'start_time, expected_ogrn',
    [
        ('2001-06-21T14:29:48.364+00:00', '1'),
        ('2019-12-21T14:29:48.364+00:00', '2'),
        ('2021-06-21T14:29:48.364+00:00', '3'),
    ],
)
async def test_legal_log(
        taxi_ridehistory,
        load_json,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_parks_replica,
        mock_territories,
        start_time,
        expected_ogrn,
        parks_fname,
        no_legal_log,
):
    mock_order_core_query(
        ['1'],
        'order_core_resp_simple',
        True,
        {'1': {'order.request.due': start_time}},
    )
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_parks_replica(parks_fname, True)
    mock_territories(False)

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': '1'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    legal_entities = response.json()['data']['legal_entities']
    assert len(legal_entities) == 1
    ogrn = [
        ap['value']
        for ap in legal_entities[0]['additional_properties']
        if ap['type'] == 'ogrn'
    ][0]
    assert ogrn.split()[-1] == ('3' if no_legal_log else expected_ogrn), ogrn


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
    RIDEHISTORY_RECEIPT_SETTINGS={
        **DEFAULT_RECEIPT_SETTINGS,
        **{
            'show_trust_receipt_countries': [],
            'show_fetched_receipt_countries': ['rus'],
        },
    },
)
@pytest.mark.parametrize(
    ['order_id', 'expected_response', 'data_source_type'],
    [
        ('1', 'expected_cargo_item_response_1.json', 'warm'),
        ('2', 'expected_cargo_item_response_2.json', 'cold'),
    ],
)
async def test_cargo_item(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_parks_replica,
        mock_territories,
        mock_yb_trust_payments,
        mock_receipt_fetching,
        order_id,
        expected_response,
        data_source_type,
):
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_parks_replica('parks.json', True)
    mock_territories(True)
    mock_yb_trust_payments(
        '124-cba', 'yb_trust_payments_resp_simple.json', False,
    )
    mock_receipt_fetching(
        '13386de2bb47265d852774a128db6255',
        'receipt_fetching_resp_simple.json',
        False,
    )

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    if data_source_type == 'warm':
        mock_order_core_query([order_id], 'order_core_resp_cargo', True)
    elif data_source_type == 'cold':
        mock_yt_queries('expected_yt_request_cargo')

    response = await taxi_ridehistory.post(
        '/cargo/v2/item',
        json={'order_id': order_id},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )
    assert response.status == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    ['rf_response', 'expected_receipt', 'rf_error', 'exp_rf_times_called'],
    [
        (
            None,
            (
                'https://trust.yandex.ru/receipts/124-cba/'
                '#receipt_url_pdf='
                'https://trust.yandex.ru/receipts/124-cba/?mode=pdf'
            ),
            False,
            0,
        ),
        pytest.param(
            None,
            None,
            False,
            0,
            marks=pytest.mark.config(
                RIDEHISTORY_RECEIPT_SETTINGS={
                    **DEFAULT_RECEIPT_SETTINGS,
                    **{'show_trust_receipt_payment_methods': []},
                },
            ),
        ),
        pytest.param(
            None,
            None,
            False,
            0,
            marks=pytest.mark.config(
                BILLING_SERVICE_NAME_MAP_BY_BRAND={
                    '__default__': 'nonexistent',
                },
            ),
        ),
        pytest.param(
            'receipt_fetching_resp_simple.json',
            'buhta_receipt',
            False,
            1,
            marks=pytest.mark.config(
                RIDEHISTORY_RECEIPT_SETTINGS={
                    **DEFAULT_RECEIPT_SETTINGS,
                    **{
                        'show_trust_receipt_countries': [],
                        'show_fetched_receipt_countries': ['rus'],
                    },
                },
            ),
        ),
        pytest.param(
            'receipt_fetching_resp_empty.json',
            None,
            False,
            1,
            marks=pytest.mark.config(
                RIDEHISTORY_RECEIPT_SETTINGS={
                    **DEFAULT_RECEIPT_SETTINGS,
                    **{
                        'show_trust_receipt_countries': [],
                        'show_fetched_receipt_countries': ['rus'],
                    },
                },
            ),
        ),
        pytest.param(
            None,
            None,
            True,
            2,
            marks=pytest.mark.config(
                RIDEHISTORY_RECEIPT_SETTINGS={
                    **DEFAULT_RECEIPT_SETTINGS,
                    **{
                        'show_trust_receipt_countries': [],
                        'show_fetched_receipt_countries': ['rus'],
                    },
                },
            ),
        ),
        pytest.param(
            None,
            None,
            False,
            0,
            marks=pytest.mark.config(
                RIDEHISTORY_RECEIPT_SETTINGS={
                    **DEFAULT_RECEIPT_SETTINGS,
                    **{
                        'show_trust_receipt_countries': [],
                        'show_fetched_receipt_countries': [],
                    },
                },
            ),
        ),
    ],
)
async def test_receipts(
        taxi_ridehistory,
        load_json,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_parks_replica,
        mock_yb_trust_payments,
        mock_receipt_fetching,
        rf_response,
        expected_receipt,
        rf_error,
        exp_rf_times_called,
):
    mock_order_core_query(['1'], 'order_core_resp_receipts', True)
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_parks_replica('parks.json', True)
    receipt_fetching_mock = mock_receipt_fetching('1', rf_response, rf_error)

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': '1'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    response_data = response.json()['data']
    receipt = response_data.get('receipt')

    if expected_receipt is None:
        assert receipt is None
    else:
        assert receipt == {'url_with_embedded_pdf': expected_receipt}

    assert receipt_fetching_mock.times_called == exp_rf_times_called


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'exp_extra_enabled',
    [
        False,
        pytest.param(
            True,
            marks=pytest.mark.config(
                ORDERS_HISTORY_EXTRA_INFO_PROVIDER_BY_ZONE={
                    'bishkek': ['stub'],
                },
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                ORDERS_HISTORY_EXTRA_INFO_PROVIDER_BY_COUNTRY={
                    'kgz': ['stub'],
                },
            ),
        ),
    ],
)
async def test_extra_enabled(
        taxi_ridehistory,
        load_json,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_parks_replica,
        mock_yb_trust_payments,
        mock_receipt_fetching,
        exp_extra_enabled,
):
    mock_order_core_query(['1'], 'order_core_resp_simple', True)
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_parks_replica('parks.json', True)

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': '1'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    assert response.json()['data']['extra_enabled'] == exp_extra_enabled


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize('order_id', ['1', '2'])
@pytest.mark.parametrize(
    'exp_vehicle',
    [
        {
            'car_number': 'A666AA',
            'color': 'зеленый',
            'color_code': 'abc',
            'model': 'some_car_model',
        },
        pytest.param(
            {
                'car_number': 'A666AA',
                'color': 'зеленый',
                'color_code': 'abc',
                'model': 'some_car_model',
            },
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={},
                CONTRACTOR_TRANSPORT_HIDE_SETTINGS={},
            ),
        ),
        pytest.param(
            {
                'car_number': 'A666AA',
                'color': 'зеленый',
                'color_code': 'abc',
                'model': 'some_car_model',
            },
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={'__default__': True},
                CONTRACTOR_TRANSPORT_HIDE_SETTINGS={},
            ),
        ),
        pytest.param(
            {
                'car_number': 'A666AA',
                'color': 'зеленый',
                'color_code': 'abc',
                'model': 'some_car_model',
            },
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={'__default__': False},
                CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
                    '__default__': {
                        'color': True,
                        'model': True,
                        'number': True,
                    },
                },
            ),
        ),
        pytest.param(
            {},
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={'__default__': True},
                CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
                    '__default__': {
                        'color': True,
                        'model': True,
                        'number': True,
                    },
                },
            ),
        ),
        pytest.param(
            {'color': 'зеленый', 'color_code': 'abc'},
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={'__default__': True},
                CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
                    '__default__': {'model': True, 'number': True},
                },
            ),
        ),
        pytest.param(
            {'model': 'some_car_model'},
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={'__default__': True},
                CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
                    '__default__': {'color': True, 'number': True},
                },
            ),
        ),
        pytest.param(
            {'car_number': 'A666AA'},
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={'__default__': True},
                CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
                    '__default__': {'color': True, 'model': True},
                },
            ),
        ),
        pytest.param(
            {},
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={
                    '__default__': False,
                    'orderhistory': True,
                },
                CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
                    '__default__': {},
                    'pedestrian': {
                        'color': True,
                        'model': True,
                        'number': True,
                    },
                },
            ),
        ),
        {
            'car_number': 'A666AA',
            'color': 'зеленый',
            'color_code': 'abc',
            'model': 'some_car_model',
        },
    ],
)
async def test_transport_hide(
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        order_id,
        exp_vehicle,
):
    mock_yt_queries('expected_yt_request_transport')
    mock_order_core_query(['1'], 'order_core_resp_transport', True)
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': False, 'order_id': order_id},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert response.json()['data']['vehicle'] == exp_vehicle


@pytest.fixture(name='item_freightage_mock_context')
def _item_freightage_mock_context(
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        mock_admin_images_custom,
        mock_eulas_freightage,
):
    class Context:
        def __init__(self):
            self.mock_eulas_freightage = mock_eulas_freightage

        def mock_default(self):
            order_id = '1'
            mock_yt_queries(None)
            mock_order_core_query([order_id], 'order_core_resp_simple', True)
            mock_transactions_query([order_id], 'transactions_resp_simple')
            mock_taxi_tariffs_query(['bishkek', 'saratov'])
            mock_driver_profiles('driver_profiles.json')
            mock_parks_replica('parks.json', True)
            mock_personal_phones('personal_phones.json')
            mock_territories(True)

    context = Context()
    context.mock_default()
    return context


DEFAULT_HEADERS = {
    'X-Yandex-UID': '12345',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android,app_brand=yataxi',
    'X-YaTaxi-PhoneId': '777777777777777777777777',
}


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
    RIDEHISTORY_FREIGHTAGE_CONTRACT_ENABLED=True,
)
@pytest.mark.parametrize('is_contract_returned', [True, False])
@pytest.mark.parametrize('format_currency', [True, False])
async def test_freightage_ok(
        taxi_ridehistory,
        item_freightage_mock_context,
        is_contract_returned,
        format_currency,
):
    order_id = '1'
    ctx = item_freightage_mock_context
    eulas_mock = ctx.mock_eulas_freightage(
        return_contract=is_contract_returned,
        order_id=order_id,
        format_currency=format_currency,
    )

    request_json = {
        'check_permissions': False,
        'order_id': order_id,
        'settings': {'format_currency': format_currency},
    }

    response = await taxi_ridehistory.post(
        'v2/item', json=request_json, headers=DEFAULT_HEADERS,
    )

    assert eulas_mock.times_called == 1
    assert response.status == 200

    if is_contract_returned:
        data = response.json()['data']
        assert data['freightage'] == {
            'title': 'test_title',
            'contract_data': [
                {
                    'item_type': 'string',
                    'name': 'test_name',
                    'value': 'test_value',
                },
            ],
        }
    else:
        assert 'freightage' not in response.json()


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
    RIDEHISTORY_FREIGHTAGE_CONTRACT_ENABLED=True,
)
async def test_freightage_error(
        taxi_ridehistory,
        item_freightage_mock_context,
        eulas_freightage_error_mock,
):
    order_id = '1'

    request_json = {'check_permissions': False, 'order_id': order_id}

    response = await taxi_ridehistory.post(
        'v2/item', json=request_json, headers=DEFAULT_HEADERS,
    )

    assert response.status == 200
    assert eulas_freightage_error_mock.times_called > 0
    assert 'freightage' not in response.json()
