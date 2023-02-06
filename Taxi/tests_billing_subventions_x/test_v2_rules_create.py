import datetime

import pytest

from testsuite.utils import ordered_object

from tests_billing_subventions_x import dbhelpers


MOCK_NOW = '2020-04-28T12:00:00+00:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json',
    (
        'single_ride.json',
        'goal.json',
        'goal_personal.json',
        'goal_multiple_counters.json',
        'single_ontop.json',
    ),
)
async def test_v2_rules_create_returns_created_rules(
        make_request, load_json, data_json,
):
    test_data = load_json(data_json)
    json = await make_request(test_data['request'])
    assert json['change_doc_id'].startswith(test_data['change_doc_zones'])
    data = _remove_uuids(json['data'])
    assert data['rule_spec']['rule'].pop('schedule_ref')
    assert data == test_data['response']


def _remove_uuids(data):
    for i in range(len(data['created_rules'])):
        data['created_rules'][i]['id'] = f'<uuid_{i+1}>'
    data['doc_id'] = '<doc_uuid>'
    return data


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json',
    (
        'single_ride.json',
        'goal.json',
        'goal_personal.json',
        'single_ontop.json',
    ),
)
async def test_v2_rules_create_generates_drafts_for_rules(
        make_request, load_json, pgsql, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    response = await make_request(query)
    data = response['data']
    internal_draft_id = data['doc_id']
    schedule_ref = data['rule_spec']['rule']['schedule_ref']
    drafts = dbhelpers.select_rule_drafts(pgsql, internal_draft_id)
    spec = query['rule_spec']
    for rule in drafts:
        assert rule.rule_id
        assert rule.rule_type == spec['rule']['rule_type']
        assert rule.internal_draft_id == internal_draft_id
        assert rule.timezone == ''
        assert rule.starts_at.isoformat() == spec['rule']['start']
        assert rule.ends_at.isoformat() == spec['rule']['end']
        assert rule.tag == spec['rule']['tag']
        assert rule.stop_tag == spec['rule'].get('stop_tag', {}).get('tag')
        assert rule.branding == spec['rule']['branding_type']
        assert rule.min_activity_points == spec['rule']['activity_points']
        assert rule.tariff_zone in spec['zones']
        assert rule.tariff in spec['tariff_classes']
        assert rule.geoarea in spec['geoareas']
        assert rule.schedule_ref == schedule_ref
        if rule.rule_type in ['single_ride', 'single_ontop']:
            assert rule.rates == spec['rule']['rates']
            # goal only fields
            assert rule.currency is None
            assert rule.window_size is None
            assert rule.unique_driver_id is None
        elif rule.rule_type == 'goal':
            assert rule.rates == spec['rule']['counters']
            assert rule.currency == spec['rule']['currency']
            assert rule.window_size == spec['rule']['window']
            assert rule.unique_driver_id == spec['rule'].get(
                'unique_driver_id',
            )
        else:
            raise RuntimeError('Unsupported rule type %r' % rule.rule_type)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json',
    (
        'single_ride.json',
        'goal.json',
        'goal_personal.json',
        'single_ontop.json',
    ),
)
async def test_v2_rules_create_returns_what_has_generated(
        make_request, load_json, pgsql, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    response = await make_request(query)
    rules = response['data']['created_rules']
    drafts = dbhelpers.select_rule_drafts(pgsql, response['data']['doc_id'])
    ordered_object.assert_eq(
        [rule['id'] for rule in rules],
        [draft.rule_id for draft in drafts],
        '',
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json',
    (
        'single_ride.json',
        'goal.json',
        'goal_personal.json',
        'single_ontop.json',
    ),
)
async def test_v2_rules_create_saves_rule_spec(
        make_request, load_json, pgsql, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    response = await make_request(query)
    internal_draft_id = response['data']['doc_id']
    spec = dbhelpers.get_draft_spec(pgsql, internal_draft_id)
    assert spec['spec']['rule'].pop('schedule_ref')
    assert spec == {
        'internal_draft_id': internal_draft_id,
        'spec': query['rule_spec'],
        'creator': 'draft_author',
        'approved_at': None,
        'approvers': None,
        'budget_id': None,
        'draft_id': None,
        'tickets': None,
        'state': 'GENERATED',
        'error': None,
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'goal.json', 'single_ontop.json'),
)
async def test_v2_rules_create_saves_rule_ids_to_close(
        make_request, load_json, pgsql, add_rules, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_rules(query['rule_spec']['rule']['rule_type'], test_data['db'])
    _set_clashing_parameters(query, geoarea='butovo')
    query['old_rule_ids'] = test_data['old_rule_ids']
    response = await make_request(query)
    data = response['data']
    assert data['old_rule_ids'] == query['old_rule_ids']
    start = datetime.datetime.fromisoformat(
        query['rule_spec']['rule']['start'],
    )
    expected = [
        {'rule_id': rule_id, 'new_ends_at': start}
        for rule_id in query['old_rule_ids']
    ]
    ordered_object.assert_eq(
        dbhelpers.select_rules_to_close(pgsql, data['doc_id']), expected, '',
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json,attrs,known_clashing_rules',
    (
        (
            'single_ride.json',
            {'geoarea': 'butovo'},
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
        ),
        (
            'single_ride.json',
            {'tag': 'tag'},
            ['cf730f12-c02b-11ea-acc8-ab6ac87f7711'],
        ),
        (
            'single_ride.json',
            {'branding': 'sticker'},
            ['7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'],
        ),
        (
            'single_ontop.json',
            {'geoarea': 'butovo'},
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
        ),
        (
            'single_ontop.json',
            {'tag': 'tag'},
            ['cf730f12-c02b-11ea-acc8-ab6ac87f7711'],
        ),
        (
            'single_ontop.json',
            {'branding': 'sticker'},
            ['7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc'],
        ),
        (
            'goal.json',
            {'geoarea': 'butovo'},
            [
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
                'b547dfdf-a718-429b-abdd-cda4d4697ba9',
            ],
        ),
        (
            'goal.json',
            {'tag': 'tag'},
            ['91765564-4044-4c06-9ca8-4fc2c1d70e31'],
        ),
        (
            'goal.json',
            {'branding': 'sticker'},
            ['291069b8-7bcf-48ff-8c8f-3e99aa161e97'],
        ),
        (
            'goal.json',
            {'window': 14},
            ['d2169f89-82d3-4d9b-8ee5-93278f3c85ca'],
        ),
        (
            'goal.json',
            {'unique_driver_id': 'fd7ca8a7-124f-4fd9-ac0a-c226ab7b2cb8'},
            [],
        ),
    ),
)
async def test_v2_rules_create_passes_clashing_check(
        make_request,
        load_json,
        add_rules,
        attrs,
        known_clashing_rules,
        data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_rules(query['rule_spec']['rule']['rule_type'], test_data['db'])
    _set_clashing_parameters(query, **attrs)
    query['old_rule_ids'] = known_clashing_rules
    await make_request(query)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json,attrs,clashing_id',
    (
        (
            'single_ride.json',
            {'geoarea': 'butovo'},
            '2abf062a-b607-11ea-998e-07e60204cbcf',
        ),
        (
            'single_ride.json',
            {'tag': 'tag'},
            'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
        ),
        (
            'single_ride.json',
            {'branding': 'sticker'},
            '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
        ),
        (
            'single_ontop.json',
            {'geoarea': 'butovo'},
            '2abf062a-b607-11ea-998e-07e60204cbcf',
        ),
        (
            'single_ontop.json',
            {'tag': 'tag'},
            'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
        ),
        (
            'single_ontop.json',
            {'branding': 'sticker'},
            '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
        ),
        (
            'goal.json',
            {'geoarea': 'butovo'},
            '5e03538d-740b-4e0b-b5f4-1425efa59319',
        ),
        ('goal.json', {'tag': 'tag'}, '91765564-4044-4c06-9ca8-4fc2c1d70e31'),
        (
            'goal.json',
            {'branding': 'sticker'},
            '291069b8-7bcf-48ff-8c8f-3e99aa161e97',
        ),
        ('goal.json', {'window': 14}, 'd2169f89-82d3-4d9b-8ee5-93278f3c85ca'),
        (
            'goal.json',
            {
                'unique_driver_id': 'fd7ca8a7-124f-4fd9-ac0a-c226ab7b2cb8',
                'tag': 'personal',
            },
            '9ad7aef7-9e09-4fd8-9ca1-4ee30ca56083',
        ),
    ),
)
async def test_v2_rules_create_fails_when_rules_clash(
        make_request, load_json, add_rules, data_json, attrs, clashing_id,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_rules(query['rule_spec']['rule']['rule_type'], test_data['db'])
    _set_clashing_parameters(query, **attrs)
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': f'There are conflicting rules. First: {clashing_id}',
    }


def _set_clashing_parameters(
        query,
        *,
        geoarea=None,
        tag=None,
        branding=None,
        window=None,
        unique_driver_id=None,
):
    spec = query['rule_spec']
    if geoarea:
        spec['geoareas'] = [geoarea]
    else:
        spec.pop('geoareas')
    if tag:
        spec['rule']['tag'] = tag
    else:
        spec['rule'].pop('tag')
    if branding:
        spec['rule']['branding_type'] = branding
    else:
        spec['rule'].pop('branding_type')
    if window:
        spec['rule']['window'] = window
    if unique_driver_id:
        spec['rule']['unique_driver_id'] = unique_driver_id


@pytest.mark.now('2020-05-01T21:00:00+0000')
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'goal.json', 'single_ontop.json'),
)
@pytest.mark.config(BILLING_SUBVENTIONS_RULES_START_MIN_THRESHOLD_IN_HOURS=2)
async def test_v2_rules_create_fails_when_late_to_create(
        make_request, load_json, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    query['rule_spec']['rule']['start'] = '2020-05-01T22:30:00+0000'
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'Rules\' start \'2020-05-01T22:30:00+0000\' must be greater than '
            '\'2020-05-01T21:00:00+0000\' + 2 hours'
        ),
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'goal.json', 'single_ontop.json'),
)
async def test_v2_rules_create_fails_when_starts_at_greater_than_ends_at(
        make_request, load_json, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    query['rule_spec']['rule']['start'] = '2020-05-28T21:00:00+0000'
    query['rule_spec']['rule']['end'] = '2020-05-20T21:00:00+0000'
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'Rules\' end \'2020-05-20T21:00:00+0000\' must be greater than '
            '\'2020-05-28T21:00:00+0000\''
        ),
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'goal.json', 'single_ontop.json'),
)
@pytest.mark.parametrize(
    'start,end',
    (
        ('2020-05-21T21:00:01+0000', '2020-05-28T21:00:00+0000'),
        ('2020-05-21T21:00:00.000001+0000', '2020-05-28T21:00:00+0000'),
        ('2020-05-21T21:00:00+0000', '2020-05-28T21:00:01+0000'),
        ('2020-05-21T21:00:00+0000', '2020-05-28T21:00:00.000001+0000'),
    ),
)
async def test_v2_rules_create_fails_when_time_boundaries_not_even(
        make_request, load_json, data_json, start, end,
):
    test_data = load_json(data_json)
    query = test_data['request']
    query['rule_spec']['rule']['start'] = start
    query['rule_spec']['rule']['end'] = end
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            f'Rules\' time boundaries ["{start}", "{end}") must be even'
        ),
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json'),
)
@pytest.mark.parametrize(
    'field,value,message',
    (
        (
            'tariff_classes',
            ['t1', 't2', 't2', 't1'],
            't1, t2: tariff classes must be unique.',
        ),
        ('geoareas', ['g1', 'g2', 'g3', 'g1'], 'g1: geoareas must be unique.'),
        (
            'zones',
            ['z1', 'z2', 'z3', 'z1'],
            'z1: tariff zones must be unique.',
        ),
        ('budget', {}, 'Budget for rules should be specified'),
    ),
)
async def test_v2_rules_create_fails_when_draft_spec_invalid(
        make_request, load_json, data_json, field, value, message,
):
    test_data = load_json(data_json)
    query = test_data['request']
    query['rule_spec'][field] = value
    response = await make_request(query, status=400)
    assert response == {'code': 'INCORRECT_PARAMETERS', 'message': message}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'field,value,message',
    (
        (
            'tariff_classes',
            ['t1', 't2', 't2', 't1'],
            't1, t2: tariff classes must be unique.',
        ),
        ('geoareas', ['g1', 'g2', 'g3', 'g1'], 'g1: geoareas must be unique.'),
        (
            'zones',
            ['z1/z11', 'z2/z21', 'z1/z11/z111'],
            'z1/z11/z111: subnodes forbidden when node (z1/z11) is set.',
        ),
        ('budget', {}, 'Budget for rules should be specified'),
    ),
)
async def test_v2_rules_create_goal_fails_when_draft_spec_invalid(
        make_request, load_json, field, value, message,
):
    query = load_json('goal.json')['request']
    query['rule_spec'][field] = value
    response = await make_request(query, status=400)
    assert response == {'code': 'INCORRECT_PARAMETERS', 'message': message}


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_create_goal_fails_when_activity_period_incorrect(
        make_request, load_json, add_rules,
):
    test_data = load_json('goal.json')
    add_rules('goal', test_data['db'])
    query = test_data['request']
    query['rule_spec']['rule']['window'] = 6
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            f'Activity period (28) must be multiple of the window size (6)'
        ),
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_create_goal_fails_when_old_is_not_exhaustive(
        make_request, load_json, add_rules,
):
    test_data = load_json('goal.json')
    add_rules('goal', test_data['db'])
    query = test_data['request']
    _set_clashing_parameters(query, geoarea='butovo')
    query['old_rule_ids'] = ['5e03538d-740b-4e0b-b5f4-1425efa59319']
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'Goals created simultaneously by the same draft must '
            'be closed simultaneously'
        ),
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_create_goal_fails_when_imposible_close_old_rules(
        make_request, load_json, add_rules,
):
    test_data = load_json('goal.json')
    add_rules('goal', test_data['db'])
    query = test_data['request']
    _set_clashing_parameters(query, branding='sticker')
    query['rule_spec']['rule'].update(
        start='2020-05-01T21:00:00+00:00', end='2020-05-29T21:00:00+00:00',
    )
    query['old_rule_ids'] = ['291069b8-7bcf-48ff-8c8f-3e99aa161e97']
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            '291069b8-7bcf-48ff-8c8f-3e99aa161e97: new activity '
            'period (8) must be multiple of the window size (7)'
        ),
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BILLING_SUBVENTIONS_RULES_START_MIN_THRESHOLD_IN_HOURS=2)
@pytest.mark.parametrize(
    'test_data',
    (
        'goal_action_period_reversed.json',
        'goal_invalid_schedule.json',
        'goal_invalid_counters.json',
    ),
)
async def test_v2_rules_create_goal_fails_when_schedule_is_invalid(
        make_request, load_json, test_data,
):
    data = load_json(test_data)
    query = load_json('goal.json')['request']
    query['rule_spec']['rule'].update(**data['rule_spec_diff'])
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': data['message'],
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'goal.json', 'single_ontop.json'),
)
async def test_v2_rules_create_fails_when_stop_tag_not_for_subventions(
        make_request, load_json, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    query['rule_spec']['rule']['stop_tag']['topics'] = ['some_topic']
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': 'Tag "stop" must have "subventions" topic.',
    }


@pytest.fixture(name='headers')
def make_headers():
    return {'X-YaTaxi-Draft-Author': 'draft_author'}


@pytest.fixture(name='make_request')
def _make_request(taxi_billing_subventions_x, headers):
    async def _run(query, *, status=200):
        response = await taxi_billing_subventions_x.post(
            '/v2/rules/create', query, headers=headers,
        )
        assert response.status_code == status, response.json()
        return response.json()

    return _run
