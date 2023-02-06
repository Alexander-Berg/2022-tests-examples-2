import pytest

from tests_coupons import util as common_util
from tests_coupons.referral import util

YANDEX_UID_0 = '1234567890'  # mocked in 'referral.sql'
YANDEX_UID_1 = '1234567892'  # mocked in 'referral.sql'
YANDEX_UID_2 = '5348953485'
YANDEX_UID_3 = '133713371337'
YANDEX_UID_NEW_USER = 'new_user'
YANDEX_UID_NOT_EXISTING_USER = '987654321'

PHONE_ID_0 = '5bbb5faf15870bd76635d5e2'
PHONE_ID_1 = '507f1f77bcf86cd799439013'

PROMOCODE_NULL_CFG_ID = 'referral0'
PROMOCODE_WRONG_CFG_ID = 'referral1'
PROMOCODE_VALID = 'referral2'
PROMOCODE_DOES_NOT_EXIST = 'code'


@pytest.mark.config(PERCENT_PROMOCODE_MIN_LIMIT=100)
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME,
    files=util.PGSQL_REFERRAL,
    queries=util.SQLS_REFERRAL_CONSUMER_CONFIG_PERCENT,
)
@pytest.mark.filldb(promocode_usages2='percent')
@pytest.mark.now('2017-03-13T11:30:00+0300')
async def test_activate_percentage_exceeded(
        taxi_coupons, mongodb, local_services,
):
    yandex_uid = '4001'

    request = common_util.mock_request(
        [yandex_uid], yandex_uid, 'percentreferral',
    )
    response = await common_util.make_activate_request(
        taxi_coupons, data=request,
    )
    content = response.json()['coupon']

    assert content['error']['code'] == 'ERROR_PERCENTAGE_LIMIT_EXCEEDED'


@pytest.mark.parametrize(
    'yandex_uid, promocode, erase_creator_config, erase_consumer_config',
    [
        (YANDEX_UID_NOT_EXISTING_USER, PROMOCODE_DOES_NOT_EXIST, True, True),
        (YANDEX_UID_0, PROMOCODE_DOES_NOT_EXIST, True, True),
        (YANDEX_UID_0, PROMOCODE_NULL_CFG_ID, True, True),
        (YANDEX_UID_3, PROMOCODE_WRONG_CFG_ID, True, True),
        (YANDEX_UID_1, PROMOCODE_VALID, True, True),
        (YANDEX_UID_1, PROMOCODE_VALID, False, True),
    ],
    ids=[
        'missing user',
        'missing code',
        'missing config ref',
        'wrong config ref',
        'empty creator config',
        'empty consumer config',
    ],
)
# pylint: disable=redefined-outer-name
async def test_postgres_promocode_error(
        taxi_coupons,
        local_services,
        mongo_db,
        referrals_postgres_db,
        taxi_config,
        yandex_uid,
        promocode,
        erase_creator_config,
        erase_consumer_config,
):
    if erase_creator_config:
        taxi_config.set_values(dict(REFERRAL_CREATOR_CONFIG=[]))
        referrals_postgres_db.execute('DELETE FROM referral.creator_configs')
    if erase_consumer_config:
        referrals_postgres_db.execute(util.SQL_CLEAR_REFERRAL_CONSUMER_CONFIGS)

    request = common_util.mock_request([yandex_uid], yandex_uid, promocode)
    response = await common_util.make_activate_request(taxi_coupons, request)
    assert response.status_code == 200
    coupon = response.json()['coupon']
    assert coupon['error']['code'] == 'ERROR_INVALID_CODE'


@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    'yandex_uid, has_activation, phone_id',
    [
        pytest.param(
            YANDEX_UID_1,
            False,
            PHONE_ID_0,
            id='error_to_add_self_promocode_by_yandex_uid',
        ),
        pytest.param(
            YANDEX_UID_2,
            False,
            PHONE_ID_1,
            id='error_to_add_self_promocode_by_phone_id',
        ),
        pytest.param(
            YANDEX_UID_NEW_USER,
            True,
            PHONE_ID_0,
            id='success_to_add_promocode',
        ),
    ],
)
# pylint: disable=redefined-outer-name
async def test_postgres_promocode(
        taxi_coupons,
        local_services,
        mongo_db,
        referrals_postgres_db,
        yandex_uid,
        has_activation,
        phone_id,
):
    promocode = PROMOCODE_VALID
    request = common_util.mock_request(
        [yandex_uid], yandex_uid, promocode, phone_id=phone_id,
    )
    response = await common_util.make_activate_request(
        taxi_coupons, data=request,
    )
    assert response.status_code == 200

    user_activations = util.referral_success_activations(
        yandex_uid, referrals_postgres_db,
    )
    if has_activation:
        assert len(user_activations) == 1
        assert user_activations[0]['campaign_id'] == 0
    else:
        assert not user_activations


CONSUMER_CONFIG_NO_SERIES = {'duration_days': 10, 'zone_name': 'moscow'}


@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_invalid_brand(
        taxi_coupons, local_services, mongo_db, referrals_postgres_db,
):
    yandex_uid = YANDEX_UID_0
    request = common_util.mock_request(
        [yandex_uid], yandex_uid, PROMOCODE_VALID, app_name='uber_iphone',
    )
    response = await common_util.make_activate_request(
        taxi_coupons, data=request,
    )
    coupon = response.json()['coupon']
    assert coupon['error']['code'] == 'ERROR_INVALID_APPLICATION'


@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    'series_id, expected_error, valid_days, start_text',
    [
        #  check promocode series start-finish dates
        pytest.param(
            'referral', None, 11, None, id='dates from consumer config',
        ),
        pytest.param(
            'referral_late_start',
            None,
            11,
            '<red>Промокод действителен с 16.03.2017</red>',
            id='start from series',
        ),
        pytest.param(
            'referral_early_finish', None, 5, None, id='finish from series',
        ),
        pytest.param(
            'referral_very_early_finish',
            'ERROR_TOO_LATE',
            None,
            None,
            id='series finished',
        ),
        pytest.param(
            'referral_very_late_start',
            'ERROR_TOO_EARLY',
            None,
            None,
            id='series will not start',
        ),
    ],
)
# pylint: disable=redefined-outer-name
async def test_postgres_promocode_time(
        taxi_coupons,
        local_services,
        mongo_db,
        referrals_postgres_db,
        taxi_config,
        series_id,
        expected_error,
        valid_days,
        start_text,
):
    referrals_postgres_db.execute(
        util.insert_referral_consumer_config(
            series_id=series_id, **CONSUMER_CONFIG_NO_SERIES,
        ),
    )

    promocode = PROMOCODE_VALID
    yandex_uid = YANDEX_UID_NEW_USER
    request = common_util.mock_request([yandex_uid], yandex_uid, promocode)
    response = await common_util.make_activate_request(
        taxi_coupons, data=request,
    )
    assert response.status_code == 200
    coupon = response.json()['coupon']
    if expected_error:
        assert coupon['error']['code'] == expected_error
    else:
        detail_text = coupon['action']['details'][0]['text']
        assert detail_text == f'Действует еще {valid_days} дней'
        description = coupon['action']['descriptions'][1]['text']
        if start_text:
            assert description == start_text
        else:
            # default text
            assert description == '<red>Оплата картой не выбрана</red>'


CONSUMER_CONFIG_NO_GEO = {'duration_days': 10, 'series_id': 'referral'}


@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME,
    files=util.PGSQL_REFERRAL,
    queries=[
        util.add_or_modify_creator_config(config_id=1, campaign_id=1),
        util.SQL_CLEAR_REFERRAL_CONSUMER_CONFIGS,
    ],
)
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize('zone_name', ['moscow', None])  # None = rus
@pytest.mark.parametrize(
    'campaigns, has_activation',
    [
        pytest.param([0], False, id='wo_campaign'),
        pytest.param([1], True, id='with_campaign'),
        pytest.param([0, 1], True, id='with_two_campaigns'),
        pytest.param([5], False, id='with_other_campaign'),
    ],
)
async def test_referral_extra_campaign(
        taxi_coupons,
        local_services,
        mongo_db,
        taxi_config,
        referrals_postgres_db,
        campaigns,
        zone_name,
        has_activation,
):
    for campaign_id in campaigns:
        referrals_postgres_db.execute(
            util.insert_referral_consumer_config(
                campaign_id=campaign_id,
                zone_name=zone_name,
                **CONSUMER_CONFIG_NO_GEO,
            ),
        )

    yandex_uid = YANDEX_UID_NEW_USER
    phone_id = PHONE_ID_0
    promocode = PROMOCODE_VALID
    request = common_util.mock_request(
        [yandex_uid], yandex_uid, promocode, phone_id=phone_id,
    )
    response = await common_util.make_activate_request(
        taxi_coupons, data=request,
    )
    assert response.status_code == 200

    user_activations = util.referral_success_activations(
        yandex_uid, referrals_postgres_db,
    )
    if has_activation:
        assert len(user_activations) == 1
        assert user_activations[0]['campaign_id'] == 1
    else:
        assert not user_activations


@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME,
    files=util.PGSQL_REFERRAL,
    queries=[util.add_or_modify_creator_config(config_id=2, campaign_id=2)],
)
@pytest.mark.now('2017-03-13T11:30:00+0300')
async def test_referral_multi_campaigns(
        taxi_coupons, local_services, referrals_postgres_db,
):
    local_services.add_card()
    yandex_uid = YANDEX_UID_NEW_USER
    phone_id = PHONE_ID_0
    yataxi_promocode = PROMOCODE_VALID
    yango_promocode = 'percentreferral'
    yataxi_request = common_util.mock_request(
        [yandex_uid], yandex_uid, yataxi_promocode, phone_id=phone_id,
    )
    response = await common_util.make_activate_request(
        taxi_coupons, data=yataxi_request,
    )
    assert response.status_code == 200
    response_coupon = response.json()['coupon']
    assert response_coupon['status'] == 'valid'

    yango_request = common_util.mock_request(
        [yandex_uid],
        yandex_uid,
        yango_promocode,
        phone_id=phone_id,
        app_name='yango_android',
    )
    response = await common_util.make_activate_request(
        taxi_coupons, data=yango_request,
    )
    assert response.status_code == 200
    response_coupon = response.json()['coupon']
    assert response_coupon['status'] == 'valid'

    user_activations = util.referral_success_activations(
        yandex_uid, referrals_postgres_db,
    )
    assert len(user_activations) == 2
    campaigns = {activation['campaign_id'] for activation in user_activations}
    assert campaigns == {0, 2}
