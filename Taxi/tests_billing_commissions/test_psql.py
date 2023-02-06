import datetime
import pathlib
import typing as tp

import pytest


@pytest.mark.pgsql(
    'billing_commissions', files=['defaults.sql', 'test_rules.sql'],
)
def test_select_success(pgsql, sql):
    cursor = pgsql['billing_commissions'].cursor()
    cursor.execute(sql, make_params())
    _assert_expected_rows(cursor, ['2abf062a-b607-11ea-998e-07e60204cbcf'])


@pytest.mark.pgsql('billing_commissions', files=['defaults.sql'])
def test_software_subscription_exists(pgsql):
    cursor = pgsql['billing_commissions'].cursor()
    cursor.execute(
        'select * from fees.category where kind = %(software_subscription)s',
        {'software_subscription': 'software_subscription'},
    )
    assert list(cursor)


@pytest.mark.pgsql(
    'billing_commissions', files=['defaults.sql', 'test_rules.sql'],
)
def test_select_success_no_tariff(pgsql, sql):
    cursor = pgsql['billing_commissions'].cursor()
    cursor.execute(
        sql,
        make_params(
            now=datetime.datetime.fromisoformat(
                '2021-01-01T22:00:00.000000+00:00',
            ),
            zone='spb',
        ),
    )
    _assert_expected_rows(cursor, ['f3a0503d-3f30-4a43-8e30-71d77ebcaa1f'])


@pytest.fixture(name='sql')
def make_sql():
    fname = (
        pathlib.Path(__file__).parent.absolute()
        / '../../src/sql/select_rules.sql'
    )
    with open(fname) as script:
        sql = script.read()
    sql = sql.replace('$1', '%(zone)s')
    sql = sql.replace('$2', '%(tariff)s')
    sql = sql.replace('$3', '%(active_at)s')
    sql = sql.replace('$4', '%(tag)s')
    sql = sql.replace('$5', '%(payment_type)s')
    sql = sql.replace('$6', '%(hiring_type)s')
    sql = sql.replace('$7', '%(fine_code)s')
    return sql


@pytest.fixture(name='explain_sql')
def make_explain_sql(sql):
    return 'explain({})'.format(sql)


def make_params(
        now=datetime.datetime.fromisoformat(
            '2021-01-01T00:00:00.000000+00:00',
        ),
        zone='moscow',
        tariff: tp.Optional[str] = 'econom',
        tag: tp.Optional[tp.List[str]] = None,
        payment_type: tp.Optional[str] = None,
        hiring_type: tp.Optional[str] = None,
        fine_code: tp.Optional[str] = None,
):
    return {
        'zone': zone,
        'active_at': now,
        'tariff': tariff,
        'tag': tag,
        'payment_type': payment_type,
        'hiring_type': hiring_type,
        'fine_code': fine_code,
    }


def _assert_expected_rows(cursor, expected):
    rules = list(sorted(row[0] for row in cursor))
    assert rules == expected
