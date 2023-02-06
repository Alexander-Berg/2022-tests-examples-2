import pytest


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(
    BILLING_MANUAL_TRANSACTIONS_SETTINGS={
        'subsidy_do_x_get_y': {
            'product': 'subvention',
            'detailed_product': 'subvention_do_x_get_y',
            'service_id': 111,
            'paid_to': 'performer',
            'description': 'Do X get Y subvention',
            'agreement_id': 'taxi/yandex_ride',
            'sub_account': 'subvention/do_x_get_y',
            'taximeter_kind': 'subvention',
        },
        'park_subvention': {
            'product': 'park_subvention',
            'detailed_product': 'park_subvention',
            'service_id': 111,
            'paid_to': 'partner',
            'description': 'Do X get Y subvention',
            'agreement_id': 'taxi/yandex_ride',
            'sub_account': 'subvention/park',
        },
        'arbitrary_revenues': {
            'product': '',
            'detailed_product': '',
            'service_id': 111,
            'paid_to': 'partner',
            'description': 'Arbitrary revenues payment',
            'category_type': 'universal',
        },
    },
)
@pytest.mark.now('2020-10-08T08:08:08+00:00')
async def test_v1_manual_transactions_categories_list(
        request_headers,
        patched_tvm_ticket_check,
        monkeypatch,
        taxi_billing_orders_client,
):
    response = await taxi_billing_orders_client.get(
        '/v1/manual_transactions/categories/list/', headers=request_headers,
    )
    assert response.status == 200
    categories_list = await response.json()
    expected_list = [
        {
            'category': 'park_subvention',
            'paid_to': 'partner',
            'category_type': 'standard',
        },
        {
            'category': 'subsidy_do_x_get_y',
            'paid_to': 'performer',
            'category_type': 'standard',
        },
        {
            'category': 'arbitrary_revenues',
            'paid_to': 'partner',
            'category_type': 'universal',
        },
    ]

    def _sorted(cat_list):
        return sorted(cat_list, key=lambda cat: cat['category'])

    assert _sorted(categories_list['categories']) == _sorted(expected_list)
