import urllib

import pytest

from tests_corp_discounts import consts


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=consts.CORP_COUNTRIES_SUPPORTED)
@pytest.mark.parametrize(
    ['discount_id', 'query', 'expected_status', 'expected_response'],
    [
        pytest.param(
            1,
            {},
            200,
            {
                'items': [
                    {
                        'link_id': 1,
                        'times_used': 1,
                        'times_left': 4,
                        'amounts': {
                            'spent': {
                                'sum': '50',
                                'vat': '10',
                                'with_vat': '60',
                            },
                        },
                        'valid_since': '2021-08-17T23:54:00+00:00',
                        'valid_until': '2031-08-17T23:54:00+00:00',
                        'activated_at': '2021-10-01T00:00:00+00:00',
                        'client_id': 'client_id_1',
                        'discount_id': 1,
                        'discount_name': 'fixed rule',
                        'discount_services': ['eats2', 'drive'],
                        'currency': 'RUB',
                        'country': 'RUS',
                        'legal_information': (
                            '<h1>Discount title</h1>'
                            '<p>Discount description</p>'
                        ),
                        'rule': {
                            'max_orders': 5,
                            'max_discount': '200',
                            'percent': 10,
                            'minimal_order_sum': '600',
                            'rule_class': 'first_orders_percent',
                        },
                    },
                    {
                        'link_id': 3,
                        'times_used': 1,
                        'times_left': 4,
                        'amounts': {
                            'spent': {
                                'sum': '50',
                                'vat': '10',
                                'with_vat': '60',
                            },
                        },
                        'valid_since': '2021-08-17T23:54:00+00:00',
                        'valid_until': '2031-08-17T23:54:00+00:00',
                        'activated_at': '2021-10-01T00:00:00+00:00',
                        'client_id': 'client_id_3',
                        'discount_id': 1,
                        'discount_name': 'fixed rule',
                        'discount_services': ['eats2', 'drive'],
                        'currency': 'RUB',
                        'country': 'RUS',
                        'legal_information': (
                            '<h1>Discount title</h1>'
                            '<p>Discount description</p>'
                        ),
                        'rule': {
                            'max_orders': 5,
                            'max_discount': '200',
                            'percent': 10,
                            'minimal_order_sum': '600',
                            'rule_class': 'first_orders_percent',
                        },
                    },
                ],
            },
            id='found client discounts',
        ),
        pytest.param(
            1,
            {'limit': 50, 'offset': 1},
            200,
            {
                'items': [
                    {
                        'link_id': 3,
                        'times_used': 1,
                        'times_left': 4,
                        'amounts': {
                            'spent': {
                                'sum': '50',
                                'vat': '10',
                                'with_vat': '60',
                            },
                        },
                        'valid_since': '2021-08-17T23:54:00+00:00',
                        'valid_until': '2031-08-17T23:54:00+00:00',
                        'activated_at': '2021-10-01T00:00:00+00:00',
                        'client_id': 'client_id_3',
                        'discount_id': 1,
                        'discount_name': 'fixed rule',
                        'discount_services': ['eats2', 'drive'],
                        'currency': 'RUB',
                        'country': 'RUS',
                        'legal_information': (
                            '<h1>Discount title</h1>'
                            '<p>Discount description</p>'
                        ),
                        'rule': {
                            'max_orders': 5,
                            'max_discount': '200',
                            'percent': 10,
                            'minimal_order_sum': '600',
                            'rule_class': 'first_orders_percent',
                        },
                    },
                ],
            },
            id='found client discounts',
        ),
        pytest.param(3, {}, 200, {'items': []}),
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
        query,
        expected_status,
        expected_response,
):
    get_params = dict(discount_id=discount_id, **query)
    get_params_str = urllib.parse.urlencode(get_params)
    uri = f'/v1/admin/discount/links/list?{get_params_str}'

    response = await taxi_corp_discounts.get(uri)

    assert response.status == expected_status
    assert response.json() == expected_response
