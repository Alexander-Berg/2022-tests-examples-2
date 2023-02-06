from tests_eats_nomenclature_viewer.sql_adaptor.getters import base
from tests_eats_nomenclature_viewer import models

SQL_SELECT_BRAND = """
select
    id as brand_id,
    slug,
    name,
    is_enabled,
    updated_at
from eats_nomenclature_viewer.brands
"""

SQL_SELECT_PLACE = """
select
    id as place_id,
    slug,
    brand_id,
    is_enabled,
    is_enabled_changed_at,
    stock_reset_limit,
    updated_at
from eats_nomenclature_viewer.places
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {
            models.Place: self._load_all_places,
            models.Brand: self._load_all_brands,
        }

    def get_load_single_getters(self):
        return {models.Place: self._load_place}

    def _load_all_brands(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_BRAND)

        return [models.Brand(**i) for i in pg_cursor.fetchall()]

    def _load_all_places(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE)

        return [models.Place(**i) for i in pg_cursor.fetchall()]

    def _load_place(self, place_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE + 'where id = %s', (place_id,))

        return models.Place(**pg_cursor.fetchone())
