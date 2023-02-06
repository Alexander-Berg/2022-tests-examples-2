import datetime

import pytest

from tests_billing_subventions_x import dbhelpers as db

START = '2021-06-19T12:00:00+03:00'
KEEP_DAYS = 1
NOW_DELETE = '2021-06-20T12:00:01+03:00'
NOW_KEEP = '2021-06-20T12:00:00+03:00'

_SPECS = (
    {'rule': {'start': START}},  # usual draft
    {'start': START},  # bulk draft
    {'close_at': START},  # close draft
)


@pytest.mark.parametrize('spec', _SPECS)
def test_sql_draft_delete_stale_removes_drafts(
        make_draft, delete_stale, assert_draft_removed, spec,
):
    draft = make_draft(spec=spec)
    delete_stale(now=NOW_DELETE)
    assert_draft_removed(draft)


@pytest.mark.parametrize('spec', _SPECS)
def test_sql_draft_delete_stale_keeps_approved(
        make_draft, delete_stale, assert_draft_kept, spec,
):
    draft = make_draft(spec=spec, approved_at='2021-06-18T13:00:00+00:00')
    delete_stale(now=NOW_DELETE)
    assert_draft_kept(draft)


@pytest.mark.parametrize('spec', _SPECS)
def test_sql_draft_delete_stale_keeps_stale_for_set_period(
        make_draft, delete_stale, assert_draft_kept, spec,
):
    draft = make_draft(spec=spec)
    delete_stale(now=NOW_KEEP)
    assert_draft_kept(draft)


@pytest.fixture(name='make_draft')
def _draft_maker(create_drafts, a_draft, a_single_ride):
    def _maker(*, spec, approved_at=None):
        draft = a_draft(
            spec=spec,
            draft_id='fake_draft_id' if approved_at is not None else None,
            budget_id='fake_budget_id' if approved_at is not None else None,
            approved_at=approved_at,
            rules=[a_single_ride()],
        )
        create_drafts(draft)
        return draft

    return _maker


@pytest.fixture(name='delete_stale')
def _make_query_runner(pgsql, load_sql):
    def _run(*, now, keep_for_days=KEEP_DAYS, limit=10):
        sql = load_sql('draft_delete_stale.sql')
        cursor = pgsql['billing_subventions'].cursor()
        cursor.execute(
            sql, (datetime.datetime.fromisoformat(now), keep_for_days, limit),
        )

    return _run


@pytest.fixture(name='assert_draft_removed')
def _make_removed_asserter(pgsql):
    def _assert(draft):
        draft_id = draft['internal_draft_id']
        msg = 'Draft hasn\'t been removed'
        assert db.get_draft_spec(pgsql, draft_id) is None, msg

    return _assert


@pytest.fixture(name='assert_draft_kept')
def _make_kept_asserter(pgsql):
    def _assert(draft):
        draft_id = draft['internal_draft_id']
        msg = 'Draft has been removed'
        assert db.get_draft_spec(pgsql, draft_id) is not None, msg

    return _assert
