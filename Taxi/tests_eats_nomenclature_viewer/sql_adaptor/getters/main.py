from typing import List

from tests_eats_nomenclature_viewer.sql_adaptor.getters import assortment
from tests_eats_nomenclature_viewer.sql_adaptor.getters import base
from tests_eats_nomenclature_viewer.sql_adaptor.getters import brand_place
from tests_eats_nomenclature_viewer.sql_adaptor.getters import category
from tests_eats_nomenclature_viewer.sql_adaptor.getters import image
from tests_eats_nomenclature_viewer.sql_adaptor.getters import place_product
from tests_eats_nomenclature_viewer.sql_adaptor.getters import place_status
from tests_eats_nomenclature_viewer.sql_adaptor.getters import product


class SqlGetter:
    def __init__(self, pg_cursor):
        self._getters: List[base.SqlGetterImplBase] = [
            assortment.SqlGetterImpl(self, pg_cursor),
            brand_place.SqlGetterImpl(self, pg_cursor),
            category.SqlGetterImpl(self, pg_cursor),
            image.SqlGetterImpl(self, pg_cursor),
            place_product.SqlGetterImpl(self, pg_cursor),
            place_status.SqlGetterImpl(self, pg_cursor),
            product.SqlGetterImpl(self, pg_cursor),
        ]
        self._load_all_getters = {}
        for i in self._getters:
            self._load_all_getters.update(i.get_load_all_getters())
        self._load_single_getters = {}
        for i in self._getters:
            self._load_single_getters.update(i.get_load_single_getters())
        self._object_id_getters = {}
        for i in self._getters:
            self._object_id_getters.update(i.get_object_id_getters())

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

    def get_object_id(self, data):
        """
        Load raw object id. Should not be used unless it's *really* necessary
        """
        if type(data) not in self._object_id_getters:  # pylint: disable=C0123
            raise ValueError('Unsupported object type')

        return self._object_id_getters[type(data)](data)
