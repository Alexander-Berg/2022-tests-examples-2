import pytest

from tests_grocery_menu.plugins import mock_pigeon

DEFAULT_GROUPS = [
    mock_pigeon.get_combo_group(
        options_to_select=1,
        is_select_unique=True,
        products=['pigeon-product-1'],
    ),
    mock_pigeon.get_combo_group(
        options_to_select=1,
        is_select_unique=True,
        products=['pigeon-product-2'],
    ),
]


@pytest.mark.parametrize(
    'combo_count,req_cursor,req_limit,out_cursor,first_combo',
    [(10, 5, 5, 10, 'combo_5'), (10, 10, 10, 10, None)],
)
async def test_cursor(
        taxi_grocery_menu,
        pigeon,
        combo_count,
        req_cursor,
        req_limit,
        out_cursor,
        first_combo,
        overlord_catalog,
):
    overlord_catalog.add_product(
        product_id='product-1', external_id='pigeon-product-1',
    )
    overlord_catalog.add_product(
        product_id='product-2', external_id='pigeon-product-2',
    )
    for i in range(combo_count):
        pigeon.add_combo_product(
            combo_id=f'combo_{i}',
            status='active',
            product_groups=DEFAULT_GROUPS,
        )

    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/combo-products/list',
        json={'limit': req_limit, 'cursor': req_cursor},
    )
    assert response.status_code == 200
    assert response.json()['cursor'] == out_cursor
    if first_combo:
        assert response.json()['combo_products'][0]['combo_id'] == first_combo
    else:
        assert not response.json()['combo_products']


async def test_combo_only_available(
        taxi_grocery_menu, pigeon, overlord_catalog,
):
    overlord_catalog.add_product(
        product_id='product-1', external_id='pigeon-product-1',
    )
    overlord_catalog.add_product(
        product_id='product-2', external_id='pigeon-product-2',
    )
    pigeon.add_combo_product(
        combo_id='combo_1', status='active', product_groups=DEFAULT_GROUPS,
    )
    pigeon.add_combo_product(
        combo_id='combo_2', status='removed', product_groups=DEFAULT_GROUPS,
    )
    pigeon.add_combo_product(
        combo_id='combo_3', status='disabled', product_groups=DEFAULT_GROUPS,
    )
    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/combo-products/list', json={'limit': 100},
    )
    assert response.status_code == 200
    assert response.json()['cursor'] == 1
    assert len(response.json()['combo_products']) == 1
    assert response.json()['combo_products'][0]['combo_id'] == 'combo_1'


async def test_combo_not_supported(
        taxi_grocery_menu, pigeon, overlord_catalog,
):
    overlord_catalog.add_product(
        product_id='product-1', external_id='pigeon-product-1',
    )
    overlord_catalog.add_product(
        product_id='product-2', external_id='pigeon-product-2',
    )
    overlord_catalog.add_product(
        product_id='product-3', external_id='pigeon-product-3',
    )

    groups = [
        mock_pigeon.get_combo_group(
            options_to_select=1,
            is_select_unique=True,
            products=['pigeon-product-1'],
        ),
        mock_pigeon.get_combo_group(
            options_to_select=2,
            is_select_unique=False,
            products=['pigeon-product-2', 'pigeon-product-3'],
        ),
    ]

    pigeon.add_combo_product(
        combo_id='combo_1', status='active', product_groups=groups,
    )
    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/combo-products/list', json={'limit': 100},
    )
    assert response.status_code == 200
    assert response.json()['cursor'] == 0
    assert not response.json()['combo_products']


async def test_combo_properties(taxi_grocery_menu, pigeon, overlord_catalog):
    combo_id = 'combo_1'
    revision = 'combo_revision'
    linked_products = ['pigeon-meta-product-1']
    options_to_select = 3
    is_select_unique = False
    products_in_group = ['pigeon-product-1', 'pigeon-product-2']
    group_name = 'group-name'
    combo_type = mock_pigeon.ComboType.RECIPE
    overlord_catalog.add_product(
        product_id='product-1', external_id='pigeon-product-1',
    )
    overlord_catalog.add_product(
        product_id='product-2', external_id='pigeon-product-2',
    )
    overlord_catalog.add_product(
        product_id='meta-product-1', external_id='pigeon-meta-product-1',
    )

    pigeon.add_combo_product(
        combo_id=combo_id,
        revision=revision,
        linked_products=linked_products,
        combo_type=combo_type,
        product_groups=[
            mock_pigeon.get_combo_group(
                options_to_select=options_to_select,
                is_select_unique=is_select_unique,
                products=products_in_group,
                title_tanker_key=group_name,
            ),
        ],
    )

    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/combo-products/list', json={'limit': 100},
    )
    assert response.status_code == 200
    assert response.json()['cursor'] == 1
    assert len(response.json()['combo_products']) == 1
    assert response.json()['combo_products'][0] == {
        'combo_id': combo_id,
        'type': combo_type.value,
        'linked_meta_products': ['meta-product-1'],
        'product_groups': [
            {
                'title_tanker_key': group_name,
                'is_selection_unique': is_select_unique,
                'options_to_select': options_to_select,
                'products': ['product-1', 'product-2'],
            },
        ],
        'revision': revision,
    }


@pytest.mark.config(GROCERY_LOCALIZATION_USED_KEYSETS=['pigeon_combo_product'])
@pytest.mark.translations(
    pigeon_combo_product={
        'combo_product': {'en': 'combo_product', 'ru': 'комбо_продукт'},
    },
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_admin_combo_products(
        taxi_grocery_menu, pigeon, overlord_catalog, locale,
):
    overlord_catalog.add_product(
        product_id='product-1', external_id='pigeon-product-1',
    )
    overlord_catalog.add_product(
        product_id='product-2', external_id='pigeon-product-2',
    )

    pigeon.add_combo_product(
        combo_id='combo_1',
        revision='revision_1',
        status='active',
        product_groups=DEFAULT_GROUPS,
        name_tanker_key={
            'keyset': 'pigeon_combo_product',
            'key': 'combo_product',
        },
    )
    pigeon.add_combo_product(
        combo_id='combo_2', status='removed', product_groups=DEFAULT_GROUPS,
    )
    pigeon.add_combo_product(
        combo_id='combo_3',
        revision='revision_3',
        status='disabled',
        product_groups=DEFAULT_GROUPS,
        name_tanker_key={
            'keyset': 'pigeon_combo_product',
            'key': 'combo_product',
        },
    )
    response = await taxi_grocery_menu.post(
        '/admin/menu/v1/combo-products/list',
        json={'limit': 100},
        headers={'Accept-Language': locale},
    )

    if locale == 'en':
        combo_product_title = 'combo_product'
    elif locale == 'ru':
        combo_product_title = 'комбо_продукт'

    assert response.status_code == 200
    assert len(response.json()['combo_products']) == 2
    assert (
        sorted(
            response.json()['combo_products'],
            key=lambda item: item['combo_id'],
        )
        == [
            {
                'combo_id': 'combo_1',
                'revision': 'revision_1',
                'title': combo_product_title,
            },
            {
                'combo_id': 'combo_3',
                'revision': 'revision_3',
                'title': combo_product_title,
            },
        ]
    )
