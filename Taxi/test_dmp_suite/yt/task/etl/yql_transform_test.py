import contextlib
import re
import textwrap
from argparse import Namespace

import pytest

from connection.yt import Pool
from dmp_suite import datetime_utils as dtu
from dmp_suite.task.args import use_arg
from dmp_suite.task.base import TaskEnvironment
from dmp_suite.yql import YqlSyntaxVersions
from dmp_suite.yt import (
    Date,
    Decimal,
    ETLTable,
    etl,
    DayPartitionScale,
    Int,
    Datetime,
    NotLayeredYtLayout,
    YTMeta,
    NotLayeredYtTable,
    scales
)
from dmp_suite.yt import operation as yt
from dmp_suite.yt.task.etl import transform
from dmp_suite.yt.task.etl.transform import BadPathError, date_range
from dmp_suite.yt.task.etl.yql_transform import (
    YqlTaskQuery,
    PlaceholderMissingError,
    YqlPathResolver
)
from dmp_suite.yt.task.etl.query import YTPoolSubstitutionError
from init_py_env import settings
from test_dmp_suite.yt import utils
from test_dmp_suite.yt.task.etl.utils import MockTask, Table

table = utils.fixture_random_yt_table(Table)


@pytest.mark.slow
def test_yql_task_query(table):
    sql = '''
    INSERT INTO {dst_table}
    SELECT 1 AS a, 2 AS b;
    '''
    accessor = YqlTaskQuery.from_string(
        sql,
        target_key='dst_table',
        syntax_version=YqlSyntaxVersions.V1,
    )
    env = transform.TransformationEnvironment(
        task=MockTask(),
    )
    source = accessor.get_value(None, env)
    path_factory = etl.temporary_buffer_table(table)
    with source.source_table(path_factory) as src:
        assert [dict(a=1, b=2)] == list(yt.read_yt_table(src))


@pytest.mark.parametrize('args, kwargs, expected_pool', [
    (None, dict(), 'priority'),
    (None, dict(pool=None), None),
    (None, dict(pool=Pool.TAXI_DWH_PRIORITY), 'priority'),
    (None, dict(pool=Pool.TAXI_DWH_BATCH), 'batch'),
    (None, dict(pool=Pool.RESEARCH), None),
    (None, dict(pool='test_pool'), 'test_pool'),
    (dict(pool=Pool.TAXI_DWH_PRIORITY), dict(), 'priority'),
    (dict(pool=Pool.TAXI_DWH_BATCH), dict(), 'batch'),
    (dict(pool=Pool.RESEARCH), dict(), None),

    (None, dict(pool=use_arg('yt_pool', default=Pool.TAXI_DWH_PRIORITY)), 'priority'),
    (None, dict(pool=use_arg('yt_pool', default='test_pool')), 'test_pool'),
    (dict(yt_pool=Pool.TAXI_DWH_BATCH), dict(), 'priority'),
    (
        dict(yt_pool=Pool.TAXI_DWH_BATCH),
        dict(pool=use_arg('yt_pool', default=Pool.TAXI_DWH_PRIORITY)),
        'batch'
    ),
])
def test_yt_pool_no_pragma(args, kwargs, expected_pool):
    if args is not None:
        args = Namespace(**args)

    settings_patch = settings.patch(
        ('yt.pools.TAXI_DWH_PRIORITY', 'priority'),
        ('yt.pools.TAXI_DWH_BATCH', 'batch'),
        ('yt.pools.RESEARCH', None),
    )

    sql = '''INSERT INTO {target_path} SELECT 1 AS a, 2 AS b;'''

    accessor = YqlTaskQuery.from_string(sql, **kwargs)
    with settings_patch, accessor._prepare(args, None, 'tst'):
        pool_re = expected_pool if expected_pool else '.*'
        match = re.search(
            fr"(?i:pragma)\s+yt.Pool\s?=\s?'{pool_re}'\s?;",
            accessor.executable_query_string,
            re.MULTILINE
        )

        if expected_pool:
            assert match
        else:
            assert not match


@pytest.mark.parametrize('args, kwargs', [
    (None, dict(pool=Pool.TAXI_DWH_PRIORITY)),
    (None, dict(pool=Pool.RESEARCH)),
    (None, dict(pool=Pool.TAXI_DWH_BATCH)),
    (None, dict(pool='test_pool')),
    (dict(yt_pool='test_pool'), dict(pool=use_arg('yt_pool'))),
])
def test_yt_pool_exception_build_in_pragma(args, kwargs):
    sql = '''
    PRAGMA yt.Pool='test';
    INSERT INTO {target_path} SELECT 1 AS a, 2 AS b;
    '''

    sql = '''
    $source = (SELECT 1 AS a, 2 AS b);

    PRAGMA yt.Pool='test';
    INSERT INTO {target_path} SELECT a, b FROM $source;
    '''

    with pytest.raises(YTPoolSubstitutionError):
        YqlTaskQuery.from_string(sql, **kwargs)


def test_yt_pool_exception_build_in_pragma_multiline():
    sql = '''
    $source = (SELECT 1 AS a, 2 AS b);

    PRAGMA yt.Pool='test';
    INSERT INTO {target_path} SELECT a, b FROM $source;
    '''
    with pytest.raises(YTPoolSubstitutionError):
        YqlTaskQuery.from_string(sql, pool='test_pool')


@pytest.mark.parametrize('args, kwargs', [
    (None, dict()),
    (None, dict(pool=None)),
])
def test_yt_pool_build_in_pragma(args, kwargs):
    target_path = 'tst'
    sql = '''
    PRAGMA yt.Pool='test';
    INSERT INTO {target_path} SELECT 1 AS a, 2 AS b;
    '''
    expected_sql = sql.format(target_path=f'`{target_path}`')
    accessor = YqlTaskQuery.from_string(sql, **kwargs)
    with accessor._prepare(args, None, target_path):
        assert accessor.executable_query_string == expected_sql


def test_yql_query_should_use_target_path():
    # YqlTaskQuery всегда должен складывать результаты своего выполнения
    # в определённую таблицу, потому что иначе таск не сможет их использовать
    # для дальнейших преобразований.
    sql = '''
    SELECT 1 AS a, 2 AS b;
    '''

    with pytest.raises(PlaceholderMissingError):
        YqlTaskQuery.from_string(sql, generate_insert_if_needed=False)

    # Так же, надо проверить, что ошибка будет и при
    # использовании кастомного target_key:
    sql = '''
    SELECT 1 AS a, 2 AS b from {target_path};
    '''

    with pytest.raises(PlaceholderMissingError):
        YqlTaskQuery.from_string(
            sql, target_key='other_path', generate_insert_if_needed=False)


class TestYqlPathResolver:
    class Table(NotLayeredYtTable):
        __layout__ = NotLayeredYtLayout('//service', 'entity')
        id = Int()
        dttm = Datetime()

    class PartitionTable(NotLayeredYtTable):
        __layout__ = NotLayeredYtLayout('//service', 'entity')
        __partition_scale__ = DayPartitionScale('dttm')
        id = Int()
        dttm = Datetime()

    def test_date_range(self):
        expected = 'RANGE(`//service/entity`, `2020-02-03`, `2020-02-06`)'
        assert expected == YqlPathResolver().date_range(
            YTMeta(TestYqlPathResolver.PartitionTable),
            dtu.Period('2020-02-03', '2020-02-06')
        )

    def test_all_partitions(self):
        expected = 'RANGE(`//service/entity`)'
        assert expected == YqlPathResolver().all_partitions(
            YTMeta(TestYqlPathResolver.PartitionTable)
        )

    def test_ext_date_range(self):
        expected = 'RANGE(`//service/entity`, `2020-02-03`, `2020-02-06`)'
        actual = YqlPathResolver().ext_date_range(
            folder_path='//service/entity',
            scale=scales.day,
            date_formatter=dtu.format_date,
            period=dtu.Period('2020-02-03', '2020-02-06')
        )
        assert expected == actual

    def test_ext_all_partitions(self):
        expected = 'RANGE(`//service/entity`)'
        actual = YqlPathResolver().ext_all_partitions('//service/entity')
        assert expected == actual

    @pytest.mark.parametrize('path, expected', [
        (object(), BadPathError),
        ('//service/entity', '`//service/entity`'),
        (
            ['//service/entity/1', '//service/entity/2'],
            'CONCAT(`//service/entity/1`, `//service/entity/2`)'
        ),
        (
            '`//service/entity/1`',
            '`//service/entity/1`',
        ),
        (
                'RANGE(`//service/entity/`, `1`, `3`)',
                'RANGE(`//service/entity/`, `1`, `3`)',
        ),
        (
                'CONCAT(`//service/entity/1`, `//service/entity/2`)',
                'CONCAT(`//service/entity/1`, `//service/entity/2`)',
        ),
    ])
    def test_one_or_several(self, path, expected):
        if isinstance(expected, type) and issubclass(expected, Exception):
            with pytest.raises(expected):
                YqlPathResolver().one_or_several(path)
        else:
            assert expected == YqlPathResolver().one_or_several(path)

    def test_resolve(self):
        resolver = YqlPathResolver()

        assert resolver.resolve('//service/entity') == '`//service/entity`'

        assert resolver.resolve(self.Table) == '`//service/entity`'

        range_ = date_range(self.PartitionTable)
        period = dtu.Period('2020-05-01', '2020-05-03')
        expected_result = 'RANGE(`//service/entity`, `2020-05-01`, `2020-05-03`)'
        assert resolver.resolve(range_, {'period': period}) == expected_result


def test_no_double_inserts():
    query = YqlTaskQuery.from_string('insert {target_path} from $result')
    with contextlib.ExitStack() as stack:
        stack.enter_context(query._prepare({}, None, '//path'))
        stack.enter_context(settings.patch(
            {'yt': {'pools': {'TAXI_DWH_PRIORITY': 'dummy'}}}
        ))
        actual_query = query.executable_query_string.strip()

    expected_query = "PRAGMA yt.Pool='dummy';\ninsert `//path` from $result"
    assert actual_query == expected_query


def test_add_insert_with_wrong_statement():
    with pytest.raises(ValueError):
        YqlTaskQuery.from_string('REDUCE {target_path} ON key')


@pytest.mark.parametrize(
    'query_string',
    [
        '$result = select * from {target_path};',
        '$result = select * from {target_path}; -- test',
        '$result = select * from {target_path};\n-- test',
        '$result = select * from 1 as n;',
        '  $result = select * from 1 as n;',
        '$result\n= select * from 1 as n;',
        '$result\t= select * from 1 as n;',
        '$result   = select * from 1 as n;',
        '$result= select * from 1 as n;',
    ]
)
def test_yql_query_without_insert(query_string):
    @utils.random_yt_table
    class _TestTable(ETLTable):
        date = Date()
        decimal = Decimal(5, 3)

    query = YqlTaskQuery.from_string(query_string)
    dummy_task = transform.replace_by_snapshot(
        name='test_complex_rps',
        source=query,
        target_table=_TestTable,
    )

    env = TaskEnvironment(task=dummy_task)

    with contextlib.ExitStack() as stack:
        stack.enter_context(query._prepare({}, env, '//path'))
        stack.enter_context(settings.patch(
            {'yt': {'pools': {'TAXI_DWH_PRIORITY': 'dummy'}}}
        ))
        actual_query = query.executable_query_string.strip()
    expected_query = textwrap.dedent(
        """
        PRAGMA yt.Pool='dummy';
        {query_string}

        -- auto-generated INSERT
        INSERT INTO `//path` (date, decimal, etl_updated)
          SELECT date, decimal, etl_updated FROM $result;
        """
    ).strip().format(
        query_string=query_string.format(target_path='`//path`')
    )
    assert actual_query == expected_query


@pytest.mark.parametrize(
    'query_string',
    [
        'select * from {target_path};',
        '-- test',
        '\n',
        '/****/',
    ]
)
def test_yql_wrong_query_without_insert(query_string):
    @utils.random_yt_table
    class _TestTable(ETLTable):
        date = Date()
        decimal = Decimal(5, 3)

    with pytest.raises(ValueError):
        YqlTaskQuery.from_string(query_string)


@pytest.mark.parametrize(
    'query_string',
    [
        'insert into {target_path} from select * from {target_path};',
        'insert into {target_path} from select * from {target_path}; -- test',
        'insert into {target_path} from select * from {target_path};\n-- test',
    ]
)
def test_yql_query_with_insert(query_string):
    @utils.random_yt_table
    class _TestTable(ETLTable):
        date = Date()
        decimal = Decimal(5, 3)

    query = YqlTaskQuery.from_string(query_string)
    dummy_task = transform.replace_by_snapshot(
        name='test_complex_rps',
        source=query,
        target_table=_TestTable,
    )

    env = TaskEnvironment(task=dummy_task)

    with contextlib.ExitStack() as stack:
        stack.enter_context(query._prepare({}, env, '//path'))
        stack.enter_context(settings.patch(
            {'yt': {'pools': {'TAXI_DWH_PRIORITY': 'dummy'}}}
        ))
        actual_query = query.executable_query_string.strip()
    expected_query = textwrap.dedent(
        """
        PRAGMA yt.Pool='dummy';
        {query_string}
        """
    ).strip().format(
        query_string=query_string.format(target_path='`//path`')
    )
    assert actual_query == expected_query
