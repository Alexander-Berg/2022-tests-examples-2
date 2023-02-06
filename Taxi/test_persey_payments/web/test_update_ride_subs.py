import pytest


@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[123])
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    [
        'headers_patch',
        'expected_resp',
        'expected_ride_subs',
        'expected_events',
        'expected_seen_bound_uids',
    ],
    [
        (
            {
                'X-Yandex-UID': 'phonish_uid',
                'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
                'X-YaTaxi-Pass-Flags': 'phonish',
            },
            'expected_resp_phonish.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
        ),
        (
            {
                'X-Yandex-UID': 'portal_uid',
                'X-YaTaxi-PhoneId': 'cccccccccccccccccccccccc',
                'X-YaTaxi-Pass-Flags': 'portal',
                'X-YaTaxi-Bound-Uids': 'phonish_uid',
            },
            'expected_resp_phonish.json',
            'expected_ride_subs_portal.json',
            'expected_events_portal.json',
            [['portal_uid', 'phonish_uid']],
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        stq,
        load_json,
        get_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
        headers_patch,
        expected_resp,
        expected_ride_subs,
        expected_events,
        expected_seen_bound_uids,
):
    headers = {
        'X-Request-Application': 'app_name=android,app_brand=yataxi',
        'X-Request-Language': 'ru',
    }
    headers.update(headers_patch)

    response = await taxi_persey_payments_web.put(
        '/4.0/persey-payments/v1/charity/ride_subs',
        json={'mod': 123},
        headers=headers,
    )

    assert response.status == 200, await response.json()
    assert await response.json() == load_json(expected_resp)
    assert get_ride_subs() == load_json(expected_ride_subs)
    check_ride_subs_events(expected_events)
    assert get_seen_bound_uids() == expected_seen_bound_uids


@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[123])
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.parametrize(
    'expected_cache',
    [
        pytest.param(
            'expected_cache_active_order.json',
            marks=pytest.mark.pgsql(
                'persey_payments',
                files=['simple.sql', 'active_order_in_cache.sql'],
            ),
        ),
        pytest.param(
            'expected_cache_no_active_order.json',
            marks=pytest.mark.pgsql('persey_payments', files=['simple.sql']),
        ),
    ],
)
async def test_cache(
        taxi_persey_payments_web,
        stq,
        load_json,
        get_ride_subs_cache,
        expected_cache,
):
    response = await taxi_persey_payments_web.put(
        '/4.0/persey-payments/v1/charity/ride_subs',
        json={'mod': 123},
        headers={
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-Request-Language': 'ru',
            'X-Yandex-UID': 'phonish_uid',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-YaTaxi-Pass-Flags': 'phonish',
        },
    )

    assert response.status == 200
    assert get_ride_subs_cache() == load_json(expected_cache)


@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
async def test_mod_suggest(
        taxi_persey_payments_web,
        load_json,
        get_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
):
    response = await taxi_persey_payments_web.put(
        '/4.0/persey-payments/v1/charity/ride_subs',
        json={'mod': 777},
        headers={
            'X-Yandex-UID': 'phonish_uid',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-YaTaxi-Pass-Flags': 'phonish',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-Request-Language': 'ru',
        },
    )

    assert response.status == 400, await response.json()
    assert await response.json() == {
        'code': 'MOD_NOT_ALLOWED',
        'message': 'Bad mod passed for yataxi. Allowed mods are {10, 100, 50}',
    }
    assert get_ride_subs() == load_json(
        'expected_ride_subs_mod_whitelist.json',
    )
    check_ride_subs_events('expected_events_empty.json')
    assert get_seen_bound_uids() == []
