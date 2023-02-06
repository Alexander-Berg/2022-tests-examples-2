import pytest

DEFAULT_SETTINGS = {'renew_subscription_by_plus': False}
DEFAULT_VERSION = '0'


async def test_works(taxi_plus_sweet_home):
    response = await taxi_plus_sweet_home.get(
        '/v1/subscriptions/settings',
        params={'yandex_uid': '123'},
        headers={'content_type': 'application/json'},
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'yandex_uid,expected_version,expected_settings',
    [
        ('yandex-uid-1-False', '1', {'renew_subscription_by_plus': False}),
        ('yandex-uid-2-True', '2', {'renew_subscription_by_plus': True}),
    ],
)
@pytest.mark.pgsql('plus', files=['settings.sql'])
async def test_simple(
        taxi_plus_sweet_home, yandex_uid, expected_version, expected_settings,
):
    response = await taxi_plus_sweet_home.get(
        '/v1/subscriptions/settings',
        params={'yandex_uid': yandex_uid},
        headers={'content_type': 'application/json'},
    )
    assert response.status == 200

    response_data = response.json()
    assert response_data['settings'] == expected_settings
    assert response_data['version'] == expected_version


@pytest.mark.pgsql('plus', files=['settings.sql'])
async def test_default_settings(taxi_plus_sweet_home):
    response = await taxi_plus_sweet_home.get(
        '/v1/subscriptions/settings',
        params={'yandex_uid': 'unknown-uid'},
        headers={'content_type': 'application/json'},
    )

    assert response.status == 200

    response_data = response.json()
    assert response_data['settings'] == DEFAULT_SETTINGS
    assert response_data['version'] == DEFAULT_VERSION
