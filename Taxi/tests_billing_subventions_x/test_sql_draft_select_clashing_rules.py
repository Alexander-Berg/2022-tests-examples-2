import pytest

INTERNAL_DRAFT_ID = '4c160831-2c63-4b0d-9193-5331128be0f1'
RULE_ID = '610360e1-0859-4f39-94d4-4d33ffb80002'


@pytest.mark.parametrize(
    'rule_attrs,draft_attrs,expected',
    (
        # identical
        ({}, {}, [RULE_ID]),
        # intersect by period
        (
            {
                'start': '2021-05-01T21:00:00+00:00',
                'end': '2021-05-31T21:00:00+00:00',
            },
            {
                'start': '2021-05-21T21:00:00+00:00',
                'end': '2021-06-09T21:00:00+00:00',
            },
            [RULE_ID],
        ),
        # do not intersect by period
        (
            {
                'start': '2021-05-01T21:00:00+00:00',
                'end': '2021-05-31T21:00:00+00:00',
            },
            {
                'start': '2021-05-31T21:00:00+00:00',
                'end': '2021-06-30T21:00:00+00:00',
            },
            [],
        ),
        # differ by tariff_zone
        ({'tariff_zone': 'g'}, {'tariff_zone': 'gg'}, []),
        # differ by tariff_class
        ({'tariff_class': 'e'}, {'tariff_class': 'b'}, []),
        # differ by geoarea
        ({'geoarea': 'a'}, {'geoarea': 'aa'}, []),
        ({'geoarea': None}, {'geoarea': 'a'}, []),
        ({'geoarea': 'a'}, {'geoarea': None}, []),
        # differ by branding
        ({'branding': 'a'}, {'branding': 'aa'}, []),
        ({'branding': None}, {'branding': 'a'}, []),
        ({'branding': 'a'}, {'branding': None}, []),
        # differ by tag
        ({'tag': 'a'}, {'tag': 'aa'}, []),
        ({'tag': None}, {'tag': 'a'}, []),
        ({'tag': 'a'}, {'tag': None}, []),
        # differ by activity points
        ({'points': 50}, {'points': 75}, [RULE_ID]),
        ({'points': None}, {'points': 50}, [RULE_ID]),
        ({'points': 50}, {'points': None}, [RULE_ID]),
    ),
)
def test_sql_select_clashing_rules(
        run_query,
        create_drafts,
        create_rules,
        a_single_ride,
        a_draft,
        rule_attrs,
        draft_attrs,
        expected,
):
    rule = a_single_ride(id=RULE_ID, **rule_attrs)
    draft = a_single_ride(**draft_attrs)
    create_drafts(a_draft(internal_draft_id=INTERNAL_DRAFT_ID, rules=[draft]))
    create_rules(rule)
    assert run_query(draft['start']) == expected


def test_sql_select_clashing_rules_with_known_clashing(
        run_query,
        create_drafts,
        create_rules,
        a_single_ride,
        a_draft,
        mark_clashing_as_known,
):
    rule = a_single_ride(
        id=RULE_ID,
        start='2021-05-01T00:00:00+03:00',
        end='2021-05-31T00:00:00+03:00',
    )
    create_rules(rule)
    draft = a_single_ride(
        start='2021-05-21T00:00:00+03:00', end='2021-08-31T00:00:00+03:00',
    )
    create_drafts(a_draft(internal_draft_id=INTERNAL_DRAFT_ID, rules=[draft]))
    mark_clashing_as_known(
        INTERNAL_DRAFT_ID, '2021-05-21T00:00:00+03:00', RULE_ID,
    )
    assert run_query(draft['start']) == []


@pytest.fixture(name='run_query')
def _make_query_runner(pgsql, load_sql):
    def _run_query(start):
        sql = load_sql('draft_select_clashing_rules.sql')
        cursor = pgsql['billing_subventions'].cursor()
        cursor.execute(sql, (INTERNAL_DRAFT_ID, start, INTERNAL_DRAFT_ID))
        return [row[0] for row in cursor.fetchall()]

    return _run_query
