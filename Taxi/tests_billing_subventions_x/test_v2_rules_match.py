import pytest

from testsuite.utils import ordered_object


async def test_v2_rules_match_returns_matching_single_ride_rule(
        taxi_billing_subventions_x, url, query, single_ride,
):
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.content
    single_ride_rules = _extract_single_ride_rules(response)
    assert len(single_ride_rules) == 1


@pytest.mark.parametrize(
    'rule_1,rule_2,params,expected',
    (
        (
            # geoarea vs None
            {'geoarea': 'butovo'},
            {'geoarea': None},
            {'geoareas': ['butovo', 'sviblovo']},
            '5b2c9c19-9778-4b99-836b-446c00955cee',
        ),
        (
            # geoarea vs later georea
            {'geoarea': 'butovo'},
            {'geoarea': 'sviblovo'},
            {'geoareas': ['butovo', 'sviblovo']},
            '5b2c9c19-9778-4b99-836b-446c00955cee',
        ),
        (
            # geoarea vs earlier georea
            {'geoarea': 'butovo'},
            {'geoarea': 'sviblovo'},
            {'geoareas': ['sviblovo', 'butovo']},
            'ae5a4b63-81f4-4aec-8006-0ea855880815',
        ),
        (
            # tag vs None
            {'tag': 'some_tag'},
            {'tag': None},
            {'tags': ['some_tag', 'another_tag']},
            '5b2c9c19-9778-4b99-836b-446c00955cee',
        ),
        (
            # tag vs earlier tag
            {'tag': 'some_tag'},
            {'tag': 'another_tag'},
            {'tags': ['some_tag', 'another_tag']},
            'ae5a4b63-81f4-4aec-8006-0ea855880815',
        ),
        (
            # branding vs None
            {'branding': 'no_full_branding'},
            {'branding': None},
            {'has_sticker': True, 'has_lightbox': False},
            '5b2c9c19-9778-4b99-836b-446c00955cee',
        ),
        (
            # branding vs more branding
            {'branding': 'no_full_branding'},
            {'branding': 'sticker'},
            {'has_sticker': True, 'has_lightbox': False},
            'ae5a4b63-81f4-4aec-8006-0ea855880815',
        ),
        (
            # activity points vs None
            {'points': 60},
            {'points': None},
            {'activity_points': 75},
            '5b2c9c19-9778-4b99-836b-446c00955cee',
        ),
        (
            # activity points vs more activity points
            {'points': 60},
            {'points': 75},
            {'activity_points': 75},
            'ae5a4b63-81f4-4aec-8006-0ea855880815',
        ),
        (
            # full house: geoarea first...
            {
                'geoarea': 'sviblovo',
                'tag': 'another_tag',
                'branding': 'sticker',
                'points': 75,
            },
            {
                'geoarea': 'butovo',
                'tag': 'some_tag',
                'branding': 'no_full_branding',
                'points': 60,
            },
            {
                'tags': ['some_tag', 'another_tag'],
                'geoareas': ['butovo', 'sviblovo'],
                'has_sticker': True,
                'has_lightbox': False,
                'activity_points': 100,
            },
            'ae5a4b63-81f4-4aec-8006-0ea855880815',
        ),
        (
            # full house: ... than tag ...
            {
                'geoarea': 'butovo',
                'tag': 'another_tag',
                'branding': 'sticker',
                'points': 75,
            },
            {
                'geoarea': 'butovo',
                'tag': 'some_tag',
                'branding': 'no_full_branding',
                'points': 60,
            },
            {
                'tags': ['some_tag', 'another_tag'],
                'geoareas': ['butovo', 'sviblovo'],
                'has_sticker': True,
                'has_lightbox': False,
                'activity_points': 100,
            },
            '5b2c9c19-9778-4b99-836b-446c00955cee',
        ),
        (
            # full house: ... than branding ...
            {
                'geoarea': 'butovo',
                'tag': 'some_tag',
                'branding': 'sticker',
                'points': 75,
            },
            {
                'geoarea': 'butovo',
                'tag': 'some_tag',
                'branding': 'no_full_branding',
                'points': 60,
            },
            {
                'tags': ['some_tag', 'another_tag'],
                'geoareas': ['butovo', 'sviblovo'],
                'has_sticker': True,
                'has_lightbox': False,
                'activity_points': 100,
            },
            '5b2c9c19-9778-4b99-836b-446c00955cee',
        ),
        (
            # full house: ... and points
            {
                'geoarea': 'butovo',
                'tag': 'some_tag',
                'branding': 'no_full_branding',
                'points': 75,
            },
            {
                'geoarea': 'butovo',
                'tag': 'some_tag',
                'branding': 'no_full_branding',
                'points': 60,
            },
            {
                'tags': ['some_tag', 'another_tag'],
                'geoareas': ['butovo', 'sviblovo'],
                'has_sticker': True,
                'has_lightbox': False,
                'activity_points': 100,
            },
            '5b2c9c19-9778-4b99-836b-446c00955cee',
        ),
    ),
)
async def test_v2_rules_match_select_the_only_single_ride(
        taxi_billing_subventions_x,
        url,
        query,
        create_rules,
        a_single_ride,
        rule_1,
        rule_2,
        params,
        expected,
):

    create_rules(
        a_single_ride(
            id='5b2c9c19-9778-4b99-836b-446c00955cee',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, '150.0')],
            **rule_1,
        ),
        a_single_ride(
            id='ae5a4b63-81f4-4aec-8006-0ea855880815',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, '150.0')],
            **rule_2,
        ),
    )
    query.update(**params)
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.content
    single_ride_rules = _extract_single_ride_rules(response)
    assert [rule['rule']['id'] for rule in single_ride_rules] == [expected]
    # cross check bulk handler
    bulk_query = {
        attr: query[attr]
        for attr in [
            'geoareas',
            'has_lightbox',
            'has_sticker',
            'tags',
            'tariff_class',
            'timezone',
            'zone',
        ]
    }
    bulk_query['reference_times'] = [query['reference_time']]
    response = await taxi_billing_subventions_x.post(
        '/v2/rules/match/bulk_single_ride', json=bulk_query,
    )
    assert response.status_code == 200, response.json()
    assert response.json()['matches'] == [
        {
            'reference_time': '2020-07-01T10:10:22+00:00',
            'id': expected,
            'amount': '150.0',
        },
    ]


async def test_v2_rules_match_returns_matching_single_ontop_rule(
        taxi_billing_subventions_x, url, query, single_ontop,
):
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.content
    single_ontop_rules = _extract_single_ontop_rules(response)
    assert len(single_ontop_rules) == 2


@pytest.mark.parametrize(
    'field,value',
    (
        ('geonode', 'br_russia/br_moscow'),
        ('geonode', 'br_russia/br_moscow/br_moscow_center'),
    ),
)
async def test_v2_rules_match_returns_matching_goal_rule(
        taxi_billing_subventions_x, url, query, goal, field, value,
):
    query[field] = value
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.content
    rules = _extract_goal_rules(response)
    assert len(rules) == 1


async def test_v2_rules_match_returns_matching_personal_goal_rule(
        taxi_billing_subventions_x, url, query, personal_goal,
):
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.content
    rules = _extract_goal_rules(response)
    assert len(rules) == 1
    assert rules[0] == {
        'rule': {
            'id': 'deef22c0-79ed-4e35-9c59-ca2ea5a9df62',
            'budget_id': 'deadbeef',
            'currency': 'RUB',
            'start': '2020-05-31T21:00:00+00:00',
            'end': '2020-08-31T21:00:00+00:00',
            'updated_at': '2020-05-31T21:00:00+00:00',
            'window_size': 7,
            'is_personal': True,
        },
        'type': 'goal',
        'window': {
            'counter': 'draft_id:A',
            'start': '2020-06-28T21:00:00+00:00',
            'end': '2020-07-05T21:00:00+00:00',
            'number': 5,
            'steps': [{'amount': '100', 'nrides': 10}],
        },
    }


async def test_v2_rules_match_returns_matching_multiple_goal_rules(
        taxi_billing_subventions_x, url, query, goal_multiple_schedule,
):
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.content
    rules = _extract_goal_rules(response)
    assert len(rules) == 2
    assert rules == [
        {
            'rule': {
                'id': '2d8e0d52-1767-402d-a572-3976bbcb29a9',
                'budget_id': 'deadbeef',
                'currency': 'RUB',
                'start': '2020-05-31T21:00:00+00:00',
                'end': '2020-08-31T21:00:00+00:00',
                'updated_at': '2020-05-31T21:00:00+00:00',
                'window_size': 7,
                'is_personal': False,
            },
            'type': 'goal',
            'window': {
                'counter': 'draft_id:A',
                'start': '2020-06-28T21:00:00+00:00',
                'end': '2020-07-05T21:00:00+00:00',
                'number': 5,
                'steps': [{'amount': '100', 'nrides': 10}],
            },
        },
        {
            'rule': {
                'id': '2d8e0d52-1767-402d-a572-3976bbcb29a9',
                'budget_id': 'deadbeef',
                'currency': 'RUB',
                'start': '2020-05-31T21:00:00+00:00',
                'end': '2020-08-31T21:00:00+00:00',
                'updated_at': '2020-05-31T21:00:00+00:00',
                'window_size': 7,
                'is_personal': False,
            },
            'type': 'goal',
            'window': {
                'counter': 'draft_id:B',
                'start': '2020-06-28T21:00:00+00:00',
                'end': '2020-07-05T21:00:00+00:00',
                'number': 5,
                'steps': [{'amount': '200', 'nrides': 20}],
            },
        },
    ]


async def test_v2_rules_match_returns_single_ride_rule_with_expected_schema(
        taxi_billing_subventions_x, url, query, single_ride,
):
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.content
    single_ride_rules = _extract_single_ride_rules(response)
    assert single_ride_rules[0] == {
        'amount': '150.0',
        'rule': {
            'activity_points': 60,
            'branding_type': 'no_full_branding',
            'budget_id': 'deadbeef',
            'draft_id': 'c0de',
            'end': '2020-08-31T21:00:00+00:00',
            'geoarea': 'butovo',
            'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
            'rates': [
                {'week_day': 'wed', 'start': '12:00', 'bonus_amount': '150.0'},
                {'week_day': 'wed', 'start': '15:00', 'bonus_amount': '0.0'},
            ],
            'rule_type': 'single_ride',
            'schedule_ref': 'schedule_ref',
            'start': '2020-05-31T21:00:00+00:00',
            'tag': 'some_tag',
            'tariff_class': 'econom',
            'zone': 'moscow',
            'updated_at': '2020-05-31T21:00:00+00:00',
        },
        'type': 'single_ride',
    }


async def test_v2_rules_match_returns_single_ontop_rule_with_expected_schema(
        taxi_billing_subventions_x, url, query, single_ontop,
):
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.content
    single_ontop_rules = _extract_single_ontop_rules(response)
    expected = [
        {
            'amount': '142.0',
            'rule': {
                'budget_id': 'deadbeef',
                'end': '2020-08-31T21:00:00+00:00',
                'id': '2abf062a-b607-11ea-998e-07e60204cbdf',
                'start': '2020-05-31T21:00:00+00:00',
                'tariff_class': 'econom',
                'zone': 'moscow',
            },
            'type': 'single_ontop',
        },
        {
            'amount': '-142.0',
            'rule': {
                'id': '2abf062a-b607-11ea-998e-07e60204cbef',
                'budget_id': 'deadbeef',
                'end': '2020-08-31T21:00:00+00:00',
                'start': '2020-05-31T21:00:00+00:00',
                'tariff_class': 'econom',
                'zone': 'moscow',
                'geoarea': 'butovo',
            },
            'type': 'single_ontop',
        },
    ]
    ordered_object.assert_eq(single_ontop_rules, expected, ['', 'rule.id'])


async def test_v2_rules_match_returns_goal_rule_with_expected_schema(
        taxi_billing_subventions_x, url, query, goal,
):
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.content
    rules = _extract_goal_rules(response)
    assert rules[0] == {
        'rule': {
            'id': '2d8e0d52-1767-402d-a572-3976bbcb29a9',
            'budget_id': 'deadbeef',
            'currency': 'RUB',
            'start': '2020-05-31T21:00:00+00:00',
            'end': '2020-08-31T21:00:00+00:00',
            'updated_at': '2020-05-31T21:00:00+00:00',
            'window_size': 7,
            'is_personal': False,
        },
        'type': 'goal',
        'window': {
            'counter': 'draft_id:A',
            'start': '2020-06-28T21:00:00+00:00',
            'end': '2020-07-05T21:00:00+00:00',
            'number': 5,
            'steps': [{'amount': '100', 'nrides': 10}],
        },
    }


@pytest.mark.parametrize(
    'field,value',
    (
        ('reference_time', '2020-01-01T13:10:22.000Z'),  # < start
        ('reference_time', '2020-10-01T13:10:22.000Z'),  # > end
        ('reference_time', '2020-07-01T13:10:22.000Z'),  # schedule miss
        (
            'reference_time',
            '2020-07-01T16:10:22.000+03:00',
        ),  # schedule miss in rule timezone
        ('activity_points', 50),
        ('tariff_class', 'comfort'),
        ('zone', 'spb'),
        ('tags', ['subv_disable_all']),
        ('tags', ['subv_disable_single_ride']),
        ('rule_types', []),
        ('rule_types', ['goal']),
    ),
)
async def test_v2_rules_match_filter_unmatched_single_ride_rules(
        taxi_billing_subventions_x, url, query, single_ride, field, value,
):
    query[field] = value
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.json()
    single_ride_rules = _extract_single_ride_rules(response)
    assert single_ride_rules == []


@pytest.mark.parametrize(
    'field,value',
    (
        ('reference_time', '2020-01-01T13:10:22.000Z'),  # < start
        ('reference_time', '2020-10-01T13:10:22.000Z'),  # > end
        ('reference_time', '2020-07-01T13:10:22.000Z'),  # schedule miss
        (
            'reference_time',
            '2020-07-01T16:10:22.000+03:00',
        ),  # schedule miss in rule timezone
        ('activity_points', 50),
        ('tariff_class', 'comfort'),
        ('zone', 'spb'),
        ('tags', ['subv_disable_all']),
        ('tags', ['subv_disable_single_ontop']),
        ('rule_types', []),
        ('rule_types', ['goal']),
    ),
)
async def test_v2_rules_match_filter_unmatched_single_ontop_rules(
        taxi_billing_subventions_x, url, query, single_ride, field, value,
):
    query[field] = value
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.json()
    single_ontop_rules = _extract_single_ontop_rules(response)
    assert single_ontop_rules == []


@pytest.mark.parametrize(
    'field,value',
    (
        ('reference_time', '2020-01-01T13:10:22.000Z'),  # < start
        ('reference_time', '2020-10-01T13:10:22.000Z'),  # > end
        ('reference_time', '2020-07-01T13:10:22.000Z'),  # schedule miss
        (
            'reference_time',
            '2020-07-01T16:10:22.000+03:00',
        ),  # schedule miss in rule timezone
        ('activity_points', 50),
        ('tariff_class', 'comfort'),
        ('tags', ['subv_disable_all']),
        ('tags', ['subv_disable_goal']),
        ('rule_types', []),
        ('rule_types', ['single_ride']),
        ('timezone', 'Asia/Vladivostok'),
        ('geonode', 'br_russia/br_moscow_region/podolsk'),
        ('geonode', 'br_russia'),
    ),
)
async def test_v2_rules_match_filter_unmatched_goal_rules(
        taxi_billing_subventions_x, url, query, goal, field, value,
):
    query[field] = value
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.json()
    rules = _extract_goal_rules(response)
    assert rules == []


@pytest.mark.parametrize(
    'field,value',
    (
        ('tags', ['subv_disable_personal_goal']),
        ('unique_driver_id', None),
        ('unique_driver_id', 'be34d3b2-8030-4826-b7f1-527612202f83'),
    ),
)
async def test_v2_rules_match_filter_unmatched_personal_goal_rules(
        taxi_billing_subventions_x, url, query, personal_goal, field, value,
):
    query[field] = value
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.json()
    rules = _extract_goal_rules(response)
    assert rules == []


_ANY_GEOAREA_RULE = '2abf062a-b607-11ea-998e-07e60204cbcf'
_GEOAREA_ONE_RULE = '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'
_GEOAREA_TWO_RULE = '2d8e0d52-1767-402d-a572-3976bbcb29a9'


@pytest.mark.parametrize(
    'geoareas,expected',
    (
        (['one', 'two'], [_ANY_GEOAREA_RULE, _GEOAREA_ONE_RULE]),
        (['two', 'one'], [_ANY_GEOAREA_RULE, _GEOAREA_TWO_RULE]),
        (['two', 'one', ''], [_ANY_GEOAREA_RULE, _GEOAREA_TWO_RULE]),
    ),
)
async def test_v2_rules_match_selects_one_goal_per_draft(
        taxi_billing_subventions_x, url, query, goals, geoareas, expected,
):
    query['geoareas'] = geoareas
    response = await taxi_billing_subventions_x.post(url, query)
    assert response.status_code == 200, response.json()
    rules = _extract_goal_rules(response)
    ordered_object.assert_eq(
        [rule['rule']['id'] for rule in rules], expected, '',
    )


@pytest.fixture(scope='module', name='url')
def make_url():
    return '/v2/rules/match'


@pytest.fixture(name='query')
def make_query():
    return {
        'activity_points': 75,
        'geoareas': ['butovo'],
        'has_lightbox': False,
        'has_sticker': True,
        'reference_time': '2020-07-01T10:10:22.000Z',
        'tags': ['some_tag'],
        'tariff_class': 'econom',
        'zone': 'moscow',
        'geonode': 'br_russia/br_moscow/br_moscow_center',
        'timezone': 'Europe/Moscow',
        'unique_driver_id': 'cd74d504-f2e0-43bd-9553-3f07cb01fa93',
        'rule_types': None,
    }


def _extract_single_ride_rules(response):
    return [
        match
        for match in response.json()['matches']
        if match['type'] == 'single_ride'
    ]


def _extract_goal_rules(response):
    return [
        match
        for match in response.json()['matches']
        if match['type'] == 'goal'
    ]


def _extract_single_ontop_rules(response):
    return [
        match
        for match in response.json()['matches']
        if match['type'] == 'single_ontop'
    ]


@pytest.fixture(name='single_ride')
def _make_single_ride(a_single_ride, create_rules):
    create_rules(
        a_single_ride(
            id='2abf062a-b607-11ea-998e-07e60204cbcf',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, '150.0')],
            rates=[
                {'bonus_amount': '150.0', 'start': '12:00', 'week_day': 'wed'},
                {'bonus_amount': '0.0', 'start': '15:00', 'week_day': 'wed'},
            ],
            branding='no_full_branding',
            geoarea='butovo',
            tag='some_tag',
            points=60,
            updated_at='2020-05-31T21:00:00+00:00',
        ),
        budget_id='deadbeef',
        draft_id='c0de',
    )


@pytest.fixture(name='single_ontop')
def _make_single_ontop(a_single_ontop, create_rules):
    create_rules(
        a_single_ontop(
            id='2abf062a-b607-11ea-998e-07e60204cbdf',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, '142.0')],
            branding='no_full_branding',
            tag='some_tag',
            points=60,
            updated_at='2020-05-31T21:00:00+00:00',
        ),
        a_single_ontop(
            id='2abf062a-b607-11ea-998e-07e60204cbef',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, '-142.0')],
            geoarea='butovo',
            points=60,
            updated_at='2020-05-31T21:00:00+00:00',
        ),
        budget_id='deadbeef',
        draft_id='dec0de',
    )


@pytest.fixture(name='goal')
def _make_goal(a_goal, create_rules):
    create_rules(
        a_goal(
            id='2d8e0d52-1767-402d-a572-3976bbcb29a9',
            geonode='br_russia/br_moscow',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, 'A')],
            points=70,
            updated_at='2020-05-31T21:00:00+00:00',
        ),
        budget_id='deadbeef',
        draft_id='draft_id',
    )


@pytest.fixture(name='personal_goal')
def _make_personal_goal(a_goal, create_rules):
    create_rules(
        a_goal(
            id='deef22c0-79ed-4e35-9c59-ca2ea5a9df62',
            geonode='br_russia/br_moscow',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, 'A')],
            points=70,
            unique_driver_id='cd74d504-f2e0-43bd-9553-3f07cb01fa93',
            updated_at='2020-05-31T21:00:00+00:00',
        ),
        budget_id='deadbeef',
        draft_id='draft_id',
    )


@pytest.fixture(name='goal_multiple_schedule')
def _make_goal_with_multiple_schedule(a_goal, create_rules):
    create_rules(
        a_goal(
            id='2d8e0d52-1767-402d-a572-3976bbcb29a9',
            geonode='br_russia/br_moscow',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, 'A,B')],
            points=70,
            updated_at='2020-05-31T21:00:00+00:00',
        ),
        budget_id='deadbeef',
        draft_id='draft_id',
    )


@pytest.fixture(name='goals')
def _make_multiple_goals(a_goal, create_rules):
    create_rules(
        a_goal(
            id='2abf062a-b607-11ea-998e-07e60204cbcf',
            geonode='br_russia/br_moscow/br_moscow_center',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(1800, 6660, 'B')],
        ),
        draft_id='11111',
    )
    create_rules(
        a_goal(
            id='7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
            geonode='br_russia/br_moscow',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, 'A')],
            geoarea='one',
        ),
        a_goal(
            id='2d8e0d52-1767-402d-a572-3976bbcb29a9',
            geonode='br_russia/br_moscow',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            schedule=[(3600, 3780, 'A')],
            geoarea='two',
        ),
        draft_id='22222',
    )
