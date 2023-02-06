import pytest

from tests_coupons.referral import util


def get_success_activations_count(promocode, db):
    db.execute(
        f"""
        select count(*)
        from referral.promocode_success_activations psa
        join referral.promocode_activations pa ON pa.id = psa.activation_id
        join referral.promocodes p ON p.id = pa.promocode_id
        where p.promocode = '{promocode}'
    """,
    )
    record = list(db)[0]
    return record[0]


# pylint: disable=redefined-outer-name
async def test_referral_created_in_postgres(
        taxi_coupons, user_statistics_services, referrals_postgres_db,
):
    """
    The test scenario is as follows:
      - Check that initially there are no records for the user
      - Call getreferral handle for referral generation
      - Check that the promocode record appeared in postgres
      - Check that the promocode record has the 'yandex_uid' inside
    """
    phone_id, yandex_uid = util.PHONE_ID_EMPTY, util.YANDEX_UID_EMPTY
    assert not util.referrals_from_postgres(yandex_uid, referrals_postgres_db)

    content = await util.referral_request_and_check(
        taxi_coupons, user_statistics_services, yandex_uid, phone_id,
    )
    data = content[-1]
    activations_limit = util.SUCCESS_ACTIVATIONS_LIMIT
    assert data['rides_count'] == activations_limit
    assert data['rides_left'] == activations_limit

    ref_promocodes = util.referrals_from_postgres(
        yandex_uid, referrals_postgres_db,
    )
    assert len(ref_promocodes) == 1
    ref_promocode = ref_promocodes[0]
    assert ref_promocode['phone_id'] == phone_id
    assert ref_promocode['brand_name'] == 'yataxi'
    assert ref_promocode['yandex_uid'] == yandex_uid
    assert ref_promocode['campaign_id'] == 0  # common_taxi


@pytest.mark.parametrize(
    'applications_sequence, expected_brand',
    [
        (['yango_android', 'yango_iphone'], 'yango'),
        (['android', 'iphone'], 'yataxi'),
    ],
)
# pylint: disable=redefined-outer-name
async def test_referral_requests_sequence(
        applications_sequence,
        expected_brand,
        taxi_coupons,
        user_statistics_services,
        referrals_postgres_db,
):
    """
    The test scenario is as follows:
      - Call referral at the first time for application *app*
      - Call referral at the second/third/... times
      - Check that promocode in DB still keeps brand name of *app* application
    """
    phone_id, yandex_uid = util.PHONE_ID_EMPTY, util.YANDEX_UID_EMPTY
    assert not util.referrals_from_postgres(yandex_uid, referrals_postgres_db)

    for application in applications_sequence:
        await util.referral_request_and_check(
            taxi_coupons,
            user_statistics_services,
            yandex_uid,
            phone_id,
            application=application,
        )
        ref_promocodes = util.referrals_from_postgres(
            yandex_uid, referrals_postgres_db,
        )
        assert len(ref_promocodes) == 1
        assert expected_brand == ref_promocodes[0]['brand_name']


@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
# pylint: disable=redefined-outer-name
async def test_referral_exists_in_postgres(
        taxi_coupons, user_statistics_services, referrals_postgres_db,
):
    """
    The test scenario is as follows:
      - Check that there is already postgres record for user promocode
      - Call getreferral handle for referral generation
    """
    phone_id, yandex_uid = util.PHONE_ID_EMPTY, '123456789'
    promocode = 'promo'
    assert util.referrals_from_postgres(yandex_uid, referrals_postgres_db)

    content = await util.referral_request_and_check(
        taxi_coupons, user_statistics_services, yandex_uid, phone_id,
    )
    data = content[-1]
    activations_limit = util.SUCCESS_ACTIVATIONS_LIMIT
    activations_count = get_success_activations_count(
        promocode, referrals_postgres_db,
    )

    assert data['promocode'] == promocode
    assert data['rides_count'] == activations_limit
    assert data['rides_left'] == activations_limit - activations_count
    assert util.referrals_from_postgres(yandex_uid, referrals_postgres_db)
