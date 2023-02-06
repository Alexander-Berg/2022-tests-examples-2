import pytest

from dmp_suite.greenplum import utils


@pytest.mark.parametrize(
    'query, expected',
    [
        ('', 0),
        (';', 0),
        ('select *;', 1),
        ('select *; select *;', 2),
    ]
)
def test_split_and_strip_query(query, expected):
    assert len(list(utils.split_and_strip_query(query))) == expected


@pytest.mark.parametrize(
    'query, expected',
    [
        ('', []),
        (';', []),
        ('--', []),
        ('-- a', []),
        ('--;', []),
        ('/**/', []),
        ('/* d */', []),
        ('/*\nd\n*/', []),
        ('select *;', ['select *;']),
        ('select *; select *;', ['select *;', 'select *;']),
        ('select *;\n\nselect *;', ['select *;', 'select *;']),
        ('select * \n from test;', ['select * \n from test;']),
        ('select 1; ----', ['select 1; ----']),
        ('select 1;\n----', ['select 1;']),
    ]
)
def test_split_and_strip_query_keep_format(query, expected):
    result = [
        str(statement).strip()
        for statement in utils.split_and_strip_query(query, strip=False)
    ]
    assert result == expected
