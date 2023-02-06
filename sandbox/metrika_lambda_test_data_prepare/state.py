# coding=utf-8

from sandbox.projects.metrika.utils.pipeline.contextable import Contextable


class Table(Contextable):
    """
    Информация по выгрузке одной таблицы
    """

    NOT_LAUNCHED = "Не запущено"
    IN_PROGRESS = "В процессе"
    FINISH_SUCCESS = "Завершено"
    FINISH_FAIL = "Ошибка"
    FINISH_NO_DATA = "Исходная таблица не существует"
    INTERNAL_ERROR = "Внутренняя ошибка"

    def __init__(self, storage=None):
        super(Table, self).__init__(storage)

    @property
    def src(self):
        return self._default_getter()

    @src.setter
    def src(self, value):
        self._default_setter(value)

    @property
    def dst(self):
        return self._default_getter()

    @dst.setter
    def dst(self, value):
        self._default_setter(value)

    @property
    def sample(self):
        return self._default_getter()

    @sample.setter
    def sample(self, value):
        self._default_setter(value)

    @property
    def operation_id(self):
        return self._default_getter()

    @operation_id.setter
    def operation_id(self, value):
        self._default_setter(value)

    @property
    def share_url(self):
        return self._default_getter()

    @share_url.setter
    def share_url(self, value):
        self._default_setter(value)

    @property
    def status(self):
        return self._default_getter()

    @status.setter
    def status(self, value):
        self._default_setter(value)

    @property
    def operation_exists(self):
        return self._default_getter()

    @operation_exists.setter
    def operation_exists(self, value):
        self._default_setter(value)

    @property
    def progress(self):
        return self._default_getter()

    @progress.setter
    def progress(self, value):
        self._default_setter(value)

    @property
    def display_progress(self):
        if self.progress:
            try:
                return "{percentage} % ({completed}/{total})".format(percentage=round(100 * (float(self.progress["completed"]) / float(self.progress["total"]))),
                                                                     completed=self.progress["completed"],
                                                                     total=self.progress["total"])
            except Exception as e:
                return e
        else:
            return "Не доступно"

    @property
    def current_state(self):
        return self._default_getter()

    @current_state.setter
    def current_state(self, value):
        self._default_setter(value)


class Query(Contextable):
    """
    Информация по выгрузке одним запросом
    """

    NOT_LAUNCHED = "Не запущено"
    IN_PROGRESS = "В процессе"
    FINISH_SUCCESS = "Завершено"
    FINISH_FAIL = "Ошибка"
    FINISH_NO_DATA = "Исходная таблица не существует"
    INTERNAL_ERROR = "Внутренняя ошибка"

    def __init__(self, storage=None):
        super(Query, self).__init__(storage)

    @property
    def src(self):
        return self._default_getter()

    @src.setter
    def src(self, value):
        self._default_setter(value)

    @property
    def dst(self):
        return self._default_getter()

    @dst.setter
    def dst(self, value):
        self._default_setter(value)

    @property
    def operation_id(self):
        return self._default_getter()

    @operation_id.setter
    def operation_id(self, value):
        self._default_setter(value)

    @property
    def share_url(self):
        return self._default_getter()

    @share_url.setter
    def share_url(self, value):
        self._default_setter(value)

    @property
    def status(self):
        return self._default_getter()

    @status.setter
    def status(self, value):
        self._default_setter(value)

    @property
    def current_state(self):
        return self._default_getter()

    @current_state.setter
    def current_state(self, value):
        self._default_setter(value)

    @property
    def query(self):
        return self._default_getter()

    @query.setter
    def query(self, value):
        self._default_setter(value)


class File(Contextable):
    """
    Информация по выгрузке одного файла
    """

    FINISH_SUCCESS = "Завершено"

    def __init__(self, storage=None):
        super(File, self).__init__(storage)

    @property
    def src(self):
        return self._default_getter()

    @src.setter
    def src(self, value):
        self._default_setter(value)

    @property
    def dst(self):
        return self._default_getter()

    @dst.setter
    def dst(self, value):
        self._default_setter(value)

    @property
    def current_state(self):
        return File.FINISH_SUCCESS


class State(Contextable):

    def __init__(self, storage=None):
        super(State, self).__init__(storage)
        if storage is None:
            self._tables = []
            self._queries = []
            self._files = []

    @property
    def start_date(self):
        return self._default_getter()

    @start_date.setter
    def start_date(self, value):
        self._default_setter(value)

    @property
    def finish_date(self):
        return self._default_getter()

    @finish_date.setter
    def finish_date(self, value):
        self._default_setter(value)

    @property
    def destination_root(self):
        return self._default_getter()

    @destination_root.setter
    def destination_root(self, value):
        self._default_setter(value)

    @property
    def _tables(self):
        return self._default_getter()

    @_tables.setter
    def _tables(self, value):
        self._default_setter(value)

    @property
    def tables(self):
        return [Table(state) for state in self._tables]

    def add_table(self, value):
        self._tables.append(value.state)

    @property
    def _queries(self):
        return self._default_getter()

    @_queries.setter
    def _queries(self, value):
        self._default_setter(value)

    @property
    def queries(self):
        return [Query(state) for state in self._queries]

    def add_query(self, value):
        self._queries.append(value.state)

    @property
    def _files(self):
        return self._default_getter()

    @_files.setter
    def _files(self, value):
        self._default_setter(value)

    @property
    def files(self):
        return [File(state) for state in self._files]

    def add_file(self, value):
        self._files.append(value.state)

    @property
    def count_completed_tables(self):
        return len([t for t in self.tables if t.current_state in (Table.FINISH_FAIL, Table.FINISH_SUCCESS, Table.FINISH_NO_DATA, Table.INTERNAL_ERROR)])

    @property
    def count_completed_queries(self):
        return len([t for t in self.queries if t.current_state in (Query.FINISH_FAIL, Query.FINISH_SUCCESS, Query.FINISH_NO_DATA, Query.INTERNAL_ERROR)])

    @property
    def completed_tables_percentage(self):
        if self.tables:
            try:
                return "{percentage} % ({completed}/{total})".format(percentage=round(100 * (float(self.count_completed_tables) / float(len(self.tables)))),
                                                                     completed=self.count_completed_tables,
                                                                     total=len(self.tables))
            except Exception as e:
                return e
        else:
            return "Не доступно"

    @property
    def completed_queries_percentage(self):
        if self.queries:
            try:
                return "{percentage} % ({completed}/{total})".format(percentage=round(100 * (float(self.count_completed_queries) / float(len(self.queries)))),
                                                                     completed=self.count_completed_queries,
                                                                     total=len(self.queries))
            except Exception as e:
                return e
        else:
            return "Не доступно"
