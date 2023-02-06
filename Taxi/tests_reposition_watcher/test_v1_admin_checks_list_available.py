import pytest


@pytest.mark.pgsql('reposition_watcher', files=['modes_zones.sql'])
@pytest.mark.parametrize(
    'mode,checks',
    [
        (
            'District',
            [
                'duration',
                'immobility',
                'route',
                'out_of_area',
                'transporting_arrival',
            ],
        ),
        (
            'home',
            [
                'duration',
                'immobility',
                'route',
                'arrival',
                'transporting_arrival',
            ],
        ),
        (
            'surge',
            [
                'duration',
                'immobility',
                'route',
                'arrival',
                'antisurge_arrival',
                'surge_arrival_local',
                'transporting_arrival',
            ],
        ),
    ],
)
async def test_get(taxi_reposition_watcher, mode, checks):
    response = await taxi_reposition_watcher.get(
        f'/v1/admin/checks/list_available?mode={mode}',
    )
    assert response.status == 200
    assert sorted(response.json()['checks']) == sorted(checks)


@pytest.mark.nofilldb()
async def test_get_errors(taxi_reposition_watcher):
    response = await taxi_reposition_watcher.get(
        '/v1/admin/checks/list_available/',
    )
    assert response.status == 400

    response = await taxi_reposition_watcher.get(
        '/v1/admin/checks/list_available?mode=any',
    )
    assert response.status == 400
