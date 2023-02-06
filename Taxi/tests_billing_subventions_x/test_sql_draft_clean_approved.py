import datetime
import time

import psycopg2
import pytest

from tests_billing_subventions_x import dbhelpers as db

NOW = '2021-06-20T19:00:00+03:00'
APPROVED_AT = '2021-06-01T19:00:00+03:00'


def test_sql_clean_approved_cleans_tables(
        make_draft, clean_approved, assert_draft_cleaned,
):
    draft = make_draft()
    clean_approved()
    assert_draft_cleaned(draft)


def test_sql_clean_appoved_does_not_touch_unapproved_drafts(
        make_draft, clean_approved, assert_draft_untouched,
):
    draft = make_draft(approved_at=None)
    clean_approved()
    assert_draft_untouched(draft)


def test_sql_clean_appoved_does_not_touch_recently_approved_drafts(
        make_draft, clean_approved, assert_draft_untouched,
):
    draft = make_draft(approved_at=NOW)
    clean_approved()
    assert_draft_untouched(draft)


def test_sql_clean_approved_starts_with_earlier_created_drafts(
        make_draft, clean_approved,
):
    older = make_draft()
    time.sleep(0.1)  # it's simplier than manually update 'created_at'
    newer = make_draft()
    cleaned = clean_approved()
    assert cleaned == [older['internal_draft_id'], newer['internal_draft_id']]


def test_sql_clean_approved_skips_cleaned_drafts(make_draft, clean_approved):
    to_skip = make_draft(rules=[], rules_to_close=[])
    only_add = make_draft(rules_to_close=[])
    only_close = make_draft(rules=[])
    cleaned = clean_approved()
    assert to_skip['internal_draft_id'] not in cleaned
    assert only_add['internal_draft_id'] in cleaned
    assert only_close['internal_draft_id'] in cleaned


def test_sql_clean_approved_clean_drafts_by_chunks(make_draft, clean_approved):
    for _ in range(3):
        make_draft()
    cleaned = clean_approved(limit=2)
    assert len(cleaned) == 2


@pytest.fixture(name='make_draft')
def _draft_maker(
        create_drafts, a_draft, a_subdraft, create_rules, a_single_ride,
):
    def _maker(*, approved_at=APPROVED_AT, rules=None, rules_to_close=None):
        clashing_rule = a_single_ride()
        create_rules(clashing_rule)
        draft = a_draft(
            draft_id='fake_draft_id',
            budget_id='fake_budget_id',
            approved_at=approved_at,
            subdrafts=[a_subdraft(spec_ref='1', spec={})],
            rules=rules if rules is not None else [a_single_ride()],
            rules_to_close=(
                rules_to_close
                if rules_to_close is not None
                else [clashing_rule['id']]
            ),
            schedule_spec=[
                {
                    'schedule_ref': 'schedule_ref',
                    'during': psycopg2.extras.NumericRange(720, 900, '[)'),
                    'value': '100',
                },
            ],
        )
        create_drafts(draft)
        return draft

    return _maker


@pytest.fixture(name='clean_approved')
def _make_query_runner(pgsql, load_sql):
    def _run(*, now=NOW, limit=10):
        sql = load_sql('draft_clean_approved.sql')
        cursor = pgsql['billing_subventions'].cursor()
        cursor.execute(sql, (datetime.datetime.fromisoformat(now), limit))
        return [row[0] for row in cursor.fetchall()]

    return _run


@pytest.fixture(name='assert_draft_cleaned')
def _make_cleaned_asserter(pgsql):
    def _assert(draft):
        internal_draft_id = draft['internal_draft_id']
        assert db.select_subdrafts(pgsql, internal_draft_id) == []
        assert db.select_rule_drafts(pgsql, internal_draft_id) == []
        assert db.select_rules_to_close(pgsql, internal_draft_id) == []
        assert db.select_draft_schedule_specs(pgsql, internal_draft_id) == []

    return _assert


@pytest.fixture(name='assert_draft_untouched')
def _make_untouched_asserter(pgsql):
    def _assert(draft):
        internal_draft_id = draft['internal_draft_id']
        assert db.select_subdrafts(pgsql, internal_draft_id) != []
        assert db.select_rule_drafts(pgsql, internal_draft_id) != []
        assert db.select_rules_to_close(pgsql, internal_draft_id) != []
        assert db.select_draft_schedule_specs(pgsql, internal_draft_id) != []

    return _assert
