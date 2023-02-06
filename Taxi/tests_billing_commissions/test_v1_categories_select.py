import pytest


@pytest.mark.parametrize(
    'query, status, expected',
    [
        (
            {},
            200,
            {
                'categories': [
                    {
                        'id': '2abf162a-b607-11ea-998e-07e60204cbcf',
                        'name': 'a122',
                        'kind': 'a122',
                        'description': 'a122',
                        'detailed_product': 'detailed_product',
                        'product': 'product',
                        'starts_at': '2019-01-01T21:00:00+00:00',
                        'ends_at': '2119-01-01T21:00:00+00:00',
                        'accounts': [],
                        'fields': 'core',
                        'ignore_driver_shift': False,
                        'ignore_driver_promocode': False,
                    },
                    {
                        'id': '2acf162a-b607-11ea-998e-07e60204cbcf',
                        'name': 'a124',
                        'kind': 'a124',
                        'description': 'a124',
                        'detailed_product': 'detailed_product',
                        'product': 'product',
                        'starts_at': '2019-01-01T21:00:00+00:00',
                        'ends_at': '2119-01-01T21:00:00+00:00',
                        'accounts': [
                            {
                                'agreement': 'taxi/yandex-ride',
                                'sub_account': 'sub_account',
                                'currency': 'order_currency',
                                'entity': 'entity',
                            },
                            {
                                'agreement': 'taxi/yandex-ride',
                                'sub_account': 'sub_account',
                                'currency': 'order_currency',
                                'entity': 'entity2',
                            },
                        ],
                        'fields': 'core',
                        'ignore_driver_shift': False,
                        'ignore_driver_promocode': False,
                    },
                    {
                        'id': '2bcf162a-b607-11ea-998e-07e60204cbcf',
                        'name': 'a123',
                        'kind': 'a123',
                        'description': 'a123',
                        'detailed_product': 'detailed_product',
                        'product': 'product',
                        'starts_at': '2019-01-01T21:00:00+00:00',
                        'ends_at': '2119-01-01T21:00:00+00:00',
                        'accounts': [
                            {
                                'agreement': 'taxi/yandex-ride',
                                'sub_account': 'sub_account',
                                'currency': 'contract_currency',
                                'entity': 'entity',
                            },
                        ],
                        'fields': 'core',
                        'ignore_driver_promocode': True,
                        'ignore_driver_shift': True,
                    },
                    {
                        'accounts': [],
                        'description': 'Opteum commission',
                        'detailed_product': 'gross_software_subscription_fee',
                        'ends_at': '2120-08-31T21:00:00+00:00',
                        'fields': 'software_subscription',
                        'id': '5d4378cb-c74c-ad34-e7d7-fa32c61f0f3b',
                        'kind': 'software_subscription',
                        'name': 'Opteum',
                        'product': 'order',
                        'ignore_driver_shift': False,
                        'ignore_driver_promocode': False,
                        'starts_at': '2020-08-31T21:00:00+00:00',
                    },
                ],
            },
        ),
        (
            {'limit': 2},
            200,
            {
                'categories': [
                    {
                        'id': '2abf162a-b607-11ea-998e-07e60204cbcf',
                        'name': 'a122',
                        'kind': 'a122',
                        'description': 'a122',
                        'detailed_product': 'detailed_product',
                        'product': 'product',
                        'starts_at': '2019-01-01T21:00:00+00:00',
                        'ends_at': '2119-01-01T21:00:00+00:00',
                        'accounts': [],
                        'fields': 'core',
                        'ignore_driver_shift': False,
                        'ignore_driver_promocode': False,
                    },
                    {
                        'id': '2acf162a-b607-11ea-998e-07e60204cbcf',
                        'name': 'a124',
                        'kind': 'a124',
                        'description': 'a124',
                        'detailed_product': 'detailed_product',
                        'product': 'product',
                        'starts_at': '2019-01-01T21:00:00+00:00',
                        'ends_at': '2119-01-01T21:00:00+00:00',
                        'accounts': [
                            {
                                'agreement': 'taxi/yandex-ride',
                                'sub_account': 'sub_account',
                                'currency': 'order_currency',
                                'entity': 'entity',
                            },
                            {
                                'agreement': 'taxi/yandex-ride',
                                'sub_account': 'sub_account',
                                'currency': 'order_currency',
                                'entity': 'entity2',
                            },
                        ],
                        'fields': 'core',
                        'ignore_driver_shift': False,
                        'ignore_driver_promocode': False,
                    },
                ],
                'next_cursor': '2acf162a-b607-11ea-998e-07e60204cbcf',
            },
        ),
        (
            {'limit': 2, 'cursor': '2acf162a-b607-11ea-998e-07e60204cbcf'},
            200,
            {
                'categories': [
                    {
                        'accounts': [
                            {
                                'agreement': 'taxi/yandex-ride',
                                'currency': 'contract_currency',
                                'entity': 'entity',
                                'sub_account': 'sub_account',
                            },
                        ],
                        'description': 'a123',
                        'detailed_product': 'detailed_product',
                        'ends_at': '2119-01-01T21:00:00+00:00',
                        'fields': 'core',
                        'id': '2bcf162a-b607-11ea-998e-07e60204cbcf',
                        'kind': 'a123',
                        'name': 'a123',
                        'product': 'product',
                        'ignore_driver_shift': True,
                        'ignore_driver_promocode': True,
                        'starts_at': '2019-01-01T21:00:00+00:00',
                    },
                    {
                        'accounts': [],
                        'description': 'Opteum commission',
                        'detailed_product': 'gross_software_subscription_fee',
                        'ends_at': '2120-08-31T21:00:00+00:00',
                        'fields': 'software_subscription',
                        'id': '5d4378cb-c74c-ad34-e7d7-fa32c61f0f3b',
                        'kind': 'software_subscription',
                        'name': 'Opteum',
                        'product': 'order',
                        'ignore_driver_shift': False,
                        'ignore_driver_promocode': False,
                        'starts_at': '2020-08-31T21:00:00+00:00',
                    },
                ],
                'next_cursor': '5d4378cb-c74c-ad34-e7d7-fa32c61f0f3b',
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_categories_select.sql'],
)
async def test_select(
        taxi_billing_commissions, query, status, expected, taxi_config,
):
    taxi_config.set_values(
        {'BILLING_COMMISSIONS_IGNORE_DRIVER_SHIFT': {'categories': ['a123']}},
    )
    taxi_config.set_values(
        {
            'BILLING_COMMISSIONS_IGNORE_DRIVER_PROMOCODE': {
                'categories': ['a123'],
            },
        },
    )
    response = await taxi_billing_commissions.post(
        'v1/categories/select', json=query,
    )
    assert response.status_code == status
    if expected != response.json():
        import json
        print(json.dumps(response.json()))
    assert expected == response.json()
