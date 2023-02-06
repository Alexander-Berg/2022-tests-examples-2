import pytest
from mock import patch

from dmp_suite.table import Table
from dmp_suite.meta import Meta


def test_table_class():
    class TestTable(Table):
        pass

    assert Meta(TestTable).table_class == TestTable


class TestMeta:
    def test_correct_table_class(self):
        class T(object):
            pass

        with pytest.raises(ValueError):
            Meta(T)

    @patch('dmp_suite.table.Table.get_layout_prefix', return_value='dummy')
    def test_etl_service(self, get_func):
        class FakeTable(Table):
            pass
        result = Meta(FakeTable).layout_prefix_key
        assert get_func.called
        assert result == 'dummy'
