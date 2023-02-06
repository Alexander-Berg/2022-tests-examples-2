import datetime as dt

import psycopg2
import pytest

from testsuite.utils import ordered_object

from tests_billing_subventions_x import dbhelpers

INTERNAL_DRAFT_ID = 'e12d920f0a0839f3743b38ffe28747cd'
SUBDRAFTS = {'from': '1', 'to': '4'}
UDID_1 = '511476f9-e08a-4826-b925-162578f12ab1'
UDID_2 = '029caf03-eb19-46fe-bae9-8f8ec13ec3b1'

MOCK_NOW = '2022-07-05T18:12:34.567890+03:00'


@pytest.mark.now(MOCK_NOW)
async def test_stq_generate_rule_drafts_splits_draft_to_chunks(
        stq_runner, stq,
):
    await _run(stq_runner, internal_draft_id=INTERNAL_DRAFT_ID)
    queue = stq.billing_subventions_x_generate_rule_drafts
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == f'{INTERNAL_DRAFT_ID}:1-4'
    assert task['kwargs']['internal_draft_id'] == INTERNAL_DRAFT_ID
    assert task['kwargs']['subdrafts'] == SUBDRAFTS
    eta = dt.datetime.fromisoformat(MOCK_NOW) + dt.timedelta(seconds=30)
    assert task['eta'] == eta.astimezone(dt.timezone.utc).replace(tzinfo=None)


async def test_stq_generate_rule_drafts_creates_drafts_with_expected_keys(
        stq_runner, pgsql,
):
    await _run(
        stq_runner, internal_draft_id=INTERNAL_DRAFT_ID, subdrafts=SUBDRAFTS,
    )
    rules = dbhelpers.select_rule_drafts(pgsql, INTERNAL_DRAFT_ID)
    assert len(rules) == 4
    expected = [
        # spec1
        ('comfort', 'g1', 'pol-1', 'a_tag', 'sticker', 75, 7, UDID_1),
        ('comfort', 'g2/g21', 'pol-1', 'a_tag', 'sticker', 75, 7, UDID_1),
        # spec2
        ('econom', 'g1', 'pol-1', 'a_tag', None, None, 7, UDID_2),
        ('econom', 'g1', 'pol-2', 'a_tag', None, None, 7, UDID_2),
    ]
    ordered_object.assert_eq(_extract_key_attrs_from(rules), expected, '')


async def test_stq_generate_rule_creates_drafts_with_schedule_refs(
        stq_runner, pgsql,
):
    await _run(
        stq_runner, internal_draft_id=INTERNAL_DRAFT_ID, subdrafts=SUBDRAFTS,
    )
    rules = dbhelpers.select_rule_drafts(pgsql, INTERNAL_DRAFT_ID)
    schedule_refs = set(r.schedule_ref for r in rules)
    assert schedule_refs == set(['schedule_ref_000001', 'schedule_ref_000002'])
    schedule_specs = dbhelpers.select_draft_schedule_specs(
        pgsql, INTERNAL_DRAFT_ID,
    )
    for spec in schedule_specs:
        assert spec['schedule_ref'] in schedule_refs
        assert (spec['during'], spec['value']) in (
            (psycopg2.extras.NumericRange(0, 10080, '[)'), 'A'),  # spec1
            (psycopg2.extras.NumericRange(6841, 7199, '[)'), 'B'),  # spec2
        )


def _extract_key_attrs_from(drafts):
    return [
        (
            d.tariff,
            d.tariff_zone,
            d.geoarea,
            d.tag,
            d.branding,
            d.min_activity_points,
            d.window_size,
            d.unique_driver_id,
        )
        for d in drafts
    ]


async def _run(stq_runner, **kwargs):
    await stq_runner.billing_subventions_x_generate_rule_drafts.call(
        task_id='id', kwargs=kwargs,
    )


@pytest.fixture(autouse=True)
def _fill_db(create_drafts, a_draft, a_subdraft, load_json):
    create_drafts(
        a_draft(
            internal_draft_id=INTERNAL_DRAFT_ID,
            spec={},
            subdrafts=[
                a_subdraft(
                    spec_ref='1',
                    spec=load_json('bulk_personal_goals_spec1.json'),
                ),
                a_subdraft(
                    spec_ref='2',
                    spec=load_json('bulk_personal_goals_spec2.json'),
                ),
                a_subdraft(
                    spec_ref='3',
                    spec=load_json('bulk_personal_goals_spec1.json'),
                    is_completed=True,
                ),
                a_subdraft(
                    spec_ref='4',
                    spec=load_json('bulk_personal_goals_spec1.json'),
                    is_completed=True,
                ),
            ],
        ),
    )
