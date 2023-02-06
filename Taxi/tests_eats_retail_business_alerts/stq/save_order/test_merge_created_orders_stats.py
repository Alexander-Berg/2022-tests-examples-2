import datetime as dt

import pytest
import pytz

from tests_eats_retail_business_alerts import models

OLD_TIME = dt.datetime(1999, 3, 2, 12, tzinfo=pytz.UTC)
MOCK_NOW = dt.datetime(2022, 4, 10, 15, tzinfo=pytz.UTC)


@pytest.mark.now(MOCK_NOW.isoformat())
async def test_insert_stats(assert_objects_equal_without, sql, stq_runner):
    brand_id = sql.save(models.Brand())
    region_id = sql.save(models.Region())
    place_id_1 = sql.save(models.Place(brand_id=brand_id, region_id=region_id))
    place_id_2 = sql.save(models.Place(brand_id=brand_id, region_id=region_id))

    old_stats = models.PlaceCreatedOrdersStats(
        place_id=place_id_1, updated_at=OLD_TIME,
    )
    sql.save(old_stats)

    old_stats_history = models.PlaceCreatedOrdersStatsHistory(
        place_id=place_id_1, updated_at=OLD_TIME,
    )
    sql.save(old_stats_history)

    new_orders_count = 1
    new_last_date_in_msc = '2022-04-10'
    new_stats = models.PlaceCreatedOrdersStats(
        place_id=place_id_2,
        orders_count=new_orders_count,
        last_date_in_msc=new_last_date_in_msc,
    )
    new_stats_history = models.PlaceCreatedOrdersStatsHistory(
        place_id=place_id_2,
        orders_count=new_orders_count,
        last_date_in_msc=new_last_date_in_msc,
    )
    await stq_runner.eats_retail_business_alerts_save_order.call(
        task_id='1',
        kwargs={'place_id': new_stats.place_id, 'order_nr': 'new_order'},
    )

    # stats
    place_id_to_stats = {
        i.place_id: i for i in sql.load_all(models.PlaceCreatedOrdersStats)
    }
    assert len(place_id_to_stats) == 2
    db_old_stats = place_id_to_stats[old_stats.place_id]
    db_new_stats = place_id_to_stats[new_stats.place_id]

    assert db_old_stats == old_stats
    assert db_new_stats.updated_at > old_stats.updated_at
    assert_objects_equal_without(db_new_stats, new_stats, ['updated_at'])

    # history
    id_to_stats_history = {
        i.record_id: i
        for i in sql.load_all(models.PlaceCreatedOrdersStatsHistory)
    }
    assert len(id_to_stats_history) == 2
    db_old_stats_history = id_to_stats_history[old_stats_history.record_id]
    db_new_stats_history = id_to_stats_history[new_stats_history.record_id]

    assert db_old_stats_history == old_stats_history
    assert db_new_stats_history.updated_at > old_stats_history.updated_at
    assert_objects_equal_without(
        db_new_stats_history, new_stats_history, ['updated_at'],
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'old_values, new_values',
    [
        pytest.param(
            {'orders_count': 5, 'last_date_in_msc': '2022-04-10'},
            {'orders_count': 6, 'last_date_in_msc': '2022-04-10'},
            id='same_date',
        ),
        pytest.param(
            {'orders_count': 5, 'last_date_in_msc': '2022-04-09'},
            {'orders_count': 1, 'last_date_in_msc': '2022-04-10'},
            id='date_before_today',
        ),
    ],
)
async def test_update_stats(
        assert_objects_equal_without,
        sql,
        stq_runner,
        # parametrize params
        old_values,
        new_values,
):
    brand_id = sql.save(models.Brand())
    region_id = sql.save(models.Region())
    place_id_1 = sql.save(models.Place(brand_id=brand_id, region_id=region_id))
    place_id_2 = sql.save(models.Place(brand_id=brand_id, region_id=region_id))

    old_stats_1 = models.PlaceCreatedOrdersStats(
        place_id=place_id_1, updated_at=OLD_TIME,
    )
    old_stats_2 = models.PlaceCreatedOrdersStats(
        place_id=place_id_2, updated_at=OLD_TIME, **old_values,
    )
    sql.save(old_stats_1)
    sql.save(old_stats_2)

    old_stats_history_1 = models.PlaceCreatedOrdersStatsHistory(
        place_id=place_id_1, updated_at=OLD_TIME,
    )
    old_stats_history_2 = models.PlaceCreatedOrdersStatsHistory(
        place_id=place_id_2, updated_at=OLD_TIME, **old_values,
    )
    sql.save(old_stats_history_1)
    sql.save(old_stats_history_2)

    changed_stats = old_stats_2.clone(reset_updated_at=True)
    changed_stats.update(new_values)
    new_stats_history = models.PlaceCreatedOrdersStatsHistory(
        place_id=changed_stats.place_id, **new_values,
    )
    await stq_runner.eats_retail_business_alerts_save_order.call(
        task_id='1',
        kwargs={'place_id': changed_stats.place_id, 'order_nr': 'new_order'},
    )

    # stats
    place_id_to_stats = {
        i.place_id: i for i in sql.load_all(models.PlaceCreatedOrdersStats)
    }
    assert len(place_id_to_stats) == 2
    db_old_stats = place_id_to_stats[old_stats_1.place_id]
    db_changed_stats = place_id_to_stats[changed_stats.place_id]

    assert db_old_stats == old_stats_1
    assert db_changed_stats.updated_at > old_stats_2.updated_at
    assert_objects_equal_without(
        db_changed_stats, changed_stats, ['updated_at'],
    )

    # history
    id_to_stats_history = {
        i.record_id: i
        for i in sql.load_all(models.PlaceCreatedOrdersStatsHistory)
    }
    assert len(id_to_stats_history) == 3
    db_old_stats_history_1 = id_to_stats_history[old_stats_history_1.record_id]
    db_old_stats_history_2 = id_to_stats_history[old_stats_history_2.record_id]
    db_new_stats_history = id_to_stats_history[new_stats_history.record_id]

    assert db_old_stats_history_1 == old_stats_history_1
    assert db_old_stats_history_2 == old_stats_history_2
    assert db_new_stats_history.updated_at > old_stats_history_2.updated_at
    assert_objects_equal_without(
        db_new_stats_history, new_stats_history, ['updated_at'],
    )
