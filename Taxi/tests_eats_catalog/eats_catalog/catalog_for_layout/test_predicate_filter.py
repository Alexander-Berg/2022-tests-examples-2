from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils


PROMO_PLACE = 'p_promo'
SHOPS_PLACE = 'p_shops'
ALL_SLUGS = {PROMO_PLACE, SHOPS_PLACE}


@pytest.fixture(autouse=True)
def default_quickfilters(mockserver):
    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def _core_quick_filters(_):
        return {'payload': []}


def add_zone(eats_catalog_storage, place_id: int):
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=place_id,
            place_id=place_id,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )


@pytest.mark.config(
    EATS_CATALOG_PREDICATE_FILTER={
        'filters': [
            {'slug': 'promo', 'name': 'promo', 'custom_filter_type': 'promo'},
            {
                'slug': 'no_surge',
                'name': 'no surge',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'surge_level',
                        'arg_type': 'int',
                        'value': 0,
                    },
                },
            },
            {
                'slug': 'shops',
                'name': 'shops',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'business',
                        'arg_type': 'string',
                        'value': 'shop',
                    },
                },
            },
        ],
    },
)
@pytest.mark.parametrize(
    'request_filter, expected_slugs',
    (
        pytest.param(
            None, (PROMO_PLACE, SHOPS_PLACE), id='no filters requested',
        ),
        pytest.param('promo', (PROMO_PLACE,), id='promo selected'),
        pytest.param('no_surge', (SHOPS_PLACE,), id='no_surge selected'),
        pytest.param('shops', (SHOPS_PLACE,), id='shops selected'),
    ),
)
@pytest.mark.parametrize(
    'discounts_off',
    [
        pytest.param(
            'all',
            marks=experiments.old_discounts_disable(True, 'all'),
            id='all_discounts_off',
        ),
        pytest.param(
            'gift',
            marks=experiments.old_discounts_disable(True, 'gift'),
            id='gift_discounts_off',
        ),
        pytest.param(
            '1plus1',
            marks=experiments.old_discounts_disable(True, '1plus1'),
            id='1plus1_discounts_off',
        ),
        pytest.param(
            'sale',
            marks=experiments.old_discounts_disable(True, 'sale'),
            id='sale_discounts_off',
        ),
        pytest.param(
            None,
            marks=experiments.old_discounts_disable(False, ''),
            id='old_discounts_disabled',
        ),
    ],
)
@pytest.mark.now('2021-03-15T12:55:00+00:00')
async def test_predicate_filter(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        surge,
        request_filter,
        expected_slugs,
        discounts_off,
):
    """
    Проверяем "фильтры на предикатах"
    """

    # PROMO_PLACE - соответствует скидке gift
    promo_place_id = 1
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=promo_place_id,
            brand=storage.Brand(brand_id=promo_place_id),
            slug=PROMO_PLACE,
        ),
    )
    add_zone(eats_catalog_storage, promo_place_id)

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [
                        {'id': promo_place_id, 'disabled_by_surge': False},
                    ],
                },
            ],
        }

    surge.set_place_info(
        place_id=promo_place_id,
        surge={
            'nativeInfo': {
                'deliveryFee': 199,
                'loadLevel': 91,
                'surgeLevel': 2,
            },
        },
    )

    # SHOPS_PLACE
    shops_place_id = 3
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=shops_place_id,
            brand=storage.Brand(brand_id=shops_place_id),
            business=storage.Business.Shop,
            slug=SHOPS_PLACE,
        ),
    )
    add_zone(eats_catalog_storage, shops_place_id)

    block_id = 'any'

    body = {
        'location': {'longitude': 37.591503, 'latitude': 55.802998},
        'blocks': [{'id': block_id, 'type': 'any', 'disable_filters': False}],
        'filters_v2': {'groups': [{'type': 'and', 'filters': []}]},
    }

    if request_filter:
        body['filters_v2']['groups'][0]['filters'] = [
            {'type': 'quickfilter', 'slug': request_filter},
        ]

    response = await catalog_for_layout(**body)
    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200
    filters: slice = response.json()['filters_v2']['list']

    def get_state(slug: str) -> str:
        return 'selected' if slug == request_filter else 'enabled'

    expected_filters = [
        {
            'slug': 'no_surge',
            'type': 'quickfilter',
            'payload': {'name': 'no surge', 'state': get_state('no_surge')},
        },
        {
            'slug': 'shops',
            'type': 'quickfilter',
            'payload': {'name': 'shops', 'state': get_state('shops')},
        },
    ]

    if discounts_off in [None, 'sale', '1plus1'] or request_filter == 'promo':
        # Фильтр скидок придет в ответе, если он выбран (применен) или
        # если есть заведения в которых не выключены акции
        expected_filters.insert(
            0,
            {
                'slug': 'promo',
                'type': 'quickfilter',
                'payload': {'name': 'promo', 'state': get_state('promo')},
            },
        )

    assert filters == expected_filters

    if discounts_off in ['all', 'gift'] and request_filter == 'promo':
        # Если выбран фильтр скидок и выключены все скидки или скидка gift,
        # на которую сейчас есть скидка, то будут пустые блоки и
        # по этому фильтру не заматчится ни одного плейса
        layout_utils.assert_no_block_or_empty(block_id, response.json())
    else:
        # В остальных случаях у всех фильтров будут найдены заведения
        block = layout_utils.find_block(block_id, response.json())
        unexpected_slugs = ALL_SLUGS - set(expected_slugs)
        for slug in expected_slugs:
            layout_utils.find_place_by_slug(slug, block)
        for slug in unexpected_slugs:
            layout_utils.assert_no_slug(slug, block)


@pytest.mark.config(
    EATS_CATALOG_PREDICATE_FILTER={
        'filters': [
            {
                'condition': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'promo_type',
                                'arg_type': 'int',
                                'value': 101,
                            },
                            'type': 'contains',
                        },
                    ],
                    'type': 'all_of',
                },
                'icon': 'asset://rating_star_new',
                'name': 'Доставка',
                'picture': 'asset://surge',
                'slug': 'free_delivery',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'has_disconuts, request_filter',
    (
        pytest.param(True, 'free_delivery', id='promo selected'),
        pytest.param(False, 'free_delivery', id='no discounts'),
    ),
)
@pytest.mark.now('2021-03-15T12:55:00+00:00')
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
async def test_free_delivery_filter(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        surge,
        eats_discounts_applicator,
        has_disconuts,
        request_filter,
):
    promo_place_id = 1
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=promo_place_id,
            brand=storage.Brand(brand_id=promo_place_id),
            slug=PROMO_PLACE,
        ),
    )
    add_zone(eats_catalog_storage, promo_place_id)

    surge.set_place_info(
        place_id=1,
        surge={
            'nativeInfo': {
                'deliveryFee': 199,
                'loadLevel': 91,
                'surgeLevel': 2,
            },
        },
    )

    hierarchy = 'place_delivery_discounts'
    if has_disconuts:
        eats_discounts_applicator.add_discount(
            discount_id='101',
            hierarchy_name=hierarchy,
            name='place_discount',
            description='discount from place',
            picture_uri='place_picture_uri',
            extra={
                'money_value': {
                    'menu_value': {'value_type': 'absolute', 'value': '10'},
                },
            },
        )
        eats_discounts_applicator.bind_discount(
            hierarchy_name=hierarchy, discount_id='101', place_id='1',
        )
    block_id = 'any'
    body = {
        'location': {'longitude': 37.591503, 'latitude': 55.802998},
        'blocks': [{'id': block_id, 'type': 'any', 'disable_filters': False}],
        'filters_v2': {
            'groups': [
                {
                    'type': 'and',
                    'filters': [
                        {'type': 'quickfilter', 'slug': request_filter},
                    ],
                },
            ],
        },
    }

    response = await catalog_for_layout(**body)
    assert response.status_code == 200
    filters: slice = response.json()['filters_v2']['list']

    def get_state(slug: str) -> str:
        return 'selected' if slug == request_filter else 'enabled'

    expected_filters = []
    if has_disconuts:
        block = layout_utils.find_block(block_id, response.json())
        layout_utils.find_place_by_slug('p_promo', block)
        expected_filters = [
            {
                'slug': request_filter,
                'type': 'quickfilter',
                'payload': {
                    'name': 'Доставка',
                    'state': get_state(request_filter),
                    'picture_url': 'asset://surge',
                    'icon_url': 'asset://rating_star_new',
                },
            },
        ]
        assert filters == expected_filters
    else:
        layout_utils.assert_no_block_or_empty(block_id, response.json())


PLACE_MENU_CATEGORY = 'place_category'
PHOTOS = ['photo1']
DEEPLINK = f'eda.yandex://lavka?link=?category={PLACE_MENU_CATEGORY}'


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.config(
    EATS_CATALOG_PLACE_MENU_CATEGORY={
        'tags': {
            PLACE_MENU_CATEGORY: {
                'brand_categories': [
                    {
                        'brand_id': 1,
                        'category': PLACE_MENU_CATEGORY,
                        'photos': PHOTOS,
                    },
                ],
            },
        },
    },
)
@pytest.mark.config(
    EATS_CATALOG_PREDICATE_FILTER={
        'filters': [
            {
                'slug': 'place_menu_category',
                'name': 'place_menu_category',
                'place_menu_category_tag': PLACE_MENU_CATEGORY,
            },
        ],
    },
)
@pytest.mark.parametrize(
    'available_categories,filter_selected',
    (
        pytest.param([], False, id='no available categories'),
        pytest.param([PLACE_MENU_CATEGORY], False, id='category available'),
        pytest.param(
            [PLACE_MENU_CATEGORY],
            True,
            id='category available, filter selected',
        ),
    ),
)
async def test_menu_category_filter(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        available_categories,
        filter_selected,
):
    """
    Проверяем логику работы фильтра "кулинария"
    он должен отображаться только если категория доступна
    после применения, в ответе должен быть deeplink
    """

    with_category_slug = 'with_category_slug'
    without_category_slug = 'without_category_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            business=storage.Business.Store,
            slug=with_category_slug,
        ),
    )
    add_zone(eats_catalog_storage, 1)

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            business=storage.Business.Shop,
            slug=without_category_slug,
        ),
    )
    add_zone(eats_catalog_storage, 2)

    @mockserver.json_handler(
        '/grocery-api/lavka/v1/api/v1/virtual-categories-availability',
    )
    def grocery_api(request):
        return {'available_virtual_categories': available_categories}

    block_id = 'any'
    body = {
        'location': {'longitude': 37.591503, 'latitude': 55.802998},
        'blocks': [{'id': block_id, 'type': 'any', 'disable_filters': False}],
        'filters_v2': {'groups': [{'type': 'and', 'filters': []}]},
    }

    if filter_selected:
        body['filters_v2']['groups'][0]['filters'] = [
            {'type': 'quickfilter', 'slug': 'place_menu_category'},
        ]

    response = await catalog_for_layout(**body)

    assert grocery_api.times_called == 1
    assert response.status == 200
    data = response.json()

    filters: slice = response.json()['filters_v2']['list']

    expected_filters = []

    state = 'selected' if filter_selected else 'enabled'
    if available_categories:
        expected_filters = [
            {
                'slug': 'place_menu_category',
                'type': 'quickfilter',
                'payload': {'name': 'place_menu_category', 'state': state},
            },
        ]
    assert filters == expected_filters

    block = layout_utils.find_block(block_id, data)

    if filter_selected:
        place = layout_utils.find_place_by_slug(with_category_slug, block)

        assert place['payload']['link']['deeplink'] == DEEPLINK
        assert place['payload']['media']['photos'] == list(
            {'uri': photo} for photo in PHOTOS
        )

        layout_utils.assert_no_slug(without_category_slug, block)
    else:
        for slug in (with_category_slug, without_category_slug):
            place = layout_utils.find_place_by_slug(slug, block)
            assert 'link' not in place['payload']


@pytest.mark.config(
    EATS_CATALOG_PREDICATE_FILTER={
        'filters': [
            {
                'slug': 'no_surge',
                'name': '_',
                'name_key': 'c4l.filters.no_surge.name',
                'description_key': 'c4l.filters.no_surge.description',
                'picture': 'filter_picture',
                'icon': 'filter_icon',
                'show_condition': {
                    'type': 'gt',
                    'init': {
                        'arg_name': 'surge_level',
                        'arg_type': 'int',
                        'value': 0,
                    },
                },
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'surge_level',
                        'arg_type': 'int',
                        'value': 0,
                    },
                },
            },
        ],
    },
)
@pytest.mark.translations(
    **{
        'eats-catalog': {
            'c4l.filters.no_surge.name': {'ru': 'no surge'},
            'c4l.filters.no_surge.description': {'ru': 'filter_description'},
        },
    },
)
@pytest.mark.parametrize(
    'has_surge',
    (
        pytest.param(False, id='no surge -> no filter'),
        pytest.param(True, id='has_surge -> show filter'),
    ),
)
@pytest.mark.now('2021-03-15T12:55:00+00:00')
async def test_show_condition(
        catalog_for_layout, eats_catalog_storage, surge, has_surge,
):
    """
    Проверяем условие отображение фильтра
    """

    for idx in range(1, 3):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx,
                brand=storage.Brand(brand_id=idx),
                slug=f'slug_{idx}',
            ),
        )
        add_zone(eats_catalog_storage, idx)

    if has_surge:
        surge.set_place_info(
            place_id=1,
            surge={
                'nativeInfo': {
                    'deliveryFee': 199,
                    'loadLevel': 91,
                    'surgeLevel': 2,
                },
            },
        )

    block_id = 'any'

    body = {
        'location': {'longitude': 37.591503, 'latitude': 55.802998},
        'blocks': [{'id': block_id, 'type': 'any', 'disable_filters': False}],
        'filters_v2': {'groups': [{'type': 'and', 'filters': []}]},
    }

    response = await catalog_for_layout(**body)
    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200
    filters: slice = response.json()['filters_v2']['list']

    expected_filters = []
    if has_surge:
        expected_filters.append(
            {
                'slug': 'no_surge',
                'type': 'quickfilter',
                'payload': {
                    'name': 'no surge',
                    'state': 'enabled',
                    'icon_url': 'filter_icon',
                    'picture_url': 'filter_picture',
                    'description': 'filter_description',
                },
            },
        )

    assert filters == expected_filters


@pytest.mark.config(
    EATS_CATALOG_PREDICATE_FILTER={
        'filters': [
            {
                'slug': 'history-order',
                'name': '_',
                'name_key': 'c4l.filters.history-order.name',
                'description_key': 'c4l.filters.history-order.description',
                'picture': 'filter_picture',
                'icon': 'filter_icon',
                'condition': {
                    'type': 'contains',
                    'init': {
                        'arg_name': 'compilations',
                        'arg_type': 'string',
                        'value': 'history-order',
                    },
                },
            },
        ],
    },
)
@pytest.mark.parametrize(
    'has_filter',
    (
        pytest.param(False, id='no compilation'),
        pytest.param(True, id='with compilation'),
    ),
)
@pytest.mark.translations(
    **{
        'eats-catalog': {
            'c4l.filters.history-order.name': {'ru': 'Random Name'},
            'c4l.filters.history-order.description': {'ru': 'No description'},
        },
    },
)
@pytest.mark.now('2022-03-05T13:19:00+03:00')
async def test_compilation_filter(
        catalog_for_layout, mockserver, eats_catalog_storage, has_filter,
):
    """
    Проверяем, что в случае если umlaas-eats присылает подборку, то мы можем
    построить по ней фильтр
    """

    for place_id in range(1, 3):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug=f'slug_{place_id}',
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2022-03-05T00:00:00+03:00'),
                        end=parser.parse('2022-03-05T23:00:00+03:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        relevance = []
        if has_filter:
            relevance = [
                {
                    'id': 2,
                    'relevance': 50,
                    'type': 'ranking',
                    'predicted_times': {'min': 20, 'max': 30},
                    'blocks': [
                        {'block_id': 'history-order', 'relevance': 0.5},
                    ],
                },
            ]

        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': ['history-order'],
            'result': relevance,
        }

    response = await catalog_for_layout(
        [{'id': 'open', 'type': 'open', 'disable_filters': False}],
        filters_v2={'groups': [{'type': 'and', 'filters': []}]},
    )

    assert eats_catalog_storage.search_times_called == 1
    assert umlaas_eats.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    layout_utils.find_place_by_slug('slug_2', block)

    if has_filter:
        item = layout_utils.find_filter_v2(
            data, 'history-order', 'quickfilter',
        )
        assert item['payload'] == {
            'name': 'Random Name',
            'state': 'enabled',
            'icon_url': 'filter_icon',
            'picture_url': 'filter_picture',
            'description': 'No description',
        }
    else:
        layout_utils.assert_no_filter_v2(data, 'history-order', 'quickfilter')
