import datetime as dt

import pytest
import pytz

from tests_eats_retail_business_alerts import models
from tests_eats_retail_business_alerts import utils
from tests_eats_retail_business_alerts.periodics.db_cleanup import constants

MOCK_NOW = dt.datetime(2022, 4, 10, 15, tzinfo=pytz.UTC)
PLACE_ID = 1
CANCELLED_BY = 'courier'


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql('eats_retail_business_alerts', files=['init_place.sql'])
@pytest.mark.parametrize(**utils.gen_bool_params('is_enabled'))
@pytest.mark.parametrize(
    **utils.gen_list_params('outdated_threshold_in_hours', [1, 2]),
)
@pytest.mark.parametrize(
    **utils.gen_list_params(
        'table_name',
        [
            'places_orders',
            'places_created_orders_stats_history',
            'places_cancelled_orders_stats_history',
        ],
    ),
)
async def test_db_cleanup(
        assert_objects_lists_equal,
        taxi_eats_retail_business_alerts,
        set_cleanup_settings,
        sql,
        # parametrize params
        is_enabled,
        outdated_threshold_in_hours,
        table_name,
):
    set_cleanup_settings(table_name, is_enabled, outdated_threshold_in_hours)

    old_time = _get_time_in_past(2 * outdated_threshold_in_hours)
    recent_time = MOCK_NOW

    old_item = None
    recent_item = None
    if table_name == 'places_orders':
        old_item = models.PlaceOrder(place_id=PLACE_ID, updated_at=old_time)
        recent_item = models.PlaceOrder(
            place_id=PLACE_ID, updated_at=recent_time,
        )
    elif table_name == 'places_created_orders_stats_history':
        old_item = models.PlaceCreatedOrdersStatsHistory(
            place_id=PLACE_ID, updated_at=old_time,
        )
        recent_item = models.PlaceCreatedOrdersStatsHistory(
            place_id=PLACE_ID, updated_at=recent_time,
        )
    elif table_name == 'places_cancelled_orders_stats_history':
        old_item = models.PlaceCancelledOrdersStatsHistory(
            place_id=PLACE_ID, cancelled_by=CANCELLED_BY, updated_at=old_time,
        )
        recent_item = models.PlaceCancelledOrdersStatsHistory(
            place_id=PLACE_ID,
            cancelled_by=CANCELLED_BY,
            updated_at=recent_time,
        )
    sql.save(old_item)
    sql.save(recent_item)

    await taxi_eats_retail_business_alerts.run_distlock_task(
        constants.PERIODIC_NAME,
    )

    db_items = None
    if table_name == 'places_orders':
        db_items = sql.load_all(models.PlaceOrder)
    elif table_name == 'places_created_orders_stats_history':
        db_items = sql.load_all(models.PlaceCreatedOrdersStatsHistory)
    elif table_name == 'places_cancelled_orders_stats_history':
        db_items = sql.load_all(models.PlaceCancelledOrdersStatsHistory)

    if is_enabled:
        assert_objects_lists_equal(db_items, [recent_item])
    else:
        assert_objects_lists_equal(db_items, [old_item, recent_item])


@pytest.fixture(name='set_cleanup_settings')
def _set_cleanup_settings(update_taxi_config):
    def do_work(table_name, is_enabled, outdated_threshold_in_hours):
        update_taxi_config(
            'EATS_RETAIL_BUSINESS_ALERTS_DB_CLEANUP_SETTINGS',
            {
                '__default__': {
                    'is_enabled': False,
                    'outdated_threshold_in_hours': 1000,
                },
                table_name: {
                    'is_enabled': is_enabled,
                    'outdated_threshold_in_hours': outdated_threshold_in_hours,
                },
            },
        )

    return do_work


def _get_time_in_past(hours):
    return MOCK_NOW - dt.timedelta(hours=hours)
