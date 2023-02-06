import datetime
import pathlib

import pytest

_SPECIFIC = '2abf062a-b607-11ea-998e-07e60204cbcf'
_NO_CONSTRAINTS = '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'


def test_sql_match_bulk_single_ride_success(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    reference_times = [
        '2022-05-25T11:59:59.999999+03:00',  # no active rules yet
        '2022-05-25T12:00:00+03:00',  # [1] most specific rule activates
        '2022-05-25T13:00:00+03:00',  # [2] no constraint rule activates
        '2022-05-25T14:00:00+03:00',  # [3] guarantee changes for most specific
        '2022-05-25T15:00:00+03:00',  # [4] most specific rule ends here
        '2022-05-25T16:00:00+03:00',  # no constraint rule ends here
    ]
    as_dt = datetime.datetime.fromisoformat
    expected = [
        # [1]
        {
            'id': _SPECIFIC,
            'reference_time': as_dt('2022-05-25T12:00:00+03:00'),
            'value': '150.0',
        },
        # [2]
        {
            'id': _SPECIFIC,
            'reference_time': as_dt('2022-05-25T13:00:00+03:00'),
            'value': '150.0',
        },
        # [3]
        {
            'id': _SPECIFIC,
            'reference_time': as_dt('2022-05-25T14:00:00+03:00'),
            'value': '100.0',
        },
        # [4]
        {
            'id': _NO_CONSTRAINTS,
            'reference_time': as_dt('2022-05-25T15:00:00+03:00'),
            'value': '15.0',
        },
    ]
    cursor.execute(sql, make_params(reference_times=reference_times))
    _assert_expected_rows(cursor, expected)


def _assert_expected_rows(cursor, expected):
    fields = [column.name for column in cursor.description]
    rules = [dict(zip(fields, r)) for r in cursor]
    assert rules == expected


@pytest.fixture(name='sql')
def make_sql():
    fname = (
        pathlib.Path(__file__).parent.absolute()
        / '../../src/sql/rules_match_bulk_single_ride.sql'
    )
    with open(fname) as script:
        sql = script.read()
    sql = sql.replace('%', '%%')
    sql = sql.replace('$1', '%(zone)s')
    sql = sql.replace('$2', '%(tariff)s')
    sql = sql.replace('$3', '%(datetimes)s')
    sql = sql.replace('$4', '%(tags)s')
    sql = sql.replace('$5', '%(geoareas)s')
    sql = sql.replace('$6', '%(brandings)s')
    sql = sql.replace('$7', '%(activity)s')
    sql = sql.replace('$8', '%(timezone)s')
    return sql


def make_params(*, reference_times):
    return {
        'zone': 'moscow',
        'tariff': 'econom',
        'datetimes': reference_times,
        'tags': ['some_tag'],
        'geoareas': ['butovo'],
        'brandings': ['no_sticker', 'no_full_branding'],
        'activity': 100,
        'timezone': 'Europe/Moscow',
    }


@pytest.fixture(autouse=True)
def _fill_db(a_single_ride, a_goal, a_single_ontop, create_rules):
    create_rules(
        a_single_ride(
            id=_SPECIFIC,
            start='2022-05-22:00:00+00:00',
            end='2022-05-29T21:00:00+00:00',
            schedule=[(3600, 3720, '150.0'), (3720, 3780, '100.0')],
            branding='no_full_branding',
            geoarea='butovo',
            tag='some_tag',
            points=60,
        ),
        a_single_ride(
            id=_NO_CONSTRAINTS,
            start='2022-05-22T00:00:00+00:00',
            end='2022-05-29T21:00:00+00:00',
            schedule=[(3660, 3840, '15.0')],
        ),
    )
