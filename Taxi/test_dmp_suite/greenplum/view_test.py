import mock
import pytest
from psycopg2 import sql

from dmp_suite.exceptions import FieldsRequiredError
from dmp_suite.greenplum import resolve_meta
from dmp_suite.greenplum.exceptions import (
    FieldsMismatchError,
    LayoutRequiredError, SQLFileMissingError,
)
from dmp_suite.greenplum.table import Datetime
from dmp_suite.greenplum.task.transformations import SqlTaskSource
from dmp_suite.greenplum.view import View, get_field_names
from dmp_suite.table import Field, SummaryLayout

import connection.greenplum as gp


def test_schema_is_required():
    with pytest.raises(LayoutRequiredError):
        class TestViewWithoutFields(View):
            blah = Field()


def test_fields_are_required():
    with pytest.raises(FieldsRequiredError):
        class TestViewWithoutFields(View):
            __layout__ = SummaryLayout('test', prefix_key='test')
            __query__ = 'select 1 as blah'


def test_query_may_be_specified_in_file():
    class ViewFromFile(View):
        __layout__ = SummaryLayout('test', prefix_key='test')
        a = Field()
        b = Field()

    assert ViewFromFile.__query__ == 'select a, b from c'


def test_view_with_layout_query_from_file():
    class ViewFromFile(View):
        __layout__ = SummaryLayout('test', prefix_key='test')
        a = Field()
        b = Field()

    assert ViewFromFile.__query__ == 'select a, b from c'


@pytest.mark.skip("TODO: this should be rewritten to a slow test")
def test_fields_mismatch_in_query_and_metadata():
    # Это не ошибка
    '''
    with pytest.raises(FieldsMismatchError):
        class SomeView(View):
            """В этом случае в запросе поле b указано, а в метаданных - нет."""
            __layout__ = SummaryLayout('test', prefix_key='test')
            __query__ = 'select a, b from c'
            a = Field()
    '''

    with pytest.raises(Exception):
        class SomeView(View):
            """А в этом случае - в метаданных поле b указано, а в запросе нет."""
            __layout__ = SummaryLayout('test', prefix_key='test')
            __query__ = 'select a from c'
            a = Field()
            b = Field()


class SomeView(View):
    """Просто тестовая вьюшечка."""
    __query__ = 'select a as blah, b as minor from drivers'
    __layout__ = SummaryLayout('test', prefix_key='test')

    blah = Field(comment='Это поле без типа, так тоже можно')
    # Если у поля есть тип, то в результирующем запросе должна быть проверка типа
    minor = Datetime()


EXPECTED_SQL = """
drop view if exists {table_full_name};


create or replace view {table_full_name} as (
  select "blah", cast("minor" as TIMESTAMP WITHOUT TIME ZONE)
  from (
    select a as blah, b as minor from drivers
  ) as the_select
);


GRANT all ON {table_full_name} TO "etl";

GRANT select ON {table_full_name} TO "developer_mlu";
comment on view {table_full_name} is 'Просто тестовая вьюшечка.';
comment on column {table_full_name}."blah" is 'Это поле без типа, так тоже можно';"""


@mock.patch('dmp_suite.greenplum.view.settings', mock.MagicMock(return_value={'select': ['developer_mlu'], 'all': ['etl']}))
@pytest.mark.parametrize('view_class, expected_sql', [
    (SomeView, EXPECTED_SQL),
])
@pytest.mark.slow('gp')
def test_get_view_sql(view_class, expected_sql):
    # Метод get_sql должен возвращать SQL запрос, который создаст нам
    # view в базе данных.
    # Если у view есть докстринг, то для объекта в базе должен быть задан комментарий
    # и то же самое для колонок
    view = view_class()
    with gp._get_default_connection() as connection, connection.cursor() as cur:
        # If tests are launched in several threads with pytest-parallel,
        # then this filthy piece of code totally screws up the shared GP connection.
        # So we use a separate connection here.
        result_sql = view.get_sql(with_drop_statement=True).as_string(cur)
    assert result_sql == expected_sql.format(table_full_name='"{}"."{}"'.format(view.get_schema(), view.get_view_name()))


def test_get_fields_from_simple_sql():
    query = """
    SELECT a, b FROM c
    """
    assert get_field_names(query) == ['a', 'b']


def test_get_fields_from_sql_with_clause():
    query = """
    with foo as (select 1 a, 2 b)
      select a, b from foo
    """
    assert get_field_names(query) == ['a', 'b']


def test_resolve_gp_meta_for_view():
    assert resolve_meta(SomeView)


def test_add_table():
    source = SqlTaskSource.from_string(
        'select 1'
    ).add_tables(
        t=SomeView
    )

    source_tables = list(source.get_sources())
    assert len(source_tables) == 1
    assert set(source.get_sources()) == {SomeView}


def test_get_field_names():
    query_1 = """
    SELECT lgh.lvl5_id
    FROM taxi_cdm_geo.dim_legacy_geohierarchy lgh;
    """

    query_2 = """
    SELECT lgh.lvl5_id
    FROM taxi_cdm_geo.dim_legacy_geohierarchy lgh
    """

    query_3 = "SELECT lgh.lvl5_id FROM taxi_cdm_geo.dim_legacy_geohierarchy lgh;"

    assert set(get_field_names(query_1)) == {'lvl5_id'}
    assert set(get_field_names(query_2)) == {'lvl5_id'}
    assert set(get_field_names(query_3)) == {'lvl5_id'}


def test_inheritance():
    class ParentView(View):
        __layout__ = SummaryLayout('test', prefix_key='test')
        __view_name__ = 'parent_view'
        __query__ = 'select a, b from t'

        a = Field()
        b = Field()

    class ChildView(ParentView):
        __view_name__ = 'child_view'
        __query__ = 'select a, b, c from t'
        b = Datetime()
        c = Field()

    try:
        assert ChildView()
    except FieldsMismatchError:
        assert False

    class GrandchildView(ChildView):
        __view_name__ = 'grandchild_view'
        __query__ = 'select a, b, c, d from t'

        d = Field()

    try:
        assert GrandchildView()
    except FieldsMismatchError:
        assert False


def test_using_prefix_in_view():
    full_name = SomeView.get_full_name()
    assert full_name.startswith('dummy_pfxvalue_summary.test')


def test_get_view_name():
    full_name = SomeView.get_view_name()
    assert full_name.startswith('test')


def test_get_formatted_query():
    class SomeView(View):
        __query__ = 'select 1 as blah from test.test'
        __layout__ = SummaryLayout('test', prefix_key='test')
        blah = Field()

    assert SomeView()._get_formatted_query() == sql.SQL('select 1 as blah from test.test').format(**{})

    class SomeViewWithTables(View):
        __layout__ = SummaryLayout('test', prefix_key='test')
        __query__ = 'select 1 as blah from {table}'
        __tables__ = {
            'table': SomeView
        }
        blah = Field()

    expected = sql.SQL('select 1 as blah from {}').format(sql.SQL(SomeView.get_full_name()))

    assert SomeViewWithTables()._get_formatted_query() == expected


def test_file_query_inheritance():
    class ViewFromFile(View):
        __layout__ = SummaryLayout('test', prefix_key='test')
        a = Field()
        b = Field()

    with pytest.raises(SQLFileMissingError):
        class Child(ViewFromFile):
            pass


def test_query_update():
    class ViewFromFile(View):
        __layout__ = SummaryLayout('test', prefix_key='test')
        a = Field()
        b = Field()

    class Child(ViewFromFile):
        __query__ = 'select 1 as blah from test.test'

    expected = sql.SQL('select 1 as blah from test.test').format(**{})

    assert Child()._get_formatted_query() == expected


def test_asterisk_view():
    class SomeView(View):
        __query__ = 'select test.* from test.test'
        __layout__ = SummaryLayout('test', prefix_key='test')
        blah = Field()

    assert SomeView().get_sql()
