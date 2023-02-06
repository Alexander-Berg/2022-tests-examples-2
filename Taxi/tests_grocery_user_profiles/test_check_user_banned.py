import uuid

import pytest

from tests_grocery_user_profiles import common
from tests_grocery_user_profiles import consts
from tests_grocery_user_profiles import models


@pytest.mark.parametrize('has_active_ban', [True, False])
async def test_check_banlist(
        taxi_grocery_user_profiles, pgsql, has_active_ban,
):
    other_admin_login = 'THE_BEST_OF_SUPPORTS'
    if has_active_ban:
        common.create_ban_info(pgsql, admin_login=other_admin_login)

    # inactive ban
    common.create_ban_info(pgsql, is_disabled=True)

    idempotency_token = 'idempotency_token0'
    headers = {'X-Idempotency-Token': idempotency_token}

    banlist_request = {
        'personal_ids': {'yandex_uid': consts.BANNED_YANDEX_UID},
        'personal_ids_filter': [],
    }

    response = await taxi_grocery_user_profiles.post(
        '/internal/v1/user-profiles/v1/check-user',
        headers=headers,
        json=banlist_request,
    )

    assert response.status_code == 200
    assert response.json()['banned'] == has_active_ban


async def test_banlist_40x(taxi_grocery_user_profiles, now):
    yandex_login = 'yandex_login0'

    idempotency_token = 'idempotency_token0'
    headers = {
        'X-Idempotency-Token': idempotency_token,
        'X-Yandex-Login': yandex_login,
    }

    banlist_request = {'personal_ids': {}, 'personal_ids_filter': []}

    response = await taxi_grocery_user_profiles.post(
        '/internal/v1/user-profiles/v1/check-user',
        headers=headers,
        json=banlist_request,
    )
    assert response.status_code == 400
