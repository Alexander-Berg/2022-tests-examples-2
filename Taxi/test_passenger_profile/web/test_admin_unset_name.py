import pytest

from test_passenger_profile import common


@pytest.mark.parametrize(
    ['brand', 'application', 'rating'],
    [['yataxi', 'yataxi', '4.90'], ['yauber', 'mobileweb_uber', '4.10']],
)
@common.mark_passenger_profile_experiment(yandex_uid='10002')
async def test_admin_unset_name(web_app_client, brand, application, rating):

    test_yandex_uid = '10002'
    query = {'yandex_uid': test_yandex_uid, 'brand': brand}
    response = await web_app_client.post('/v1/admin/unset-name', params=query)

    assert response.status == 200

    control = await web_app_client.get(
        '/passenger-profile/v1/profile',
        params={'yandex_uid': test_yandex_uid, 'application': application},
    )

    assert control.status == 200

    control_data = await control.json()

    assert 'first_name' not in control_data
    assert control_data['rating'] == rating


async def test_admin_unset_empty(web_app_client):

    response = await web_app_client.post(
        '/v1/admin/unset-name', params={'yandex_uid': '', 'brand': ''},
    )

    assert response.status == 409


async def test_admin_unset_no_profile(web_app_client):

    response = await web_app_client.post(
        '/v1/admin/unset-name',
        params={'yandex_uid': '10005', 'brand': 'yataxi'},
    )

    assert response.status == 409
