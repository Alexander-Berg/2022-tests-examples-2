import pytest

from . import const

DEFAULT_UID = 'test_uid'
# DEFAULT_DEPOT_ID = 'test-depot-id'
# DEFAULT_LOCATION = [0, 0]
DEFAULT_DEPOT_ID = const.DEPOT_ID
DEFAULT_LOCATION = const.LOCATION
DEFAULT_LEGACY_DEPOT_ID = const.LEGACY_DEPOT_ID
DEFAULT_CART_ID = '11111111-2222-aaaa-bbbb-cccdddeee002'
DEFAULT_DEVICE_POSITION = [11, 21]
DEFAULT_ADDITIONAL_DATA = {
    'cart_id': DEFAULT_CART_ID,
    'device_coordinates': {'location': DEFAULT_DEVICE_POSITION},
    'city': 'Moscow',
    'street': 'Bolshie Kamenshiki',
    'house': '8k4',
    'flat': '32',
    'comment': 'test comment',
}
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) '
'Gecko/20100101 Firefox/97.0'

DEFAULT_HEADERS = {
    'X-YaTaxi-Session': 'taxi:user_id',
    'X-Yandex-UID': DEFAULT_UID,
    'X-YaTaxi-PhoneId': 'test_phone_id',
}

HANDLERS = pytest.mark.parametrize(
    'test_handler',
    [
        pytest.param(
            '/lavka/v1/api/v1/modes/category-group', id='category_group',
        ),
        pytest.param('/lavka/v1/api/v1/modes/category', id='category'),
    ],
)

CASHBACK_ANNIHILATION_ENABLED = pytest.mark.config(
    GROCERY_API_CASHBACK_ANNIHILATION_ENABLED=True,
)
CASHBACK_ANNIHILATION_DISABLED = pytest.mark.config(
    GROCERY_API_CASHBACK_ANNIHILATION_ENABLED=False,
)

STICKERS_INFO_CONFIG = pytest.mark.config(
    GROCERY_API_STICKERS_INFO={
        'sticker_id_1': {'sticker_color': 'yellow', 'text_color': 'white'},
        'sticker_id_2': {'sticker_color': 'black', 'text_color': 'white'},
    },
)


def prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location=None,
        products_data=None,
        product_stocks=None,
        depot_id=None,
        currency='RUB',
        legacy_depot_id=None,
        category_tree=None,
        categories_data=None,
        country_iso3='RUS',
        region_id=213,
):
    if location is None:
        location = DEFAULT_LOCATION

    if depot_id is None:
        depot_id = DEFAULT_DEPOT_ID
    if legacy_depot_id is None:
        legacy_depot_id = DEFAULT_LEGACY_DEPOT_ID

    overlord_catalog.clear()

    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id,
        depot_id=depot_id,
        currency=currency,
        country_iso3=country_iso3,
        region_id=region_id,
    )
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )

    if category_tree is None:
        category_tree = load_json(
            'overlord_catalog_category_tree_response.json',
        )
    overlord_catalog.add_category_tree(
        depot_id=depot_id, category_tree=category_tree,
    )

    if categories_data is None:
        categories_data = load_json('overlord_catalog_categories_data.json')
    overlord_catalog.add_categories_data(new_categories_data=categories_data)
    if products_data is None:
        products_data = load_json('overlord_catalog_products_data.json')
    overlord_catalog.add_products_data(new_products_data=products_data)
    if product_stocks is None:
        product_stocks = load_json('overlord_catalog_products_stocks.json')
    overlord_catalog.add_products_stocks(
        depot_id=depot_id, new_products_stocks=product_stocks,
    )


def build_basic_layout(grocery_products, layout_test_id='1'):
    layout = grocery_products.add_layout(test_id=layout_test_id)

    category_group_1 = layout.add_category_group(test_id='1')

    virtual_category_1 = category_group_1.add_virtual_category(
        test_id='1', add_short_title=True,
    )
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    virtual_category_2 = category_group_1.add_virtual_category(test_id='2')
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-2',
    )
    return layout


def build_grocery_mode_request(
        handler,
        layout_id,
        group_id,
        category_id,
        product_id=None,
        query=None,
        location=None,
):
    if location is None:
        location = DEFAULT_LOCATION
    if 'category-group' in handler:
        return {
            'modes': ['grocery'],
            'position': {'location': location},
            'layout_id': layout_id,
            'group_id': group_id,
            'offer_id': 'some-offer-id',
        }
    if 'category' in handler:
        return {
            'modes': ['grocery'],
            'position': {'location': location},
            'category_path': {'layout_id': layout_id, 'group_id': group_id},
            'category_id': category_id,
            'offer_id': 'some-offer-id',
        }
    if 'product' in handler:
        return {'product_id': product_id, 'position': {'location': location}}
    if 'search' in handler:
        return {'text': query, 'position': {'location': location}}
    # modes/root
    return {'modes': ['grocery'], 'position': {'location': location}}


def build_tree(category_tree, product_prices=None, parent_products=None):
    categories = {}
    products = {}
    for category_idx, category in enumerate(category_tree):
        categories[category['id']] = {'id': category['id']}
        for product_idx, product_id in enumerate(category['products']):
            if product_id in products:
                products[product_id]['category_ids'].append(category['id'])
            else:
                products[product_id] = {
                    'full_price': '123.456',
                    'id': product_id,
                    'category_ids': [category['id']],
                    'rank': category_idx * 10 + product_idx,
                }

    if parent_products is not None:
        for parent_id, children in parent_products.items():
            for child_id in children:
                if child_id in products:
                    products[child_id]['parent_id'] = parent_id

    if product_prices is not None:
        for item in product_prices:
            if item['id'] in products:
                products[item['id']]['full_price'] = item['price']

    return {
        'categories': list(categories.values()),
        'products': list(products.values()),
        'markdown_products': [],
    }


def build_empty_tree():
    return build_tree(category_tree=[])


def prepare_overlord_catalog(
        overlord_catalog,
        location,
        depot_id=const.DEPOT_ID,
        category_tree=None,
        product_stocks=None,
        legacy_depot_id=const.LEGACY_DEPOT_ID,
):
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    overlord_catalog.add_depot(
        depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    if category_tree is None:
        category_tree = build_empty_tree()
    overlord_catalog.add_category_tree(
        depot_id=depot_id, category_tree=category_tree,
    )
    if product_stocks:
        overlord_catalog.add_products_stocks(
            depot_id=depot_id, new_products_stocks=product_stocks,
        )


def build_overlord_catalog_products(
        overlord_catalog,
        tree,
        product_prices=None,
        parent_products=None,
        master_categories=None,
):
    category_tree = build_tree(tree, product_prices, parent_products)
    overlord_catalog.add_category_tree(
        depot_id=DEFAULT_DEPOT_ID, category_tree=category_tree,
    )

    if master_categories is None:
        master_categories = {}

    for subcategory in tree:
        overlord_catalog.add_categories_data(
            new_categories_data=[
                {
                    'category_id': subcategory['id'],
                    'description': subcategory['id'] + 'description',
                    'image_url_template': subcategory['id'] + 'image',
                    'title': subcategory['id'] + 'title',
                },
            ],
        )
        for product in subcategory['products']:
            product_master_categories = master_categories.get(product, None)
            overlord_catalog.add_products_data(
                new_products_data=[
                    {
                        'description': 'product-description',
                        'image_url_template': 'product-image-url-template',
                        'long_title': 'product-long-title',
                        'product_id': product,
                        'title': 'product-title',
                        **(
                            {'master_categories': product_master_categories}
                            if product_master_categories
                            else {}
                        ),
                    },
                ],
            )
            overlord_catalog.add_products_stocks(
                depot_id=DEFAULT_DEPOT_ID,
                new_products_stocks=[
                    {
                        'in_stock': '10',
                        'product_id': product,
                        'quantity_limit': '5',
                    },
                ],
            )


def setup_hide_if_tests(
        overlord_catalog,
        grocery_products,
        location,
        category_tree,
        stocks,
        virtual_category_item_meta,
):
    depot_id = const.DEPOT_ID

    overlord_category_tree = build_tree(category_tree)
    product_stocks = []
    for product_id, in_stock in stocks.items():
        product_stocks.append(
            {
                'in_stock': in_stock,
                'product_id': product_id,
                'quantity_limit': in_stock,
            },
        )

    prepare_overlord_catalog(
        overlord_catalog,
        location,
        depot_id=depot_id,
        category_tree=overlord_category_tree,
        product_stocks=product_stocks,
    )
    for category_data in category_tree:
        for product_id in category_data['products']:
            if product_id in stocks:
                overlord_catalog.set_category_availability(
                    category_id=category_data['id'],
                    available=int(stocks[product_id]) > 0,
                )

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')

    virtual_category = category_group.add_virtual_category(
        test_id='1',
        add_short_title=True,
        item_meta=virtual_category_item_meta,
    )
    for item in category_tree:
        virtual_category.add_subcategory(subcategory_id=item['id'])

    return virtual_category


def setup_catalog_for_paths_test(
        overlord_catalog, grocery_products, product_id,
):
    tree = [
        {'id': 'subcategory-1', 'products': [product_id]},
        {'id': 'subcategory-2', 'products': [product_id]},
        {'id': 'subcategory-3', 'products': [product_id]},
    ]
    build_overlord_catalog_products(overlord_catalog, tree)

    layout_1 = grocery_products.add_layout(test_id='1')
    category_group_1 = layout_1.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(test_id='1')
    virtual_category_2 = category_group_1.add_virtual_category(test_id='2')

    layout_2 = grocery_products.add_layout(test_id='2')
    category_group_2 = layout_2.add_category_group(test_id='2')
    virtual_category_3 = category_group_2.add_virtual_category(test_id='3')

    virtual_category_1.add_subcategory(subcategory_id='subcategory-1')
    virtual_category_1.add_subcategory(subcategory_id='subcategory-2')

    virtual_category_2.add_subcategory(subcategory_id='subcategory-1')

    virtual_category_3.add_subcategory(subcategory_id='subcategory-3')


def check_catalog_paths(catalog_paths, layout_id):
    assert layout_id in ['layout-1', 'layout-2']
    if layout_id == 'layout-1':
        assert len(catalog_paths) == 3
        catalog_paths.sort(
            key=lambda item: (
                item['subcategory']['id'],
                item['category']['id'],
            ),
        )
        expected_ids = [
            ('subcategory-1', 'virtual-category-1'),
            ('subcategory-1', 'virtual-category-2'),
            ('subcategory-2', 'virtual-category-1'),
        ]
        for path, ids in zip(catalog_paths, expected_ids):
            assert (path['subcategory']['id'], path['category']['id']) == ids
    else:
        assert len(catalog_paths) == 1
        assert (
            catalog_paths[0]['subcategory']['id'],
            catalog_paths[0]['category']['id'],
        ) == ('subcategory-3', 'virtual-category-3')


def default_on_modifiers_request(orders_count=None, has_parcels=None):
    def _inner(headers, body):
        if orders_count is not None:
            assert body['orders_count'] == orders_count
        if has_parcels:
            assert body['has_parcels']
        return True

    return _inner
