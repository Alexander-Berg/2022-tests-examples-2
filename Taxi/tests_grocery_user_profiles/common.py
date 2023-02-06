import json

from tests_grocery_user_profiles import consts
from tests_grocery_user_profiles import models


def create_default_frauder_profile(pgsql, tag_name='antifraud'):
    return models.UserProfile(
        pgsql=pgsql,
        created_at=models.NOW_DT,
        updated_at=models.NOW_DT,
        is_disabled=False,
        tag_name=tag_name,
        tag_info=json.dumps({'name': consts.ANTIFRAUD_RULE}),
        yandex_uid=consts.FRAUD_YANDEX_UID,
        personal_phone_id=consts.FRAUD_PERSONAL_PHONE_ID,
        appmetrica_device_id=None,
        bound_session=None,
    )


def create_ban_info(
        pgsql,
        ban_action=consts.BAN_ACTION_BAN,
        admin_login=consts.ADMIN_LOGIN,
        reason=consts.BAN_REASON,
        yandex_uid=consts.BANNED_YANDEX_UID,
        personal_phone_id=None,
        is_disabled=False,
):
    return models.UserProfile(
        pgsql=pgsql,
        created_at=models.NOW_DT,
        updated_at=models.NOW_DT,
        is_disabled=is_disabled,
        tag_name=consts.BAN_TAG,
        tag_info=json.dumps(
            {
                'action': ban_action,
                'idempotency_token': 'urbanned',
                'yandex_login': admin_login,
                'reason': reason,
                'imposed_at': models.BEFORE_NOW,
            },
        ),
        yandex_uid=yandex_uid,
        appmetrica_device_id=None,
        personal_phone_id=personal_phone_id,
        bound_session=None,
    )
