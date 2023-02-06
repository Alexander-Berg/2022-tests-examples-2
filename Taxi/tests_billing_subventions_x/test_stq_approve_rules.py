import datetime as dt

import psycopg2
import pytest


from tests_billing_subventions_x import dbhelpers
from tests_billing_subventions_x import types

INTERNAL_DRAFT_ID = 'e12d920f0a0839f3743b38ffe28747cd'
SUBDRAFTS = {'from': '1', 'to': '1'}
RULE_ID = 'c64b2937-e5c3-4b61-a1e4-3aef0c76d134'

MOCK_NOW = '2022-07-05T18:12:34.567890+03:00'


@pytest.mark.now(MOCK_NOW)
async def test_stq_approve_rules_rescheduled_when_draft_not_ready(
        stq_runner, stq, with_draft,
):
    with_draft(draft_id=None)
    await _run(stq_runner)
    queue = stq.billing_subventions_x_approve_rules
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == 'id'
    eta = dt.datetime.fromisoformat(MOCK_NOW) + dt.timedelta(seconds=10)
    assert task['eta'] == eta.astimezone(dt.timezone.utc).replace(tzinfo=None)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    BILLING_SUBVENTIONS_BULK_DRAFTS_CONTROL={'approve_max_reschedules': 2},
)
async def test_stq_approve_rules_stops_when_rescheduling_limit_reached(
        stq_runner, stq, with_draft,
):
    with_draft(draft_id=None)
    await _run(stq_runner, reschedule_counter=2)
    assert stq.billing_subventions_x_approve_rules.times_called == 0


@pytest.mark.now(MOCK_NOW)
async def test_stq_approve_rules_splits_draft_to_chunks(
        stq_runner, stq, with_draft,
):
    with_draft()
    await _run(stq_runner)
    queue = stq.billing_subventions_x_approve_rules
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == f'{INTERNAL_DRAFT_ID}:1-1'
    assert task['kwargs']['internal_draft_id'] == INTERNAL_DRAFT_ID
    assert task['kwargs']['subdrafts'] == SUBDRAFTS
    eta = dt.datetime.fromisoformat(MOCK_NOW) + dt.timedelta(seconds=30)
    assert task['eta'] == eta.astimezone(dt.timezone.utc).replace(tzinfo=None)


async def test_stq_approve_rules_creates_consistent_rules(
        stq_runner, pgsql, with_draft, mark_as_applying,
):
    draft = with_draft()
    mark_as_applying(draft['internal_draft_id'], 'draft_id', 'budget_id')
    await _run(stq_runner, subdrafts=SUBDRAFTS)
    rule = dbhelpers.get_rule_by_id(pgsql, RULE_ID)
    rule.pop('updated_at')
    assert rule == {
        'branding': 'sticker',
        'budget_id': 'budget_id',
        'counters_mapping': [{'global': 'draft_id:A', 'local': 'A'}],
        'currency': 'RUB',
        'draft_id': 'draft_id',
        'ends_at': dt.datetime.fromisoformat('2021-06-01T00:00:00+03:00'),
        'geoarea': 'pol-1',
        'min_activity_points': 75,
        'rates': {
            'schedule': [
                {'counter': 'A', 'start': '00:00', 'week_day': 'mon'},
            ],
            'steps': [{'id': 'A', 'steps': [{'amount': '100', 'nrides': 10}]}],
        },
        'id': RULE_ID,
        'type': 'goal',
        'schedule_ref': 'schedule_ref_000001',
        'starts_at': dt.datetime.fromisoformat('2021-05-01T00:00:00+03:00'),
        'tag': 'a_tag',
        'stop_tag': None,
        'tariff': 'comfort',
        'zone': 'g1',
        'unique_driver_id': '511476f9-e08a-4826-b925-162578f12ab1',
        'window_size': 7,
    }
    _assert_schedule_for_rule(pgsql, RULE_ID)


async def test_stq_approve_rules_run_twice(
        stq_runner, pgsql, with_draft, mark_as_applying,
):
    draft = with_draft()
    mark_as_applying(draft['internal_draft_id'], 'draft_id', 'budget_id')
    await _run(stq_runner, subdrafts=SUBDRAFTS)
    await _run(stq_runner, subdrafts=SUBDRAFTS)
    _assert_schedule_for_rule(pgsql, RULE_ID)


def _assert_schedule_for_rule(pgsql, rule_id):
    schedule = dbhelpers.get_schedule_by_id(pgsql, rule_id)
    assert schedule == [
        types.ScheduleRange(
            during=psycopg2.extras.NumericRange(0, 10080, '[)'), value='A',
        ),
    ]


async def _run(stq_runner, **kwargs):
    kwargs.setdefault('internal_draft_id', INTERNAL_DRAFT_ID)
    await stq_runner.billing_subventions_x_approve_rules.call(
        task_id='id',
        reschedule_counter=kwargs.pop('reschedule_counter', 0),
        kwargs=kwargs,
    )


@pytest.fixture(name='with_draft')
def _make_draft(create_drafts, a_draft, a_subdraft, a_goal, load_json):
    def _builder(*, draft_id='draft_id'):
        spec = load_json('bulk_personal_goals_spec1.json')
        draft = a_draft(
            internal_draft_id=INTERNAL_DRAFT_ID,
            draft_id=draft_id,
            spec={},
            subdrafts=[a_subdraft(spec_ref='1', spec=spec, is_completed=True)],
            rules=[
                a_goal(
                    id=RULE_ID,
                    geonode=spec['zones'][0],
                    tariff_class=spec['tariff_classes'][0],
                    start=spec['rule']['start'],
                    end=spec['rule']['end'],
                    counters=spec['rule']['counters'],
                    tag=spec['rule']['tag'],
                    geoarea=spec['geoareas'][0],
                    branding=spec['rule']['branding_type'],
                    points=spec['rule']['activity_points'],
                    currency=spec['rule']['currency'],
                    window_size=spec['rule']['window'],
                    unique_driver_id=spec['rule']['unique_driver_id'],
                    schedule_ref='schedule_ref_000001',
                ),
            ],
            schedule_spec=[
                {
                    'schedule_ref': 'schedule_ref_000001',
                    'during': psycopg2.extras.NumericRange(0, 10080, '[)'),
                    'value': 'A',
                },
            ],
        )
        create_drafts(draft)
        return draft

    return _builder
