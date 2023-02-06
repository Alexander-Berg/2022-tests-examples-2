import pytest


@pytest.mark.now('2018-09-06T11:00:00+0300')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_surge.sql',
        'mode_poi.sql',
        'simple.sql',
    ],
)
async def test_simple_check(taxi_reposition_api, load_json):
    response = await taxi_reposition_api.get(
        '/v1/admin/drivers/locations?park_id=pg_park'
        '&driver_profile_id=pg_driver',
        {},
    )

    assert response.status == 200
    assert response.json() == load_json('data_simple.json')


@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'rules.sql',
        'points.sql',
    ],
)
async def test_get_modes(taxi_reposition_api, load_json):
    response = await taxi_reposition_api.get(
        '/v1/admin/drivers/locations?park_id=1488&driver_profile_id=driverSS',
        {},
    )
    assert response.status == 200
    data = load_json('data.json')
    resp = response.json()

    data['poi']['locations'].sort(key=lambda x: x['name'])
    resp['poi']['locations'].sort(key=lambda x: x['name'])

    assert resp == data


@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'zone_default.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'rules.sql',
    ],
)
async def test_get_modes_no_settings(taxi_reposition_api):
    response = await taxi_reposition_api.get(
        '/v1/admin/drivers/locations?park_id=1488&driver_profile_id=driverSS2',
        {},
    )
    assert response.status == 200
    assert response.json() == {
        'home': {'locations': []},
        'poi': {'locations': []},
    }


@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'mode_surge.sql', 'simple.sql'],
)
@pytest.mark.now('2018-09-06T11:00:00+0300')
async def test_mode_offer_radius(taxi_reposition_api):
    response = await taxi_reposition_api.get(
        '/v1/admin/drivers/locations?park_id=pg_park'
        '&driver_profile_id=pg_driver',
        {},
    )
    assert response.status == 200
    resp = response.json()
    assert (
        resp['surge']['locations'][0]['offer']['destination_radius'] == 10000.0
    )
