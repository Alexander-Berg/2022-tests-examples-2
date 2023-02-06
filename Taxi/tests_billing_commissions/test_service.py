import datetime as dt

import pytest

_HEADERS = {
    'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
    'X-Yandex-Login': 'author',
    'X-YaTaxi-Draft-Approvals': 'approver',
    'X-YaTaxi-Draft-Id': 'draft_id',
}


@pytest.mark.servicetest
@pytest.mark.pgsql('billing_commissions', files=['defaults.sql'])
async def test_category_and_rules_creation_1(
        taxi_billing_commissions, load_json,
):
    await _run_test_category_and_rules_creation(
        taxi_billing_commissions,
        load_json,
        '01_category_request.json',
        '01_rule_request.json',
        '01-categories_response.json',
        '01-rules_response.json',
    )


@pytest.mark.pgsql('billing_commissions', files=['defaults.sql'])
async def test_category_and_rules_creation_2(
        taxi_billing_commissions, load_json,
):
    await _run_test_category_and_rules_creation(
        taxi_billing_commissions,
        load_json,
        '01_category_request.json',
        '02_rule_request.json',
        '01-categories_response.json',
        '02-rules_response.json',
    )


async def _run_test_category_and_rules_creation(
        taxi_billing_commissions,
        load_json,
        category_request,
        rules_request,
        category_response,
        rule_response,
):
    now = dt.datetime.now(tz=dt.timezone.utc)
    start = (now + dt.timedelta(seconds=5)).isoformat()

    # category
    category_query = load_json(category_request)
    category_query['category']['starts_at'] = start
    response = await taxi_billing_commissions.post(
        'v1/categories/create', json=category_query,
    )
    assert response.status == 200
    approve_categories = response.json()
    response = await taxi_billing_commissions.post(
        'v1/categories/create/approve',
        json=approve_categories['data'],
        headers=_HEADERS,
    )
    assert response.status == 200
    # rules
    rules_query = load_json(rules_request)
    for rule in rules_query['rules']:
        rule['matcher']['starts_at'] = start
    response = await taxi_billing_commissions.post(
        'v3/rules/create', json=rules_query,
    )
    assert response.status == 200, response.json()
    approve_rules = response.json()
    response = await taxi_billing_commissions.post(
        'v3/rules/create/approve',
        json=approve_rules['data'],
        headers=_HEADERS,
    )
    assert response.status == 200
    # view db
    response = await taxi_billing_commissions.post(
        'v1/categories/select', json={},
    )
    assert response.status == 200
    categories = response.json()
    for category in categories['categories']:
        del category['id']
        del category['starts_at']
        del category['ends_at']
    expected_categories = load_json(category_response)
    categories['categories'].sort(key=lambda obj: obj['kind'])
    expected_categories['categories'].sort(key=lambda obj: obj['kind'])
    assert categories == expected_categories

    response = await taxi_billing_commissions.post(
        'v2/rules/select',
        json={
            'zone': ['moscow', 'spb'],
            'starts_at': '2000-01-01T00:00:00+00:00',
            'ends_at': '2500-01-01T00:00:00+00:00',
        },
    )
    assert response.status == 200
    rules = response.json()
    for rule in rules['rules']:
        del rule['id']
        del rule['matcher']['starts_at']
        del rule['matcher']['ends_at']
    expected_rules = load_json(rule_response)
    rules['rules'].sort(key=lambda obj: obj['kind'])
    expected_rules['rules'].sort(key=lambda obj: obj['kind'])
    assert rules == expected_rules
