from typing import List


class _MockYqlResults:
    _column_names: List[str] = []
    _result: List[set] = []

    def __init__(self, column_names, result):
        self._column_names = column_names
        self._result = result

    @property
    def status(self):
        return 'COMPLETED'

    @property
    def table(self):
        for table in self:
            return table

    class result:  # pylint: disable=C0103
        status_code = 200
        text = 'OK'

    def __iter__(self):
        return iter([_MockYqlTable(self._column_names, self._result)])


class MockYqlRequestOperation:
    _column_names: List[str] = []
    _result: List[set] = []

    def __init__(self, column_names, result):
        self._column_names = column_names
        self._result = result

    @property
    def operation_id(self):
        return 'OPERATION_ID'

    @property
    def share_url(self):
        return 'SHARE_URL'

    def run(self):
        return self

    def get_results(self):
        return _MockYqlResults(self._column_names, self._result)


class _MockYqlTable:
    _column_names: List[str] = []
    _result: List[set] = []

    def __init__(self, column_names, result):
        self._column_names = column_names
        self._rows = result

    def get_iterator(self):
        return iter(self._rows)
