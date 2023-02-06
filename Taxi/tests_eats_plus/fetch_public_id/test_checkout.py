import pytest

from tests_eats_plus import conftest

EATS_CATALOG_STORAGE_CONTENT = [
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'rus',
            'name': 'Russia',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 1,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'shop',
        'type': 'native',
    },
]


@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CONTENT)
@pytest.mark.config(EATS_PLUS_FETCH_PUBLIC_ID=True)
@pytest.mark.experiments3(filename='exp3_discounts.json')
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': 'public-product-1',
            'place_menu_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '10.0',
                    'maximum_discount': '1234',
                },
            },
        },
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_fetch_public_id_checkout(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        mockserver,
        eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 120})
    eats_order_stats()

    @mockserver.json_handler(
        '/eats-products/internal/v2/products/public_id_by_origin_id',
    )
    def public_id_by_origin_id(request):
        assert request.json == {
            'place_id': 1,
            'origin_ids': ['product-1', 'product-2', 'product-3'],
        }
        return {
            'products_ids': [
                {'origin_id': 'product-1', 'public_id': 'public-product-1'},
                {'origin_id': 'product-2'},
                {'origin_id': 'product-3', 'public_id': ''},
            ],
        }

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'origin_id': 'product-1',
                },
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'origin_id': 'product-2',
                },
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'origin_id': 'product-3',
                },
            ],
        },
    )

    assert public_id_by_origin_id.times_called == 1
    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback_income': {
            'eda_part': 0,
            'decimal_eda_part': '0',
            'full': 31,
            'decimal_full': '31',
            'place_part': 31,
            'decimal_place_part': '31',
        },
        'cashback_outcome': 0,
        'decimal_cashback_outcome': '0',
        'hide_cashback_income': False,
        'has_plus': True,
    }
