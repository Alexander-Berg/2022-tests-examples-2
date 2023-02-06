import pytest


def test_sql_subdrafts_select_returns_subdrafts_for_interval(
        draft, select_subdrafts,
):
    subdrafts = select_subdrafts(draft['internal_draft_id'], '1', '3')
    assert [s['spec_ref'] for s in subdrafts] == ['1', '2', '3']


def test_sql_subdrafts_select_returns_needed_attributes(
        draft, select_subdrafts,
):
    subdrafts = select_subdrafts(draft['internal_draft_id'], '1', '2')
    assert subdrafts == [
        {'spec_ref': '1', 'spec': {'start': 'some_value'}, 'error': None},
        {'spec_ref': '2', 'spec': {}, 'error': 'Error'},
    ]


def test_sql_subdrafts_select_returns_only_incompleted_subdrafts(
        draft, select_subdrafts,
):
    subdrafts = select_subdrafts(draft['internal_draft_id'], '3', '6')
    assert [s['spec_ref'] for s in subdrafts] == ['3', '4', '6']


@pytest.fixture(name='draft')
def _make_draft(create_drafts, a_draft, a_subdraft):
    subdrafts = [
        a_subdraft(
            spec_ref=str(i),
            spec={'start': 'some_value'} if i == 1 else {},
            error='Error' if i == 2 else None,
            is_completed=(i == 5),
        )
        for i in range(1, 10)
    ]
    draft = a_draft(subdrafts=subdrafts)
    create_drafts(draft)
    return draft


@pytest.fixture(name='select_subdrafts')
def _make_query_runner(pgsql, load_sql):
    def _run(internal_draft_id, first, last):
        sql = load_sql('subdrafts_select_by_refs.sql')
        cursor = pgsql['billing_subventions'].cursor()
        cursor.execute(sql, (internal_draft_id, first, last))
        fields = [column.name for column in cursor.description]
        return [dict(zip(fields, row)) for row in cursor.fetchall()]

    return _run
