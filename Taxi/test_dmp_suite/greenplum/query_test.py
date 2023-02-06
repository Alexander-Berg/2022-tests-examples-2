import pandas as pd
import pytest
from psycopg2.sql import Identifier
from psycopg2.sql import SQL

from dmp_suite.greenplum.query import GreenplumQuery


@pytest.mark.slow('gp')
def test_get_dataframe():
    query = GreenplumQuery.from_string('select 1 as a;')
    pd.testing.assert_frame_equal(
        query.get_dataframe(),
        pd.DataFrame.from_records([dict(a=1)])
    )


def test_query_string():
    query = (
        GreenplumQuery.from_string('select 1 as {a};').add_identifiers(a='b')
    )
    assert query.query_string == SQL('select 1 as {};').format(Identifier('b'))
    query = (
        GreenplumQuery.from_string('select %(p)s as {a};')
        .add_identifiers(a='b')
        .add_params(p=1)
    )
    expected = SQL('select %(p)s as {};').format(Identifier('b'))
    assert query.query_string == expected
