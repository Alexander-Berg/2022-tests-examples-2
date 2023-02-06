import pandas as pd
import pytest
import random

from connection import greenplum as gp

from dmp_suite.file_utils import from_same_directory
from dmp_suite.greenplum.task import validators
from dmp_suite.greenplum.query import GreenplumQuery


def build_full_query(query, data):
    rows = []
    rows.append('create temporary table {result_table} (value integer) on commit drop')
    if len(data):
        rows.append('insert into {result_table} values ' + ', \n'.join(['({})'.format(i) for i in data]))
    rows.append(query)
    return ";\n".join(rows)


def random_table_name() -> str:
    return 'test-table-{}'.format(hash(random.random()))


def do_assert_test(query, data, expected):
    with gp.connection.transaction():
        full_query = build_full_query(query, data)
        validator = validators.validate_assert(full_query, expected)
        validator.validate(gp.connection, random_table_name())


def do_empty_test(query, data):
    with gp.connection.transaction():
        full_query = build_full_query(query, data)
        validator = validators.validate_empty(full_query)
        validator.validate(gp.connection, random_table_name())


def do_nulls_test(data, expected):
    with gp.connection.transaction():
        table_name = random_table_name()
        gp.connection.execute(
            build_full_query("", data).replace('{result_table}', f'"{table_name}"')
        )
        validator = validators.validate_nulls('value', expected)
        validator.validate(gp.connection, table_name)


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'query, data, expected',
    [
        ('select value from {result_table}', [0], 0),
        ('select count(value) as value from {result_table}', ['null'], 0),
        ('select count(value) as value from {result_table}', [0], 1),
        ('select count(value) as value from {result_table}', [1, 2, 3, 'null'], 3),
    ]
)
def test_successful_validate_assert(query, data, expected):
    do_assert_test(query, data, expected)


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'query, data, expected',
    [
        ('select value from {result_table}', [1], 0),
        ('select value from {result_table}', [0, 0], 0),
        ('select count(value) as value from {result_table}', ['null'], 1),
        ('select count(value) as value from {result_table}', [1, 2, 3, 'null'], 4),
    ]
)
def test_failed_validate_assert(query, data, expected):
    with pytest.raises(ValueError):
        do_assert_test(query, data, expected)


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'query, data',
    [
        ('select value from {result_table}', []),
    ]
)
def test_successful_validate_empty(query, data):
    do_empty_test(query, data)


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'query, data',
    [
        ('select value from {result_table}', [0]),
        ('select value from {result_table}', [0, 1]),
    ]
)
def test_failed_validate_empty(query, data):
    with pytest.raises(ValueError):
        do_empty_test(query, data)


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'data, expected',
    [
        ([0, 1], 0),
        (['null'], 1),
        ([0, 1, 'null', 'null', 'null'], 3),
    ]
)
def test_successful_validate_nulls(data, expected):
    do_nulls_test(data, expected)


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'data, expected',
    [
        ([0, 1], 1),
        (['null'], 0),
        ([0, 1, 'null', 'null', 'null'], 0),
        ([0, 1, 'null', 'null', 'null'], 1),
    ]
)
def test_failed_validate_nulls(data, expected):
    with pytest.raises(ValueError):
        do_nulls_test(data, expected)


def test_query_or_file():
    query = "select 0 as value from {result_table}"
    file_name = from_same_directory(__file__, 'validators_test_query.sql')
    validators.validate_assert(query=query)
    validators.validate_assert(query_file=file_name)
    with pytest.raises(ValueError):
        validators.validate_assert()
    with pytest.raises(ValueError):
        validators.validate_assert(query=query, query_file=file_name)


def test_query_validator_wrong_query():
    def validation_func(_): pass

    query = GreenplumQuery.from_string('select 1 from {a}')

    with pytest.raises(ValueError):
        validators.QueryValidator(query, validation_func)

    validators.QueryValidator(query, validation_func, table_name_parameter='a')

    query = GreenplumQuery.from_string('select 1 from {result_table}')
    validators.QueryValidator(query, validation_func)


def generate_data(size):
    return [dict(a=i) for i in range(size)]


def test_query_result_to_much_data():
    with pytest.raises(ValueError):
        validators.QueryResult(
            generate_data(validators.QueryResult.MAX_DATA_SIZE + 1)
        )
    validators.QueryResult(generate_data(validators.QueryResult.MAX_DATA_SIZE))


@pytest.mark.parametrize('data', [
    [],
    generate_data(1),
    generate_data(10),
    generate_data(validators.QueryResult.MAX_DATA_SIZE),
])
def test_query_result(data):
    result = validators.QueryResult(data)

    assert len(result) == len(data)
    assert result.row_count == len(result)
    assert bool(result) == bool(data)

    if data:
        assert result[0] == data[0]
        assert result[-1] == data[-1]
        assert result.first_row == result[0]

    for result_raw, data_row in zip(result, data):
        assert result_raw == data_row

    pd.testing.assert_frame_equal(
        result.as_dataframe(),
        pd.DataFrame.from_records(data),
    )
