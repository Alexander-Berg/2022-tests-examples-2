import pytest

from tests_scooters_misc import common


@common.TRANSLATIONS
@pytest.mark.experiments3(filename='config3_scooters_shortcuts.json')
async def test_shortcuts(taxi_scooters_misc, load_json):
    resp = await taxi_scooters_misc.post(
        '/scooters-misc/v1/shortcuts', headers={'Accept-Language': 'ru-ru'},
    )
    assert resp.status == 200
    assert resp.json() == load_json('expected_scooters_shortcuts.json')


async def test_shortcuts_no_exp(taxi_scooters_misc):
    resp = await taxi_scooters_misc.post(
        '/scooters-misc/v1/shortcuts', headers={'Accept-Language': 'ru-ru'},
    )
    assert resp.status == 200
    assert resp.json() == {'scenario_tops': []}
