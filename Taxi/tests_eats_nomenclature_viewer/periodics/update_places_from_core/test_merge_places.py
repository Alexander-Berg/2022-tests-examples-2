import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer.periodics.update_places_from_core import (
    constants,
)
from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils

PERIODIC_NAME = constants.PERIODIC_NAME
OLD_TIME = dt.datetime(1999, 3, 2, 12, tzinfo=pytz.UTC)


async def test_merge_update_unchanged(
        taxi_eats_nomenclature_viewer,
        testpoint_periodic_ok,
        mock_core_handler,
        sql,
):
    brand_id = sql.save(models.Brand())

    old_place = models.Place(
        brand_id=brand_id, updated_at=OLD_TIME, is_enabled_changed_at=OLD_TIME,
    )
    sql.save(old_place)

    # save the same data
    mock_core_handler.set_places_to_mock_data([old_place])
    await taxi_eats_nomenclature_viewer.run_distlock_task(PERIODIC_NAME)
    assert testpoint_periodic_ok.has_calls

    db_places = sql.load_all(models.Place)
    assert db_places == [old_place]


@pytest.mark.parametrize(
    'old_value, new_value',
    [
        pytest.param({'slug': 'old_slug'}, {'slug': 'new_slug'}, id='slug'),
        pytest.param(
            {'stock_reset_limit': 0},
            {'stock_reset_limit': 999},
            id='stock_reset_limit',
        ),
    ],
)
async def test_merge_update_changed(
        taxi_eats_nomenclature_viewer,
        mock_core_handler,
        sql,
        testpoint_periodic_ok,
        # parametrize
        old_value,
        new_value,
):
    brand_id = sql.save(models.Brand())

    old_place = models.Place(
        brand_id=brand_id, updated_at=OLD_TIME, **old_value,
    )
    sql.save(old_place)

    # change value
    changed_place = old_place.clone()
    changed_place.updated_at = None
    changed_place.update(new_value)
    mock_core_handler.set_places_to_mock_data([changed_place])
    await taxi_eats_nomenclature_viewer.run_distlock_task(PERIODIC_NAME)
    assert testpoint_periodic_ok.has_calls

    db_places = sql.load_all(models.Place)
    assert len(db_places) == 1
    db_place = db_places[0]

    assert db_place.updated_at > old_place.updated_at
    db_place.updated_at = None
    db_place.is_enabled_changed_at = None
    assert db_place == changed_place


async def test_merge_update_brand(
        taxi_eats_nomenclature_viewer,
        mock_core_handler,
        mockserver,
        sql,
        testpoint_periodic_ok,
):
    brand_id_old = sql.save(models.Brand())
    brand_id_new = sql.save(models.Brand())

    old_place = models.Place(brand_id=brand_id_old, updated_at=OLD_TIME)
    sql.save(old_place)

    brand_id_to_mock_data = {}

    @mockserver.json_handler(constants.CORE_PLACES_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        brand_id = int(request.query['brand_id'])
        if brand_id not in brand_id_to_mock_data:
            return mock_core_handler.generate_mock_data([])
        return brand_id_to_mock_data[brand_id]

    # change value
    changed_place = old_place.clone()
    changed_place.updated_at = None
    changed_place.brand_id = brand_id_new
    brand_id_to_mock_data[brand_id_new] = mock_core_handler.generate_mock_data(
        [changed_place],
    )
    await taxi_eats_nomenclature_viewer.run_distlock_task(PERIODIC_NAME)
    assert testpoint_periodic_ok.has_calls

    db_places = sql.load_all(models.Place)
    assert len(db_places) == 1
    db_place = db_places[0]

    assert db_place.updated_at > old_place.updated_at
    db_place.updated_at = None
    db_place.is_enabled_changed_at = None
    assert db_place == changed_place


@pytest.mark.parametrize(**utils.gen_bool_params('should_be_enabled'))
async def test_merge_update_is_enabled_value(
        taxi_eats_nomenclature_viewer,
        mock_core_handler,
        sql,
        testpoint_periodic_ok,
        # parametrize
        should_be_enabled,
):
    brand_id = sql.save(models.Brand())

    old_place = models.Place(
        brand_id=brand_id,
        is_enabled=not should_be_enabled,
        updated_at=OLD_TIME,
        is_enabled_changed_at=OLD_TIME,
    )
    sql.save(old_place)

    # change is_enabled state
    expected_place = old_place.clone()
    expected_place.updated_at = None
    expected_place.is_enabled_changed_at = None
    expected_place.is_enabled = should_be_enabled

    mock_core_handler.set_places_to_mock_data([expected_place])
    await taxi_eats_nomenclature_viewer.run_distlock_task(PERIODIC_NAME)
    assert testpoint_periodic_ok.has_calls

    db_places = sql.load_all(models.Place)
    assert len(db_places) == 1
    db_place = db_places[0]

    assert db_place.updated_at > old_place.updated_at
    assert db_place.is_enabled_changed_at > old_place.is_enabled_changed_at
    db_place.updated_at = None
    db_place.is_enabled_changed_at = None
    assert db_place == expected_place


async def test_merge_insert(
        taxi_eats_nomenclature_viewer,
        mock_core_handler,
        sql,
        testpoint_periodic_ok,
):
    brand_id = sql.save(models.Brand())

    old_place = models.Place(
        brand_id=brand_id,
        place_id=1,
        slug='slug_1',
        updated_at=OLD_TIME,
        is_enabled_changed_at=OLD_TIME,
    )
    sql.save(old_place)

    # insert new place
    new_place = models.Place(brand_id=brand_id, place_id=2, slug='slug_2')
    mock_core_handler.set_places_to_mock_data([old_place, new_place])
    await taxi_eats_nomenclature_viewer.run_distlock_task(PERIODIC_NAME)
    assert testpoint_periodic_ok.has_calls

    id_to_place = {i.place_id: i for i in sql.load_all(models.Place)}
    assert len(id_to_place) == 2
    db_old_place = id_to_place[old_place.place_id]
    db_new_place = id_to_place[new_place.place_id]

    assert db_old_place == old_place
    assert db_new_place.updated_at > old_place.updated_at
    db_new_place.updated_at = None
    db_new_place.is_enabled_changed_at = None
    assert db_new_place == new_place


async def test_merge_disable_when_missing(
        taxi_eats_nomenclature_viewer,
        mock_core_handler,
        sql,
        testpoint_periodic_ok,
):
    """
    Places that are not recieved from core
    are disabled and not deleted
    """

    brand_id = sql.save(models.Brand())

    old_place_1 = models.Place(
        brand_id=brand_id, updated_at=OLD_TIME, is_enabled_changed_at=OLD_TIME,
    )
    old_place_2 = models.Place(
        brand_id=brand_id, updated_at=OLD_TIME, is_enabled_changed_at=OLD_TIME,
    )
    sql.save(old_place_1)
    sql.save(old_place_2)

    expected_place_2 = old_place_2.clone()
    expected_place_2.updated_at = None
    expected_place_2.is_enabled_changed_at = None
    expected_place_2.is_enabled = False

    # send only place 1, this should disable place 2
    mock_core_handler.set_places_to_mock_data([old_place_1])
    await taxi_eats_nomenclature_viewer.run_distlock_task(PERIODIC_NAME)
    assert testpoint_periodic_ok.has_calls

    id_to_place = {i.place_id: i for i in sql.load_all(models.Place)}
    assert len(id_to_place) == 2
    db_place_1 = id_to_place[old_place_1.place_id]
    db_place_2 = id_to_place[old_place_2.place_id]

    assert db_place_1 == old_place_1
    assert db_place_2.updated_at > old_place_2.updated_at
    assert db_place_2.is_enabled_changed_at > old_place_2.is_enabled_changed_at
    db_place_2.updated_at = None
    db_place_2.is_enabled_changed_at = None
    assert db_place_2 == expected_place_2
