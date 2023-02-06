import pytest


@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
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
                'X-YaTaxi-PhoneId': 'nonexistent',
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
        pytest.param(
            {
                'X-Yandex-UID': 'phonish_uid',
                'X-YaTaxi-PhoneId': 'nonexistent',
                'X-YaTaxi-Pass-Flags': 'phonish',
            },
            'expected_resp_phonish.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            marks=pytest.mark.config(
                CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
            ),
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

    response = await taxi_persey_payments_web.get(
        '/4.0/persey-payments/v1/charity/ride_subs', headers=headers,
    )

    assert response.status == 200, await response.json()
    assert await response.json() == load_json(expected_resp)
    assert get_ride_subs() == load_json(expected_ride_subs)
    check_ride_subs_events(expected_events)
    assert get_seen_bound_uids() == expected_seen_bound_uids
