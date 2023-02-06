from typing import List
from typing import Type
from typing import TypeVar

from tests_eats_nomenclature_viewer.sql_adaptor import getters
from tests_eats_nomenclature_viewer.sql_adaptor import setters

ModelT = TypeVar('ModelT')


class SqlAdaptor:
    def __init__(self, pg_cursor):
        self._setter = setters.SqlSetter(pg_cursor)
        self._getter = getters.SqlGetter(pg_cursor)

    def save(self, data):
        return self._setter.save(data)

    def load_all(self, data_type: Type[ModelT]) -> List[ModelT]:
        """
        Load all data from the table corresponding to the object type
        """
        return self._getter.load_all(data_type)

    def get_object_id(self, data):
        """
        Load raw object id. Should not be used unless it's *really* necessary
        """
        return self._getter.get_object_id(data)
