from tests_eats_nomenclature_viewer.sql_adaptor.getters import base
from tests_eats_nomenclature_viewer import models

SQL_SELECT_PLACE_PRODUCT_PRICE = """
select
    place_id,
    product_nmn_id,
    price,
    old_price,
    full_price,
    old_full_price,
    vat,
    updated_at
from eats_nomenclature_viewer.place_product_prices
"""

SQL_SELECT_PLACE_PRODUCT_VENDOR_DATA = """
select
    place_id,
    product_nmn_id,
    vendor_code,
    position,
    updated_at
from eats_nomenclature_viewer.place_product_vendor_data
"""

SQL_SELECT_PLACE_PRODUCT_STOCK = """
select
    place_id,
    product_nmn_id,
    value,
    updated_at
from eats_nomenclature_viewer.place_product_stocks
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {
            models.PlaceProductPrice: self._load_all_prices,
            models.PlaceProductStock: self._load_all_stocks,
            models.PlaceProductVendorData: self._load_all_vendor_data,
        }

    def get_load_single_getters(self):
        return {}

    def _load_all_prices(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE_PRODUCT_PRICE)

        return [models.PlaceProductPrice(**i) for i in pg_cursor.fetchall()]

    def _load_all_vendor_data(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE_PRODUCT_VENDOR_DATA)

        return [
            models.PlaceProductVendorData(**i) for i in pg_cursor.fetchall()
        ]

    def _load_all_stocks(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE_PRODUCT_STOCK)

        return [models.PlaceProductStock(**i) for i in pg_cursor.fetchall()]
