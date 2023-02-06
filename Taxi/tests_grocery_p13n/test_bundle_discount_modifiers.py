from tests_grocery_p13n import depot


async def test_bundle_discount_v2(taxi_grocery_p13n, grocery_discounts):
    bundle_id = 'bundle_id'
    revision = 'revision_id'
    grocery_discounts.add_money_discount(
        product_id=revision,
        value_type='fraction',
        value='10',
        hierarchy_name='bundle_discounts',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [
                {
                    'product_id': bundle_id,
                    'category_ids': [],
                    'bundle_revision': revision,
                },
            ],
        },
    )
    assert response.json()['modifiers'] == [
        {
            'bundle_id': 'bundle_id',
            'meta': {'hierarchy_name': 'bundle_discounts'},
            'rule': {'discount_percent': '10'},
            'type': 'bundle_discount_v2',
        },
    ]
