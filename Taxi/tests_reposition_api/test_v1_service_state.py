# pylint: disable=C5521
import pytest


@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
    ],
)
async def test_state(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/state',
        json={'park_db_id': 'dbid777', 'driver_id': 'uuid'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_session': True,
        'active': True,
        'mode': 'poi',
        'point': [37.617664, 55.752121],
    }


@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
    ],
)
async def test_state_with_submodule(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/state',
        json={'park_db_id': 'dbid777', 'driver_id': 'uuid3'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_session': True,
        'active': True,
        'mode': 'poi',
        'submode': 'fast',
        'point': [3, 4],
    }


@pytest.mark.now('2018-10-12T19:04:45+0300')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
        'home_bonus.sql',
    ],
)
async def test_state_with_bonus(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/state',
        json={'park_db_id': 'dbid777', 'driver_id': '888'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_session': True,
        'active': True,
        'mode': 'home',
        'bonus': {'until': '2018-10-12T16:22:45.540859+0000'},
        'point': [3, 7],
    }


@pytest.mark.now('2018-10-12T19:04:45+0300')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
        'inactive_session.sql',
    ],
)
async def test_state_inactive(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/state',
        json={'park_db_id': '1488', 'driver_id': 'driverSS'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_session': True,
        'active': False,
        'mode': 'home',
        'point': [3, 5],
    }


@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
    ],
)
async def test_no_state(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/state',
        json={'park_db_id': 'dbid777', 'driver_id': '888'},
    )
    assert response.status_code == 200
    assert response.json() == {'has_session': False}


@pytest.mark.now('2018-10-12T19:04:45+0300')
async def test_invalid_driver_id(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/state',
        json={'park_db_id': '1337', 'driver_id': 'driverSS'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'UNKNOWN_DRIVER_ID',
        'message': 'Unknown driver_id 1337_driverSS, try again later',
    }
