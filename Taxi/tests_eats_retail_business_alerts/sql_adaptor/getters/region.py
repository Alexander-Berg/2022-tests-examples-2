from tests_eats_retail_business_alerts.sql_adaptor.getters import base
from tests_eats_retail_business_alerts import models

SQL_SELECT_REGIONS = """
select
    id as region_id,
    slug,
    name,
    is_enabled,
    updated_at
from eats_retail_business_alerts.regions
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {models.Region: self._load_all_regions}

    def get_load_single_getters(self):
        return {}

    def _load_all_regions(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_REGIONS)

        return [models.Region(**i) for i in pg_cursor.fetchall()]
