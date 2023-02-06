import pytest


@pytest.mark.pgsql('reposition', files=['modes.sql'])
@pytest.mark.parametrize(
    'mode,deviation_formulae',
    [
        ('home', ['regular_mode']),
        ('poi', ['regular_mode']),
        ('surge', ['regular_offer_mode', 'surge_mode']),
        ('my_district', ['destination_district_mode', 'area_mode']),
    ],
)
def test_get(taxi_reposition, mode, deviation_formulae):
    response = taxi_reposition.get(
        '/v1/settings/modes/available_deviation_formulae?mode={}'.format(mode),
    )
    assert response.status_code == 200

    data = response.json()
    data['deviation_formulae'].sort()

    assert data == {'deviation_formulae': sorted(deviation_formulae)}


@pytest.mark.nofilldb()
def test_get_errors(taxi_reposition):
    response = taxi_reposition.get(
        '/v1/settings/modes/available_deviation_formulae',
    )
    assert response.status_code == 400

    response = taxi_reposition.get(
        '/v1/settings/modes/available_deviation_formulae?mode=any',
    )
    assert response.status_code == 404
