import pytest

DEFAULT_YANDEX_UID = 'yandex_uid'

HEADERS = {
    'X-SDK-Client-ID': 'taxi.test',
    'X-SDK-Version': '10.10.10',
    'X-Yandex-UID': '111111',
    'X-YaTaxi-Pass-Flags': 'portal,cashback-plus',
    'X-Request-Language': 'ru',
    'X-Remote-IP': '185.15.98.233',
}


async def test_works(taxi_plus_sweet_home):
    response = await taxi_plus_sweet_home.put(
        '/v1/subscriptions/settings',
        params={'yandex_uid': DEFAULT_YANDEX_UID},
        headers={'content_type': 'application/json'},
        json={
            'settings': {'renew_subscription_by_plus': True},
            'version': '1',
        },
    )
    assert response.status == 200
    assert response.json()['settings']['renew_subscription_by_plus'] is True


@pytest.mark.parametrize('renew_subscription', (True, False))
@pytest.mark.pgsql('plus', files=['settings.sql'])
async def test_simple(taxi_plus_sweet_home, renew_subscription, pgsql):
    response = await taxi_plus_sweet_home.put(
        '/v1/subscriptions/settings',
        params={'yandex_uid': DEFAULT_YANDEX_UID},
        headers={'content_type': 'application/json'},
        json={
            'settings': {'renew_subscription_by_plus': renew_subscription},
            'version': '1',
        },
    )
    assert response.status == 200

    given_settings = response.json()['settings']
    assert given_settings['renew_subscription_by_plus'] == renew_subscription

    cursor = pgsql['plus'].cursor()
    cursor.execute(
        """
        SELECT
         yandex_uid,
         version,
         renew_subscription_by_plus
        FROM plus.user_settings
        WHERE yandex_uid = 'yandex_uid'
        """,
    )
    result = cursor.fetchall()
    assert len(result) == 1
    assert result[0][2] == renew_subscription


@pytest.mark.pgsql('plus', files=['settings.sql'])
async def test_conflict_error(taxi_plus_sweet_home):
    response = await taxi_plus_sweet_home.put(
        '/v1/subscriptions/settings',
        params={'yandex_uid': 'yandex-uid-1-False'},
        headers={'content_type': 'application/json'},
        json={
            'settings': {'renew_subscription_by_plus': True},
            'version': '10',
        },
    )
    assert response.status == 409


@pytest.mark.pgsql('plus', files=['settings.sql'])
async def test_success_changes_preferences(taxi_plus_sweet_home):
    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v1/user/preferences/changes',
        params={'yandex_uid': DEFAULT_YANDEX_UID},
        headers=HEADERS,
        json={
            'changes': [
                {
                    'type': 'update',
                    'setting_id': 'subscription_renewal_for_points',
                    'value': True,
                },
            ],
            'version': '0',
        },
    )
    assert response.status == 200
    assert len(response.json()['settings']) == 1
    assert response.json()['settings'][0] == {
        'setting_id': 'subscription_renewal_for_points',
        'type': 'boolean',
        'value': True,
        'is_local': False,
        'enabled': True,
    }


@pytest.mark.pgsql('plus', files=['settings.sql'])
async def test_partial_change_of_settings(taxi_plus_sweet_home):
    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v1/user/preferences/changes',
        params={'yandex_uid': DEFAULT_YANDEX_UID},
        headers=HEADERS,
        json={
            'changes': [
                {
                    'type': 'update',
                    'setting_id': 'subscription_renewal_for_points',
                    'value': True,
                },
                {
                    'type': 'update',
                    'setting_id': 'unknown_setting',
                    'value': True,
                },
            ],
            'version': '0',
        },
    )
    assert response.status == 200
    assert len(response.json()['settings']) == 1
    assert response.json()['settings'][0] == {
        'setting_id': 'subscription_renewal_for_points',
        'type': 'boolean',
        'value': True,
        'is_local': False,
        'enabled': True,
    }
