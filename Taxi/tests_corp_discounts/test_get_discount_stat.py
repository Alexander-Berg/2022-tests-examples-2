import pytest

from tests_corp_discounts import consts


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=consts.CORP_COUNTRIES_SUPPORTED)
@pytest.mark.parametrize(
    ['discount_id', 'expected_status', 'expected_response'],
    [
        pytest.param(
            1,
            200,
            {
                'discount_name': 'fixed rule',
                'discount_services': ['eats2', 'drive'],
                'currency': 'RUB',
                'country': 'RUS',
                'legal_information': (
                    '<h1>Discount title</h1><p>Discount description</p>'
                ),
                'rule': {
                    'max_orders': 5,
                    'max_discount': '200',
                    'percent': 10,
                    'minimal_order_sum': '600',
                    'rule_class': 'first_orders_percent',
                },
                'discount_id': 1,
                'times_used': 2,
                'times_left': 8,
                'amounts': {
                    'spent': {'sum': '100', 'vat': '20', 'with_vat': '120'},
                },
                'client_ids': ['client_id_1', 'client_id_3'],
            },
            id='discount with 2 clients',
        ),
        pytest.param(
            3,
            200,
            {
                'discount_name': 'first discount-3',
                'discount_services': ['eats2'],
                'currency': 'RUB',
                'country': 'RUS',
                'legal_information': (
                    '<h1>New discount title</h1>'
                    '<p>Another discount description</p>'
                ),
                'rule': {
                    'max_amount_spent': '500',
                    'max_discount': '200',
                    'percent': 10,
                    'minimal_order_sum': '600',
                    'rule_class': 'amount_spent_percent',
                },
                'discount_id': 3,
                'times_used': 0,
                'amounts': {
                    'left': {'sum': '0', 'vat': '0', 'with_vat': '0'},
                    'limit': {'sum': '0', 'vat': '0', 'with_vat': '0'},
                    'spent': {'sum': '0', 'vat': '0', 'with_vat': '0'},
                },
                'client_ids': [],
            },
            id='discount without clients',
        ),
        pytest.param(777, 404, None, id='non existing discount'),
    ],
)
@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_client_discount_links(
        taxi_corp_discounts,
        load_json,
        discount_id,
        expected_status,
        expected_response,
):
    uri = f'/v1/admin/discount/stat?discount_id={discount_id}'

    response = await taxi_corp_discounts.get(uri)

    assert response.status == expected_status

    if expected_status == 200:
        resp = response.json()
        assert resp == expected_response
