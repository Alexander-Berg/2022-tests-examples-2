# pylint: disable=no-member
import pytest
import test_utils


@pytest.mark.parametrize(
    'ttype',
    [
        'TIMESTAMP',
        'TIMESTAMP (2)',
        'TIMESTAMP WITHOUT TIME ZONE',
        'TIMESTAMP (2) WITHOUT TIME ZONE',
    ],
)
@pytest.mark.parametrize('last', [True, False])
def test_no_tz(last, ttype):
    query = f'CREATE TABLE tbl (x {ttype}'
    if not last:
        query += ', y BIGINT'
    query += ')'

    remarks = test_utils.check_string(query)
    assert len(remarks) == 1

    expect_msg = (
        'Do not use TIMESTAMP WITHOUT TIME ZONE, '
        'see more at https://nda.ya.ru/t/25um2WA353SFcw'
    )
    assert remarks[0].message == expect_msg


@pytest.mark.parametrize(
    'ttype',
    [
        'TIMESTAMPTZ',
        'TIMESTAMPTZ (2)',
        'TIMESTAMP WITH TIME ZONE',
        'TIMESTAMP (2) WITH TIME ZONE',
    ],
)
@pytest.mark.parametrize('last', [True, False])
def test_tz(last, ttype):
    query = f'CREATE TABLE tbl (x {ttype}'
    if not last:
        query += ', y BIGINT'
    query += ')'

    remarks = test_utils.check_string(query)
    assert not remarks
