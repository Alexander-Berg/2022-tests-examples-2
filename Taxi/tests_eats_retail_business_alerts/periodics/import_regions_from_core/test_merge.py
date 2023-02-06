import datetime as dt
from typing import List

import pytest
import pytz

from tests_eats_retail_business_alerts import models

CORE_REGIONS_HANDLER = '/eats-core/v1/export/regions'
PERIODIC_NAME = 'import-regions-from-core-periodic'
OLD_TIME = dt.datetime(1999, 3, 2, 12, tzinfo=pytz.UTC)


async def test_merge_update_unchanged(
        assert_objects_lists_equal,
        taxi_eats_retail_business_alerts,
        mockserver,
        sql,
):
    core_data = []

    @mockserver.json_handler(CORE_REGIONS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'payload': core_data}

    old_region = models.Region(updated_at=OLD_TIME)
    sql.save(old_region)

    # save the same data
    core_data = _generate_mock_data([old_region])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    db_regions = sql.load_all(models.Region)
    assert_objects_lists_equal(db_regions, [old_region])


@pytest.mark.parametrize(
    'changed_value',
    [
        pytest.param({'slug': 'new_slug'}, id='slug'),
        pytest.param({'name': 'New Name'}, id='name'),
    ],
)
async def test_merge_update_changed(
        assert_objects_equal_without,
        taxi_eats_retail_business_alerts,
        mockserver,
        sql,
        # parametrize
        changed_value,
):
    core_data = []

    @mockserver.json_handler(CORE_REGIONS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'payload': core_data}

    old_region = models.Region(updated_at=OLD_TIME)
    sql.save(old_region)

    # change value
    changed_region = old_region.clone()
    changed_region.update(changed_value)
    changed_region.updated_at = None
    core_data = _generate_mock_data([changed_region])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    db_regions = sql.load_all(models.Region)
    assert len(db_regions) == 1
    db_region = db_regions[0]

    assert db_region.updated_at > old_region.updated_at
    assert_objects_equal_without(db_region, changed_region, ['updated_at'])


async def test_merge_insert(
        assert_objects_equal_without,
        taxi_eats_retail_business_alerts,
        mockserver,
        sql,
):
    core_data = []

    @mockserver.json_handler(CORE_REGIONS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'payload': core_data}

    old_region = models.Region(region_id=1, slug='slug_1', updated_at=OLD_TIME)
    sql.save(old_region)

    # insert new region
    new_region = models.Region(region_id=2, slug='slug_2')
    core_data = _generate_mock_data([old_region, new_region])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    id_to_region = {i.region_id: i for i in sql.load_all(models.Region)}
    assert len(id_to_region) == 2
    db_old_region = id_to_region[old_region.region_id]
    db_new_region = id_to_region[new_region.region_id]

    assert db_old_region == old_region
    assert db_new_region.updated_at > old_region.updated_at
    assert_objects_equal_without(db_new_region, new_region, ['updated_at'])


async def test_merge_enable(
        assert_objects_equal_without,
        taxi_eats_retail_business_alerts,
        mockserver,
        sql,
):
    core_data = []

    @mockserver.json_handler(CORE_REGIONS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'payload': core_data}

    old_region_1 = models.Region(updated_at=OLD_TIME)
    old_region_2 = models.Region(is_enabled=False, updated_at=OLD_TIME)
    sql.save(old_region_1)
    sql.save(old_region_2)

    expected_region_2 = old_region_2.clone()
    expected_region_2.is_enabled = True
    expected_region_2.updated_at = None

    # send two regions, should enable both
    core_data = _generate_mock_data([old_region_1, old_region_2])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    id_to_region = {i.region_id: i for i in sql.load_all(models.Region)}
    assert len(id_to_region) == 2
    db_region_1 = id_to_region[old_region_1.region_id]
    db_region_2 = id_to_region[old_region_2.region_id]

    assert db_region_1 == old_region_1
    assert db_region_2.updated_at > old_region_2.updated_at
    assert_objects_equal_without(
        db_region_2, expected_region_2, ['updated_at'],
    )


async def test_merge_disable(
        assert_objects_equal_without,
        taxi_eats_retail_business_alerts,
        mockserver,
        sql,
):
    """
    Regions that are not received from core
    are disabled and not deleted
    """

    core_data = []

    @mockserver.json_handler(CORE_REGIONS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'payload': core_data}

    old_region_1 = models.Region(updated_at=OLD_TIME)
    old_region_2 = models.Region(updated_at=OLD_TIME)
    sql.save(old_region_1)
    sql.save(old_region_2)

    expected_region_2 = old_region_2.clone()
    expected_region_2.is_enabled = False
    expected_region_2.updated_at = None

    # send only region 1, this should disable region 2
    core_data = _generate_mock_data([old_region_1])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    id_to_region = {i.region_id: i for i in sql.load_all(models.Region)}
    assert len(id_to_region) == 2
    db_region_1 = id_to_region[old_region_1.region_id]
    db_region_2 = id_to_region[old_region_2.region_id]

    assert db_region_1 == old_region_1
    assert db_region_2.updated_at > old_region_2.updated_at
    assert_objects_equal_without(
        db_region_2, expected_region_2, ['updated_at'],
    )


def _generate_mock_data(data: List[models.Region]):
    return [
        {
            'id': i.region_id,
            'slug': i.slug,
            'name': i.name,
            'genitive': i.name,
            'isAvailable': True,
            'isDefault': False,
            'bbox': [35.918658, 54.805858, 39.133684, 56.473673],
            'center': [37.642806, 55.724266],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [999],
            'country': {'code': 'RU', 'id': 1, 'name': 'Российская Федерация'},
        }
        for i in data
    ]
