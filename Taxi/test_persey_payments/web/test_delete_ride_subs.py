import pytest


@pytest.mark.parametrize(
    [
        'headers_patch',
        'expected_hidden_at',
        'expected_active_ride_subs',
        'expected_events',
        'expected_seen_bound_uids',
    ],
    [
        pytest.param(
            {
                'X-Yandex-UID': 'portal_uid',
                'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
                'X-YaTaxi-Pass-Flags': 'social',
                'X-YaTaxi-Bound-Uids': 'phonish_uid',
            },
            {'phonish_uid': False, 'portal_uid': True},
            [[1, 'phonish_uid', 'yataxi']],
            'expected_events_portal.json',
            [['portal_uid', 'phonish_uid']],
            marks=pytest.mark.pgsql(
                'persey_payments', files=['simple.sql', 'social_passport.sql'],
            ),
        ),
        pytest.param(
            {
                'X-Yandex-UID': 'portal_uid',
                'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
                'X-YaTaxi-Pass-Flags': 'social',
            },
            {'phonish_uid': False, 'portal_uid': True},
            [[1, 'phonish_uid', 'yataxi']],
            'expected_events_portal.json',
            [],
            marks=pytest.mark.pgsql(
                'persey_payments', files=['simple.sql', 'social_passport.sql'],
            ),
        ),
        pytest.param(
            {
                'X-Yandex-UID': 'phonish_uid',
                'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
                'X-YaTaxi-Pass-Flags': 'phonish',
            },
            {'phonish_uid': True},
            [],
            'expected_events_phonish.json',
            [],
            marks=pytest.mark.pgsql('persey_payments', files=['simple.sql']),
        ),
        pytest.param(
            {
                'X-Yandex-UID': 'portal_uid',
                'X-YaTaxi-PhoneId': 'cccccccccccccccccccccccc',
                'X-YaTaxi-Pass-Flags': 'portal',
                'X-YaTaxi-Bound-Uids': 'phonish_uid',
            },
            {'phonish_uid': False},
            [[1, 'phonish_uid', 'yataxi']],
            'expected_events_empty.json',
            [['portal_uid', 'phonish_uid']],
            marks=pytest.mark.pgsql('persey_payments', files=['simple.sql']),
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        stq,
        load_json,
        get_ride_subs,
        get_active_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
        headers_patch,
        expected_hidden_at,
        expected_active_ride_subs,
        expected_events,
        expected_seen_bound_uids,
):
    headers = {
        'X-Request-Application': 'app_name=android,app_brand=yataxi',
        'X-Request-Language': 'ru',
    }
    headers.update(headers_patch)

    response = await taxi_persey_payments_web.delete(
        '/4.0/persey-payments/v1/charity/ride_subs', headers=headers,
    )

    assert response.status == 204, await response.json()
    hidden_at = {data[0]: data[-1] for data in get_ride_subs()}
    assert hidden_at == expected_hidden_at
    assert get_active_ride_subs() == expected_active_ride_subs
    check_ride_subs_events(expected_events)
    assert get_seen_bound_uids() == expected_seen_bound_uids


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
    response = await taxi_persey_payments_web.delete(
        '/4.0/persey-payments/v1/charity/ride_subs',
        headers={
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-Request-Language': 'ru',
            'X-Yandex-UID': 'phonish_uid',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-YaTaxi-Pass-Flags': 'phonish',
        },
    )

    assert response.status == 204
    assert get_ride_subs_cache() == load_json(expected_cache)
