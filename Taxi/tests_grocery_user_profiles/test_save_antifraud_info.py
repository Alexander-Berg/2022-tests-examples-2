from tests_grocery_user_profiles import common
from tests_grocery_user_profiles import consts


async def test_basic(taxi_grocery_user_profiles, pgsql):
    user_profile = common.create_default_frauder_profile(pgsql)
    response = await taxi_grocery_user_profiles.post(
        '/processing/v1/antifraud/info/save',
        json={
            'yandex_uid': consts.FRAUD_YANDEX_UID,
            'personal_phone_id': consts.FRAUD_PERSONAL_PHONE_ID,
            'antifraud_info': {'name': consts.ANTIFRAUD_RULE},
        },
    )
    assert response.status_code == 200

    user_profile.compare_with_db()
