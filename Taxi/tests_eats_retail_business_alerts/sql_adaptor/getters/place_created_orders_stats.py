from . import base
from ... import models

SQL_SELECT_PLACES_CREATED_ORDERS_STATS = """
select
    place_id,
    orders_count,
    last_date_in_msc,
    updated_at
from eats_retail_business_alerts.places_created_orders_stats
"""

SQL_SELECT_PLACES_CREATED_ORDERS_STATS_HISTORY = """
select
    place_id,
    orders_count,
    last_date_in_msc,
    id as record_id,
    updated_at
from eats_retail_business_alerts.places_created_orders_stats_history
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {
            models.PlaceCreatedOrdersStats: (
                self._load_all_places_created_orders_stats
            ),
            models.PlaceCreatedOrdersStatsHistory: (
                self._load_all_places_created_orders_stats_history
            ),
        }

    def get_load_single_getters(self):
        return {}

    def _load_all_places_created_orders_stats(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACES_CREATED_ORDERS_STATS)

        return [
            models.PlaceCreatedOrdersStats(**i) for i in pg_cursor.fetchall()
        ]

    def _load_all_places_created_orders_stats_history(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACES_CREATED_ORDERS_STATS_HISTORY)

        return [
            models.PlaceCreatedOrdersStatsHistory(**i)
            for i in pg_cursor.fetchall()
        ]
