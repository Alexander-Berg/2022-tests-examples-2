from . import base
from ... import models

SQL_SELECT_PLACES_CANCELLED_ORDERS_STATS = """
select
    place_id,
    cancelled_by,
    orders_count,
    last_date_in_msc,
    updated_at
from eats_retail_business_alerts.places_cancelled_orders_stats
"""

SQL_SELECT_PLACES_CANCELLED_ORDERS_STATS_HISTORY = """
select
    place_id,
    cancelled_by,
    orders_count,
    last_date_in_msc,
    id as record_id,
    updated_at
from eats_retail_business_alerts.places_cancelled_orders_stats_history
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {
            models.PlaceCancelledOrdersStats: (
                self._load_all_places_cancelled_orders_stats
            ),
            models.PlaceCancelledOrdersStatsHistory: (
                self._load_all_places_cancelled_orders_stats_history
            ),
        }

    def get_load_single_getters(self):
        return {}

    def _load_all_places_cancelled_orders_stats(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACES_CANCELLED_ORDERS_STATS)

        return [
            models.PlaceCancelledOrdersStats(**i) for i in pg_cursor.fetchall()
        ]

    def _load_all_places_cancelled_orders_stats_history(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACES_CANCELLED_ORDERS_STATS_HISTORY)

        return [
            models.PlaceCancelledOrdersStatsHistory(**i)
            for i in pg_cursor.fetchall()
        ]
