from tests_eats_retail_business_alerts.sql_adaptor.getters import base
from tests_eats_retail_business_alerts import models

SQL_SELECT_PLACES = """
select
    id as place_id,
    slug,
    name,
    brand_id,
    region_id,
    is_enabled,
    is_enabled_changed_at,
    updated_at
from eats_retail_business_alerts.places
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {models.Place: self._load_all_places}

    def get_load_single_getters(self):
        return {models.Place: self._load_place}

    def _load_all_places(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACES)

        return [models.Place(**i) for i in pg_cursor.fetchall()]

    def _load_place(self, place_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACES + 'where id = %s', (place_id,))

        return models.Place(**pg_cursor.fetchone())
