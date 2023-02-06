from typing import List

from tests_eats_retail_business_alerts.sql_adaptor.getters import base
from tests_eats_retail_business_alerts.sql_adaptor.getters import brand
from tests_eats_retail_business_alerts.sql_adaptor.getters import place
from tests_eats_retail_business_alerts.sql_adaptor.getters import (
    place_cancelled_orders_stats,
)
from tests_eats_retail_business_alerts.sql_adaptor.getters import (
    place_created_orders_stats,
)
from tests_eats_retail_business_alerts.sql_adaptor.getters import place_order
from tests_eats_retail_business_alerts.sql_adaptor.getters import region


class SqlGetter:
    def __init__(self, pg_cursor):
        self._getters: List[base.SqlGetterImplBase] = [
            brand.SqlGetterImpl(self, pg_cursor),
            place.SqlGetterImpl(self, pg_cursor),
            place_cancelled_orders_stats.SqlGetterImpl(self, pg_cursor),
            place_created_orders_stats.SqlGetterImpl(self, pg_cursor),
            place_order.SqlGetterImpl(self, pg_cursor),
            region.SqlGetterImpl(self, pg_cursor),
        ]
        self._load_all_getters = {}
        for i in self._getters:
            self._load_all_getters.update(i.get_load_all_getters())
        self._load_single_getters = {}
        for i in self._getters:
            self._load_single_getters.update(i.get_load_single_getters())

    def load_all(self, data_type):
        """
        Load all data from the table corresponding to the object type
        """
        if data_type not in self._load_all_getters:
            raise ValueError('Unsupported object type')

        return self._load_all_getters[data_type]()

    def load_single(self, data_type, object_id):
        """
        Load a single row data from the table corresponding to the object type
        """
        if data_type not in self._load_single_getters:
            raise ValueError('Unsupported object type')

        return self._load_single_getters[data_type](object_id)
