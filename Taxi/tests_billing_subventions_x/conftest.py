# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json
import uuid

from billing_subventions_x_plugins import *  # noqa: F403 F401
import psycopg2
import pytest

from tests_billing_subventions_x import dbhelpers


@pytest.fixture(name='tariffs', autouse=True)
def mock_taxi_tariffs(mockserver, load_json):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _tariff_zones(request):
        zones = [
            {
                'name': name,
                'time_zone': 'Europe/Moscow',
                'country': 'rus',
                'translation': '',
                'currency': 'RUB',
            }
            for name in request.query['zone_names'].split(',')
        ]
        return {'zones': zones}

    @mockserver.json_handler('/taxi-tariffs/v1/tariff/current')
    def _current_tariff(_):
        return {
            'home_zone': 'moscow_home_zone',
            'activation_zone': 'moscow_home_zone_activation',
            'date_from': '2020-01-22T15:30:00+00:00',
            'categories': load_json('categories.json'),
        }


@pytest.fixture(name='a_draft')
def _draft_builder():
    def _builder(
            internal_draft_id=None,
            spec=None,
            creator=None,
            subdrafts=None,
            rules=None,
            rules_to_close=None,
            schedule_spec=None,
            approved_at=None,
            approvers='',
            tickets='',
            draft_id=None,
            budget_id=None,
    ):
        spec = spec if spec is not None else {}
        close_clashing_at = spec.get('rule', {}).get(
            'start', '2021-01-01T00:00:00+03:00',
        )
        return {
            'internal_draft_id': internal_draft_id or str(uuid.uuid4()),
            'spec': json.dumps(spec),
            'creator': creator or 'fake_author',
            'subdrafts': subdrafts or [],
            'rules': rules or [],
            'rules_to_close': rules_to_close or [],
            'close_clashing_at': close_clashing_at,
            'schedule_spec': schedule_spec or [],
            'approved_at': approved_at,
            'approvers': approvers,
            'tickets': tickets,
            'draft_id': draft_id,
            'budget_id': budget_id,
        }

    return _builder


@pytest.fixture(name='a_subdraft')
def _subdraft_builder():
    def _builder(*, spec_ref, spec, error=None, is_completed=False):
        return {
            'spec_ref': spec_ref,
            'spec': json.dumps(spec if spec is not None else {}),
            'error': error,
            'is_completed': is_completed,
        }

    return _builder


@pytest.fixture(name='create_drafts')
def _make_drafts_inserter(pgsql):
    def _create_drafts(*drafts):
        cursor = pgsql['billing_subventions'].cursor()
        _insert_draft_specs(cursor, drafts)
        _update_draft_specs(cursor, drafts)
        _mark_drafts_approved(cursor, drafts)

    return _create_drafts


def _update_draft_specs(cursor, drafts):
    sql = dbhelpers.load_sql('update_draft_spec.sql')
    attrs = ['draft_id', 'tickets', 'approvers']
    for draft in drafts:
        if any(draft[attr] for attr in attrs):
            cursor.execute(
                sql,
                (
                    draft['draft_id'],
                    draft['tickets'],
                    draft['approvers'],
                    draft['approved_at'],
                    draft['internal_draft_id'],
                ),
            )


def _mark_drafts_approved(cursor, drafts):
    approved = [d for d in drafts if d['approved_at'] is not None]
    for draft in approved:
        _approve_drafts(
            cursor,
            draft['internal_draft_id'],
            draft['draft_id'],
            draft['budget_id'],
        )
        _log_changed_rules(cursor, draft['draft_id'], draft['rules_to_close'])


def _insert_draft_specs(cursor, drafts):
    sql = dbhelpers.load_sql('create_spec_draft.sql')
    fields = ['internal_draft_id', 'spec', 'creator']
    for draft in drafts:
        values = [draft.get(f) for f in fields]
        cursor.execute(sql, values)
        _insert_subdrafts(
            cursor, draft['internal_draft_id'], draft['subdrafts'],
        )
        _mark_subdrafts_completed(
            cursor, draft['internal_draft_id'], draft['subdrafts'],
        )
        _insert_schedule_specs(
            cursor, draft['internal_draft_id'], draft['schedule_spec'],
        )
        _insert_drafts(cursor, draft['internal_draft_id'], draft['rules'])
        _insert_rules_to_close(
            cursor,
            draft['internal_draft_id'],
            draft['close_clashing_at'],
            draft['rules_to_close'],
        )


def _insert_subdrafts(cursor, internal_draft_id, subdrafts):
    if not subdrafts:
        return
    sql = dbhelpers.load_sql('subdrafts_insert.sql')
    fields = ['spec_ref', 'spec', 'error', 'is_completed']
    values = [[s.get(f) for s in subdrafts] for f in fields]
    cursor.execute(sql, [internal_draft_id] + values)


def _mark_subdrafts_completed(cursor, internal_draft_id, subdrafts):
    if not subdrafts:
        return
    sql = dbhelpers.load_sql('subdrafts_set_completed.sql')
    values = [s['spec_ref'] for s in subdrafts if s['is_completed']]
    if values:
        cursor.execute(sql, (internal_draft_id, values))


def _insert_schedule_specs(cursor, internal_draft_id, specs):
    if not specs:
        return
    sql = dbhelpers.load_sql('draft_insert_schedule_specs.sql')
    fields = ['schedule_ref', 'during', 'value']
    values = [[s.get(f) for s in specs] for f in fields]
    cursor.execute(sql, [internal_draft_id] + values)


@pytest.fixture(name='a_single_ride')
def _single_ride_builder():
    # pylint: disable=invalid-name,redefined-builtin
    def _builder(
            id=None,
            tariff_zone='moscow',
            tariff_class='econom',
            start='2020-05-01T21:00:00+00:00',
            end='2020-05-30T21:00:00+00:00',
            schedule=None,
            rates=None,
            tag=None,
            geoarea=None,
            branding=None,
            points=None,
            updated_at=None,
            schedule_ref=None,
            stop_tag=None,
    ):
        rates = rates or [
            {'bonus_amount': '100', 'start': '12:00', 'week_day': 'mon'},
            {'bonus_amount': '0', 'start': '15:00', 'week_day': 'mon'},
        ]
        return {
            'activity_points': points,
            'branding': branding,
            'end': end,
            'geoarea': geoarea,
            'id': id or str(uuid.uuid4()),
            'rates': json.dumps(rates),
            'rule_type': 'single_ride',
            'schedule': schedule,
            'schedule_ref': schedule_ref or 'schedule_ref',
            'start': start,
            'tag': tag,
            'tariff_class': tariff_class,
            'timezone': '',
            'updated_at': updated_at,
            'tariff_zone': tariff_zone,
            'stop_tag': stop_tag,
        }

    return _builder


@pytest.fixture(name='a_single_ontop')
def _single_ontop_builder():
    # pylint: disable=invalid-name,redefined-builtin
    def _builder(
            id=None,
            tariff_zone='moscow',
            tariff_class='econom',
            start='2020-05-01T21:00:00+00:00',
            end='2020-05-30T21:00:00+00:00',
            schedule=None,
            rates=None,
            tag=None,
            geoarea=None,
            branding=None,
            points=None,
            updated_at=None,
            schedule_ref=None,
            stop_tag=None,
    ):
        rates = rates or [
            {'bonus_amount': '100', 'start': '12:00', 'week_day': 'mon'},
            {'bonus_amount': '0', 'start': '15:00', 'week_day': 'mon'},
        ]
        return {
            'activity_points': points,
            'branding': branding,
            'end': end,
            'geoarea': geoarea,
            'id': id or str(uuid.uuid4()),
            'rates': json.dumps(rates),
            'rule_type': 'single_ontop',
            'schedule': schedule,
            'schedule_ref': schedule_ref or 'schedule_ref',
            'start': start,
            'tag': tag,
            'tariff_class': tariff_class,
            'timezone': '',
            'updated_at': updated_at,
            'tariff_zone': tariff_zone,
            'stop_tag': stop_tag,
        }

    return _builder


@pytest.fixture(name='a_goal')
def _goal_builder():
    # pylint: disable=invalid-name,redefined-builtin
    def _builder(
            id=None,
            geonode='br_russia/br_moscow',
            tariff_class='econom',
            start='2020-05-01T21:00:00+00:00',
            end='2020-05-29T21:00:00+00:00',
            counters=None,
            schedule=None,
            tag=None,
            geoarea=None,
            branding=None,
            points=None,
            currency='RUB',
            window_size=7,
            unique_driver_id=None,
            updated_at=None,
            schedule_ref=None,
            stop_tag=None,
    ):
        counters = counters or {
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
        }
        return {
            'activity_points': points,
            'branding': branding,
            'currency': currency,
            'end': end,
            'geoarea': geoarea,
            'id': id or str(uuid.uuid4()),
            'rates': json.dumps(counters),
            'rule_type': 'goal',
            'schedule': schedule,
            'schedule_ref': schedule_ref or 'schedule_ref',
            'start': start,
            'tag': tag,
            'tariff_class': tariff_class,
            'tariff_zone': geonode,
            'timezone': '',
            'unique_driver_id': unique_driver_id,
            'updated_at': updated_at,
            'window_size': window_size,
            'stop_tag': stop_tag,
        }

    return _builder


@pytest.fixture(name='create_rules')
def _make_rules_inserter(pgsql, a_draft):
    def _create_rules(
            *rules, draft_id=None, budget_id='fake_budget_id', changed=None,
    ):
        internal_draft_id = str(uuid.uuid4())
        draft_id = draft_id or str(uuid.uuid4())
        cursor = pgsql['billing_subventions'].cursor()
        _insert_draft_specs(
            cursor, [a_draft(internal_draft_id=internal_draft_id)],
        )
        _insert_drafts(cursor, internal_draft_id, rules)
        _approve_drafts(cursor, internal_draft_id, draft_id, budget_id)
        _set_schedule(cursor, rules)
        _set_updated_at(cursor, rules)
        _log_changed_rules(cursor, draft_id, changed)

    return _create_rules


@pytest.fixture(name='approve_rules')
def _make_approver(pgsql):
    def _approve_rules(
            internal_draft_id,
            *rules,
            draft_id='draft_id',
            budget_id='budget_id',
    ):
        cursor = pgsql['billing_subventions'].cursor()
        _approve_drafts(
            cursor,
            internal_draft_id,
            draft_id,
            budget_id,
            [rule['schedule_ref'] for rule in rules],
        )

    return _approve_rules


def _insert_drafts(cursor, internal_draft_id, rules):
    sql = dbhelpers.load_sql('create_rules_to_add_draft.sql')
    fields = [
        'id',
        'rule_type',
        'tariff_zone',
        'tariff_class',
        'timezone',
        'start',
        'end',
        'geoarea',
        'tag',
        'branding',
        'activity_points',
        'rates',
        'currency',
        'window_size',
        'unique_driver_id',
        'schedule_ref',
        'stop_tag',
    ]
    values = [[r.get(f) for r in rules] for f in fields]
    cursor.execute(sql, [internal_draft_id] + values)


def _approve_drafts(
        cursor, internal_draft_id, draft_id, budget_id, with_schedules=None,
):
    sql = dbhelpers.load_sql('insert_rules.sql')
    cursor.execute(
        sql,
        [
            budget_id,
            draft_id,
            internal_draft_id,
            with_schedules,
            with_schedules,
            draft_id,
        ],
    )


def _set_updated_at(cursor, rules):
    sql = 'UPDATE subventions.rule SET updated_at = %s WHERE rule_id = %s'
    updated_at = [
        (r['id'], r['updated_at'])
        for r in rules
        if r['updated_at'] is not None
    ]
    for rule_id, value in updated_at:
        cursor.execute(sql, [value, rule_id])


def _set_schedule(cursor, rules):
    sql = """
        INSERT INTO subventions.schedule (rule_id, during, amount)
        VALUES(%s, %s, %s)
    """
    all_schedules = [
        (r['id'], r['schedule']) for r in rules if r['schedule'] is not None
    ]
    for rule_id, schedules in all_schedules:
        for since, till, value in schedules:
            cursor.execute(
                sql,
                [
                    rule_id,
                    psycopg2.extras.NumericRange(since, till, '[)'),
                    value,
                ],
            )


def _log_changed_rules(cursor, draft_id, rule_ids):
    if not rule_ids:
        return
    sql = """
        INSERT INTO subventions.rule_change_log
            (rule_id, initiator, draft_id, description)
        SELECT UNNEST(%s::UUID[]), '', %s, 'Close rule';
    """
    cursor.execute(sql, (rule_ids, draft_id))


def _insert_rules_to_close(cursor, internal_draft_id, ends_at, rule_ids):
    if not rule_ids:
        return
    sql = dbhelpers.load_sql('create_rules_to_close_draft.sql')
    cursor.execute(sql, (internal_draft_id, rule_ids, ends_at))


@pytest.fixture(name='mark_clashing_as_known')
def _mark_clashing_rule_as_known(pgsql):
    def _marker(internal_draft, ends_at, *rule_ids):
        cursor = pgsql['billing_subventions'].cursor()
        _insert_rules_to_close(
            cursor, internal_draft, ends_at, [rule_id for rule_id in rule_ids],
        )

    return _marker


@pytest.fixture(name='mark_as_applying')
def _mark_draft_as_applying(pgsql, load_sql):
    def _run(
            internal_draft_id,
            draft_id='fake_draft_id',
            budget_id='fake_budget_id',
    ):
        sql = load_sql('draft_update_spec.sql')
        cursor = pgsql['billing_subventions'].cursor()
        cursor.execute(
            sql, (draft_id, 'TICKET-1', 'me', budget_id, internal_draft_id),
        )

    return _run


@pytest.fixture(name='load_sql')
def _load_sql_fixture():
    def _wrapper(fname):
        return dbhelpers.load_sql(fname)

    return _wrapper


@pytest.fixture(name='add_rules')
def _make_add_rules(create_rules, a_single_ride, a_goal, a_single_ontop):
    def _add_rules(rule_type, dbdata):
        builder = {
            'single_ride': a_single_ride,
            'single_ontop': a_single_ontop,
            'goal': a_goal,
        }[rule_type]
        for draft in dbdata:
            create_rules(
                *[builder(**attrs) for attrs in draft['rules']],
                draft_id=draft.get('draft_id'),
            )

    return _add_rules
