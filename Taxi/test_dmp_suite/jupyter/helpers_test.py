from dmp_suite.greenplum import GPTable, String as GPString
from dmp_suite.jupyter.helpers import dev_schema


class TestGPTable(GPTable):
    foo = GPString()


def test_dev_schema_keeps_table_module():
    # Важно чтобы при изменении схемы сохранялся
    # атрибут __module__. Иначе определение сервиса,
    # к которому принадлежит таблица, будет работать
    # неправильно.
    assert dev_schema(TestGPTable, 'some_schema').__module__ == TestGPTable.__module__
