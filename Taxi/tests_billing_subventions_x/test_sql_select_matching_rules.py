import datetime
import pathlib

import pytest


def test_matching_sql_success(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, make_params())
    _assert_expected_rows(
        cursor,
        [
            '21eb278d-0289-4ab6-b6c6-fe2e73cb02a7',
            '2abf062a-b607-11ea-998e-07e60204cbcf',
            'bef8e75e-c032-11ea-be69-cff5c0924950',
        ],
    )


@pytest.mark.parametrize(
    'reference_time,expected',
    (
        ('2020-07-04T09:59:59.999999+03:00', []),
        (
            '2020-07-04T10:00:00.000000+03:00',
            [
                '21eb278d-0289-4ab6-b6c6-fe2e73cb02a7',  # single_ontop
                '2abf062a-b607-11ea-998e-07e60204cbcf',  # single_ride
                'bef8e75e-c032-11ea-be69-cff5c0924950',  # goal
            ],
        ),
        (
            '2020-07-04T10:29:59.999999+03:00',
            [
                '21eb278d-0289-4ab6-b6c6-fe2e73cb02a7',  # single_ontop
                '2abf062a-b607-11ea-998e-07e60204cbcf',  # single_ride
                'bef8e75e-c032-11ea-be69-cff5c0924950',  # goal
            ],
        ),
        ('2020-07-04T10:30:00.000000+03:00', []),
    ),
)
def test_matching_sql_schedule_bounds(pgsql, sql, reference_time, expected):
    cursor = pgsql['billing_subventions'].cursor()
    now = datetime.datetime.fromisoformat(reference_time)
    cursor.execute(sql, make_params(now=now))
    _assert_expected_rows(cursor, expected)


def test_matching_sql_when_mismatched_tag(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, make_params(tags=['unknown_tag']))
    _assert_expected_rows(cursor, ['7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'])


def test_matching_sql_when_no_tags(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, make_params(tags=[]))
    _assert_expected_rows(cursor, ['7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'])


def test_matching_sql_when_mismatched_geoarea(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, make_params(geoareas=['some_area']))
    _assert_expected_rows(cursor, ['7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'])


def test_matching_sql_when_no_geoareas(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, make_params(geoareas=[]))
    _assert_expected_rows(cursor, ['7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'])


def test_matching_sql_when_mismatched_branding(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, make_params(brandings=['sticker', 'full_branding']))
    _assert_expected_rows(cursor, ['7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'])


def test_matching_sql_when_no_brandings(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, make_params(brandings=[]))
    _assert_expected_rows(cursor, ['7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'])


def test_matching_sql_when_mismatched_activity_points(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, make_params(activity=50.0))
    _assert_expected_rows(cursor, ['7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'])


def test_matching_sql_when_activity_not_set(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, make_params(activity=100))
    _assert_expected_rows(
        cursor,
        [
            '21eb278d-0289-4ab6-b6c6-fe2e73cb02a7',
            '2abf062a-b607-11ea-998e-07e60204cbcf',
            'bef8e75e-c032-11ea-be69-cff5c0924950',
        ],
    )


def test_matching_sql_when_stop_tag_set(pgsql, sql):
    cursor = pgsql['billing_subventions'].cursor()
    tags = [
        'some_tag',
        'another_tag',
        'stop_single_ride_another',
        'stop_goal',
        'stop_ontop',
    ]
    cursor.execute(sql, make_params(tags=tags))
    _assert_expected_rows(cursor, ['2abf062a-b607-11ea-998e-07e60204cbcf'])


def _assert_expected_rows(cursor, expected):
    rules = list(sorted(row[0] for row in cursor))
    assert rules == expected


@pytest.fixture(name='sql')
def make_sql():
    fname = (
        pathlib.Path(__file__).parent.absolute()
        / '../../src/sql/select_matching_rules.sql'
    )
    with open(fname) as script:
        sql = script.read()
    sql = sql.replace('%', '%%')
    sql = sql.replace('$10', '%(geonode)s')
    sql = sql.replace('$11', '%(unique_driver_id)s')
    sql = sql.replace('$1', '%(zone)s')
    sql = sql.replace('$2', '%(tariff)s')
    sql = sql.replace('$3', '%(datetime)s')
    sql = sql.replace('$4', '%(tags)s')
    sql = sql.replace('$5', '%(geoareas)s')
    sql = sql.replace('$6', '%(brandings)s')
    sql = sql.replace('$7', '%(activity)s')
    sql = sql.replace('$8', '%(rule_types)s')
    sql = sql.replace('$9', '%(timezone)s')
    return sql


def make_params(
        now=datetime.datetime.fromisoformat(
            '2020-07-01T10:10:00.000000+00:00',
        ),
        tags=None,
        geoareas=None,
        brandings=None,
        activity=75,
):
    geonode = 'br_russia/br_moscow/br_moscow_center'
    segments = geonode.split('/')
    return {
        'zone': 'moscow',
        'tariff': 'econom',
        'datetime': now,
        'tags': tags if tags is not None else ['some_tag'],
        'geoareas': geoareas if geoareas is not None else ['butovo'],
        'brandings': (
            brandings
            if brandings is not None
            else ['no_sticker', 'no_full_branding']
        ),
        'activity': activity,
        'rule_types': ['single_ride', 'goal', 'single_ontop'],
        'timezone': 'Europe/Moscow',
        'geonode': [
            '/'.join(segments[0 : n + 1]) for n in range(len(segments))
        ],
        'unique_driver_id': None,
    }


@pytest.fixture(autouse=True)
def _fill_db(a_single_ride, a_goal, a_single_ontop, create_rules):
    create_rules(
        a_single_ride(
            id='2abf062a-b607-11ea-998e-07e60204cbcf',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, '150.0'), (7800, 7830, '100.0')],
            branding='no_full_branding',
            geoarea='butovo',
            tag='some_tag',
            points=60,
        ),
        a_single_ride(
            id='cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, '50.0')],
            branding='no_full_branding',
            geoarea='butovo',
            tag='another_tag',
            points=60,
            stop_tag='stop_single_ride_another',
        ),
        a_single_ride(
            id='7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, '15.0')],
        ),
        a_goal(
            id='bef8e75e-c032-11ea-be69-cff5c0924950',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[
                (0, 3780, 'A'),
                (7800, 7830, 'A'),
                # accidently duplicated record (TAXIBILLING-7147)
                (0, 3780, 'A'),
            ],
            branding='no_full_branding',
            geoarea='butovo',
            tag='some_tag',
            points=60,
            stop_tag='stop_goal',
        ),
        a_single_ontop(
            id='21eb278d-0289-4ab6-b6c6-fe2e73cb02a7',
            start='2020-06-28T21:00:00+00:00',
            end='2020-07-05T21:00:00+00:00',
            schedule=[(3600, 3780, '15.0'), (7800, 7830, '10.0')],
            branding='no_sticker',
            geoarea='butovo',
            points=60,
            tag='some_tag',
            stop_tag='stop_ontop',
        ),
    )
