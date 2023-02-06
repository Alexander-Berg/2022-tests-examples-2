from . import base
from ... import models

SQL_SELECT_PLACES_ORDERS = """
select
    place_id,
    order_nr,
    updated_at
from eats_retail_business_alerts.places_orders
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {models.PlaceOrder: self._load_all_places_orders}

    def get_load_single_getters(self):
        return {}

    def _load_all_places_orders(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACES_ORDERS)

        return [models.PlaceOrder(**i) for i in pg_cursor.fetchall()]
