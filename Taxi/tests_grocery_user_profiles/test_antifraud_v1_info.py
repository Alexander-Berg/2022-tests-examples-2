import json

import pytest

from tests_grocery_user_profiles import common
from tests_grocery_user_profiles import consts
from tests_grocery_user_profiles import models


@pytest.mark.parametrize(
    'yandex_uid, personal_phone_id',
    [
        (consts.FRAUD_YANDEX_UID, 'personal_phone_id'),
        ('yandex_uid', consts.FRAUD_PERSONAL_PHONE_ID),
    ],
)
async def test_basic(
        taxi_grocery_user_profiles, pgsql, yandex_uid, personal_phone_id,
):
    user_profile = common.create_default_frauder_profile(pgsql)
    user_profile.update_db()

    response = await taxi_grocery_user_profiles.post(
        '/internal/antifraud/v1/info',
        json={
            'yandex_uid': yandex_uid,
            'personal_phone_id': personal_phone_id,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'antifraud_info': {'name': consts.ANTIFRAUD_RULE},
    }


async def test_empty_personal_phone_id(taxi_grocery_user_profiles, pgsql):
    yandex_uid = 'yandex-uid'
    personal_phone_id = ''
    user_profile = models.UserProfile(
        pgsql=pgsql,
        created_at=models.NOW_DT,
        updated_at=models.NOW_DT,
        is_disabled=False,
        tag_name='antifraud',
        tag_info=json.dumps({'name': consts.ANTIFRAUD_RULE}),
        yandex_uid=consts.FRAUD_YANDEX_UID,
        personal_phone_id='',
        appmetrica_device_id=None,
        bound_session=None,
    )
    user_profile.update_db()

    response = await taxi_grocery_user_profiles.post(
        '/internal/antifraud/v1/info',
        json={
            'yandex_uid': yandex_uid,
            'personal_phone_id': personal_phone_id,
        },
    )
    assert response.status_code == 404


async def test_not_found(taxi_grocery_user_profiles, pgsql):
    user_profile = common.create_default_frauder_profile(pgsql, 'positive-tag')
    user_profile.update_db()

    response = await taxi_grocery_user_profiles.post(
        '/internal/antifraud/v1/info',
        json={
            'yandex_uid': consts.FRAUD_YANDEX_UID,
            'personal_phone_id': consts.FRAUD_PERSONAL_PHONE_ID,
        },
    )
    assert response.status_code == 404
