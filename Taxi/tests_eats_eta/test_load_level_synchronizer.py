import pytest

from . import utils


PERIODIC_NAME = 'load-level-synchronizer'


@utils.eats_eta_settings_config3()
async def test_load_level_synchronizer_empty_db(
        taxi_eats_eta, db_select_places,
):
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_places() == []


@utils.eats_eta_settings_config3(load_level_batch_size=2)
@pytest.mark.config(
    EATS_ETA_PERIODICS_SETTINGS={
        '__default__': {'tasks_count': 3, 'interval': 1},
    },
)
async def test_load_level_synchronizer_surge_errors(
        mockserver,
        load_json,
        taxi_eats_eta,
        make_place,
        db_insert_place,
        db_select_places,
):
    places = [make_place(id=i) for i in range(5)]
    for place in places:
        db_insert_place(place)

    @mockserver.json_handler('/eats-surge-resolver/api/v1/surge-level')
    def mock_surge_level(request):
        return mockserver.make_response(
            status=200, json=load_json('surge_error.json'),
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_places() == places
    assert mock_surge_level.times_called == 3


@utils.eats_eta_settings_config3(load_level_batch_size=1)
@pytest.mark.config(
    EATS_ETA_PERIODICS_SETTINGS={
        '__default__': {'tasks_count': 2, 'interval': 1},
    },
)
async def test_load_level_synchronizer_happy_path(
        now_utc,
        surge_resolver,
        load_json,
        taxi_eats_eta,
        make_place,
        db_insert_place,
        db_select_places,
):
    places = [make_place(id=i) for i in range(5)]
    for place in places:
        db_insert_place(place)

        surge_resolver.add_place(place_id=place['id'])

        surge = load_json('surge.json')
        place['load_level'] = surge['nativeInfo']['loadLevel']
        place['load_level_updated_at'] = now_utc

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_places() == places
    assert surge_resolver.mock_surge_level.times_called == 5
