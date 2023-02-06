# pylint: disable=too-many-lines

import datetime

import pytest

from . import common
from . import conftest
from . import const
from . import experiments
from . import tests_headers

NOW = datetime.datetime.fromisoformat('2020-09-09T10:00:00+00:00')


def build_grocery_products_data(grocery_products, layout_id='1'):
    layout = grocery_products.add_layout(test_id=layout_id)

    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_2 = category_group_1.add_virtual_category(
        test_id='2', item_meta='{"special_item_meta_param": 123}',
    )
    virtual_category_2.add_image(dimensions=[{'width': 4, 'height': 2}])
    virtual_category_2.add_subcategory(subcategory_id='category-1')
    virtual_category_2.add_subcategory(subcategory_id='category-2')

    category_group_1.add_virtual_category(
        test_id='1', layout_meta='{"special_layout_meta_param": 456}',
    )

    category_group_no_images = layout.add_category_group(
        test_id='no-images', image='',
    )
    virtual_category_3 = category_group_no_images.add_virtual_category(
        test_id='3',
    )
    virtual_category_3.add_image(dimensions=[{'width': 6, 'height': 2}])

    layout.add_category_group(test_id='3')

    category_group_2 = layout.add_category_group(test_id='2')
    virtual_category_no_images = category_group_2.add_virtual_category(
        test_id='no-images',
    )
    virtual_category_no_images.add_image(
        image='', dimensions=[{'width': 4, 'height': 2}],
    )

    virtual_category_no_subs = category_group_2.add_virtual_category(
        test_id='no-subs',
    )
    virtual_category_no_subs.add_image(dimensions=[{'width': 6, 'height': 2}])

    virtual_category_alt_image = category_group_2.add_virtual_category(
        test_id='1',
    )
    virtual_category_alt_image.add_image(
        image='alternative_image.jpg', dimensions=[{'width': 2, 'height': 2}],
    )

    category_group_short_title = layout.add_category_group(
        test_id='short-title', add_short_title=True,
    )
    virtual_category_short_title = (
        category_group_short_title.add_virtual_category(
            test_id='short-title', add_short_title=True,
        )
    )
    virtual_category_short_title.add_image(
        dimensions=[{'width': 4, 'height': 2}],
    )


# POST /lavka/v1/api/v1/modes/root
# Заворачивает сетку, полученную от grocery-products, для отображения на
# фронте.
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('locale', [None, 'ru', 'en'])
@pytest.mark.parametrize('fallback_locale', ['ru', 'en'])
@conftest.DIFFERENT_LAYOUT_SOURCE
async def test_modes_root_wraps_layout_from_grocery_products(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_products,
        load_json,
        locale,
        fallback_locale,
        taxi_config,
):
    taxi_config.set(
        GROCERY_LOCALIZATION_FALLBACK_LANGUAGES={
            '__default__': fallback_locale,
        },
    )

    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)
    build_grocery_products_data(grocery_products)

    json = {'modes': ['grocery', 'upsale'], 'position': {'location': location}}

    headers = {}
    if locale:
        headers['Accept-Language'] = locale

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json, headers=headers,
    )
    assert response.status_code == 200

    if not locale:
        locale = fallback_locale
    expected_response = load_json('modes_root_layout_expected_response.json')[
        locale
    ]
    assert response.json() == expected_response


# POST /lavka/v1/api/v1/modes/root
# Пробрасывает входной параметр offer_id без изменения, если он успешно найден,
# и создаёт новый, если не найден.
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('matched', [True, False])
async def test_modes_root_forwards_offer_id(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        matched,
        now,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID

    common.prepare_overlord_catalog(
        overlord_catalog, location, depot_id=depot_id,
    )
    build_grocery_products_data(grocery_products)

    offer_id = 'some-offer-id'
    if matched:
        offers.add_offer_elementwise(offer_id, now, depot_id, location)

    json = {
        'modes': ['grocery', 'upsale'],
        'offer_id': offer_id,
        'position': {'location': location},
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200
    assert (response.json()['offer_id'] == offer_id) == matched


# POST /lavka/v1/api/v1/modes/root
# Возвращает 404, если лавка не нашлась.
@pytest.mark.parametrize(
    'location_resolve',
    [
        pytest.param(False, id='Unknown location'),
        pytest.param(True, id='Depot is not in cache'),
    ],
)
async def test_modes_root_returns_404_if_depot_is_not_found(
        overlord_catalog, taxi_grocery_api, location_resolve,
):
    location = [0, 0]
    dummy_legacy_id = '456'

    if location_resolve:
        overlord_catalog.add_location(
            location=location,
            depot_id='dummy_id',
            legacy_depot_id=dummy_legacy_id,
        )

    json = {'modes': ['grocery', 'upsale'], 'position': {'location': location}}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'DEPOT_NOT_FOUND'


# POST /lavka/v1/api/v1/modes/root
# Experiment is not available.
async def test_modes_root_returns_404_without_experiment(
        overlord_catalog, taxi_grocery_api, mockserver,
):
    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)

    json = {'modes': ['grocery'], 'position': {'location': location}}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'LAYOUT_NOT_FOUND'


# POST /lavka/v1/api/v1/modes/root
# No layout in grocery-products.
@experiments.MODES_ROOT_LAYOUT_ENABLED
@conftest.DIFFERENT_LAYOUT_SOURCE
async def test_modes_root_returns_404_layout_not_in_grocery_products(
        overlord_catalog, taxi_grocery_api, mockserver,
):
    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)

    json = {'modes': ['grocery'], 'position': {'location': location}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'LAYOUT_NOT_FOUND'


# POST /lavka/v1/api/v1/modes/root
# Берёт id сетки из эксперимента.
@pytest.mark.experiments3(filename='modes_root_layout_experiment.json')
@pytest.mark.parametrize(
    'legacy_depot_id,country,region_id,location,modes,exp_layout_id',
    [
        pytest.param(
            '100',
            'RUS',
            10,
            [10, 10],
            ['grocery'],
            '1',
            id='match by place id',
        ),
        pytest.param(
            '301',
            'GBR',
            20,
            [20, 20],
            ['grocery'],
            '2',
            id='match by country',
        ),
        pytest.param(
            '300',
            'RUS',
            30,
            [30, 30],
            ['grocery'],
            '3',
            id='match by region id',
        ),
        pytest.param(
            '400',
            'RUS',
            40,
            [40, 40],
            ['grocery-preview'],
            '4',
            id='match by preview mode',
        ),
        pytest.param(
            '500',
            'RUS',
            50,
            [50, 50],
            ['grocery'],
            'default',
            id='fallback to default',
        ),
    ],
)
@conftest.DIFFERENT_LAYOUT_SOURCE
async def test_modes_root_with_experiment(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        legacy_depot_id,
        country,
        region_id,
        location,
        modes,
        exp_layout_id,
        grocery_depots,
):
    depot_id = 'dummy_id'

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        country_iso3=country,
        region_id=region_id,
    )

    overlord_catalog.clear()

    overlord_catalog.add_depot(
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
        country_iso3=country,
        region_id=region_id,
    )
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )

    overlord_catalog.add_category_tree(
        depot_id=depot_id, category_tree=common.build_empty_tree(),
    )
    build_grocery_products_data(grocery_products, layout_id=exp_layout_id)

    await taxi_grocery_api.invalidate_caches()

    json = {'modes': modes, 'position': {'location': location}}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200


# POST /lavka/v1/api/v1/modes/root
# Id сетки для юзеров с одним заказом ровно
@pytest.mark.experiments3(filename='modes_root_layout_experiment.json')
@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_api_catalog': {
            'tag': 'total_paid_orders_count',
            'payment_id_divisor': 3,
        },
    },
)
@pytest.mark.parametrize(
    'total_orders_count,payment_id_orders_count',
    [(1, None), (None, 3), (0, 3)],
)
async def test_modes_root_for_new_users(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_marketing,
        total_orders_count,
        payment_id_orders_count,
        grocery_depots,
):
    depot_id = 'dummy_id'
    legacy_depot_id = '400'
    country = 'RUS'
    region_id = 40
    location = [40, 40]

    layout_id = '2'
    yandex_uid = '1236281'
    payment_id = '1'

    if total_orders_count is not None:
        grocery_marketing.add_user_tag(
            tag_name='total_paid_orders_count',
            usage_count=total_orders_count,
            user_id=yandex_uid,
        )
    if payment_id_orders_count is not None:
        grocery_marketing.add_payment_id_tag(
            tag_name='total_paid_orders_count',
            usage_count=payment_id_orders_count,
            payment_id=payment_id,
        )

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        country_iso3=country,
        region_id=region_id,
    )

    overlord_catalog.clear()
    overlord_catalog.add_depot(
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
        country_iso3=country,
        region_id=region_id,
    )
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    overlord_catalog.add_category_tree(
        depot_id=depot_id, category_tree=common.build_empty_tree(),
    )
    build_grocery_products_data(grocery_products, layout_id=layout_id)

    await taxi_grocery_api.invalidate_caches()

    json = {
        'modes': ['grocery'],
        'current_payment_method': {'type': 'card', 'id': payment_id},
        'position': {'location': location},
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={'X-Yandex-UID': yandex_uid, 'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json()['layout_id'] == 'layout-2'

    assert grocery_marketing.retrieve_v2_times_called == 1


# POST /lavka/v1/api/v1/modes/root
# Возвращает в полях метаданных сообщение об ошибке при неудачной проверке
#  корректности JSON в метаинформации в сетке, полученной из grocery-products
#  (проверка проводится для каждого из полей с метаданными)
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_modes_root_returns_errors_for_bad_meta_in_grocery_products(
        taxi_grocery_api, overlord_catalog, grocery_products, testpoint,
):
    bad_meta_scalar = ['123', 'true']

    @testpoint('parse_json_expected_object')
    def parse_json_expected_object(data):
        assert data['str'] in bad_meta_scalar

    bad_meta = ['{ bad-meta }', '"{"bad-meta": "bad-meta"}"']

    @testpoint('parse_json_failure')
    def parse_json_failure(data):
        assert data['str'] in bad_meta

    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(
        test_id='bad-meta', item_meta=bad_meta[0], layout_meta=bad_meta[1],
    )
    category_group = layout.add_category_group(
        test_id='bad-meta-2',
        item_meta=bad_meta_scalar[0],
        layout_meta=bad_meta_scalar[1],
    )
    category_group.add_virtual_category(
        test_id='1', item_meta='{"enabled": true}',
    )

    json = {'modes': ['grocery'], 'position': {'location': location}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200
    assert parse_json_failure.times_called == 2
    assert parse_json_expected_object.times_called == 2


# Проверяем, что специальные виртуальные категории могут не попасть в
# выдачу ручки. Они могут не попасть, если в мете указано "enabled = false",
# либо другая, специфичная для категории валидация не сработала. Тестируется
# специальная категория - "уцененные товары", внутрення валидация которой
# основана на эксперименте.
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.experiments3(
    name='lavka_selloncogs',
    consumers=['grocery-caas/client_library'],
    clauses=[
        {
            'title': 'match phone id',
            'predicate': {
                'init': {
                    'value': 'test_phone_id',
                    'arg_name': 'phone_id',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize(
    'phone_id,should_match',
    (
        pytest.param('test_phone_id', True, id='match'),
        pytest.param('test_phone_id_1', False, id='no-match'),
    ),
)
async def test_modes_root_special_category(
        taxi_grocery_api,
        grocery_products,
        overlord_catalog,
        phone_id,
        should_match,
):
    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    category_group.add_virtual_category(
        test_id='1', special_category='markdown',
    )

    json = {'modes': ['grocery'], 'position': {'location': location}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={'X-YaTaxi-PhoneId': phone_id},
    )
    assert response.status_code == 200
    body = response.json()

    if should_match:
        # group+category
        assert len(body['products']) == 2
        assert len(body['modes'][0]['items']) == 2
    else:
        # only group
        assert not body['products']
        assert not body['modes'][0]['items']


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'layout_width,category_width',
    [(None, 6), (2, 2), (4, 4), (6, 6), (10, 6)],
)
async def test_modes_root_stretch_category_layout_width(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        layout_width,
        category_width,
):
    """ Checks that category stretching up to layout width """

    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)

    meta = '{}'
    if layout_width is not None:
        meta = '{' + f'"width": {layout_width}' + '}'

    layout = grocery_products.add_layout(test_id='1', meta=meta)
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(test_id='1')
    virtual_category.add_image(
        image='image-vc-1-2x2', dimensions=[{'width': 2, 'height': 2}],
    )
    virtual_category.add_image(
        image='image-vc-1-4x2', dimensions=[{'width': 4, 'height': 2}],
    )
    virtual_category.add_image(
        image='image-vc-1-6x2', dimensions=[{'width': 6, 'height': 2}],
    )

    json = {'modes': ['grocery'], 'position': {'location': location}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200

    response_json = response.json()

    grocery_mode = response_json['modes'][0]
    assert grocery_mode['mode'] == 'grocery'
    assert grocery_mode['items'][1]['width'] == category_width

    assert (
        response_json['products'][1]['image_url_template']
        == f'image-vc-1-{category_width}x2'
    )


@pytest.mark.parametrize(
    'stretch_priority,width', [(None, [2, 4]), (0, [2, 4]), (10, [4, 2])],
)
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_modes_root_stretch_categories(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        stretch_priority,
        width,
):
    """ Checks that categories stretching according to the stretch_priority """

    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)

    layout_meta = '{}'
    if stretch_priority is not None:
        layout_meta = '{' + f'"stretch_priority": {stretch_priority}' + '}'

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(
        test_id='1', layout_meta=layout_meta,
    )
    virtual_category_1.add_image(
        image='image-vc-1-2x2', dimensions=[{'width': 2, 'height': 2}],
    )
    virtual_category_1.add_image(
        image='image-vc-1-4x2', dimensions=[{'width': 4, 'height': 2}],
    )

    virtual_category_2 = category_group_1.add_virtual_category(
        test_id='2', layout_meta='{"stretch_priority": 5}',
    )
    virtual_category_2.add_image(
        image='image-vc-2-2x2', dimensions=[{'width': 2, 'height': 2}],
    )
    virtual_category_2.add_image(
        image='image-vc-2-4x2', dimensions=[{'width': 4, 'height': 2}],
    )

    json = {'modes': ['grocery'], 'position': {'location': location}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200

    response_json = response.json()

    grocery_mode = response_json['modes'][0]
    assert grocery_mode['mode'] == 'grocery'
    assert grocery_mode['items'][1]['width'] == width[0]
    assert grocery_mode['items'][2]['width'] == width[1]

    assert (
        response_json['products'][1]['image_url_template']
        == f'image-vc-1-{width[0]}x2'
    )
    assert (
        response_json['products'][2]['image_url_template']
        == f'image-vc-2-{width[1]}x2'
    )


@pytest.mark.parametrize(
    'stretch_priority,width', [(None, [2, 4]), (0, [2, 4]), (10, [4, 2])],
)
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_modes_root_stretch_categories_multi(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        stretch_priority,
        width,
):
    """ Checks that multi dimensional images working properly """

    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)

    layout_meta = '{}'
    if stretch_priority is not None:
        layout_meta = '{' + f'"stretch_priority": {stretch_priority}' + '}'

    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(
        test_id='1', layout_meta=layout_meta,
    )
    virtual_category_1.add_image(
        image='image-vc-1-multi',
        dimensions=[{'width': 2, 'height': 2}, {'width': 4, 'height': 2}],
    )

    virtual_category_2 = category_group_1.add_virtual_category(
        test_id='2', layout_meta='{"stretch_priority": 5}',
    )
    virtual_category_2.add_image(
        image='image-vc-2-multi',
        dimensions=[
            {'width': 2, 'height': 2},
            {'width': 3, 'height': 2},
            {'width': 4, 'height': 2},
            {'width': 6, 'height': 2},
        ],
    )

    json = {'modes': ['grocery'], 'position': {'location': location}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200

    response_json = response.json()

    grocery_mode = response_json['modes'][0]
    assert grocery_mode['mode'] == 'grocery'
    assert grocery_mode['items'][1]['width'] == width[0]
    assert grocery_mode['items'][2]['width'] == width[1]

    assert (
        response_json['products'][1]['image_url_template']
        == f'image-vc-1-multi'
    )
    assert (
        response_json['products'][2]['image_url_template']
        == f'image-vc-2-multi'
    )


@pytest.mark.config(GROCERY_API_RETRIEVE_STOCKS_LIMIT=3)
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'products_count,expected_times_called',
    [
        pytest.param(1, 1, id='one_product'),
        pytest.param(0, 0, id='no_products'),
        pytest.param(7, 3, id='indivisible'),
        pytest.param(9, 3, id='divisible'),
    ],
)
async def test_modes_root_get_stocks_by_parts(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        taxi_config,
        mockserver,
        products_count,
        expected_times_called,
):
    @mockserver.json_handler('overlord-catalog/internal/v1/catalog/v1/stocks')
    def mock_stocks(request):
        return {
            'stocks': [
                {
                    'product_id': request.json['product_ids'][i],
                    'in_stock': '10',
                    'quantity_limit': '10',
                }
                for i in range(len(request.json['product_ids']))
            ],
        }

    subcategory_id = 'category-1'
    location = const.LOCATION
    products = ['product_id_{}'.format(i) for i in range(products_count)]
    category_tree = common.build_tree(
        [{'id': subcategory_id, 'products': products}],
    )
    product_stocks = []
    common.prepare_overlord_catalog(
        overlord_catalog,
        location,
        category_tree=category_tree,
        product_stocks=product_stocks,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    products = ['"product_id_{}"'.format(i) for i in range(products_count)]
    products = '[' + ','.join(products) + ']'
    item_meta = '{"hide_if_all_products_are_missing":' + products + '}'
    virtual_category = category_group.add_virtual_category(
        test_id='1',
        alias='test-category',
        add_short_title=True,
        item_meta=item_meta,
    )
    virtual_category.add_subcategory(subcategory_id=subcategory_id)

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )

    assert response.status_code == 200
    assert mock_stocks.times_called == expected_times_called


# POST /lavka/v1/api/v1/modes/root
# При наличии в item_meta группы флага show_as_carousels,
# отправляем все категории этой группы в виде каруселей.
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[experiments.parent_products_exp(True)], id='parent enabled',
        ),
        pytest.param(
            marks=[experiments.parent_products_exp(False)],
            id='parent disabled',
        ),
    ],
)
async def test_modes_root_show_as_carousels(
        taxi_grocery_api, overlord_catalog, grocery_products, load_json,
):
    location = const.LOCATION

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {
                'id': 'category-1',
                'products': ['product-1', 'product-2', 'product-3'],
            },
            {'id': 'category-2', 'products': ['product-4', 'product-5']},
        ],
    )

    build_grocery_products_data(grocery_products)

    layout_1 = grocery_products.get_layout('layout-1')
    group_1 = layout_1.groups['category-group-1']
    group_1.layout_meta = (
        group_1.layout_meta[:-1]
        + f', "show_as_carousels": true'
        + f', "products_per_category_count": {5}'
        + '}'
    )

    json = {'modes': ['grocery'], 'position': {'location': location}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200

    expected_products = load_json(
        'modes_root_layout_carousels_expected_response.json',
    )['products']
    products = [product['id'] for product in response.json()['products']]
    assert products == expected_products


@pytest.mark.now(NOW.isoformat())
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.experiments3(filename='surge_exp_delivery.json')
async def test_modes_root_offer_additional_info_check_logged(
        taxi_grocery_api,
        grocery_products,
        overlord_catalog,
        grocery_surge,
        grocery_marketing,
        offers,
        testpoint,
):
    """ /modes/root should save additional info for new offer_id """

    location = const.LOCATION
    lat_lon_str = str(float(location[1])) + ';' + str(float(location[0]))
    legacy_depot_id = const.LEGACY_DEPOT_ID
    depot_id = const.DEPOT_ID

    common.prepare_overlord_catalog(
        overlord_catalog,
        location,
        depot_id=depot_id,
        # legacy_depot_id=legacy_depot_id,
    )
    build_grocery_products_data(grocery_products)

    timestamp = NOW.isoformat()
    grocery_surge.add_record(
        legacy_depot_id=legacy_depot_id,
        timestamp=timestamp,
        pipeline='calc_surge_grocery_v1',
        load_level=4,
    )

    await taxi_grocery_api.invalidate_caches(
        cache_names=['grocery-surge-cache'],
    )

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, NOW, depot_id, location)

    user_id = '123456abcd'

    @testpoint('yt_offer_additional_info')
    def yt_offer_additional_info(offer_additional_info):
        assert offer_additional_info['offer_id'] == offer_id
        assert offer_additional_info['version'] == 1
        assert offer_additional_info['doc'] == {
            'active_zone': 'foot',
            'foot': {
                'delivery_cost': '199',
                'is_surge': True,
                'is_manual': False,
                'max_eta_minutes': '23',
                'min_eta_minutes': '12',
                'next_delivery_cost': '0',
                'next_delivery_threshold': '1300',
                'surge_minimum_order': '0',
                'delivery_conditions': [
                    {'order_cost': '0', 'delivery_cost': '199'},
                    {'order_cost': '1300', 'delivery_cost': '0'},
                ],
            },
        }
        assert offer_additional_info['params'] == {
            'lat_lon': lat_lon_str,
            'depot_id': legacy_depot_id,
        }
        assert offer_additional_info['user_id'] == user_id

    json = {
        'offer_id': 'some-offer-id',
        'modes': ['grocery'],
        'position': {'location': location},
    }
    headers = {'X-Yandex-UID': '1234567', 'X-YaTaxi-UserId': user_id}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert yt_offer_additional_info.times_called == 1
    assert grocery_marketing.retrieve_v2_times_called == 1


@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_modes_root_grocery_marketing_500(
        taxi_grocery_api, mockserver, grocery_products, overlord_catalog,
):
    """ grocery-marketing fail should not affect /modes/root """

    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)
    build_grocery_products_data(grocery_products)

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def _grocery_marketing_fail(request):
        return mockserver.make_response('Something went wrong', status=500)

    json = {'modes': ['grocery'], 'position': {'location': location}}
    headers = {'X-Yandex-UID': '1234567'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert _grocery_marketing_fail.has_calls is True


# POST /lavka/v1/api/v1/modes/root
# Только если специальная категория находится в группе
# которая должная быть отрисована как карусель,
# мы запрашиваем ее содержимое
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.UPSALE_EXPERIMENT
@pytest.mark.parametrize('special_category_is_carousel', [True, False])
async def test_modes_root_show_as_carousels_with_special_categories(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_upsale,
        load_json,
        special_category_is_carousel,
):
    upsale_products = ['product-1', 'product-2']
    grocery_upsale.add_products(upsale_products)

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {
                'id': 'category-1',
                'products': ['product-1', 'product-2', 'product-3'],
            },
            {'id': 'category-2', 'products': ['product-4', 'product-5']},
        ],
    )

    build_grocery_products_data(grocery_products)
    layout_1 = grocery_products.get_layout('layout-1')
    group_1 = layout_1.groups['category-group-1']
    group_1.layout_meta = (
        group_1.layout_meta[:-1]
        + f', "show_as_carousels": true'
        + f', "products_per_category_count": {5}'
        + '}'
    )
    special_category_group = layout_1.add_category_group(test_id='upsale')
    if special_category_is_carousel:
        special_category_group.layout_meta = (
            special_category_group.layout_meta[:-1]
            + f', "show_as_carousels": true'
            + f', "products_per_category_count": {5}'
            + '}'
        )
    special_category_group.add_virtual_category(
        test_id='upsale', special_category='upsale',
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': common.DEFAULT_LOCATION},
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200

    expected_products = load_json(
        'modes_root_layout_carousels_expected_response.json',
    )['products'] + ['category-group-upsale', 'virtual-category-upsale']
    if special_category_is_carousel:
        expected_products = expected_products + upsale_products

    products = [product['id'] for product in response.json()['products']]
    assert products == expected_products
    assert grocery_upsale.times_called == (
        1 if special_category_is_carousel else 0
    )


# проверяем что запрос в скидки идет с мастер категориями
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud, '
    'antifraud_user_profile_tagged, is_fraud_in_user_profile',
    [
        pytest.param(
            False,
            True,
            False,
            False,
            marks=experiments.ANTIFRAUD_CHECK_DISABLED,
        ),
        pytest.param(
            True,
            False,
            False,
            True,
            marks=experiments.ANTIFRAUD_CHECK_ENABLED,
        ),
        pytest.param(
            True,
            False,
            True,
            True,
            marks=experiments.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
        pytest.param(
            True,
            False,
            True,
            False,
            marks=experiments.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
        pytest.param(
            True,
            True,
            True,
            False,
            marks=experiments.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
    ],
)
async def test_modes_root_carousels_discounts_request(
        taxi_grocery_api,
        overlord_catalog,
        antifraud,
        grocery_marketing,
        grocery_user_profiles,
        grocery_p13n,
        grocery_products,
        mockserver,
        testpoint,
        antifraud_enabled,
        is_fraud,
        antifraud_user_profile_tagged,
        is_fraud_in_user_profile,
):
    location = const.LOCATION
    device_coordinates = common.DEFAULT_DEVICE_POSITION
    yandex_uid = tests_headers.HEADER_YANDEX_UID
    eats_uid = tests_headers.HEADER_EATS_ID
    personal_phone_id = 'personal-phone-id'
    appmetrica_device_id = 'appmetrica-device-id'
    user_agent = common.DEFAULT_USER_AGENT
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'
    city = 'Moscow'
    street = 'Bolshie Kamenshiki'
    house = '8k4'
    flat = '32'
    comment = 'test comment'
    payment_id = '1'
    discount_prohibited = (
        antifraud_enabled
        and is_fraud
        or antifraud_user_profile_tagged
        and is_fraud_in_user_profile
    )
    if discount_prohibited:
        orders_count_p13n = None
        orders_count_marketing = 0
    else:
        orders_count_p13n = 2
        orders_count_marketing = 2

    grocery_marketing.add_user_tag(
        'total_orders_count', orders_count_marketing, user_id=yandex_uid,
    )

    antifraud.set_is_fraud(is_fraud)
    antifraud.check_discount_antifraud(
        user_id=yandex_uid,
        user_id_service='passport',
        user_personal_phone_id=personal_phone_id,
        user_agent=user_agent,
        application_type='android',
        service_name='grocery',
        short_address=f'{city}, {street} {house} {flat}',
        address_comment=comment,
        order_coordinates={
            'lat': float(location[1]),
            'lon': float(location[0]),
        },
        device_coordinates={
            'lat': float(device_coordinates[1]),
            'lon': float(device_coordinates[0]),
        },
        payment_method_id='1',
        payment_method='card',
        user_device_id=appmetrica_device_id,
        store_id=const.LEGACY_DEPOT_ID,
        request_source='catalogue',
    )
    grocery_user_profiles.set_is_fraud(is_fraud_in_user_profile)
    grocery_user_profiles.check_info_request(
        yandex_uid=yandex_uid, personal_phone_id=personal_phone_id,
    )
    grocery_user_profiles.check_save_request(
        yandex_uid=yandex_uid,
        personal_phone_id=personal_phone_id,
        antifraud_info={'name': 'lavka_newcomer_discount_fraud'},
    )

    @testpoint('yt_discount_offer_info')
    def yt_discount_offer_info(discount_offer_info):
        assert discount_offer_info['cart_id'] == cart_id
        assert discount_offer_info['doc'] == {
            'cart_id': cart_id,
            'passport_uid': yandex_uid,
            'eats_uid': eats_uid,
            'personal_phone_id': personal_phone_id,
            'personal_email_id': '',
            'discount_allowed_by_antifraud': not discount_prohibited,
            'discount_allowed': False,
            'discount_allowed_by_rt_xaron': not (
                antifraud_enabled and is_fraud
            ),
            'discount_allowed_by_truncated_flat': True,
            'discount_allowed_by_user_profile': not (
                antifraud_user_profile_tagged and is_fraud_in_user_profile
            ),
            'usage_count': orders_count_marketing,
            'usage_count_according_to_uid': orders_count_marketing,
            'promocode_id': '',
            'promocode': '',
        }

    master_categories_1 = ['master-category-1', 'master-category-2']
    master_categories_2 = ['master-category-1', 'master-category-3']

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {
                'id': 'category-1',
                'products': ['product-1', 'product-2', 'product-3'],
            },
            {'id': 'category-2', 'products': ['product-4', 'product-5']},
        ],
        master_categories={
            'product-1': master_categories_1,
            'product-4': master_categories_2,
        },
    )

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def discount_modifiers(request):
        assert (
            sorted(
                [
                    (item['product_id'], item.get('master_categories', None))
                    for item in request.json['items']
                ],
            )
            == [
                ('product-1', master_categories_1),
                ('product-2', None),
                ('product-3', None),
                ('product-4', master_categories_2),
                ('product-5', None),
            ]
        )
        assert common.default_on_modifiers_request(orders_count_p13n)(
            request.headers, request.json,
        )
        return {'modifiers': []}

    build_grocery_products_data(grocery_products)

    layout_1 = grocery_products.get_layout('layout-1')
    group_1 = layout_1.groups['category-group-1']
    group_1.layout_meta = (
        group_1.layout_meta[:-1]
        + f', "show_as_carousels": true'
        + f', "products_per_category_count": {5}'
        + '}'
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'current_payment_method': {'type': 'card', 'id': payment_id},
        'additional_data': common.DEFAULT_ADDITIONAL_DATA,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={
            'X-Yandex-UID': yandex_uid,
            'Accept-Language': 'ru',
            'X-AppMetrica-DeviceId': appmetrica_device_id,
            'User-Agent': user_agent,
            'X-YaTaxi-User': (
                f'eats_user_id={eats_uid}, '
                f'personal_phone_id={personal_phone_id}'
            ),
            'X-Request-Application': 'app_name=android',
        },
    )
    assert response.status_code == 200
    assert discount_modifiers.times_called == 1
    assert antifraud.times_discount_antifraud_called() == int(
        antifraud_enabled,
    )
    assert grocery_user_profiles.times_antifraud_info_called() == int(
        antifraud_user_profile_tagged,
    )
    if is_fraud and not is_fraud_in_user_profile:
        assert grocery_user_profiles.times_antifraud_save_called() == int(
            antifraud_user_profile_tagged,
        )
    assert yt_discount_offer_info.times_called == 1


# проверяем что размер иконок для продуктов имеет значение
# из конфига grocery_api_modes_products_small_cards, эксперимент
# grocery_api_modes_products_big_cards игнорируется
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.GROCERY_PRODUCTS_SMALL_CARDS
@experiments.GROCERY_PRODUCTS_BIG_CARDS
async def test_modes_root_carousels_icon_size(
        taxi_grocery_api, overlord_catalog, grocery_products,
):
    location = const.LOCATION

    common.build_overlord_catalog_products(
        overlord_catalog,
        [{'id': 'category-1', 'products': ['product-1', 'product-2']}],
    )

    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    group.layout_meta = (
        group.layout_meta[:-1]
        + f', "show_as_carousels": true'
        + f', "products_per_category_count": {5}'
        + '}'
    )
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='category-1')
    virtual_category.add_subcategory(subcategory_id='category-2')

    json = {'modes': ['grocery'], 'position': {'location': location}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert [
        (item['width'], item['height'])
        for item in response.json()['modes'][0]['items']
        if item['type'] == 'good'
    ] == [(3, 4), (3, 4)]


# modes/root должна возвращать только информеры
# c show_in_root = True и непустыми category_group_ids
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.GROCERY_API_DIFFERENT_PLACES_INFORMER
async def test_modes_root_informer(
        taxi_grocery_api, overlord_catalog, grocery_products,
):
    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)
    build_grocery_products_data(grocery_products)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json={'modes': ['grocery'], 'position': {'location': location}},
        headers={},
    )
    assert response.status_code == 200
    assert response.json()['informers'] == [
        {'show_in_root': True, 'text': 'Only root'},
        {
            'category_group_ids': ['category-group-1'],
            'category_ids': [],
            'show_in_root': False,
            'text': 'Only category group',
        },
    ]


# Ручка modes/root возвращает сторис с продуктом
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.GROCERY_API_INFORMER_STORIES
async def test_modes_root_stories_with_product(
        taxi_grocery_api, overlord_catalog, grocery_products,
):
    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)
    build_grocery_products_data(grocery_products)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json={'modes': ['grocery'], 'position': {'location': location}},
        headers={},
    )
    assert response.status_code == 200
    assert 'informers' in response.json()


# проверяем, что при передаче глубины, modes/root
# возвращает всё на глубине structure_depth включительно от рута
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('structure_depth', [1, 2, 3])
async def test_modes_root_show_with_depth(
        taxi_grocery_api, overlord_catalog, grocery_products, structure_depth,
):
    # category_group_depth = 1
    category_depth = 2
    subcategory_depth = 3

    location = const.LOCATION

    common.build_overlord_catalog_products(
        overlord_catalog,
        [{'id': 'subcategory-1', 'products': ['product-1', 'product-2']}],
    )

    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory-1')

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'offer_id': '1a0ba19ca7b644808fea3bc314724ed6',
        'structure_depth': structure_depth,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    products = response.json()['products']

    assert len(products) == structure_depth

    assert products[0]['id'] == 'category-group-1'
    if structure_depth >= category_depth:
        assert products[1]['id'] == 'virtual-category-1'
    if structure_depth >= subcategory_depth:
        assert products[2]['id'] == 'subcategory-1'


# modes/root не возвращает сурж-информеры
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.GROCERY_ROOT_SURGE_INFORMER
async def test_modes_root_informer_surge(
        taxi_grocery_api, overlord_catalog, grocery_products,
):
    location = const.LOCATION
    common.prepare_overlord_catalog(overlord_catalog, location)
    build_grocery_products_data(grocery_products)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json={'modes': ['grocery'], 'position': {'location': location}},
        headers={},
    )
    assert response.status_code == 200
    assert response.json()['informers'] == []


# Проверяем что лайки прорастают в карусельные категории
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_modes_root_favorites(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_fav_goods,
):
    location = const.LOCATION

    common.build_overlord_catalog_products(
        overlord_catalog,
        [
            {
                'id': 'category-1',
                'products': ['product-1', 'product-2', 'product-3'],
            },
            {'id': 'category-2', 'products': ['product-4', 'product-5']},
        ],
    )

    build_grocery_products_data(grocery_products)

    layout_1 = grocery_products.get_layout('layout-1')
    group_1 = layout_1.groups['category-group-1']
    group_1.layout_meta = (
        group_1.layout_meta[:-1]
        + f', "show_as_carousels": true'
        + f', "products_per_category_count": {5}'
        + '}'
    )

    json = {'modes': ['grocery'], 'position': {'location': location}}
    grocery_fav_goods.add_favorite(
        yandex_uid=common.DEFAULT_UID, product_id='product-1',
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={'X-Yandex-UID': common.DEFAULT_UID},
    )
    assert response.status_code == 200
    product_1_in_response = False
    for product in response.json()['products']:
        if product['id'] == 'product-1':
            assert product['is_favorite']
            product_1_in_response = True
    assert product_1_in_response


# Проверяем что приходят legal_restrictions в категориях
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_modes_root_category_restrictions(
        taxi_grocery_api, overlord_catalog, grocery_products, load_json,
):
    location = const.LOCATION

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data=load_json(
            'overlord_catalog_products_data_with_options.json',
        ),
    )
    common.build_basic_layout(grocery_products)
    layout_1 = grocery_products.get_layout('layout-1')
    group_1 = layout_1.groups['category-group-1']
    group_1.layout_meta = (
        group_1.layout_meta[:-1]
        + f', "show_as_carousels": true'
        + f', "products_per_category_count": {5}'
        + '}'
    )

    json = {'modes': ['grocery'], 'position': {'location': location}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200

    category_1_in_response = False
    for product in response.json()['products']:
        if product['id'] == 'virtual-category-1':
            assert product['legal_restrictions'] == ['RU_18+']
            category_1_in_response = True
    assert category_1_in_response


# Проверяем что при ошибке парсинга мет, ничего не ломается
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_failed_parse_meta(
        taxi_grocery_api, overlord_catalog, grocery_products,
):
    common.prepare_overlord_catalog(
        overlord_catalog, location=common.DEFAULT_LOCATION,
    )
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(
        test_id='1',
        item_meta='{"stretch_priority": true}',
        layout_meta='{"products_per_category_count": true}',
    )
    category_group.add_virtual_category(
        test_id='1',
        item_meta='{"hide_if_all_products_are_missing": true}',
        layout_meta='{"stretch_priority": true}',
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': common.DEFAULT_LOCATION},
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200


# при отсутсвии перевода у заголовка категории/прилавки
# отправляем пустую строку
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_untranslated_title(
        taxi_grocery_api, overlord_catalog, grocery_products,
):
    common.prepare_overlord_catalog(
        overlord_catalog, location=common.DEFAULT_LOCATION,
    )
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(
        test_id='1', title_tanker_key='unknown title',
    )
    category_group.add_virtual_category(
        test_id='1', title_tanker_key='unknown title',
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root',
        json={
            'modes': ['grocery'],
            'position': {'location': common.DEFAULT_LOCATION},
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert {item['title'] for item in data['modes'][0]['items']} == {''}
    assert {item['title'] for item in data['products']} == {''}
