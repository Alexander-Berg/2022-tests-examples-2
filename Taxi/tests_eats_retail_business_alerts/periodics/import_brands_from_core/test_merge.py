import datetime as dt
from typing import List

import pytest
import pytz

from tests_eats_retail_business_alerts import models

CORE_BRANDS_HANDLER = '/eats-core-retail/v1/brands/retrieve'
PERIODIC_NAME = 'import-brands-from-core-periodic'
OLD_TIME = dt.datetime(1999, 3, 2, 12, tzinfo=pytz.UTC)


async def test_merge_update_unchanged(
        assert_objects_lists_equal,
        taxi_eats_retail_business_alerts,
        mockserver,
        sql,
):
    core_data = []

    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'brands': core_data}

    old_brand = models.Brand(updated_at=OLD_TIME)
    sql.save(old_brand)

    # save the same data
    core_data = _generate_mock_data([old_brand])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    db_brands = sql.load_all(models.Brand)
    assert_objects_lists_equal(db_brands, [old_brand])


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

    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'brands': core_data}

    old_brand = models.Brand(updated_at=OLD_TIME)
    sql.save(old_brand)

    # change value
    changed_brand = old_brand.clone()
    changed_brand.update(changed_value)
    changed_brand.updated_at = None
    core_data = _generate_mock_data([changed_brand])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    db_brands = sql.load_all(models.Brand)
    assert len(db_brands) == 1
    db_brand = db_brands[0]

    assert db_brand.updated_at > old_brand.updated_at
    assert_objects_equal_without(db_brand, changed_brand, ['updated_at'])


async def test_merge_insert(
        assert_objects_equal_without,
        taxi_eats_retail_business_alerts,
        mockserver,
        sql,
):
    core_data = []

    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'brands': core_data}

    old_brand = models.Brand(brand_id=1, slug='slug_1', updated_at=OLD_TIME)
    sql.save(old_brand)

    # insert new brand
    new_brand = models.Brand(brand_id=2, slug='slug_2')
    core_data = _generate_mock_data([old_brand, new_brand])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    id_to_brand = {i.brand_id: i for i in sql.load_all(models.Brand)}
    assert len(id_to_brand) == 2
    db_old_brand = id_to_brand[old_brand.brand_id]
    db_new_brand = id_to_brand[new_brand.brand_id]

    assert db_old_brand == old_brand
    assert db_new_brand.updated_at > old_brand.updated_at
    assert_objects_equal_without(db_new_brand, new_brand, ['updated_at'])


async def test_merge_enable(
        assert_objects_equal_without,
        taxi_eats_retail_business_alerts,
        mockserver,
        sql,
):
    core_data = []

    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'brands': core_data}

    old_brand_1 = models.Brand(updated_at=OLD_TIME)
    old_brand_2 = models.Brand(is_enabled=False, updated_at=OLD_TIME)
    sql.save(old_brand_1)
    sql.save(old_brand_2)

    expected_brand_2 = old_brand_2.clone()
    expected_brand_2.is_enabled = True
    expected_brand_2.updated_at = None

    # send two brands, should enable both
    core_data = _generate_mock_data([old_brand_1, old_brand_2])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    id_to_brand = {i.brand_id: i for i in sql.load_all(models.Brand)}
    assert len(id_to_brand) == 2
    db_brand_1 = id_to_brand[old_brand_1.brand_id]
    db_brand_2 = id_to_brand[old_brand_2.brand_id]

    assert db_brand_1 == old_brand_1
    assert db_brand_2.updated_at > old_brand_2.updated_at
    assert_objects_equal_without(db_brand_2, expected_brand_2, ['updated_at'])


async def test_merge_disable(
        assert_objects_equal_without,
        taxi_eats_retail_business_alerts,
        mockserver,
        sql,
):
    """
    Brands that are not received from core
    are disabled and not deleted
    """

    core_data = []

    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'brands': core_data}

    old_brand_1 = models.Brand(updated_at=OLD_TIME)
    old_brand_2 = models.Brand(updated_at=OLD_TIME)
    sql.save(old_brand_1)
    sql.save(old_brand_2)

    expected_brand_2 = old_brand_2.clone()
    expected_brand_2.is_enabled = False
    expected_brand_2.updated_at = None

    # send only brand 1, this should disable brand 2
    core_data = _generate_mock_data([old_brand_1])
    await taxi_eats_retail_business_alerts.run_distlock_task(PERIODIC_NAME)

    id_to_brand = {i.brand_id: i for i in sql.load_all(models.Brand)}
    assert len(id_to_brand) == 2
    db_brand_1 = id_to_brand[old_brand_1.brand_id]
    db_brand_2 = id_to_brand[old_brand_2.brand_id]

    assert db_brand_1 == old_brand_1
    assert db_brand_2.updated_at > old_brand_2.updated_at
    assert_objects_equal_without(db_brand_2, expected_brand_2, ['updated_at'])


def _generate_mock_data(data: List[models.Brand]):
    return [
        {'id': str(i.brand_id), 'slug': i.slug, 'name': i.name} for i in data
    ]
