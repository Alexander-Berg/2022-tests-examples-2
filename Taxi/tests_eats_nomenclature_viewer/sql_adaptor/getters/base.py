class SqlGetterImplBase:
    def __init__(self, parent, pg_cursor):
        self._pg_cursor = pg_cursor
        self._parent = parent

    def get_load_all_getters(self):
        return {}

    def get_load_single_getters(self):
        return {}

    def get_object_id_getters(self):
        return {}
