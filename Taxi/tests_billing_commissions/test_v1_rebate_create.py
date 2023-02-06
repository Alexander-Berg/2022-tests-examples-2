import decimal

from dateutil import parser
import pytest

_ENDLESS_DATE = parser.parse('2100-01-01T00:00:00+03:00')


@pytest.mark.parametrize(
    'query_json, status, expected_message, expected_draft_records, expected_rules_to_close',
    [
        (
            'request.json',
            200,
            None,
            {
                'fields': ['tariff_zone', 'starts_at', 'ends_at'],
                'data': [
                    (
                        'moscow',
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                    ),
                ],
            },
            [],
        ),
        (
            'request_no_ends.json',
            200,
            None,
            {
                'fields': ['tariff_zone', 'starts_at', 'ends_at'],
                'data': [
                    (
                        'moscow',
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        None,
                    ),
                ],
            },
            [],
        ),
        (
            'request_rule_to_old.json',
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid rule start-end bounds',
            },
            {},
            [],
        ),
        (
            'request_rule_in_future_exists.json',
            200,
            None,
            {
                'fields': ['tariff_zone', 'starts_at', 'ends_at'],
                'data': [
                    (
                        'spb',
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                    ),
                ],
            },
            [],
        ),
        (
            'request_many_zones.json',
            200,
            {},
            {
                'fields': ['tariff_zone'],
                'data': [
                    ('moscowwwwwwwwww',),
                    ('moscowwwwwwwwww10',),
                    ('moscowwwwwwwwww11',),
                    ('moscowwwwwwwwww12',),
                    ('moscowwwwwwwwww13',),
                    ('moscowwwwwwwwww14',),
                    ('moscowwwwwwwwww15',),
                    ('moscowwwwwwwwww16',),
                    ('moscowwwwwwwwww17',),
                    ('moscowwwwwwwwww18',),
                    ('moscowwwwwwwwww19',),
                    ('moscowwwwwwwwww2',),
                    ('moscowwwwwwwwww20',),
                    ('moscowwwwwwwwww21',),
                    ('moscowwwwwwwwww22',),
                    ('moscowwwwwwwwww23',),
                    ('moscowwwwwwwwww24',),
                    ('moscowwwwwwwwww25',),
                    ('moscowwwwwwwwww26',),
                    ('moscowwwwwwwwww27',),
                    ('moscowwwwwwwwww28',),
                    ('moscowwwwwwwwww3',),
                    ('moscowwwwwwwwww4',),
                    ('moscowwwwwwwwww5',),
                    ('moscowwwwwwwwww6',),
                    ('moscowwwwwwwwww7',),
                    ('moscowwwwwwwwww8',),
                    ('moscowwwwwwwwww9',),
                ],
            },
            [],
        ),
    ],
)
@pytest.mark.now('2019-01-01T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rebate_create.sql'],
)
async def test_create_check(
        taxi_billing_commissions,
        load_json,
        query_json,
        status,
        expected_message,
        billing_commissions_postgres_db,
        expected_draft_records,
        expected_rules_to_close,
):
    query = load_json(query_json)
    response = await taxi_billing_commissions.post(
        'v1/rebate/create',
        json=query,
        headers={'X-YaTaxi-Draft-Author': 'testsuite'},
    )
    assert response.status_code == status
    if status != 200:
        assert expected_message == response.json()
    fields = expected_draft_records.get('fields', [])
    if 'ends_at' in fields:
        ends_at_position = fields.index('ends_at')
        fields[ends_at_position] = (
            'CASE WHEN ends_at > \'{}\'::TIMESTAMPTZ '
            'THEN NULL ELSE ends_at END as ends_at'
        ).format(_ENDLESS_DATE.isoformat())
    billing_commissions_postgres_db.execute(
        'SELECT {} FROM fees.draft_rebate_rule '
        'ORDER BY tariff_zone, tariff'.format(','.join(fields)),
    )
    rows = billing_commissions_postgres_db.fetchall()
    assert expected_draft_records.get('data', []) == rows
    billing_commissions_postgres_db.execute(
        'SELECT rule_id, ends_at FROM fees.draft_rebate_rule_to_close '
        'ORDER BY rule_id',
    )
    assert (
        expected_rules_to_close == billing_commissions_postgres_db.fetchall()
    )


@pytest.mark.now('2019-12-31T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rebate_create_approve.sql'],
)
@pytest.mark.parametrize(
    'query_json, status, expected_closed_rules, expected_rule_changes',
    [
        (
            'request_close_one_rule.json',
            200,
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
            [{'r.id': '2abf162a-b607-11ea-998e-07e60204cbcf'}],
        ),
        (
            'request_approve_two_rules.json',
            200,
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
            [
                # updated rules
                {'r.id': '2abf062a-b607-11ea-998e-07e60204cbcf'},
                # new rules
                {'r.id': '2abf164a-b607-11ea-998e-07e60204cbcf'},
                {'r.id': '2cbf164a-b607-11ea-998e-07e60204cbcf'},
            ],
        ),
        (
            'request_approve_two_draft_for_one_rule_5.json',
            200,
            ['f3a0503d-3f30-4b43-8e30-71d77ebcaa1f'],
            [
                # closed ryles
                {
                    'r.id': 'f3a0503d-3f30-4b43-8e30-71d77ebcaa1f',
                    'r.ends_at': parser.parse('2024-01-01T15:00:00+00:00'),
                },
                # new ryles
                {'r.id': '2cbf164a-b603-11ea-998e-07e60204cbcf'},
            ],
        ),
        (
            'request_approve_two_draft_for_one_rule_6.json',
            200,
            ['f3a0503d-3f30-4b43-8e30-71d77ebcaa1f'],
            [
                # closed ryles
                {
                    'r.id': 'f3a0503d-3f30-4b43-8e30-71d77ebcaa1f',
                    'r.ends_at': parser.parse('2024-01-01T15:30:00+00:00'),
                },
                # new ryles
                {'r.id': '2cbf164a-b604-11ea-998e-07e60204cbcf'},
            ],
        ),
        (
            'request_create_and_close_all_tariffs_draft_7.json',
            200,
            ['f3a0503d-3f40-4a43-8e30-71d77ebcaa1f'],
            [
                # closed ryles
                {
                    'r.id': 'f3a0503d-3f40-4a43-8e30-71d77ebcaa1f',
                    'r.ends_at': parser.parse('2024-01-01T15:30:00+00:00'),
                },
                # new ryles
                {'r.id': '2caf164a-b604-12ea-998e-07e60204cbcf'},
            ],
        ),
        (
            'request_create_and_close_draft_8.json',
            200,
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
            [
                # closed ryles
                {'r.id': '2abf062a-b607-11ea-998e-07e60204cbcf'},
                # new ryles
                {'r.id': '2cae164a-b604-11ea-998e-07e60204cbcf'},
            ],
        ),
        (
            'request_create_and_close_draft_9.json',
            200,
            [
                'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
                'f3a0503d-3f30-4a43-8e30-72d77ebcaa1f',
            ],
            [
                # closed ryles
                {
                    'r.id': 'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
                    'r.ends_at': parser.parse('2024-01-01T21:00:00+00:00'),
                },
                {
                    'r.id': 'f3a0503d-3f30-4a43-8e30-72d77ebcaa1f',
                    'r.ends_at': parser.parse('2030-01-01T21:00:00+00:00'),
                },
                # new ryles
                {'r.id': '2caf164a-b604-12eb-998e-07e60204cbcf'},
            ],
        ),
    ],
)
async def test_create_approve(
        taxi_billing_commissions,
        load_json,
        query_json,
        status,
        expected_closed_rules,
        expected_rule_changes,
        pgsql,
):
    query = load_json(query_json)
    headers = {
        'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
        'X-YaTaxi-Draft-Author': 'author',
        'X-YaTaxi-Draft-Approvals': 'approver',
        'X-YaTaxi-Draft-Id': 'draft_id',
    }
    response = await taxi_billing_commissions.post(
        'v1/rebate/create/approve', json=query, headers=headers,
    )
    assert response.status_code == status
    # new rules
    db_rules = _read_rules(
        pgsql['billing_commissions'].cursor(), expected_rule_changes,
    )
    assert _compare_db_and_expected(db_rules, expected_rule_changes)
    # load log data
    cursor = pgsql['billing_commissions'].cursor()
    cursor.execute('select rule_id from fees.rebate_rule_change_log')
    rules_in_log = [row[0] for row in cursor]
    # expect log for closed and new rules
    update_rule_ids = set(
        [rule['r.id'] for rule in expected_rule_changes]
        + expected_closed_rules,
    )
    assert update_rule_ids == set(rules_in_log)
    assert len(rules_in_log) == len(update_rule_ids)
    # check draft_spec update
    cursor = pgsql['billing_commissions'].cursor()
    cursor.execute(
        'SELECT ticket, approvers, initiator, external_draft_id from'
        ' fees.draft_spec where id = %(id)s',
        {'id': query['draft_id']},
    )
    db_data = list(cursor)
    assert db_data[0][0] == headers['X-YaTaxi-Draft-Tickets']
    assert db_data[0][1] == headers['X-YaTaxi-Draft-Approvals']
    assert db_data[0][3] == headers['X-YaTaxi-Draft-Id']


def _read_rules(cursor, rules_query):
    fetched_rules = []
    for rule in rules_query:
        select_keys = list(rule.keys())
        select_keys_str = ','.join(select_keys)
        cursor.execute(
            (
                f'SELECT {select_keys_str} FROM fees.rebate_rule as r '
                'WHERE r.id = %(id)s'
            ),
            {'id': rule['r.id']},
        )
        fetched_rules.append(dict(zip(select_keys, list(cursor)[0])))
    return fetched_rules


def _compare_db_and_expected(db, expected):
    return sorted(db, key=lambda data: data['r.id']) == sorted(
        expected, key=lambda data: data['r.id'],
    )


@pytest.mark.parametrize(
    'query_json', ['create_brand_new_rule.json', 'create_and_close.json'],
)
@pytest.mark.now('2019-01-01T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rebate_create.sql'],
)
async def test_create_and_approve(
        taxi_billing_commissions,
        billing_commissions_postgres_db,
        pgsql,
        load_json,
        query_json,
):
    query = load_json(query_json)
    response = await taxi_billing_commissions.post(
        'v1/rebate/create',
        json=query,
        headers={'X-YaTaxi-Draft-Author': 'author'},
    )
    assert response.status_code == 200
    approve_body = response.json()['data']
    approve_response = await taxi_billing_commissions.post(
        'v1/rebate/create/approve',
        json=approve_body,
        headers={
            'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
            'X-YaTaxi-Draft-Author': 'author',
            'X-YaTaxi-Draft-Approvals': 'approver',
            'X-YaTaxi-Draft-Id': 'draft_id',
        },
    )
    assert approve_response.status_code == 200
    for input_rule in query['rules']:
        matching_rules = _select_last_rule(
            pgsql,
            zone=input_rule['matcher']['zones'],
            tariff=input_rule['matcher'].get('tariffs', ['']),
        )
        assert len(matching_rules) == 1
        created_rule = matching_rules[0]
        actual_fees = created_rule['fees']
        expected_fees = decimal.Decimal(input_rule['fees']['percent'])
        assert actual_fees == expected_fees


def _select_last_rule(pgsql, zone, tariff):
    cursor = pgsql['billing_commissions'].cursor()
    cursor.execute(
        """
          SELECT tariff_zone,
                 tariff,
                 fee
            FROM fees.rebate_rule
           WHERE tariff_zone = ANY(%(zones)s)
                 -- tariff can be NULL for all rules.
             AND COALESCE(tariff, '') = ANY(%(tariffs)s)
        ORDER BY starts_at DESC
           LIMIT 1
        """,
        {'zones': zone, 'tariffs': tariff},
    )
    return [
        {'zone': row[0], 'tariff': row[1], 'fees': row[2]} for row in cursor
    ]
