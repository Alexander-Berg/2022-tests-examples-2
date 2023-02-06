import pytest

from testsuite.utils import ordered_object

UDID = '511476f9-e08a-4826-b925-162578f12ab1'


@pytest.mark.parametrize(
    'first,last,expected',
    (('1', '1', ['schedule_ref_000001']), ('1', '2', ['schedule_ref_000001'])),
)
def test_sql_subdrafts_get_schedule_refs_returns_list_of_schedule_refs(
        draft, select_schedule_refs, first, last, expected,
):
    schedule_refs = select_schedule_refs(
        draft['internal_draft_id'], first, last,
    )
    ordered_object.assert_eq(schedule_refs, expected, '')


@pytest.fixture(name='draft')
def _make_draft(create_drafts, a_draft, a_subdraft, a_goal, load_json):
    subdrafts = [
        a_subdraft(
            spec_ref='1',
            spec=load_json('bulk_personal_goals_spec1.json'),
            error=None,
            is_completed=True,
        ),
        a_subdraft(
            spec_ref='2',
            spec=load_json('bulk_personal_goals_spec2.json'),
            error='This spec is broken somehow',
            is_completed=True,
        ),
    ]
    rules = [
        a_goal(
            unique_driver_id=UDID,
            window_size=7,
            schedule_ref='schedule_ref_000001',
        ),
        a_goal(
            unique_driver_id=UDID,
            window_size=3,
            schedule_ref='schedule_ref_000002',
        ),
    ]
    draft = a_draft(subdrafts=subdrafts, rules=rules)
    create_drafts(draft)
    return draft


@pytest.fixture(name='select_schedule_refs')
def _make_query_runner(pgsql, load_sql):
    def _run(internal_draft_id, first, last):
        sql = load_sql('subdrafts_get_schedule_refs.sql')
        cursor = pgsql['billing_subventions'].cursor()
        cursor.execute(sql, (internal_draft_id, first, last))
        return [row[0] for row in cursor.fetchall()]

    return _run
