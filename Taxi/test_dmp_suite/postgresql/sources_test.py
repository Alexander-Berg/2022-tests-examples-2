import uuid
from operator import itemgetter
from contextlib import contextmanager

import mock
import pytest

from psycopg2.sql import SQL, Identifier, Placeholder

from dmp_suite.yt import NotLayeredYtTable, Int, Datetime, Double, NotLayeredYtLayout
from dmp_suite.postgresql.sources import all_rows
from dmp_suite.postgresql.queries import identifier_or_expression

from connection.pgaas import get_pgaas_connection


def mocked_ctl_storage(param_value):
    """A mock CtlStorage which returns a constant value on any query."""
    return mock.MagicMock(
        yt=mock.MagicMock(get_param=mock.MagicMock(return_value=param_value))
    )


@contextmanager
def temporary_table(fields, table_name, connection):
    with connection.transaction():
        connection.execute(
            SQL("CREATE TEMPORARY TABLE {} {} ON COMMIT DROP").format(
                Identifier(table_name), SQL(fields)
            )
        )
        yield table_name


def insert_rows(connection, table, rows):
    """Insert rows into the source Postgres table."""
    table = identifier_or_expression(table)
    connection.execute(
        SQL("INSERT INTO {} VALUES {}").format(
            table, SQL(", ").join(Placeholder() * len(rows))
        ),
        *rows
    )


@pytest.fixture
def connection():
    with get_pgaas_connection("testing", writable=True) as connection:
        yield connection


@pytest.fixture
def entity_name():
    return uuid.uuid4().hex


@pytest.fixture
def source(request, entity_name, connection):
    """A source table with the same name as the entity name."""
    fields = request.param
    with temporary_table(fields, entity_name, connection) as table_name:
        yield table_name


@pytest.fixture
def differently_named_source(request, connection):
    """A source table with a name distinct from the entity name."""
    fields = request.param
    with temporary_table(fields, uuid.uuid4().hex, connection) as table_name:
        yield table_name


@pytest.fixture
def destination(request, entity_name):
    table_class = request.param

    class TableWithRandomName(table_class):
        __layout__ = NotLayeredYtLayout(folder='randoms', name=entity_name)

    return TableWithRandomName


class Destination(NotLayeredYtTable):
    id = Int()
    created_at = Datetime()
    value = Double()


class DestinationSorted(NotLayeredYtTable):
    created_at = Datetime(sort_key=True, sort_position=0)
    id = Int(sort_key=True, sort_position=1)


SOURCE_FIELDS = """
    (id INT, created_at TIMESTAMP, value NUMERIC)
"""
SOURCE_SORTED_FIELDS = """
    (created_at TIMESTAMP, id INT)
"""

GENERIC_TEST_DATA = [
    (0, "2019-05-12 10:29:00", 7.0),
    (1, "2019-05-12 10:30:00", 3.14),
    (2, "2019-05-12 10:32:00", None),
    (3, "2019-05-12 10:32:00", 3.14),
    (4, "2019-05-12 10:33:00", 3.14),
    (5, "2019-05-12 10:35:00", 3.14),
    (6, None, 3.14),
]
GENERIC_TEST_RESULTS = [
    dict(id=0, created_at="2019-05-12 10:29:00.000000", value=7.0),
    dict(id=1, created_at="2019-05-12 10:30:00.000000", value=3.14),
    dict(id=2, created_at="2019-05-12 10:32:00.000000", value=None),
    dict(id=3, created_at="2019-05-12 10:32:00.000000", value=3.14),
    dict(id=4, created_at="2019-05-12 10:33:00.000000", value=3.14),
    dict(id=5, created_at="2019-05-12 10:35:00.000000", value=3.14),
    dict(id=6, created_at=None, value=3.14),
]


@pytest.mark.slow
def test_connection_pg_simple_select(connection):
    sql = 'select 1;'
    res = next(connection.query(sql))
    assert res[0] == 1


@pytest.mark.slow
@pytest.mark.parametrize(
    "source, differently_named_source, destination",
    [(SOURCE_FIELDS, SOURCE_FIELDS, Destination)], indirect=True)
@pytest.mark.parametrize("wrap_source, use_from", [
    (False, False),
    (True, False),
    (True, True),
])
def test_all_rows(
        connection, source, differently_named_source, destination,
        wrap_source, use_from,
):
    source = differently_named_source if use_from else source
    source = identifier_or_expression(source) if wrap_source else source
    from_ = source if use_from else None
    insert_rows(connection, source, GENERIC_TEST_DATA)
    result = all_rows(connection, destination, from_=from_)
    get_id = itemgetter('id')
    assert sorted(list(result), key=get_id) == sorted(GENERIC_TEST_RESULTS, key=get_id)


@pytest.mark.slow
@pytest.mark.parametrize(
    "source, destination", [(SOURCE_SORTED_FIELDS, DestinationSorted)], indirect=True
)
def test_all_rows_sorted(connection, source, destination):
    insert_rows(
        connection,
        source,
        [
            ("2019-05-12 10:32:00", 3),
            ("2019-05-12 10:32:00", 1),
            ("2019-05-12 10:30:00", 2),
        ],
    )
    assert list(all_rows(connection, destination)) == [
        dict(created_at="2019-05-12 10:30:00.000000", id=2),
        dict(created_at="2019-05-12 10:32:00.000000", id=1),
        dict(created_at="2019-05-12 10:32:00.000000", id=3),
    ]


@pytest.mark.slow
@pytest.mark.parametrize("source, destination", [(SOURCE_FIELDS, Destination)], indirect=True)
def test_all_rows_empty(connection, source, destination):
    assert list(all_rows(connection, destination)) == []
