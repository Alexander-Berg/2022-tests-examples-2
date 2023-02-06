import pytest

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
        'type': 'marketplace',
    },
]


@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CONTENT)
@pytest.mark.config(EATS_PLUS_FETCH_PUBLIC_ID=True)
@pytest.mark.experiments3(filename='exp3_discounts.json')
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': 'offer_0',
            'place_cashback': {
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
async def test_log_discount_cashback(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        pgsql,
        eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 120})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': '20211129-123456',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'public_id': 'product-1',
                },
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'public_id': 'product-2',
                },
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'public_id': 'product-3',
                },
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback_income': {
            'decimal_eda_part': '0',
            'decimal_full': '94',
            'decimal_place_part': '94',
            'eda_part': 0,
            'full': 94,
            'place_part': 94,
        },
        'cashback_outcome': 120,
        'decimal_cashback_outcome': '120',
        'hide_cashback_income': False,
        'cashback_outcome_details': [
            {'cashback_outcome': '120', 'service_type': 'product'},
        ],
        'has_plus': True,
    }
    cursor = pgsql['eats_plus'].cursor()
    cursor.execute(
        'SELECT order_nr, place_id, discounts '
        'FROM eats_plus.eats_discount_stats '
        f'WHERE order_nr=\'20211129-123456\'',
    )
    stats = cursor.fetchall()

    assert stats is not None
    assert len(stats) == 1

    assert stats[0][0] == '20211129-123456'
    assert stats[0][1] == 1
    assert stats[0][2] == {'plus_happy_hours': 93.6}
