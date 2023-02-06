import datetime as dt

import pytest
import pytz

from tests_eats_retail_business_alerts import models
from tests_eats_retail_business_alerts.stq.save_order import constants

OLD_TIME = dt.datetime(1999, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql('eats_retail_business_alerts', files=['init_place.sql'])
async def test_same_place_order(assert_objects_lists_equal, sql, stq_runner):
    old_place_order = models.PlaceOrder(
        place_id=constants.PLACE_ID, updated_at=OLD_TIME,
    )
    sql.save(old_place_order)

    old_place_stats = models.PlaceCreatedOrdersStats(
        place_id=constants.PLACE_ID, updated_at=OLD_TIME,
    )
    sql.save(old_place_stats)

    old_place_stats_history = models.PlaceCreatedOrdersStatsHistory(
        place_id=constants.PLACE_ID, updated_at=OLD_TIME,
    )
    sql.save(old_place_stats_history)

    # send the same data
    await stq_runner.eats_retail_business_alerts_save_order.call(
        task_id='1',
        kwargs={
            'place_id': old_place_order.place_id,
            'order_nr': old_place_order.order_nr,
        },
    )

    assert_objects_lists_equal(
        sql.load_all(models.PlaceOrder), [old_place_order],
    )
    assert_objects_lists_equal(
        sql.load_all(models.PlaceCreatedOrdersStats), [old_place_stats],
    )
    assert_objects_lists_equal(
        sql.load_all(models.PlaceCreatedOrdersStatsHistory),
        [old_place_stats_history],
    )


async def test_insert_place_order(
        assert_objects_equal_without, sql, stq_runner,
):
    brand_id = sql.save(models.Brand())
    region_id = sql.save(models.Region())
    place_id_1 = sql.save(models.Place(brand_id=brand_id, region_id=region_id))
    place_id_2 = sql.save(models.Place(brand_id=brand_id, region_id=region_id))

    old_place_order = models.PlaceOrder(
        place_id=place_id_1, order_nr='1', updated_at=OLD_TIME,
    )
    sql.save(old_place_order)

    # send new data
    new_place_order = models.PlaceOrder(place_id=place_id_2, order_nr='2')
    await stq_runner.eats_retail_business_alerts_save_order.call(
        task_id='1',
        kwargs={
            'place_id': new_place_order.place_id,
            'order_nr': new_place_order.order_nr,
        },
    )

    order_nr_to_data = {i.order_nr: i for i in sql.load_all(models.PlaceOrder)}
    assert len(order_nr_to_data) == 2
    db_old_place_order = order_nr_to_data[old_place_order.order_nr]
    db_new_place_order = order_nr_to_data[new_place_order.order_nr]

    assert db_old_place_order == old_place_order
    assert db_new_place_order.updated_at > old_place_order.updated_at
    assert_objects_equal_without(
        db_new_place_order, new_place_order, ['updated_at'],
    )
