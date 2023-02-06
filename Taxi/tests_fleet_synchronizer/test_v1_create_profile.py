import pytest

FLEET_TYPE_VEZET = 'vezet'
REQUEST_OK = {
    'park_id': 'ParkOne',
    'driver_id': 'DriverOne',
    'car_id': 'CarOne',
    'app_family': FLEET_TYPE_VEZET,
}
ENDPOINT_URL = '/v1/profile/create'


@pytest.fixture(autouse=True)
def mock_selfemployed(mockserver):
    @mockserver.json_handler(
        '/selfemployed/selfemployed/service/v1/sync/driver',
    )
    def _sync_driver_handler(request):
        return


@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    queries=[
        f"""
        INSERT INTO fleet_sync.parks_mappings
          (park_id, mapped_park_id, app_family)
        VALUES
          ('ParkOne', 'ParkOneVezet', '{FLEET_TYPE_VEZET}')
        ON CONFLICT DO NOTHING;""",
    ],
)
async def test_create_profile(taxi_fleet_synchronizer, mongodb):
    assert len(list(mongodb.dbdrivers.find({}))) == 1
    assert len(list(mongodb.dbcars.find({}))) == 1

    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json=REQUEST_OK,
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert response.json()['mapped_park_id'] == 'ParkOneVezet'

    assert len(list(mongodb.dbdrivers.find({}))) == 2
    assert len(list(mongodb.dbcars.find({}))) == 2
    drivers = list(mongodb.dbdrivers.find({'fleet_type': FLEET_TYPE_VEZET}))
    assert len(drivers) == 1
    assert drivers[0]['park_id'] == 'ParkOneVezet'
    cars = list(mongodb.dbcars.find({'fleet_type': FLEET_TYPE_VEZET}))
    assert len(cars) == 1


@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    queries=[
        f"""
        INSERT INTO fleet_sync.parks_mappings
          (park_id, mapped_park_id, app_family)
        VALUES
          ('ParkOne', 'ParkOneVezet', '{FLEET_TYPE_VEZET}')
        ON CONFLICT DO NOTHING;""",
    ],
)
@pytest.mark.config(FLEET_SYNCHRONIZER_LOGIN_TIMEOUT={'timeout_seconds': 200})
async def test_timeout(taxi_fleet_synchronizer, mongodb):
    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json=REQUEST_OK,
        headers={'Content-Type': 'application/json'},
    )
    assert response.json()['eta_minutes'] == 4


async def test_no_mapped_park(taxi_fleet_synchronizer, mongodb):
    assert len(list(mongodb.dbdrivers.find({}))) == 1
    assert len(list(mongodb.dbcars.find({}))) == 1

    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json=REQUEST_OK,
        headers={'Content-Type': 'application/json'},
    )

    assert len(list(mongodb.dbdrivers.find({}))) == 1
    assert len(list(mongodb.dbcars.find({}))) == 1
    assert response.status_code == 400
    assert response.json()['code'] == 'no_mapped_park'


@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    queries=[
        f"""
        INSERT INTO fleet_sync.parks_mappings
          (park_id, mapped_park_id, app_family)
        VALUES
          ('ParkTwo', 'ParkTwoVezet', '{FLEET_TYPE_VEZET}')
        ON CONFLICT DO NOTHING;""",
    ],
)
async def test_mapped_not_active(taxi_fleet_synchronizer, mongodb):
    assert len(list(mongodb.dbdrivers.find({}))) == 1
    assert len(list(mongodb.dbcars.find({}))) == 1

    mongodb.dbparks.insert_one(
        {
            '_id': 'ParkTwoVezet',
            'city': 'CityOne',
            'login': 'loginTwo - Таксометр X',
            'name': 'ParkNameTwo - Таксометр X',
            'fleet_type': FLEET_TYPE_VEZET,
            'is_active': False,
        },
    )
    await taxi_fleet_synchronizer.invalidate_caches()

    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json={
            'park_id': 'ParkTwo',
            'driver_id': 'DriverTwo',
            'car_id': 'CarTwo',
            'app_family': FLEET_TYPE_VEZET,
        },
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'no_mapped_park',
        'message': 'Failed to get park id',
    }
