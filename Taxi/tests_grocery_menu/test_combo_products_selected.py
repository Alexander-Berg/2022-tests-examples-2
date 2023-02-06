import pytest

from tests_grocery_menu.plugins import mock_pigeon

PIGEON_ID = 'pigeon-{}'


def _format_pigeon_product_ids(products):
    return [PIGEON_ID.format(product_id) for product_id in products]


def _add_products(products, overlord_catalog):
    for product_id in products:
        overlord_catalog.add_product(
            product_id=product_id, external_id=PIGEON_ID.format(product_id),
        )


# Проверяем что возвращается комбо для продуктов
@pytest.mark.parametrize(
    'combo_type',
    [mock_pigeon.ComboType.DISCOUNT, mock_pigeon.ComboType.RECIPE],
)
async def test_combo_selected(
        taxi_grocery_menu, pigeon, overlord_catalog, combo_type,
):
    combo_id = 'combo_1'
    revision = 'combo_revision'
    options_to_select = 1
    is_select_unique = True
    group_title = 'group-title'

    _add_products(['product-1', 'product-2'], overlord_catalog)
    pigeon.add_combo_product(
        combo_id=combo_id,
        revision=revision,
        combo_type=combo_type,
        product_groups=[
            mock_pigeon.get_combo_group(
                title_tanker_key=group_title,
                options_to_select=options_to_select,
                is_select_unique=is_select_unique,
                products=_format_pigeon_product_ids(['product-1']),
            ),
            mock_pigeon.get_combo_group(
                title_tanker_key=group_title,
                options_to_select=options_to_select,
                is_select_unique=is_select_unique,
                products=_format_pigeon_product_ids(['product-2']),
            ),
        ],
    )

    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/combo-products/selected',
        json={
            'products': [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-2', 'quantity': 1},
            ],
        },
    )
    assert response.status_code == 200
    combo_products = response.json()['combo_products']
    if combo_type == mock_pigeon.ComboType.RECIPE:
        assert not combo_products
    else:
        assert combo_products == [
            {
                'combo_id': combo_id,
                'type': mock_pigeon.ComboType.DISCOUNT.value,
                'linked_meta_products': [],
                'product_groups': [
                    {
                        'title_tanker_key': group_title,
                        'is_selection_unique': is_select_unique,
                        'options_to_select': options_to_select,
                        'products': ['product-1'],
                    },
                    {
                        'title_tanker_key': group_title,
                        'is_selection_unique': is_select_unique,
                        'options_to_select': options_to_select,
                        'products': ['product-2'],
                    },
                ],
                'revision': revision,
            },
        ]


# Проверяем что возвращается комбо для продуктов
# подходящие по options_to_select и is_select_unique
@pytest.mark.parametrize(
    'product_groups,products,combos_count',
    [
        pytest.param(
            [
                mock_pigeon.get_combo_group(
                    options_to_select=1,
                    is_select_unique=False,
                    products=['pigeon-product-1'],
                ),
                mock_pigeon.get_combo_group(
                    options_to_select=1,
                    is_select_unique=True,
                    products=['pigeon-product-2'],
                ),
            ],
            [
                {'product_id': 'product-1', 'quantity': 2},
                {'product_id': 'product-2', 'quantity': 2},
            ],
            1,
            id='single selection in group',
        ),
        pytest.param(
            [
                mock_pigeon.get_combo_group(
                    options_to_select=2,
                    is_select_unique=False,
                    products=['pigeon-product-1', 'pigeon-product-2'],
                ),
            ],
            [{'product_id': 'product-1', 'quantity': 2}],
            1,
            id='non unique selection',
        ),
        pytest.param(
            [
                mock_pigeon.get_combo_group(
                    options_to_select=1,
                    is_select_unique=True,
                    products=['pigeon-product-1', 'pigeon-product-2'],
                ),
                mock_pigeon.get_combo_group(
                    options_to_select=1,
                    is_select_unique=False,
                    products=['pigeon-product-3', 'pigeon-product-4'],
                ),
            ],
            [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-3', 'quantity': 1},
            ],
            1,
            id='single selection in group',
        ),
        # not supported combo
        pytest.param(
            [
                mock_pigeon.get_combo_group(
                    options_to_select=1,
                    is_select_unique=True,
                    products=['pigeon-product-1', 'pigeon-product-2'],
                ),
                mock_pigeon.get_combo_group(
                    options_to_select=2,
                    is_select_unique=False,
                    products=['pigeon-product-3', 'pigeon-product-4'],
                ),
            ],
            [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-3', 'quantity': 2},
            ],
            0,
            id='not unique choice',
        ),
        # not supported combo
        pytest.param(
            [
                mock_pigeon.get_combo_group(
                    options_to_select=1,
                    is_select_unique=True,
                    products=['pigeon-product-1', 'pigeon-product-2'],
                ),
                mock_pigeon.get_combo_group(
                    options_to_select=2,
                    is_select_unique=True,
                    products=['pigeon-product-3', 'pigeon-product-4'],
                ),
            ],
            [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-3', 'quantity': 2},
                {'product_id': 'product-4', 'quantity': 1},
            ],
            0,
            id='unique choice',
        ),
        # not supported combo
        pytest.param(
            [
                mock_pigeon.get_combo_group(
                    options_to_select=1,
                    is_select_unique=True,
                    products=['pigeon-product-1', 'pigeon-product-2'],
                ),
                mock_pigeon.get_combo_group(
                    options_to_select=2,
                    is_select_unique=False,
                    products=['pigeon-product-3', 'pigeon-product-4'],
                ),
            ],
            [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-3', 'quantity': 1},
            ],
            0,
            id='no combo with not unique choice',
        ),
        # not supported combo
        pytest.param(
            [
                mock_pigeon.get_combo_group(
                    options_to_select=1,
                    is_select_unique=True,
                    products=['pigeon-product-1', 'pigeon-product-2'],
                ),
                mock_pigeon.get_combo_group(
                    options_to_select=2,
                    is_select_unique=True,
                    products=['pigeon-product-3', 'pigeon-product-4'],
                ),
            ],
            [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-3', 'quantity': 3},
            ],
            0,
            id='no combo with unique choice',
        ),
    ],
)
async def test_combo_selected_by_options(
        taxi_grocery_menu,
        pigeon,
        combos_count,
        products,
        product_groups,
        overlord_catalog,
):
    combo_id = 'combo_1'
    revision = 'combo_revision'
    _add_products(
        ['product-1', 'product-2', 'product-3', 'product-4'], overlord_catalog,
    )
    pigeon.add_combo_product(
        combo_id=combo_id, revision=revision, product_groups=product_groups,
    )

    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/combo-products/selected',
        json={'products': products},
    )
    assert response.status_code == 200
    assert len(response.json()['combo_products']) == combos_count


# Проверяем что возвращаются только подходящие комбо
@pytest.mark.parametrize(
    'products,expected_combos',
    [
        pytest.param(
            [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-3', 'quantity': 1},
            ],
            ['combo_1'],
            id='first combo in response',
        ),
        pytest.param(
            [
                {'product_id': 'product-5', 'quantity': 1},
                {'product_id': 'product-7', 'quantity': 1},
            ],
            ['combo_2'],
            id='second combo in response',
        ),
        pytest.param(
            [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-3', 'quantity': 2},
                {'product_id': 'product-5', 'quantity': 1},
                {'product_id': 'product-7', 'quantity': 1},
            ],
            ['combo_1', 'combo_2'],
            id='two combos in response',
        ),
        pytest.param(
            [
                {'product_id': 'product-1', 'quantity': 1},
                {'product_id': 'product-2', 'quantity': 1},
                {'product_id': 'product-5', 'quantity': 2},
                {'product_id': 'product-6', 'quantity': 2},
            ],
            [],
            id='no combo in response',
        ),
    ],
)
async def test_combo_selected_many_combos(
        taxi_grocery_menu, pigeon, products, expected_combos, overlord_catalog,
):
    _add_products([f'product-{i}' for i in range(1, 9)], overlord_catalog)
    pigeon.add_combo_product(
        combo_id='combo_1',
        revision='revision_1',
        product_groups=[
            mock_pigeon.get_combo_group(
                options_to_select=1,
                is_select_unique=True,
                products=['pigeon-product-1', 'pigeon-product-2'],
            ),
            mock_pigeon.get_combo_group(
                options_to_select=1,
                is_select_unique=True,
                products=['pigeon-product-3', 'pigeon-product-4'],
            ),
        ],
    )
    pigeon.add_combo_product(
        combo_id='combo_2',
        revision='revision_2',
        product_groups=[
            mock_pigeon.get_combo_group(
                options_to_select=1,
                is_select_unique=True,
                products=['pigeon-product-5', 'pigeon-product-6'],
            ),
            mock_pigeon.get_combo_group(
                options_to_select=1,
                is_select_unique=True,
                products=['pigeon-product-7', 'pigeon-product-8'],
            ),
        ],
    )

    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/combo-products/selected',
        json={'products': products},
    )
    assert response.status_code == 200
    actual_combos = []
    for combo in response.json()['combo_products']:
        actual_combos.append(combo['combo_id'])
    assert sorted(actual_combos) == sorted(expected_combos)
