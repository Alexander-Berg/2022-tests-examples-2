import pytest

from dmp_suite.exceptions import ConfigError
from dmp_suite.dq_metrics.impl import (
    _get_tmp_table_names_from_string,
    _get_tmp_table_names,
    get_tmp_table_names,
    is_similar,
    check_attribute_membership,
)
from test_dmp_suite import dq_metrics
from .query_data import SomeTable, OtherTable


@pytest.mark.parametrize(
    "query, expected",
    [
        (None, []),
        ("create temporary table tmp_table1 on commit drop as", ["tmp_table1"]),
        ("""
        CREATE TEMPORARY TABLE tmp_table1 ON COMMIT DROP AS
        SOME IRRELEVANT STUFF
        SOME IRRELEVANT STUFF
        create  temporary  table  tmp_table2    ON  COMMIT  DROP  AS   
        """, ["tmp_table1", "tmp_table2"]),
    ]
)
def test_get_tmp_table_names_from_string(query, expected):
    assert _get_tmp_table_names_from_string(query) == expected


@pytest.mark.parametrize(
    "query_file, query_package, expected",
    [
        (None, None, []),
        ("some_query.sql", dq_metrics, ["tmp_table1", "tmp_table2", "tmp_table1__exclude", "tmp_table3"]),
    ]
)
def test__get_tmp_table_names(query_file, query_package, expected):
    assert _get_tmp_table_names(query_file, query_package) == expected


@pytest.mark.parametrize(
    "query_file, query_package, expected",
    [
        (None, None, []),
        ("some_query.sql", dq_metrics, ["tmp_table1", "tmp_table2", "tmp_table3"]),
    ]
)
def test_get_tmp_table_names(query_file, query_package, expected):
    assert get_tmp_table_names(query_file, query_package) == expected


@pytest.mark.parametrize(
    "obj, other, by_attributes, expected",
    [
        (SomeTable, SomeTable, ["some_attribute_1", "some_attribute_2", "some_attribute_3", "some_attribute_4"], True),
        (SomeTable, OtherTable, ["some_attribute_1", "some_attribute_2", "some_attribute_3", "some_attribute_4"], False),
        (SomeTable, OtherTable, ["some_attribute_1", "some_attribute_2"], True),
    ]
)
def test_is_similar(obj, other, by_attributes, expected):
    assert is_similar(obj, other, *by_attributes) is expected


@pytest.mark.parametrize(
    "table, attribute, raise_exception",
    [
        (SomeTable, SomeTable.some_attribute_1, False),
        (SomeTable, OtherTable.some_attribute_5, True),
    ]
)
def test_check_attribute_membership(table, attribute, raise_exception):
    if raise_exception:
        with pytest.raises(ConfigError):
            check_attribute_membership(table, attribute)
    else:
        check_attribute_membership(table, attribute)
