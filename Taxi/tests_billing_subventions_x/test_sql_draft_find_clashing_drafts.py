import pytest

INTERNAL_DRAFT_ID = '1e610b8e-f612-4cd7-b56e-9b7fc48d73b1'
DRAFT_ID = '11111'


@pytest.mark.parametrize(
    'rule_attrs,draft_attrs,expected',
    (
        # identical
        ({}, {}, [DRAFT_ID]),
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
            [DRAFT_ID],
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
        # differ by geonode
        ({'geonode': 'g'}, {'geonode': 'gg'}, []),
        # differ by tariff_class
        ({'tariff_class': 'e'}, {'tariff_class': 'b'}, []),
        # differ by geoarea
        ({'geoarea': None}, {'geoarea': 'a'}, []),
        ({'geoarea': 'a'}, {'geoarea': None}, []),
        ({'geoarea': 'a'}, {'geoarea': 'aa'}, []),
        # differ by branding
        ({'branding': None}, {'branding': 'a'}, []),
        ({'branding': 'a'}, {'branding': None}, []),
        ({'branding': 'a'}, {'branding': 'aa'}, []),
        # differ by tag
        ({'tag': None}, {'tag': 'a'}, []),
        ({'tag': 'a'}, {'tag': None}, []),
        ({'tag': 'a'}, {'tag': 'aa'}, []),
        # differ by activity points
        ({'points': None}, {'points': 50}, [DRAFT_ID]),
        ({'points': 50}, {'points': None}, [DRAFT_ID]),
        ({'points': 50}, {'points': 75}, [DRAFT_ID]),
        # differ by window size
        ({'window_size': 7}, {'window_size': 5}, []),
        # differ by unique_driver_id
        ({'unique_driver_id': None}, {'unique_driver_id': 'b'}, []),
        ({'unique_driver_id': 'a'}, {'unique_driver_id': None}, []),
        ({'unique_driver_id': 'a'}, {'unique_driver_id': 'b'}, []),
    ),
)
def test_sql_select_clashing_drafts(
        pgsql,
        load_sql,
        create_drafts,
        create_rules,
        a_goal,
        a_draft,
        rule_attrs,
        draft_attrs,
        expected,
):
    rule_attrs.setdefault('unique_driver_id', 'x')
    draft_attrs.setdefault('unique_driver_id', 'x')
    rule = a_goal(**rule_attrs)
    draft = a_goal(**draft_attrs)
    create_drafts(a_draft(internal_draft_id=INTERNAL_DRAFT_ID, rules=[draft]))
    create_rules(rule, draft_id=DRAFT_ID)
    assert _run_query(pgsql, load_sql) == expected


def _run_query(pgsql, load_sql):
    sql = load_sql('draft_select_clashing_drafts_for_goals.sql')
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(
        sql,
        (INTERNAL_DRAFT_ID, '2020-01-01T00:00:00+03:00', INTERNAL_DRAFT_ID),
    )
    return [row[0] for row in cursor.fetchall()]
