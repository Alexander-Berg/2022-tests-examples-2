import pytest

INTERNAL_DRAFT_ID = '4c160831-2c63-4b0d-9193-5331128be0f1'


@pytest.mark.parametrize(
    'drafts,expected',
    (
        # identical
        ([{}, {}], True),
        # not all identical
        ([{}, {}, {'tag': 't'}, {'branding': 'b'}], True),
        # differ by tariff_zone
        ([{'tariff_zone': 'g'}, {'tariff_zone': 'gg'}], False),
        # differ by tariff_class
        ([{'tariff_class': 'e'}, {'tariff_class': 'b'}], False),
        # differ by geoarea
        ([{'geoarea': 'a'}, {'geoarea': 'aa'}], False),
        ([{'geoarea': None}, {'geoarea': 'a'}], False),
        ([{'geoarea': 'a'}, {'geoarea': None}], False),
        # differ by branding
        ([{'branding': 'a'}, {'branding': 'aa'}], False),
        ([{'branding': None}, {'branding': 'a'}], False),
        ([{'branding': 'a'}, {'branding': None}], False),
        # differ by tag
        ([{'tag': 'a'}, {'tag': 'aa'}], False),
        ([{'tag': None}, {'tag': 'a'}], False),
        ([{'tag': 'a'}, {'tag': None}], False),
        # differ by activity points
        ([{'points': 50}, {'points': 75}], True),
        ([{'points': None}, {'points': 50}], True),
        ([{'points': 50}, {'points': None}], True),
    ),
)
def test_sql_draft_has_clashing_rules_for_single_ride(
        pgsql,
        load_sql,
        create_drafts,
        create_rules,
        a_single_ride,
        a_draft,
        drafts,
        expected,
):
    create_drafts(
        a_draft(
            internal_draft_id=INTERNAL_DRAFT_ID,
            rules=[a_single_ride(**attrs) for attrs in drafts],
        ),
    )
    assert _run_query(pgsql, load_sql) is expected


@pytest.mark.parametrize(
    'drafts,expected',
    (
        # identical
        ([{}, {}], True),
        # not all identical
        ([{}, {}, {'tag': 't'}, {'branding': 'b'}], True),
        # differ by geonode
        ([{'geonode': 'g'}, {'geonode': 'gg'}], False),
        # differ by tariff_class
        ([{'tariff_class': 'e'}, {'tariff_class': 'b'}], False),
        # differ by geoarea
        ([{'geoarea': 'a'}, {'geoarea': 'aa'}], False),
        ([{'geoarea': None}, {'geoarea': 'a'}], False),
        ([{'geoarea': 'a'}, {'geoarea': None}], False),
        # differ by branding
        ([{'branding': 'a'}, {'branding': 'aa'}], False),
        ([{'branding': None}, {'branding': 'a'}], False),
        ([{'branding': 'a'}, {'branding': None}], False),
        # differ by tag
        ([{'tag': 'a'}, {'tag': 'aa'}], False),
        ([{'tag': None}, {'tag': 'a'}], False),
        ([{'tag': 'a'}, {'tag': None}], False),
        # differ by activity points
        ([{'points': 50}, {'points': 75}], True),
        ([{'points': None}, {'points': 50}], True),
        ([{'points': 50}, {'points': None}], True),
        # differ by window_size
        ([{'window_size': 3}, {'window_size': 7}], False),
        # differ by unique_driver_id
        ([{'unique_driver_id': None}, {'unique_driver_id': 'b'}], False),
        ([{'unique_driver_id': 'a'}, {'unique_driver_id': None}], False),
        ([{'unique_driver_id': 'a'}, {'unique_driver_id': 'b'}], False),
    ),
)
def test_sql_draft_has_clashing_rules_for_goals(
        pgsql,
        load_sql,
        create_drafts,
        create_rules,
        a_goal,
        a_draft,
        drafts,
        expected,
):
    create_drafts(
        a_draft(
            internal_draft_id=INTERNAL_DRAFT_ID,
            rules=[a_goal(**attrs) for attrs in drafts],
        ),
    )
    assert _run_query(pgsql, load_sql) is expected


def _run_query(pgsql, load_sql):
    sql = load_sql('draft_has_clashing_rules.sql')
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, (INTERNAL_DRAFT_ID,))
    return cursor.fetchone()[0]
