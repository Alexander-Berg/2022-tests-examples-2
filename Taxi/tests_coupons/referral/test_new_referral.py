import pytest

from tests_coupons.referral import util


@pytest.mark.parametrize(
    'completed_rides, expected', [(0, 406), (1, 200), (2, 200)],
)
async def test_user_completed_orders_count(
        taxi_coupons, user_statistics_services, completed_rides, expected,
):
    user_statistics_services.set_total_rides(completed_rides)
    user_statistics_services.set_phone_id(util.PHONE_ID_EMPTY)

    await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_EMPTY,
        expected_code=expected,
    )


async def test_new_percent_per_trip(taxi_coupons, user_statistics_services):
    user_statistics_services.set_phone_id(util.PHONE_ID_EMPTY)

    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_EMPTY,
        zone_name='moscow_ppt_promocode',
    )

    assert content[-1]['descr'] == (
        'Gift your friend a discount of 30% (up to 250 $SIGN$$CURRENCY$) '
        'on their first 13 rides when they pay with card. Discount is '
        'available to new users only.'
    )

    util.check_message(
        content[-1],
        (
            'I use Yandex.Taxi. Click on the link to get a new user discount '
            'of 30 % (up to 250 rub) on your first 13 rides when you pay with '
            'card https://m.taxi.yandex.ru/invite/{promocode}. '
            'After the app is installed use promocode {promocode}'
        ),
    )


async def test_new_percent_no_per_trip(taxi_coupons, user_statistics_services):
    user_statistics_services.set_phone_id(util.PHONE_ID_EMPTY)

    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_EMPTY,
        zone_name='moscow_percent_promocode',
    )

    assert content[-1]['descr'] == (
        'Gift your friend a discount of 28% off their first 58 rides (up to '
        '200 $SIGN$$CURRENCY$ total) when they pay with card. Discount is '
        'available to new users only.'
    )

    util.check_message(
        content[-1],
        (
            'I\'m using Yandex.Taxi. Click on the link to get a new user '
            'discount of 28% (up to 200 rub total) on your first 58 rides '
            'when you pay with card '
            'https://m.taxi.yandex.ru/invite/{promocode}. '
            'After the app is installed use promocode {promocode}'
        ),
    )


async def test_new_no_percent(taxi_coupons, user_statistics_services):
    user_statistics_services.set_phone_id(util.PHONE_ID_EMPTY)

    content = await util.referral_request_and_check(
        taxi_coupons, user_statistics_services, util.YANDEX_UID_EMPTY,
    )

    assert content[-1]['descr'] == util.COMMON_NO_PERCENT_DESCR
    util.check_message(content[-1], util.COMMON_NO_PERCENT_MESSAGE)


@pytest.mark.config(REFERRALS_CONFIG={'count': 7, 'enabled': False})
async def test_config_disabled(taxi_coupons, user_statistics_services):
    await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_EMPTY,
        expected_code=406,
    )


async def test_user_no_stat(
        taxi_coupons, user_statistics_services, mockserver,
):
    user_statistics_services.user_statistics = {
        'data': [
            {
                'identity': {'type': 'phone_id', 'value': util.PHONE_ID_EMPTY},
                'counters': [],
            },
        ],
    }

    await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_EMPTY,
        expected_code=406,
    )
