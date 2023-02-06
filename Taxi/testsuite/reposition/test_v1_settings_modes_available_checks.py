import pytest


@pytest.mark.pgsql('reposition', files=['modes.sql'])
@pytest.mark.parametrize(
    'mode,checks',
    [
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
            'poi',
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
        (
            'my_district',
            [
                'duration',
                'immobility',
                'route',
                'out_of_area',
                'transporting_arrival',
            ],
        ),
    ],
)
def test_get(taxi_reposition, mode, checks):
    response = taxi_reposition.get(
        '/v1/settings/modes/available_checks?mode={}'.format(mode),
    )
    assert response.status_code == 200

    data = response.json()
    data['checks'].sort()

    assert data == {'checks': sorted(checks)}


@pytest.mark.nofilldb()
def test_get_errors(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/modes/available_checks')
    assert response.status_code == 400

    response = taxi_reposition.get(
        '/v1/settings/modes/available_checks?mode=any',
    )
    assert response.status_code == 404
