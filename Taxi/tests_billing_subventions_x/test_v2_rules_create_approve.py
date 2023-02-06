import datetime
import json

import psycopg2
import pytest

from testsuite.utils import ordered_object

from tests_billing_subventions_x import dbhelpers
from tests_billing_subventions_x import types


MOCK_NOW = '2020-04-28T12:00:00+00:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json', 'goal.json'),
)
async def test_v2_rules_create_approve_check_response(
        make_request, load_json, add_draft, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_draft(test_data['draft'], query['rule_spec'])
    response = await make_request(query)
    assert response == {}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json', 'goal.json'),
)
async def test_v2_rules_create_approve_creates_limit(
        make_request, limits, load_json, add_draft, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_draft(test_data['draft'], query['rule_spec'])
    await make_request(query)
    assert limits.times_called == 1
    request = limits.next_call()['request'].json
    assert request == load_json('limits.json')


@pytest.mark.parametrize(
    'budget, limits_calls, subgmv',
    [
        (
            {
                'subgmv': '42',
                'weekly_validation': True,
                'daily_validation': True,
            },
            0,
            True,
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json', 'goal.json'),
)
async def test_v2_rules_create_approve_creates_only_subgmv(
        make_request,
        load_json,
        pgsql,
        limits,
        add_draft,
        budget,
        limits_calls,
        subgmv,
        data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    query['rule_spec']['budget'] = budget
    add_draft(test_data['draft'], query['rule_spec'])
    await make_request(query)
    rule = dbhelpers.get_rule_by_id(
        pgsql, test_data['draft']['rules'][0]['id'],
    )
    budget_id = rule['budget_id']
    actual_budget = dbhelpers.get_budget_by_id(pgsql, budget_id)
    actual_budget.pop('updated_at')
    assert actual_budget == {
        'budget_id': budget_id,
        'threshold': budget['subgmv'],
        'daily': budget['daily_validation'],
        'weekly': budget['weekly_validation'],
        'ticket': 'TAXITICKET1,TAXITICKET2',
    }
    assert limits.times_called == limits_calls


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json', 'goal.json'),
)
async def test_v2_rules_create_approve_creates_rule_from_draft(
        make_request, load_json, pgsql, add_draft, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_draft(test_data['draft'], query['rule_spec'])
    await make_request(query)
    _assert_rules(
        dbhelpers.get_rules_by_draft_id(pgsql, '1111'), test_data['rules'],
    )


def _assert_rules(actual, expected):
    for rule in actual:
        rule.pop('updated_at')
    for rule in expected:
        for field in ('starts_at', 'ends_at'):
            rule[field] = datetime.datetime.fromisoformat(rule[field])
    ordered_object.assert_eq(actual, expected, 'id')


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json', 'goal.json'),
)
@pytest.mark.parametrize(
    'restriction,expected',
    (
        ('geoarea', 'butovo'),
        ('geoarea', None),
        ('tag', 'tag'),
        ('tag', None),
        ('branding', None),
        ('branding', 'sticker'),
        ('activity', None),
        ('activity', 30),
        ('stop_tag', None),
        ('stop_tag', 'stop'),
    ),
)
async def test_v2_rules_create_approve_creates_restriction(
        make_request,
        load_json,
        pgsql,
        add_draft,
        restriction,
        expected,
        data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_draft(test_data['draft'], query['rule_spec'])
    _set_draft_restriction_to(pgsql, restriction, expected, query['doc_id'])
    await make_request(query)
    rule_id = test_data['draft']['rules'][0]['id']
    _assert_restriction(pgsql, restriction, rule_id, expected)


def _set_draft_restriction_to(pgsql, restriction, value, internal_draft_id):
    field = {'activity': 'min_activity_points'}.get(restriction, restriction)
    cursor = pgsql['billing_subventions'].cursor()
    sql = f"""
       UPDATE subventions.draft_rules_to_add
       SET {field} = %s
       WHERE internal_draft_id = %s
    """
    cursor.execute(sql, (value, internal_draft_id))


def _assert_restriction(pgsql, restriction, rule_id, expected):
    field = {
        'branding': 'branding_type',
        'activity': 'min_points',
        'stop_tag': 'tag',
    }.get(restriction, restriction)
    cursor = pgsql['billing_subventions'].cursor()
    sql = f"""
        SELECT {field} FROM subventions.{restriction}_restriction
        WHERE rule_id='{rule_id}'
    """
    cursor.execute(sql)
    value = cursor.fetchone()
    if expected is None:
        assert value is None
    else:
        assert value == (expected,)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json', 'goal.json'),
)
async def test_v2_rules_create_approve_updates_draft_info(
        make_request, load_json, pgsql, add_draft, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_draft(test_data['draft'], query['rule_spec'])
    await make_request(query)
    assert dbhelpers.get_draft_spec(pgsql, query['doc_id']) == {
        'internal_draft_id': query['doc_id'],
        'spec': query['rule_spec'],
        'creator': 'draft_author',
        'approved_at': datetime.datetime.fromisoformat(MOCK_NOW),
        'approvers': 'approver1,approver2',
        'draft_id': '1111',
        'tickets': 'TAXITICKET1,TAXITICKET2',
        'budget_id': None,
        'state': 'APPROVED',
        'error': None,
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json,spec_field,rates,expected',
    (
        (
            'single_ride.json',
            'rates',
            [
                dict(week_day='mon', start='00:00', bonus_amount='15'),
                dict(week_day='mon', start='18:05', bonus_amount='10'),
                dict(week_day='tue', start='12:17', bonus_amount='20'),
            ],
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(0, 1085, '[)'),
                    value='15',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(1085, 2177, '[)'),
                    value='10',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(2177, 10080, '[)'),
                    value='20',
                ),
            ],
        ),
        (
            'single_ride.json',
            'rates',
            [dict(week_day='tue', start='12:17', bonus_amount='20')],
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(0, 2177, '[)'),
                    value='20',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(2177, 10080, '[)'),
                    value='20',
                ),
            ],
        ),
        (
            'single_ride.json',
            'rates',
            [
                dict(week_day='mon', start='23:30', bonus_amount='100'),
                dict(week_day='tue', start='01:30', bonus_amount='0'),
            ],
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(1410, 1530, '[)'),
                    value='100',
                ),
            ],
        ),
        (
            'single_ride.json',
            'rates',
            [
                dict(week_day='sun', start='23:30', bonus_amount='100'),
                dict(week_day='mon', start='00:30', bonus_amount='0'),
            ],
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(0, 30, '[)'),
                    value='100',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(10050, 10080, '[)'),
                    value='100',
                ),
            ],
        ),
        (
            'single_ontop.json',
            'rates',
            [
                dict(week_day='mon', start='00:00', bonus_amount='15'),
                dict(week_day='mon', start='18:05', bonus_amount='10'),
                dict(week_day='tue', start='12:17', bonus_amount='20'),
            ],
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(0, 1085, '[)'),
                    value='15',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(1085, 2177, '[)'),
                    value='10',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(2177, 10080, '[)'),
                    value='20',
                ),
            ],
        ),
        (
            'single_ontop.json',
            'rates',
            [dict(week_day='tue', start='12:17', bonus_amount='20')],
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(0, 2177, '[)'),
                    value='20',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(2177, 10080, '[)'),
                    value='20',
                ),
            ],
        ),
        (
            'single_ontop.json',
            'rates',
            [
                dict(week_day='mon', start='23:30', bonus_amount='100'),
                dict(week_day='tue', start='01:30', bonus_amount='0'),
            ],
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(1410, 1530, '[)'),
                    value='100',
                ),
            ],
        ),
        (
            'single_ontop.json',
            'rates',
            [
                dict(week_day='sun', start='23:30', bonus_amount='100'),
                dict(week_day='mon', start='00:30', bonus_amount='0'),
            ],
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(0, 30, '[)'),
                    value='100',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(10050, 10080, '[)'),
                    value='100',
                ),
            ],
        ),
        (
            'goal.json',
            'counters',
            {
                'schedule': [
                    {'counter': 'A', 'start': '12:00', 'week_day': 'mon'},
                    {'counter': '0', 'start': '13:00', 'week_day': 'mon'},
                    {'counter': 'B', 'start': '18:00', 'week_day': 'mon'},
                    {'counter': '0', 'start': '19:00', 'week_day': 'mon'},
                ],
                'steps': [
                    {'id': 'A', 'steps': [{'amount': '100', 'nrides': 10}]},
                    {'id': 'B', 'steps': [{'amount': '200', 'nrides': 20}]},
                ],
            },
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(720, 780, '[)'),
                    value='A',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(1080, 1140, '[)'),
                    value='B',
                ),
            ],
        ),
        (
            'goal.json',
            'counters',
            {
                'schedule': [
                    {'counter': 'A', 'start': '18:00', 'week_day': 'sun'},
                    {'counter': '0', 'start': '06:00', 'week_day': 'mon'},
                ],
                'steps': [
                    {'id': 'A', 'steps': [{'amount': '100', 'nrides': 10}]},
                ],
            },
            [
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(0, 360, '[)'),
                    value='A',
                ),
                types.ScheduleRange(
                    during=psycopg2.extras.NumericRange(9720, 10080, '[)'),
                    value='A',
                ),
            ],
        ),
    ),
)
async def test_v2_rules_create_approve_creates_internal_schedule(
        make_request,
        pgsql,
        load_json,
        add_draft,
        data_json,
        spec_field,
        rates,
        expected,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_draft(test_data['draft'], query['rule_spec'])
    rule_id = test_data['draft']['rules'][0]['id']
    _update_rates(pgsql, rates, spec_field)
    await make_request(query)
    assert dbhelpers.get_schedule_by_id(pgsql, rule_id) == expected


def _update_rates(pgsql, data, field):
    cursor = pgsql['billing_subventions'].cursor()
    select = """
        SELECT spec from subventions.draft_spec
        WHERE internal_draft_id = 'deadbeef'
    """
    cursor.execute(select)
    spec = cursor.fetchone()[0]
    spec['rule'][field] = data
    update = """
       UPDATE subventions.draft_spec SET spec = %s
       WHERE internal_draft_id = 'deadbeef'
    """
    cursor.execute(update, (json.dumps(spec),))


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json', 'goal.json'),
)
async def test_v2_rules_create_approve_fails_on_unknown_clashing_rules(
        make_request,
        load_json,
        add_draft,
        add_rules,
        data_json,
        limits,
        pgsql,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_draft(test_data['draft'], query['rule_spec'])
    add_rules(query['rule_spec']['rule']['rule_type'], test_data['db'])
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'There are conflicting rules. First: %s' % test_data['clashing'][0]
        ),
    }
    assert limits.times_called == 0
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute('SELECT COUNT(*) FROM subventions.budget')
    assert cursor.fetchone()[0] == 0


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json', 'goal.json'),
)
async def test_v2_rules_create_approve_changes_ends_at_for_known_clashing_rule(
        make_request,
        pgsql,
        load_json,
        add_draft,
        add_rules,
        mark_clashing_as_known,
        data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_draft(test_data['draft'], query['rule_spec'])
    add_rules(query['rule_spec']['rule']['rule_type'], test_data['db'])
    new_ends_at = query['rule_spec']['rule']['start']
    mark_clashing_as_known('deadbeef', new_ends_at, test_data['clashing'])

    await make_request(query)

    for rule_id in test_data['clashing']:
        rule = dbhelpers.get_rule_by_id(pgsql, rule_id)
        assert rule['ends_at'] == datetime.datetime.fromisoformat(new_ends_at)
        assert rule['updated_at'] != datetime.datetime.fromisoformat(
            '2020-03-30T17:45:00+03:00',
        )
        assert _get_log_for_rule(pgsql, rule_id) == {
            'rule_id': rule_id,
            'draft_id': '1111',
            'initiator': 'draft_author',
            'description': 'Close rule at 2020-04-30T21:00:00+0000',
        }


def _get_log_for_rule(pgsql, rule_id):
    cursor = pgsql['billing_subventions'].cursor()
    sql = """
        SELECT rule_id, draft_id, initiator, description
        FROM subventions.rule_change_log
        WHERE rule_id = %s"""
    cursor.execute(sql, (rule_id,))
    fields = [column.name for column in cursor.description]
    rows = cursor.fetchall()
    assert len(rows) == 1
    return dict(zip(fields, rows[0]))


@pytest.mark.now('2020-04-30T21:00:00+00:00')
@pytest.mark.parametrize(
    'data_json', ('single_ride.json', 'single_ontop.json', 'goal.json'),
)
async def test_v2_rules_create_approve_fails_when_late_to_approve(
        make_request, load_json, add_draft, data_json,
):
    test_data = load_json(data_json)
    query = test_data['request']
    add_draft(test_data['draft'], query['rule_spec'])
    response = await make_request(query, status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'Rules\' start \'2020-04-30T21:00:00+0000\' must be greater than '
            '\'2020-04-30T21:00:00+0000\''
        ),
    }


@pytest.fixture(name='limits', autouse=True)
def mock_limits(mockserver):
    @mockserver.json_handler('/billing-limits/v1/create')
    def _limits(request):
        limits_response = request.json
        ref = 'be0a091c-f230-4033-ab89-ba576e279c46'
        limits_response['ref'] = ref
        limits_response['account_id'] = f'budget/{ref}'
        limits_response['tags'] = []
        return limits_response

    return _limits


@pytest.fixture(name='headers')
def make_headers():
    return {
        'X-YaTaxi-Draft-Author': 'me',
        'X-YaTaxi-Draft-Tickets': 'TAXITICKET1,TAXITICKET2',
        'X-YaTaxi-Draft-Approvals': 'approver1,approver2',
        'X-YaTaxi-Draft-Id': '1111',
    }


@pytest.fixture(name='add_draft')
def _make_add_draft(
        create_drafts, a_draft, a_single_ride, a_goal, a_single_ontop,
):
    def _add_draft(draft, spec):
        builder = {
            'single_ride': a_single_ride,
            'single_ontop': a_single_ontop,
            'goal': a_goal,
        }[spec['rule']['rule_type']]
        create_drafts(
            a_draft(
                internal_draft_id=draft['internal_draft_id'],
                spec=draft.get('spec', spec) or {},
                rules=[builder(**rule) for rule in draft.get('rules', [])],
                creator=draft['creator'],
            ),
        )

    return _add_draft


@pytest.fixture(name='make_request')
def _make_request(taxi_billing_subventions_x, headers):
    async def _run(query, *, status=200):
        response = await taxi_billing_subventions_x.post(
            '/v2/rules/create/approve', query, headers=headers,
        )
        assert response.status_code == status, response.json()
        return response.json()

    return _run
