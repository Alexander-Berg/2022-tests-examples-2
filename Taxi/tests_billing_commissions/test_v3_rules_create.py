import decimal

from dateutil import parser
import pytest

_ENDLESS_DATE = parser.parse('2100-01-01T00:00:00+03:00')


@pytest.mark.parametrize(
    'query_json, category_requirements, status, '
    'expected_message, expected_close, '
    'expected_draft_records',
    [
        (
            'request.json',
            {},
            200,
            None,
            [],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                    'hiring_type',
                    'hiring_age',
                    'fine_code',
                ],
                'data': [
                    (
                        'moscow',
                        True,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                        None,
                        None,
                        None,
                    ),
                ],
            },
        ),
        (
            'request_no_ends.json',
            {},
            200,
            None,
            [],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                ],
                'data': [
                    (
                        'moscow',
                        True,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        None,
                    ),
                ],
            },
        ),
        (
            'request_wo_withdraw.json',
            {},
            200,
            None,
            [],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                ],
                'data': [
                    (
                        'moscow',
                        None,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                    ),
                ],
            },
        ),
        (
            'request_close_one_rule.json',
            {},
            200,
            None,
            [('2abf062a-b607-11ea-998e-07e60204cbcf',)],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                ],
                'data': [
                    (
                        'moscow',
                        True,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                    ),
                ],
            },
        ),
        (
            'request_rule_to_old.json',
            {},
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'Object starts in the past',
            },
            [],
            {},
        ),
        (
            'request_rule_in_future_exists.json',
            {},
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': (
                    'Future rule exists for rule: '
                    'kind(software_subscription), zone(spb), '
                    'tariff(econom), starts_at(2019-12-31T21:00:00Z), '
                    'tag(None), payment_type(None)'
                ),
            },
            [],
            {},
        ),
        (
            'request_reposition_no_tag.json',
            {},
            200,
            {},
            [],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                ],
                'data': [
                    (
                        'moscow',
                        None,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                    ),
                ],
            },
        ),
        (
            'request_reposition.json',
            {},
            200,
            {},
            [],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                ],
                'data': [
                    (
                        'moscow',
                        None,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                    ),
                ],
            },
        ),
        (
            'request_reposition_no_tag.json',
            {'reposition': ['tag']},
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'Fill required fields for this category',
            },
            [],
            {},
        ),
        (
            'request_reposition.json',
            {'reposition': ['tag']},
            200,
            {},
            [],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                ],
                'data': [
                    (
                        'moscow',
                        None,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                    ),
                ],
            },
        ),
        (
            'request_hiring.json',
            {},
            200,
            {},
            [],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                    'hiring_type',
                    'hiring_age',
                    'fees',
                ],
                'data': [
                    (
                        'moscow',
                        None,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                        'commercial_returned',
                        42,
                        {'percent': '100.1'},
                    ),
                ],
            },
        ),
        (
            'request_hiring_with_rent.json',
            {},
            200,
            {},
            [],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                    'hiring_type',
                    'hiring_age',
                    'fees',
                ],
                'data': [
                    (
                        'moscow',
                        None,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                        'commercial_with_rent',
                        42,
                        {'percent': '100.1'},
                    ),
                ],
            },
        ),
        (
            'request_fine.json',
            {},
            200,
            {},
            [],
            {
                'fields': [
                    'tariff_zone',
                    'withdraw_from_driver_account',
                    'starts_at',
                    'ends_at',
                    'hiring_type',
                    'hiring_age',
                    'fine_code',
                ],
                'data': [
                    (
                        'ekb',
                        None,
                        parser.parse('2020-01-01T00:00:00+03:00'),
                        parser.parse('2021-01-01T00:00:00+03:00'),
                        None,
                        None,
                        'fine!!!',
                    ),
                ],
            },
        ),
        (
            'request_many_zones.json',
            {},
            200,
            {},
            [],
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
        ),
    ],
)
@pytest.mark.now('2019-01-01T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v3_rules_create.sql'],
)
async def test_create_check(
        taxi_billing_commissions,
        load_json,
        query_json,
        status,
        expected_message,
        expected_close,
        billing_commissions_postgres_db,
        expected_draft_records,
        category_requirements,
        taxi_config,
):
    taxi_config.set_values(
        {
            'BILLING_COMMISSIONS_CATEGORY_REQUIRED_FIELDS': (
                category_requirements
            ),
        },
    )
    query = load_json(query_json)
    response = await taxi_billing_commissions.post(
        'v3/rules/create', json=query,
    )
    assert response.status_code == status, response.json()
    if status != 200:
        assert expected_message == response.json()
    billing_commissions_postgres_db.execute(
        'SELECT rule_id FROM fees.draft_rule_to_close',
    )
    rows = billing_commissions_postgres_db.fetchall()
    assert rows == expected_close
    fields = expected_draft_records.get('fields', [])
    if 'ends_at' in fields:
        ends_at_position = fields.index('ends_at')
        fields[ends_at_position] = (
            'CASE WHEN ends_at > \'{}\'::TIMESTAMPTZ '
            'THEN NULL ELSE ends_at END as ends_at'
        ).format(_ENDLESS_DATE.isoformat())
    billing_commissions_postgres_db.execute(
        'SELECT {} FROM fees.draft_rule order by tariff_zone, tariff'.format(
            ','.join(fields),
        ),
    )
    rows = billing_commissions_postgres_db.fetchall()
    assert expected_draft_records.get('data', []) == rows


@pytest.mark.now('2019-12-31T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v3_rules_create_approve.sql'],
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
                {
                    'r.id': '2cbf164a-b603-11ea-998e-07e60204cbcf',
                    'rpt.payment_type': 'payment_type',
                    'rt.tag': 'tag',
                },
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
                {
                    'r.id': '2cbf164a-b604-11ea-998e-07e60204cbcf',
                    'rpt.payment_type': 'payment_type',
                    'rt.tag': 'tag',
                },
            ],
        ),
        (
            'request_approve_hiring_rule_draft_7.json',
            200,
            [],
            [
                # closed ryles
                # new ryles
                {
                    'r.id': '2caf164a-b604-11ea-998e-07e60204cbcf',
                    'rpt.payment_type': 'payment_type',
                    'rt.tag': 'tag',
                    'rht.hiring_type': 'commercial_returned',
                    'rht.hiring_age': 128,
                },
            ],
        ),
        (
            'request_approve_fine_rule_draft_8.json',
            200,
            [],
            [
                # closed ryles
                # new ryles
                {
                    'r.id': '2cae164a-b604-11ea-998e-07e60204cbcf',
                    'rpt.payment_type': 'fine_payment_type',
                    'rt.tag': 'fine_tag',
                    'rht.hiring_type': None,
                    'rht.hiring_age': None,
                    'rft.fine_code': 'fine!!!',
                },
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
        'X-Yandex-Login': 'author',
        'X-YaTaxi-Draft-Approvals': 'approver',
        'X-YaTaxi-Draft-Id': 'draft_id',
    }
    response = await taxi_billing_commissions.post(
        'v3/rules/create/approve', json=query, headers=headers,
    )
    assert response.status_code == status
    # new rules
    db_rules = _read_rules(
        pgsql['billing_commissions'].cursor(), expected_rule_changes,
    )
    assert _compare_db_and_expected(db_rules, expected_rule_changes)
    # load log data
    cursor = pgsql['billing_commissions'].cursor()
    cursor.execute('select rule_id from fees.rule_change_log')
    rules_in_log = [row[0] for row in cursor]
    print(rules_in_log)
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
    assert db_data[0][2] == headers['X-Yandex-Login']
    assert db_data[0][3] == headers['X-YaTaxi-Draft-Id']


@pytest.mark.parametrize(
    'query_json',
    [
        'create_brand_new_rule.json',
        'create_and_close.json',
        'with_unrealized.json',
    ],
)
@pytest.mark.now('2019-01-01T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v3_rules_create.sql'],
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
        'v3/rules/create', json=query,
    )
    assert response.status_code == 200
    approve_body = response.json()['data']
    approve_response = await taxi_billing_commissions.post(
        'v3/rules/create/approve',
        json=approve_body,
        headers={
            'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
            'X-Yandex-Login': 'author',
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
        actual_fees = _get_fees(created_rule)
        expected_fees = _get_fees(input_rule)
        assert actual_fees == expected_fees


def _select_last_rule(pgsql, zone, tariff):
    cursor = pgsql['billing_commissions'].cursor()
    cursor.execute(
        """
          SELECT tariff_zone,
                 tariff,
                 fees
            FROM fees.rule
           WHERE tariff_zone = ANY(%(zones)s)
             AND tariff = ANY(%(tariffs)s)
        ORDER BY starts_at DESC
           LIMIT 1
        """,
        {'zones': zone, 'tariffs': tariff},
    )
    return [
        {'zone': row[0], 'tariff': row[1], 'fees': row[2]} for row in cursor
    ]


def _get_fees(rule):
    if isinstance(rule['fees'], dict):
        return (
            (rule['fees']['fee']),
            _maybe_decimal(rule['fees'].get('unrealized_fee')),
        )
    return sorted(
        [
            (fee_obj['subscription_level'], decimal.Decimal(fee_obj['fee']))
            for fee_obj in rule['fees']
        ],
        key=lambda fee: fee[0],
    )


def _maybe_decimal(what):
    return decimal.Decimal(what) if what is not None else None


def _read_rules(cursor, rules_query):
    fetched_rules = []
    for rule in rules_query:
        select_keys = list(rule.keys())
        select_keys_str = ','.join(select_keys)
        cursor.execute(
            (
                f'SELECT {select_keys_str} FROM fees.rule as r '
                'LEFT JOIN fees.withdraw_from_driver_account as wfda '
                'ON r.id = wfda.rule_id '
                'LEFT JOIN fees.rule_min_max_cost as rmmc '
                'ON r.id = rmmc.rule_id '
                'LEFT JOIN fees.category as c on r.kind = c.kind '
                'LEFT JOIN fees.rule_tag as rt on r.id = rt.rule_id '
                'LEFT JOIN fees.rule_payment_type as rpt '
                'ON r.id = rpt.rule_id '
                'LEFT JOIN fees.rule_hiring_type as rht '
                'ON r.id = rht.rule_id '
                'LEFT JOIN fees.rule_fine_code as rft '
                'ON r.id = rft.rule_id '
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
