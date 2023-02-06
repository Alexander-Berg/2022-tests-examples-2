import pytest

from testsuite.utils import ordered_object

SINGLE_RIDES = [
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
    'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
]

GOALS = ['d2169f89-82d3-4d9b-8ee5-93278f3c85ca']

ALL_RULE_IDS = SINGLE_RIDES + GOALS


@pytest.mark.parametrize(
    'start,end,expected',
    (
        (
            '2020-01-01T20:00:00+00:00',
            '2021-01-01T20:00:00+00:00',
            ALL_RULE_IDS,
        ),
        (
            '2020-02-01T20:00:00+00:00',
            '2021-01-01T20:00:00+00:00',
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
        (
            '2020-03-01T20:00:00+00:00',
            '2021-01-01T20:00:00+00:00',
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
        (
            '2020-04-01T20:00:00+00:00',
            '2021-01-01T20:00:00+00:00',
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
        ),
        ('2020-05-01T20:00:00+00:00', '2021-01-01T20:00:00+00:00', []),
        (
            '2020-02-01T20:00:00+00:00',
            '2020-04-01T20:00:00+00:00',
            [
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
    ),
)
async def test_v2_rules_updates_returns_rules_from_interval(
        taxi_billing_subventions_x, start, end, expected,
):
    query = _make_query(start=start, end=end)
    data = await _make_request(taxi_billing_subventions_x, query)
    _assert_rules(data, expected)


@pytest.mark.parametrize(
    'rule_type,expected',
    ((None, ALL_RULE_IDS), ('single_ride', SINGLE_RIDES), ('goal', GOALS)),
)
async def test_v2_rules_updates_filtered_by_rule_types(
        taxi_billing_subventions_x, rule_type, expected,
):
    query = _make_query(rule_type=rule_type)
    data = await _make_request(taxi_billing_subventions_x, query)
    _assert_rules(data, expected)


@pytest.mark.parametrize(
    'cursor,expected_rules,expected_cursor',
    (
        (
            {},
            [
                'd2169f89-82d3-4d9b-8ee5-93278f3c85ca',
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
            {
                '2020-03-01T21:00:00+0000': (
                    'cf730f12-c02b-11ea-acc8-ab6ac87f7711'
                ),
            },
        ),
        (
            {
                '2020-03-01T21:00:00+0000': (
                    'cf730f12-c02b-11ea-acc8-ab6ac87f7711'
                ),
            },
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
            None,
        ),
    ),
)
async def test_v2_rules_updates_paginated(
        taxi_billing_subventions_x, cursor, expected_rules, expected_cursor,
):
    query = _make_query(limit=3, cursor=cursor)
    data = await _make_request(taxi_billing_subventions_x, query)
    _assert_rules(data, expected_rules)
    assert data.get('next_cursor') == expected_cursor


def _assert_rules(data, expected):
    actual = [rule['id'] for rule in data['rules']]
    ordered_object.assert_eq(actual, expected, '')


async def _make_request(taxi_billing_subventions_x, query):
    url = '/v2/rules/updates'
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.json()
    return response.json()


def _make_query(
        rule_type=None,
        start='2020-01-01T20:00:00+00:00',
        end='2021-01-01T20:00:00+00:00',
        limit=10,
        cursor=None,
):
    query = {'time_range': {'start': start, 'end': end}, 'limit': limit}
    if rule_type is not None:
        query['rule_type'] = rule_type
    if cursor is not None:
        query['cursor'] = cursor
    return query


@pytest.fixture(autouse=True)
def _fill_db(a_single_ride, a_goal, create_rules):
    create_rules(
        a_single_ride(
            id='2abf062a-b607-11ea-998e-07e60204cbcf',
            updated_at='2020-04-01T21:00:00+00:00',
        ),
        a_single_ride(
            id='cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            updated_at='2020-03-01T21:00:00+00:00',
        ),
        a_single_ride(
            id='7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
            updated_at='2020-02-01T21:00:00+00:00',
        ),
        a_goal(
            id='d2169f89-82d3-4d9b-8ee5-93278f3c85ca',
            updated_at='2020-01-01T21:00:00+00:00',
        ),
    )
