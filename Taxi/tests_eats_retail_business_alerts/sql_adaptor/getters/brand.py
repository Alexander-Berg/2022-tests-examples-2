from tests_eats_retail_business_alerts.sql_adaptor.getters import base
from tests_eats_retail_business_alerts import models

SQL_SELECT_BRANDS = """
select
    id as brand_id,
    slug,
    name,
    is_enabled,
    updated_at
from eats_retail_business_alerts.brands
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {models.Brand: self._load_all_brands}

    def get_load_single_getters(self):
        return {}

    def _load_all_brands(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_BRANDS)

        return [models.Brand(**i) for i in pg_cursor.fetchall()]
