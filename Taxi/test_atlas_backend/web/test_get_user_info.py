import pytest


async def test_get_user_info(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.get('/api/user-info')
    assert response.status == 200
    content = await response.json()

    assert content['login'] == 'omnipotent_user'
    assert content['events'] is True
    assert content['autoupdate'] is True
    assert content['monitoring'] is True
    assert content['access_restricted'] is True
    assert content['car_map'] is True
    assert content['superuser'] is True
    assert content['main'] is True
    assert content['ivr'] is True
    assert content['reposition_manager'] is True
    assert content['anomaly_viewer'] is True
    assert content['anomaly_admin'] is True
    assert content['detailed_data_taxi_orders'] is True
    assert content['metrics_admin'] is True
    assert content['atlas_foodtech_monitoring'] is True
    assert content['car_map_driver_phones'] is True
    assert content['cities'] == []
    assert content['restricted_cities'] == []
    assert content['restricted_preset_cities'] == []


@pytest.mark.parametrize('username', ['city_user'])
async def test_get_user_info_city_user(
        web_app_client, atlas_blackbox_mock, username,
):
    response = await web_app_client.get('/api/user-info')
    assert response.status == 200
    content = await response.json()

    assert content['login'] == 'city_user'
    assert content['events'] is False
    assert content['autoupdate'] is False
    assert content['monitoring'] is False
    assert content['access_restricted'] is False
    assert content['car_map'] is False
    assert content['superuser'] is False
    assert content['main'] is False
    assert content['ivr'] is False
    assert content['reposition_manager'] is False
    assert content['anomaly_viewer'] is False
    assert content['anomaly_admin'] is False
    assert content['detailed_data_taxi_orders'] is False
    assert content['metrics_admin'] is False
    assert content['atlas_foodtech_monitoring'] is False
    assert content['car_map_driver_phones'] is False
    assert set(content['cities']) == {'Москва', 'Казань'}
    assert set(content['restricted_cities']) == {'Москва', 'Казань'}
    assert content['restricted_preset_cities'] == []


@pytest.mark.parametrize('username', ['preset_user'])
async def test_get_user_info_preset_user(
        web_app_client, atlas_blackbox_mock, username,
):
    response = await web_app_client.get('/api/user-info')
    assert response.status == 200
    content = await response.json()

    assert content['login'] == 'preset_user'
    assert content['events'] is False
    assert content['autoupdate'] is False
    assert content['monitoring'] is False
    assert content['access_restricted'] is False
    assert content['car_map'] is False
    assert content['superuser'] is False
    assert content['main'] is False
    assert content['ivr'] is False
    assert content['reposition_manager'] is False
    assert content['anomaly_viewer'] is False
    assert content['anomaly_admin'] is False
    assert content['detailed_data_taxi_orders'] is False
    assert content['metrics_admin'] is False
    assert content['atlas_foodtech_monitoring'] is False
    assert content['car_map_driver_phones'] is False
    assert set(content['cities']) == {'Москва', 'Казань'}
    assert content['restricted_cities'] == []
    assert content['restricted_preset_cities'] == [
        {'cities': ['Москва', 'Казань'], 'name': 'RTT Experiment 2'},
    ]


@pytest.mark.parametrize('username', ['metrics_edit_protected_user'])
async def test_get_user_info_metrics_edit_protected_user(
        web_app_client, atlas_blackbox_mock, username,
):
    response = await web_app_client.get('/api/user-info')
    assert response.status == 200
    content = await response.json()
    assert content['edit_protected_metrics'] == ['z_edit_protected_metric']


@pytest.mark.parametrize('username', ['metrics_view_protected_group_user'])
async def test_get_user_info_metrics_view_protected_group_user(
        web_app_client, atlas_blackbox_mock, username,
):
    response = await web_app_client.get('/api/user-info')
    assert response.status == 200
    content = await response.json()
    assert content['view_protected_metric_groups'] == ['ci_kd']


async def test_get_user_info_no_login(web_app_client):
    response = await web_app_client.get(
        '/api/user-info', allow_redirects=False,
    )
    assert response.status == 302
    assert 'Location' in response.headers
    assert response.headers['Location'] == 'https://passport.yandex-team.ru'


async def test_user_info_unchanged_cities(web_app_client, mockserver):
    blackbox_data = {'uid': {'value': '01234'}, 'status': {'value': 'VALID'}}

    @mockserver.json_handler('/passport-yateam/blackbox')
    async def handler(request):  # pylint: disable=unused-variable
        assert request.query['method'] == 'sessionid'
        assert request.query['sessionid'] == ''
        assert request.query['userip'] == '127.0.0.1'

        return blackbox_data

    blackbox_data['login'] = 'car_map_user'
    response = await web_app_client.get('/api/user-info')
    assert response.status == 200
    car_map_user_1 = await response.json()
    assert car_map_user_1['car_map'] is True
    assert set(car_map_user_1['cities']) == set()

    blackbox_data['login'] = 'city_user'
    response = await web_app_client.get('/api/user-info')
    assert response.status == 200
    city_user = await response.json()
    assert city_user['car_map'] is False
    assert set(city_user['cities']) == {'Москва', 'Казань'}

    blackbox_data['login'] = 'car_map_user'
    response = await web_app_client.get('/api/user-info')
    assert response.status == 200
    car_map_user_2 = await response.json()
    assert car_map_user_2['car_map'] is True
    assert set(car_map_user_2['cities']) == set()
