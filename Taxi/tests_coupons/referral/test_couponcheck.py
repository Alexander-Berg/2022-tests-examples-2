import pytest

from tests_coupons import util as coupons_utils
from tests_coupons.referral import util

# referral.promocode_activations table
YANDEX_UID_LATE_CHECK = '1234567778'
YANDEX_UID_ACTIVE = '1234567779'


@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'referral.sql'],
)
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    'yandex_uid, expected_error, valid_date',
    [
        #  check referral promocode start-finish dates
        pytest.param(
            YANDEX_UID_LATE_CHECK,
            'ERROR_TOO_LATE',
            None,
            id='referral_promocode_late_check',
        ),
        pytest.param(
            YANDEX_UID_ACTIVE,
            None,
            '03/30/2017',
            id='referral_promocode_active_check',
        ),
    ],
)
# pylint: disable=redefined-outer-name
async def test_referral_promocode_time(
        taxi_coupons,
        local_services,
        mongo_db,
        referrals_postgres_db,
        yandex_uid,
        expected_error,
        valid_date,
):
    local_services.add_card()
    promocode = 'referral2'
    request = coupons_utils.mock_request_couponcheck(
        promocode,
        {'type': 'card', 'method_id': 'card_id'},
        yandex_uid=yandex_uid,
    )
    request['locale'] = 'en'
    response = await taxi_coupons.post('v1/couponcheck', json=request)
    assert response.status_code == 200

    content = response.json()
    error = content.get('error_code')
    assert error == expected_error

    details = content['details']
    detail_text = details[1] if len(details) > 1 else None
    if detail_text or valid_date:
        assert detail_text == f'Expires: {valid_date}'

    assert (
        content['descr'] == '300 $SIGN$$CURRENCY$ discount'
        ' on the next 100 rides in tariff Econom'
    )


@pytest.mark.now('2017-01-10T00:00:00+0300')
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME,
    files=[util.PGSQL_DEFAULT, 'referral.sql'],
    queries=[util.SQL_CLEAR_REFERRAL_CONSUMER_CONFIGS],
)
async def test_referral_valid_after_activation(taxi_coupons, local_services):
    """ Tests the following scenario.

    User is assumed to activate referral promocode in some zone and
    to use it afterwards in the same zone, but when zone is already
    turned off for new activations.

    The step-by-step scenario is as follows:

    - A referral promocode was activated when a zone was presented
      in the consumer config.
    - The zone is removed from the config.
    - The couponcheck is requested for the referral promocode.

    The promocode should be valid, since activation has been done
    with the old config parameters.
    """
    local_services.add_card()

    request = coupons_utils.mock_request_couponcheck(
        'promo', {'type': 'card', 'method_id': 'card_id'},
    )
    response = await taxi_coupons.post('v1/couponcheck', json=request)
    assert response.status_code == 200

    response_json = response.json()
    assert response_json['valid'] is True


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'referral.sql'],
)
async def test_referral_series_purpose(taxi_coupons, local_services):
    local_services.add_card()

    request = coupons_utils.mock_request_couponcheck(
        'referral2',
        {'type': 'card', 'method_id': 'card_id'},
        yandex_uid=YANDEX_UID_ACTIVE,
    )
    response = await taxi_coupons.post('v1/couponcheck', json=request)
    assert response.status_code == 200

    body = response.json()

    assert body['valid'] is True
    assert body['series_purpose'] == 'referral'


@pytest.mark.skip(
    reason='enable after fix https://st.yandex-team.ru/TAXIBACKEND-41465',
)
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    COUPONS_USAGES_EXTENDED_ANTIFRAUD_USER_IDS=['device_id', 'card_id'],
)
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'referral.sql'],
)
@pytest.mark.translations(
    client_messages={
        'couponcheck.details_invalid.user_limit_exceeded_single': {
            'ru': 'Вы использовали все поездки по промокоду',
        },
    },
)
async def test_referral_sbp_method_id(taxi_coupons, local_services):
    local_services.add_card()

    request = coupons_utils.mock_request_couponcheck(
        'referralone1',
        {'type': 'sbp', 'method_id': 'sbp_qr'},
        yandex_uid=YANDEX_UID_ACTIVE,
    )
    response = await taxi_coupons.post('v1/couponcheck', json=request)
    assert response.status_code == 200

    body = response.json()

    assert body['valid'] is True
    assert body['series_purpose'] == 'referral'
