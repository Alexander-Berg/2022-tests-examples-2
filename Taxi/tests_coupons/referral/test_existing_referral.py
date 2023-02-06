import pytest

from tests_coupons.referral import util

YANDEX_UID_WITH_PPT = '111111111'

PHONE_ID_WITH_PPT = '5714f45e98956f06baaae3d4'
PHONE_ID_WITH_PERCENT = '5714f45e98956f06baaae3d5'


async def test_simple(taxi_coupons, user_statistics_services):
    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_WITH_PERCENT,
        phone_id=util.REFERRAL_USER_PHONE_ID,
    )
    assert content


async def test_disabled_zone(taxi_coupons, user_statistics_services):
    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_WITH_PERCENT,
        phone_id=util.REFERRAL_USER_PHONE_ID,
        payment_options=['cash'],
    )
    assert not content


@pytest.mark.parametrize(
    'is_referral_expected',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='referral_taxi_check_db_first_exp3.json',
            ),
        ),
        False,
    ],
)
@pytest.mark.experiments3(
    filename='referral_campaign_light_business_experiments3.json',
)
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
@pytest.mark.parametrize(
    'yandex_uid, referrals_count',
    [
        (util.YANDEX_UID_CAMPAINGS, 2),
        (util.YANDEX_UID_BUSINESS, 1),
        (util.YANDEX_UID_COMMON, 1),
    ],
)
async def test_promocode_in_unknown_zone(
        taxi_coupons,
        yandex_uid,
        referrals_count,
        is_referral_expected,
        user_statistics_services,
):
    response = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        expected_code=200 if is_referral_expected else 406,
        zone_name='no_creator_configs_here',
        phone_id=util.REFERRAL_USER_PHONE_ID,
    )
    if is_referral_expected:
        assert len(response) == referrals_count


@pytest.mark.parametrize(
    'referral_exp_on,expected_referrals_count',
    [
        pytest.param(
            True,
            2,
            marks=pytest.mark.experiments3(
                filename='external_referral_experiments3.json',
            ),
        ),
        (False, 1),
    ],
)
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
async def test_existing_percent_per_trip(
        taxi_coupons,
        user_statistics_services,
        eda_promocodes,
        referral_exp_on,
        expected_referrals_count,
        mockserver,
):
    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        YANDEX_UID_WITH_PPT,
        phone_id=PHONE_ID_WITH_PPT,
    )

    assert len(content) == expected_referrals_count

    assert content[-1]['descr'] == (
        'Gift your friend a discount of 30% (up to 250 $SIGN$$CURRENCY$) '
        'on their first 13 rides when they pay with card. Discount is '
        'available to new users only.'
    )
    assert content[-1]['message'] == (
        'I use Yandex.Taxi. Click on the link to get a new user discount of '
        '30 % (up to 250 rub) on your first 13 rides when you pay with card '
        'https://m.taxi.yandex.ru/invite/promowithppt. '
        'After the app is installed use promocode promowithppt'
    )
    assert content[-1]['promocode'] == 'promowithppt'

    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        YANDEX_UID_WITH_PPT,
        phone_id=PHONE_ID_WITH_PPT,
        format_currency=False,
    )
    assert content[-1]['descr'] == (
        'Gift your friend a discount of 30% (up to 250 rub) on their first '
        '13 rides when they pay with card. Discount is available to new users '
        'only.'
    )
    assert content[-1]['message'] == (
        'I use Yandex.Taxi. Click on the link to get a new user discount of '
        '30 % (up to 250 rub) on your first 13 rides when you pay with card '
        'https://m.taxi.yandex.ru/invite/promowithppt. '
        'After the app is installed use promocode promowithppt'
    )


@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
async def test_existing_percent_no_per_trip(
        taxi_coupons, user_statistics_services,
):
    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_WITH_PERCENT,
        phone_id=PHONE_ID_WITH_PERCENT,
    )

    assert content[-1]['descr'] == (
        'Gift your friend a discount of 28% off their first 58 rides (up to '
        '200 $SIGN$$CURRENCY$ total) when they pay with card. Discount is '
        'available to new users only.'
    )
    assert content[-1]['message'] == (
        'I\'m using Yandex.Taxi. Click on the link to get a new user discount '
        'of 28% (up to 200 rub total) on your first 58 rides when you pay '
        'with card https://m.taxi.yandex.ru/invite/promowithpercent. '
        'After the app is installed use promocode promowithpercent'
    )
    assert content[-1]['promocode'] == 'promowithpercent'

    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_WITH_PERCENT,
        phone_id=PHONE_ID_WITH_PERCENT,
        format_currency=False,
    )
    assert content[-1]['descr'] == (
        'Gift your friend a discount of 28% off their first 58 rides (up to '
        '200 rub total) when they pay with card. Discount is available to '
        'new users only.'
    )
    assert content[-1]['message'] == (
        'I\'m using Yandex.Taxi. Click on the link to get a new user discount '
        'of 28% (up to 200 rub total) on your first 58 rides when you pay '
        'with card https://m.taxi.yandex.ru/invite/promowithpercent. '
        'After the app is installed use promocode promowithpercent'
    )


@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
async def test_existing_no_percent(taxi_coupons, user_statistics_services):
    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_NO_PERCENT,
        phone_id=util.PHONE_ID_NO_PERCENT,
    )
    assert content[-1]['descr'] == util.COMMON_NO_PERCENT_DESCR
    assert content[-1]['message'] == util.COMMON_NO_PERCENT_MESSAGE.format(
        promocode='promonopercent',
    )
    assert content[-1]['promocode'] == 'promonopercent'
