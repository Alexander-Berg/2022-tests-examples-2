import pytest

from testsuite.utils import ordered_object

MOCK_NOW = '2022-06-16T13:21:00+03:00'


@pytest.mark.pgsql('billing_commissions', files=['call_center.sql'])
@pytest.mark.config(
    BILLING_COMMISSIONS_IGNORE_DRIVER_PROMOCODE={
        'categories': ['call_center'],
    },
)
async def test_select_category(taxi_billing_commissions, load_json):
    response = await taxi_billing_commissions.post(
        'v1/categories/select', json={},
    )
    assert response.status_code == 200, response.json()
    assert response.json() == load_json('categories_select.json')


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('billing_commissions', files=['call_center.sql'])
async def test_create_rules(
        taxi_billing_commissions, billing_commissions_postgres_db, load_json,
):
    response = await taxi_billing_commissions.post(
        '/v3/rules/create', json=load_json('create_rules.json'),
    )
    assert response.status_code == 200, response.json()
    data = response.json()['data']
    response = await taxi_billing_commissions.post(
        'v3/rules/create/approve',
        json=data,
        headers={
            'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
            'X-Yandex-Login': 'author',
            'X-YaTaxi-Draft-Approvals': 'approver',
            'X-YaTaxi-Draft-Id': 'draft_id',
        },
    )
    assert response.status_code == 200, response.json()
    assert _count_rules(billing_commissions_postgres_db) == 2


def _count_rules(cursor):
    sql = 'SELECT COUNT(*) FROM fees.rule;'
    cursor.execute(sql)
    return cursor.fetchone()[0]


@pytest.mark.pgsql('billing_commissions', files=['call_center.sql'])
async def test_select_rules(
        taxi_billing_commissions, load_json, a_rule, create_rules,
):
    create_rules(
        a_rule(
            rule_id='0b415ed6-01b7-4c61-95b8-037873396818',
            kind='call_center',
            fees={'fee': '5'},
        ),
        a_rule(
            rule_id='1e0dbf80-7117-402e-9935-ed6a676546a3',
            kind='call_center',
            fees={'percent': '3'},
            ends_at='2022-06-16T00:00:00+03:00',
            tag='percentage',
        ),
    )
    query = {
        'zone': ['moscow'],
        'starts_at': '2022-06-01T00:00:00+03:00',
        'ends_at': '2022-07-01T00:00:00+03:00',
        'kind': ['call_center'],
    }
    response = await taxi_billing_commissions.post(
        '/v2/rules/select', json=query,
    )
    assert response.status_code == 200, response.json()
    ordered_object.assert_eq(
        response.json(), load_json('select_rules.json'), ['rules', 'id'],
    )


@pytest.mark.pgsql('billing_commissions', files=['call_center.sql'])
@pytest.mark.parametrize(
    'query_attrs, expected',
    (
        (
            # not yet switched to pricing
            {'reference_time': '2022-06-22T09:15:37+03:00'},
            [
                {
                    'contract_id': '0b0f5b73-daa3-4e19-b0b3-943456175ba3',
                    'rate': {'kind': 'flat', 'rate': '3'},
                },
            ],
        ),
        (
            # switched to pricing, no rule
            {'reference_time': '2022-06-25T09:15:37+03:00'},
            [],
        ),
        (
            # switched to pricing, rule with percent
            {'reference_time': '2022-06-26T09:15:37+03:00'},
            [
                {
                    'contract_id': '1e0dbf80-7117-402e-9935-ed6a676546a3',
                    'rate': {'kind': 'flat', 'rate': '5'},
                },
            ],
        ),
        (
            # switched to pricing, rule with absolute fee
            {'reference_time': '2022-06-27T09:15:37+03:00'},
            [
                {
                    'contract_id': '0b415ed6-01b7-4c61-95b8-037873396818',
                    'rate': {'kind': 'absolute_value', 'commission': '10'},
                },
            ],
        ),
    ),
)
@pytest.mark.config(
    BILLING_USE_CALL_CENTER_COST_FROM_ORDER_SINCE={
        '__default__': '2022-06-25T00:00:00+03:00',
    },
)
async def test_match_rules(
        taxi_billing_commissions,
        load_json,
        a_rule,
        create_rules,
        a_base_rule,
        base_create_rules,
        query_attrs,
        expected,
):
    base_create_rules(
        a_base_rule(
            rule_id='0b0f5b73-daa3-4e19-b0b3-943456175ba3', call_center=30000,
        ),
    )
    create_rules(
        a_rule(
            rule_id='1e0dbf80-7117-402e-9935-ed6a676546a3',
            kind='call_center',
            fees={'percent': '5'},
            starts_at='2022-06-26:00:00+03:00',
            ends_at='2022-06-27T00:00:00+03:00',
        ),
        a_rule(
            rule_id='0b415ed6-01b7-4c61-95b8-037873396818',
            kind='call_center',
            starts_at='2022-06-27:00:00+03:00',
            ends_at='2022-06-28T00:00:00+03:00',
            fees={'fee': '10'},
        ),
    )
    query = {
        'billing_type': 'normal',
        'payment_type': 'card',
        'tags': [],
        'tariff_class': 'econom',
        'zone': 'moscow',
    }
    query.update(query_attrs)
    response = await taxi_billing_commissions.post(
        '/v1/rules/match', json=query,
    )
    assert response.status_code == 200, response.json()
    actual = [
        {field: agreement[field] for field in ['contract_id', 'rate']}
        for agreement in response.json()['agreements']
        if agreement['group'] == 'call_center'
    ]

    assert actual == expected
