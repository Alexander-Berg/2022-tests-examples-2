import pytest

from . import catalog
from . import experiments
from . import legacy
from . import rest_menu_storage
from . import utils


SAAS_PREFIX = 2
REST_MENU_PREFIX = 4
SET_SAAS_SETTINGS = pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': 'eats_fts',
        'prefix': SAAS_PREFIX,
        'misspell': 'try_at_first',
        'prefix_erms_menu': REST_MENU_PREFIX,
    },
)
PLACE_SLUG = 'my_place_slug'
HANDLER = f'/api/v2/menu/goods/search/{PLACE_SLUG}'

EXPECTED_ITEMS = [
    legacy.Goods(
        id=10,
        name='item_name_1',
        description='item_description_1',
        available=True,
        inStock=10,
        price=123,
        decimalPrice='123.45',
        promoPrice=99,
        decimalPromoPrice='99.6',
        adult=False,
        promoTypes=[],
        optionGroups=[
            legacy.LegacyOptionGroup(
                id=1,
                name='option_group_name_1',
                options=[
                    legacy.LegacyOption(
                        id=10,
                        name='option_name_1',
                        price=10,
                        decimalPrice='10.5',
                        promoPrice=8,
                        decimalPromoPrice='8.5',
                        multiplier=1,
                    ),
                ],
                required=True,
                minSelected=10,
                maxSelected=20,
            ),
            legacy.LegacyOptionGroup(
                id=2,
                name='option_group_name_2',
                options=[
                    legacy.LegacyOption(
                        id=30,
                        name='option_name_3',
                        price=0,
                        decimalPrice='0',
                        multiplier=3,
                    ),
                ],
                required=False,
                minSelected=None,
                maxSelected=None,
            ),
        ],
        picture=legacy.LegacyPicture(
            url='https://eda.yandex.ru/image.png',
        ).as_dict(),
        weight='500 л',
        shippingType='all',
    ).as_dict(),
    legacy.Goods(
        adult=True,
        id=40,
        name='min_item_name',
        description='',
        available=True,
        price=500,
        decimalPrice='500',
        shippingType='all',
    ).as_dict(),
    legacy.Goods(
        adult=False,
        id=20,
        name='item_name_2',
        description='',
        available=False,
        price=500,
        decimalPrice='500',
        shippingType='all',
    ).as_dict(),
]


@pytest.mark.pgsql(
    'eats_full_text_search_indexer',
    files=['pg_eats_full_text_search_indexer.sql'],
)
@experiments.USE_ERMS_IN_RESTAURANT_SEARCH
@SET_SAAS_SETTINGS
async def test_erms_in_restaurant_goods(
        taxi_eats_full_text_search, mockserver, rest_menu_storage_get_items,
):
    """
    Проверяет, что при поиске с каталога и включенном флаге
    1) Есть запрос в erms с айтемами из saas
    2) Нет запроса в elastic search
    3) Модель айтема из erms попадает в ответ поиска
    """

    full_item_id = 'my_full_item_id'
    min_item_id = 'my_min_item_id'
    disabled_item_id = 'disabled_item_id'
    not_found_item_id = 'not_found_item_id'

    full_item = rest_menu_storage.Item(
        id=full_item_id,
        origin_id='item_origin_id_1',
        legacy_id=10,
        adult=False,
        available=True,
        name='item_name_1',
        price='123.45',
        promo_price='99.6',
        description='item_description_1',
        pictures=[rest_menu_storage.ItemPicture()],
        weight_unit=rest_menu_storage.WeightUnits.LITER.value,
        weight_value='500',
        categories_ids=[
            rest_menu_storage.CategoryIds(id='category_id_1', legacy_id=10),
        ],
        sort=100,
        stock=10,
        options_groups=[
            rest_menu_storage.OptionsGroup(  # all fields
                id='full_option_group_id_1',
                origin_id='option_group_origin_id_1',
                name='option_group_name_1',
                legacy_id=1,
                sort=10,
                is_required=True,
                min_selected_options=10,
                max_selected_options=20,
                options=[
                    rest_menu_storage.Option(  # available + promo_price
                        id='option_id_1',
                        origin_id='option_origin_id_1',
                        name='option_name_1',
                        multiplier=1,
                        available=True,
                        price='10.5',
                        promo_price='8.5',
                        legacy_id=10,
                    ),
                    rest_menu_storage.Option(  # unavailable + no price
                        id='option_id_2',
                        origin_id='option_origin_id_2',
                        name='option_name_2',
                        multiplier=2,
                        available=False,
                        legacy_id=20,
                    ),
                ],
            ),
            rest_menu_storage.OptionsGroup(  # required fields
                id='min_option_group_id_2',
                origin_id='option_group_origin_id_12',
                name='option_group_name_2',
                legacy_id=2,
                options=[
                    rest_menu_storage.Option(
                        id='option_id_3',
                        origin_id='option_origin_id_3',
                        name='option_name_3',
                        multiplier=3,
                        available=True,
                        legacy_id=30,
                    ),
                    rest_menu_storage.Option(  # without legacy id
                        id='option_id_4',
                        origin_id='option_origin_id_4',
                        name='option_name_4',
                        multiplier=4,
                        available=True,
                    ),
                ],
            ),
        ],
    )

    min_item = rest_menu_storage.Item(
        id=min_item_id,
        origin_id='min_item_origind_id',
        name='min_item_name',
        adult=True,
        legacy_id=40,
        categories_ids=[
            rest_menu_storage.CategoryIds(id='category_id_2', legacy_id=20),
        ],
    )

    disabled_item = rest_menu_storage.Item(
        id=disabled_item_id,
        origin_id='item_origin_id_2',
        name='item_name_2',
        legacy_id=20,
        adult=False,
        available=False,
        categories_ids=[
            rest_menu_storage.CategoryIds(id='category_id_2', legacy_id=20),
        ],
    )

    # этот айтем не добавляем в ответ erms
    not_found_item = rest_menu_storage.Item(
        id=not_found_item_id,
        origin_id='item_origin_id_3',
        name='item_name_3',
        legacy_id=30,
        adult=False,
        available=True,
    )

    rest_menu_storage_get_items.places = [
        rest_menu_storage.Place(
            place_id='1', items=[full_item, min_item, disabled_item],
        ),
    ]

    def rest_menu_storage_callback(request):
        assert len(request.json['places']) == 1
        assert frozenset(request.json['shipping_types']) == frozenset(
            ['delivery'],
        )
        place = request.json['places'][0]
        assert place['place_id'] == '1'
        assert frozenset(place['items']) == frozenset(
            [full_item_id, min_item_id, disabled_item_id, not_found_item_id],
        )

    rest_menu_storage_get_items.assert_callback = rest_menu_storage_callback

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        args = request.query
        assert tuple(map(int, args['kps'].split(','))) == (
            SAAS_PREFIX,
            REST_MENU_PREFIX,
        )
        return utils.get_saas_response(
            [
                utils.rest_menu_item_to_saas_doc(
                    place_id='1', place_slug=PLACE_SLUG, item=full_item,
                ),
                utils.rest_menu_item_to_saas_doc(
                    place_id='1', place_slug=PLACE_SLUG, item=min_item,
                ),
                utils.rest_menu_item_to_saas_doc(
                    place_id='1', place_slug=PLACE_SLUG, item=disabled_item,
                ),
                utils.rest_menu_item_to_saas_doc(
                    place_id='1', place_slug=PLACE_SLUG, item=not_found_item,
                ),
            ],
        )

    @mockserver.json_handler(
        '/eats-fts-elastic-search/menu_item_production/_search',
    )
    def eats_fts_elastic_search(_):
        assert False

    response = await taxi_eats_full_text_search.get(
        HANDLER,
        params={'text': 'My search text', 'shipping_type': 'delivery'},
    )

    assert saas.times_called > 0
    assert rest_menu_storage_get_items.times_called > 0
    assert eats_fts_elastic_search.times_called == 0

    assert response.status == 200

    response_json = response.json()

    response_items = None

    for block in response_json['payload']:
        if block['itemsType']['type'] == 'item':
            response_items = block['items']

    assert len(response_items) == 3

    assert sorted(response_items, key=lambda item: item['id']) == sorted(
        EXPECTED_ITEMS, key=lambda item: item['id'],
    )


@pytest.mark.pgsql(
    'eats_full_text_search_indexer',
    files=['pg_eats_full_text_search_indexer.sql'],
)
@experiments.USE_ERMS_IN_RESTAURANT_SEARCH
@SET_SAAS_SETTINGS
async def test_erms_in_restaurant_goods_error(
        taxi_eats_full_text_search, mockserver, rest_menu_storage_get_items,
):
    """
    Проверяет, что при 500 erms, сам поиск не 500-тит
    """

    rest_menu_storage_get_items.status_code = 500

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(_):
        return utils.get_saas_response(
            [
                utils.item_preview_to_saas_doc(
                    place_id='1',
                    place_slug=PLACE_SLUG,
                    item_preview=rest_menu_storage.ItemPreview(),
                ),
            ],
        )

    @mockserver.json_handler(
        '/eats-fts-elastic-search/menu_item_production/_search',
    )
    def eats_fts_elastic_search(_):
        assert False

    response = None
    response = await taxi_eats_full_text_search.get(
        HANDLER,
        params={'text': 'My search text', 'shipping_type': 'delivery'},
    )

    assert saas.times_called > 0
    assert rest_menu_storage_get_items.times_called > 0
    assert eats_fts_elastic_search.times_called == 0

    assert response.status == 200

    for block in response.json()['payload']:
        if block['itemsType']['type'] == 'item':
            response_items = block['items']
            assert not response_items


@pytest.mark.pgsql(
    'eats_full_text_search_indexer',
    files=['pg_eats_full_text_search_indexer.sql'],
)
@experiments.USE_ERMS_IN_RESTAURANT_SEARCH
@SET_SAAS_SETTINGS
async def test_erms_in_restaurant_goods_pickup(
        taxi_eats_full_text_search, mockserver, rest_menu_storage_get_items,
):
    """
    Проверяет, что pickup из запроса к поиску
    пробрасывается в erms
    """

    delivery_time = '2022-05-31T12:00:00+00:00'

    def rest_menu_storage_callback(request):
        assert len(request.json['places']) == 1
        assert frozenset(request.json['shipping_types']) == frozenset(
            ['pickup'],
        )
        assert request.json['delivery_time'] == delivery_time

    rest_menu_storage_get_items.assert_callback = rest_menu_storage_callback

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(_):
        return utils.get_saas_response(
            [
                utils.item_preview_to_saas_doc(
                    place_id='1',
                    place_slug=PLACE_SLUG,
                    item_preview=rest_menu_storage.ItemPreview(),
                ),
            ],
        )

    response = await taxi_eats_full_text_search.get(
        HANDLER,
        params={
            'text': 'My search text',
            'shippingType': 'pickup',
            'deliveryTime': delivery_time,
        },
    )

    assert saas.times_called > 0
    assert rest_menu_storage_get_items.times_called > 0

    assert response.status == 200


@pytest.mark.pgsql(
    'eats_full_text_search_indexer',
    files=['pg_eats_full_text_search_indexer.sql'],
)
@experiments.USE_ERMS_IN_RESTAURANT_SEARCH
@SET_SAAS_SETTINGS
async def test_erms_in_restaurant_goods_no_items(
        taxi_eats_full_text_search, mockserver, rest_menu_storage_get_items,
):
    """
    Проверяем, если SAAS не вернул айтемов,
    то запроса в erms не будет
    """

    place = catalog.Place(
        business=catalog.Business.Restaurant, id=1, slug=PLACE_SLUG,
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(_):
        return utils.get_saas_response(
            [utils.catalog_place_to_saas_doc(place)],
        )

    response = await taxi_eats_full_text_search.get(
        HANDLER, params={'text': 'My search text', 'shippingType': 'delivery'},
    )

    assert saas.times_called > 0
    assert rest_menu_storage_get_items.times_called == 0

    assert response.status == 200
