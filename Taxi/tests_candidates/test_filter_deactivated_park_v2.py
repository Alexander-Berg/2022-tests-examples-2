import pytest


async def test_park_deactivated(taxi_candidates, driver_positions):
    # dbid1_uuid3 drivers park(clid1) deactivated
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/deactivated_park_v2'],
        'point': [55, 35],
        'payment_method': 'card',
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert drivers[0]['uuid'] == 'uuid0'


@pytest.mark.parametrize(
    ('allow',),
    (
        pytest.param(
            True,
            marks=(
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'courier_service_id_1': {'region_id_2': 'dbid1'},
                    },
                )
            ),
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'selfemployed': 'dbid1',
                        'selfemployed_by_country': {'RU': 'dbid1'},
                    },
                )
            ),
        ),
        pytest.param(
            False, marks=(pytest.mark.config(EATS_COURIER_SERVICE_MAPPING={})),
        ),
        pytest.param(False),
    ),
)
async def test_park_deactivated_eats_service(
        taxi_candidates, driver_positions, allow,
):
    # dbid1_uuid3 drivers park(clid1) deactivated
    await driver_positions(
        [{'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/deactivated_park_v2'],
        'point': [55, 35],
        'payment_method': 'card',
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    if allow:
        assert len(drivers) == 1
        assert drivers[0]['uuid'] == 'uuid3'
    else:
        assert not drivers
