import pytest

from tests_corp_discounts import consts

LEGAL_TEXTS = {
    1: '<h1>Discount title</h1><p>Discount description</p>',
    2: '<h1>New discount title</h1><p>Another discount description</p>',
}


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=consts.CORP_COUNTRIES_SUPPORTED)
@pytest.mark.parametrize(
    ['client_id', 'expected_status', 'expected_response'],
    [
        pytest.param(
            'client_id_1',
            200,
            {
                'items': [
                    {
                        'activated_at': '2021-10-01T00:00:00+00:00',
                        'amounts': {
                            'spent': {
                                'sum': '50',
                                'vat': '10',
                                'with_vat': '60',
                            },
                        },
                        'country': 'RUS',
                        'currency': 'RUB',
                        'discount_id': 1,
                        'client_id': 'client_id_1',
                        'discount_name': 'fixed rule',
                        'discount_services': ['eats2', 'drive'],
                        'legal_information': LEGAL_TEXTS[1],
                        'link_id': 1,
                        'rule': {
                            'max_discount': '200',
                            'max_orders': 5,
                            'minimal_order_sum': '600',
                            'percent': 10,
                            'rule_class': 'first_orders_percent',
                        },
                        'times_left': 4,
                        'times_used': 1,
                        'valid_since': '2021-08-17T23:54:00+00:00',
                        'valid_until': '2031-08-17T23:54:00+00:00',
                    },
                    {
                        'amounts': {
                            'left': {
                                'sum': '400',
                                'vat': '80',
                                'with_vat': '480',
                            },
                            'limit': {
                                'sum': '500',
                                'vat': '100',
                                'with_vat': '600',
                            },
                            'spent': {
                                'sum': '100',
                                'vat': '20',
                                'with_vat': '120',
                            },
                        },
                        'country': 'RUS',
                        'currency': 'RUB',
                        'client_id': 'client_id_1',
                        'discount_id': 2,
                        'discount_name': 'first discount',
                        'discount_services': ['eats2'],
                        'legal_information': LEGAL_TEXTS[2],
                        'link_id': 2,
                        'rule': {
                            'max_amount_spent': '500',
                            'max_discount': '200',
                            'minimal_order_sum': '600',
                            'percent': 10,
                            'rule_class': 'amount_spent_percent',
                        },
                        'times_used': 1,
                        'valid_since': '2031-09-01T00:00:00+00:00',
                        'valid_until': '2031-10-01T00:00:00+00:00',
                    },
                ],
            },
            id='found client discounts',
        ),
        pytest.param(
            'client_id_2', 200, {'items': []}, id='not found client discounts',
        ),
    ],
)
@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_client_discount_links(
        taxi_corp_discounts,
        load_json,
        client_id,
        expected_status,
        expected_response,
):
    response = await taxi_corp_discounts.get(
        f'/v1/admin/client/links/list?client_id={client_id}',
    )
    assert response.status == expected_status
    assert response.json() == expected_response
