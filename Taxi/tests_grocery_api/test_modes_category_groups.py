import pytest

from . import common
from . import const
from . import experiments


@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.parametrize('with_options', [False, True])
async def test_modes_category_group_200(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        offers,
        grocery_products,
        load_json,
        locale,
        with_options,
        now,
):
    """ basic test POST /lavka/v1/api/v1/modes/category-group should
    build category-group without disconts and return 200 """

    location = const.LOCATION
    depot_id = const.DEPOT_ID
    products_data = None
    if with_options:
        products_data = load_json(
            'overlord_catalog_products_data_with_options.json',
        )
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data,
        depot_id=depot_id,
    )

    layout = common.build_basic_layout(grocery_products)

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'layout_id': layout.layout_id,
        'group_id': layout.group_ids_ordered[0],
        'offer_id': offer_id,
        'additional_data': common.DEFAULT_ADDITIONAL_DATA,
    }

    headers = {}
    if locale:
        headers['Accept-Language'] = locale
        headers['User-Agent'] = common.DEFAULT_USER_AGENT

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group', json=json, headers=headers,
    )
    assert response.status_code == 200

    if not locale:
        locale = 'en'
    if with_options:
        expected_response = load_json(
            'modes_category_group_with_options_expected_response.json',
        )[locale]
    else:
        expected_response = load_json(
            'modes_category_group_expected_response.json',
        )[locale]
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'error_code,error_message',
    [
        (
            'LAYOUT_NOT_FOUND',
            'Cannot find layout in cache: layout-not-found-id',
        ),
        (
            'GROUP_NOT_FOUND',
            'Cannot find group in cache: category-group-not-found',
        ),
    ],
)
async def test_modes_category_group_404(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_products,
        error_code,
        error_message,
):
    """ basic test POST /lavka/v1/api/v1/modes/category-group should
    return 404 when layout_id of group_id not found in cache """

    overlord_catalog.add_category_tree(
        depot_id=const.DEPOT_ID,
        category_tree={
            'categories': [],
            'products': [],
            'currency': '',
            'markdown_products': [],
        },
    )
    layout_id = 'layout-not-found-id'
    if error_code != 'LAYOUT_NOT_FOUND':
        layout = grocery_products.add_layout(test_id='1')
        layout_id = layout.layout_id

    json = {
        'modes': ['grocery', 'upsale'],
        'position': {'location': const.LOCATION},
        'layout_id': layout_id,
        'group_id': 'category-group-not-found',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group', json=json,
    )
    assert response.status_code == 404
    assert response.json()['code'] == error_code
    assert response.json()['message'] == error_message


async def test_modes_category_group_depot_not_found(taxi_grocery_api):
    """ basic test POST /lavka/v1/api/v1/modes/category-group should
    return 404 when depot not found in location """

    location = [0, 0]

    json = {
        'modes': ['grocery', 'upsale'],
        'position': {'location': location},
        'layout_id': 'layout-not-found-id',
        'group_id': 'category-group-not-found',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group', json=json,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'DEPOT_NOT_FOUND'


# Ручка modes/category-group, новый способ проверки досутпности
# подкатегорий через overlord-catalog
@pytest.mark.parametrize(
    'subcategory_available,response_items', [(True, 9), (False, 6)],
)
async def test_modes_category_new_subcategories_availability(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        subcategory_available,
        response_items,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)

    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1',
        available=subcategory_available,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'layout_id': layout.layout_id,
        'group_id': layout.group_ids_ordered[0],
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group', json=json,
    )
    assert response.status_code == 200
    assert overlord_catalog.internal_categories_availability_times_called == 1
    assert len(response.json()['modes'][0]['items']) == response_items


def all_items_ids(response):
    return [item['id'] for item in response.json()['modes'][0]['items']]


@experiments.FIRST_SUBCATEGORY_DISCOUNT
async def test_first_subcategory_is_discount_with_multiple_virtual_categories(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
        grocery_p13n,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    products_data = None

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data,
        depot_id=depot_id,
    )

    layout = common.build_basic_layout(grocery_products)

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    grocery_p13n.add_modifier(product_id='product-1', value='1.1')

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'layout_id': layout.layout_id,
        'group_id': layout.group_ids_ordered[0],
        'offer_id': offer_id,
    }

    headers = {}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group', json=json, headers=headers,
    )

    assert all_items_ids(response) == [
        'virtual-category-1',
        'discounts_subcategory',
        'product-1',
        'category-1-subcategory-1',
        'product-1',
        'product-2',
        'virtual-category-2',
        'discounts_subcategory',
        'product-1',
        'category-2-subcategory-1',
        'product-1',
        'category-2-subcategory-2',
        'product-2',
    ]
    for item in response.json()['modes'][0]['items']:
        if item['id'] == 'discounts_subcategory':
            assert item['type'] == 'carousel'


@experiments.GROCERY_API_DIFFERENT_PLACES_INFORMER
async def test_modes_category_group_informers(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
):
    """ POST /lavka/v1/api/v1/modes/category-group should
    return only category-group informers """

    location = const.LOCATION
    depot_id = const.DEPOT_ID
    products_data = None
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data,
        depot_id=depot_id,
    )

    layout = common.build_basic_layout(grocery_products)

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group',
        json={
            'modes': ['grocery'],
            'position': {'location': location},
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
            'offer_id': offer_id,
        },
        headers={},
    )
    assert response.status_code == 200
    assert response.json()['informers'] == [
        {
            'text': 'Only category group',
            'show_in_root': False,
            'category_group_ids': ['category-group-1'],
            'category_ids': [],
        },
    ]


# Проверяем что на фронт попадают поля меты которые используются на беке
@pytest.mark.parametrize(
    'layout_meta,expected_properties',
    [
        (
            '{"show_as_carousels": true}',
            {
                'item_meta': {
                    'item-meta-property': 'item-meta-value-category-group-1',
                },
                'layout_meta': {'show_as_carousels': True},
            },
        ),
        (
            '{ }',
            {
                'item_meta': {
                    'item-meta-property': 'item-meta-value-category-group-1',
                },
                'layout_meta': {},
            },
        ),
    ],
)
async def test_category_group_front_meta(
        taxi_grocery_api,
        grocery_products,
        load_json,
        overlord_catalog,
        layout_meta,
        expected_properties,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    products_data = None
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data,
        depot_id=depot_id,
    )
    layout = grocery_products.add_layout(test_id='1')

    layout.add_category_group(test_id='1', layout_meta=layout_meta)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group',
        json={
            'modes': ['grocery'],
            'position': {'location': location},
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        headers={},
    )
    assert response.status_code == 200
    assert (
        response.json()['category_group']['properties'] == expected_properties
    )
