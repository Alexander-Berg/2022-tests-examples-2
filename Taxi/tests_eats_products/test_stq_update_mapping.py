import copy
import dataclasses
import datetime as dt
from typing import Optional

import pytest
import pytz

from tests_eats_products import conftest
from tests_eats_products import utils


NOW = dt.datetime(2019, 1, 1, 0, tzinfo=pytz.UTC)

PLACE_SLUG = 'slug'
PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': PLACE_SLUG}


@dataclasses.dataclass
class Brand:
    brand_id: int
    slug: str
    picture_scale: str
    updated_at: dt.datetime
    is_enabled: bool


@dataclasses.dataclass
class Place:
    place_id: int
    slug: str
    updated_at: dt.datetime
    brand_id: int
    is_enabled: bool
    currency_code: Optional[str]
    currency_sign: Optional[str]


@dataclasses.dataclass
class Category:
    category_id: int
    place_id: int
    core_id: int
    core_parent_id: int
    nomenclature_id: str
    updated_at: dt.datetime


@dataclasses.dataclass
class Product:
    product_id: int
    category_id: int
    core_id: int
    nomenclature_id: str
    updated_at: dt.datetime


def _to_utc(stamp):
    if isinstance(stamp, dt.datetime):
        if stamp.tzinfo is not None:
            stamp = stamp.astimezone(pytz.UTC)
    return stamp


def _build_entity_row(entity, data):
    row = globals()[entity](*data)
    row.updated_at = _to_utc(row.updated_at)
    return row


def _select_rows(pgsql, entity, where=None):
    cursor = pgsql['eats_products'].cursor()
    query = 'select * from eats_products.%s' % entity
    if where:
        query += ' where ' + where

    cursor.execute(query)
    return {r[0]: _build_entity_row(entity.title(), r) for r in list(cursor)}


@pytest.mark.parametrize('nmn_integration_version', ['v1'])
async def test_all_mappings_exist(
        stq,
        mock_nomenclature_for_v2_menu_goods,
        add_default_product_mapping,
        # parametrize
        nmn_integration_version,
):
    # Тест проверяет, что stq таска не создается,
    # если маппинги есть для всех товаров и категорий.
    add_default_product_mapping()

    place_id = 1
    brand_id = 1

    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods

    root_cat_5 = conftest.CategoryMenuGoods(
        public_id='5', name='Овощи', origin_id='category_id_5',
    )
    root_cat_6 = conftest.CategoryMenuGoods(
        public_id='6', name='Фрукты', origin_id='category_id_6',
    )
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='1', name='Овощи и фрукты', origin_id='category_id_1',
    )
    root_cat_1.add_child_category(root_cat_5)
    root_cat_1.add_child_category(root_cat_6)

    product_1 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        name='Огурцы',
        origin_id='item_id_1',
    )
    product_2 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
        name='Помидоры',
        origin_id='item_id_2',
    )
    product_3 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
        name='Яблоки',
        origin_id='item_id_3',
    )
    product_4 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
        name='Апельсины',
        origin_id='item_id_4',
    )
    product_5 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
        name='Бананы',
        origin_id='item_id_5',
    )

    root_cat_6.add_product(product_3, sort_order=3)
    root_cat_6.add_product(product_4, sort_order=1)
    root_cat_6.add_product(product_5, sort_order=2)

    root_cat_5.add_product(product_1, sort_order=1)
    root_cat_5.add_product(product_2, sort_order=2)

    place = conftest.PlaceMenuGoods(
        place_id=place_id, slug=PLACE_SLUG, brand_id=brand_id,
    )
    place.add_root_category(root_cat_1)

    mock_nomenclature_context.set_place(place)

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['maxDepth'] = 200
    await mock_nomenclature_context.invoke_menu_goods_basic(
        products_request, integration_version=nmn_integration_version,
    )

    assert stq.eats_products_update_mapping.times_called == 0


async def test_no_mapping_for_request_category(
        taxi_eats_products,
        mockserver,
        load_json,
        stq,
        add_default_product_mapping,
):
    # Тест проверяет, что stq таска не создается,
    # если нет маппинга для запрашиваемой категории.
    add_default_product_mapping()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature-categories.json')

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 123
    products_request['maxDepth'] = 3
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200

    assert not stq.eats_products_update_mapping.has_calls


async def test_no_mapping_for_response_product(
        taxi_eats_products, mockserver, load_json, stq,
):
    # Тест проверяет, что stq таска создается,
    # если нет маппинга для продукта,
    # вернувшегося из сервиса номенклатур.
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        nomenclature_response = load_json('nomenclature-categories.json')
        new_product = load_json('nomenclature-unknown-product.json')
        nomenclature_response['categories'][0]['items'].append(new_product)
        return nomenclature_response

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1
    products_request['maxDepth'] = 3
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200

    assert stq.eats_products_update_mapping.times_called == 1
    task_info = stq.eats_products_update_mapping.next_call()
    assert task_info['queue'] == 'eats_products_update_mapping'
    assert task_info['id'] == 'update_id_mapping_slug'
    assert 'place_slug' in task_info['kwargs']
    assert task_info['kwargs']['place_slug'] == 'slug'


async def test_no_mapping_for_response_category_and_product(
        taxi_eats_products, mockserver, load_json, stq,
):
    # Тест проверяет, что создается только одна stq таска,
    # если нет маппинга для продукта и категории,
    # вернувшихся из сервиса номенклатур.
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        nomenclature_response = load_json('nomenclature-categories.json')
        new_category = load_json('nomenclature-unknown-category.json')
        nomenclature_response['categories'].append(new_category)
        new_product = load_json('nomenclature-unknown-product.json')
        nomenclature_response['categories'][0]['items'].append(new_product)
        return nomenclature_response

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1
    products_request['maxDepth'] = 3
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200

    assert stq.eats_products_update_mapping.times_called == 1
    task_info = stq.eats_products_update_mapping.next_call()
    assert task_info['queue'] == 'eats_products_update_mapping'
    assert task_info['id'] == 'update_id_mapping_slug'
    assert 'place_slug' in task_info['kwargs']
    assert task_info['kwargs']['place_slug'] == 'slug'


@pytest.mark.parametrize(
    'update_mapping_pause_sec, update_mapping_by_handle_enabled, '
    'in_progress, started_at, task_added',
    [
        pytest.param(
            60,
            False,
            False,
            NOW - dt.timedelta(seconds=61),
            False,
            id='not updated by enabled',
        ),
        pytest.param(
            60,
            True,
            False,
            NOW - dt.timedelta(seconds=61),
            True,
            id='updated by in_progress',
        ),
        pytest.param(
            60,
            True,
            False,
            NOW - dt.timedelta(seconds=59),
            True,
            id='updated by in_progress 2',
        ),
        pytest.param(
            60,
            True,
            True,
            NOW - dt.timedelta(seconds=61),
            True,
            id='updated by started_at',
        ),
        pytest.param(60, True, True, None, True, id='updated by started_at 2'),
        pytest.param(
            60,
            True,
            True,
            NOW - dt.timedelta(seconds=59),
            False,
            id='not updated by started_at',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_no_mapping_is_stq_added(
        taxi_eats_products,
        pgsql,
        taxi_config,
        mockserver,
        load_json,
        stq,
        update_mapping_pause_sec,
        update_mapping_by_handle_enabled,
        in_progress,
        started_at,
        task_added,
):
    # Тест проверяет, что stq таска создается,
    # только если включен флаг update_mapping_by_handle_enabled
    # и плейс достаточно давно обновлялся
    place_id = 1
    cursor = pgsql['eats_products'].cursor()
    if started_at is None:
        cursor.execute(
            f"""
            update eats_products.place_update_statuses
            set mapping_update_in_progress = {in_progress},
                mapping_update_started_at = null
            where place_id = {place_id}
        """,
        )
    else:
        cursor.execute(
            f"""
            update eats_products.place_update_statuses
            set mapping_update_in_progress = {in_progress},
                mapping_update_started_at = '{started_at}'
            where place_id = {place_id}
        """,
        )

    taxi_config.set(
        EATS_PRODUCTS_SETTINGS={
            'update_mapping_pause_sec': update_mapping_pause_sec,
            'update_mapping_by_handle_enabled': (
                update_mapping_by_handle_enabled
            ),
        },
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        nomenclature_response = load_json('nomenclature-categories.json')
        new_category = load_json('nomenclature-unknown-category.json')
        nomenclature_response['categories'].append(new_category)
        new_product = load_json('nomenclature-unknown-product.json')
        nomenclature_response['categories'][0]['items'].append(new_product)
        return nomenclature_response

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1
    products_request['maxDepth'] = 3
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200

    if task_added:
        assert stq.eats_products_update_mapping.times_called == 1
        task_info = stq.eats_products_update_mapping.next_call()
        assert task_info['queue'] == 'eats_products_update_mapping'
        assert task_info['id'] == 'update_id_mapping_slug'
        assert 'place_slug' in task_info['kwargs']
        assert task_info['kwargs']['place_slug'] == 'slug'
    else:
        assert not stq.eats_products_update_mapping.has_calls


def read_place_products_mapping(pgsql):
    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        """
            SELECT place_id, origin_id, core_id
            FROM eats_products.place_products;
        """,
    )
    return {(row[0], row[1]): row[2] for row in cursor}


def read_places_mappings(pgsql):
    cursor = pgsql['eats_products'].cursor()
    cursor.execute('SELECT * FROM eats_products.place;')
    return {r[0]: (r[0], r[1], r[3]) for r in list(cursor)}


def read_brands(pgsql):
    cursor = pgsql['eats_products'].cursor()
    cursor.execute('SELECT * FROM eats_products.brand;')
    return {r[0]: (r[0], r[1], r[2]) for r in list(cursor)}


async def test_stq_update_place_products(
        pgsql, mockserver, load_json, stq_runner, add_place_products_mapping,
):
    place_id = 1
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='new_product_101', public_id='public_id_1',
            ),
        ],
    )

    place_products_mapping = read_place_products_mapping(pgsql)
    assert place_products_mapping[(place_id, 'new_product_101')] is None
    assert (place_id, 'new_product_102') not in place_products_mapping
    assert (place_id, 'new_product_103') not in place_products_mapping

    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_MAPPING)
    def _mock_eats_core_retail_mapping(request):
        return load_json('core_retail_mapping.json')

    await stq_runner.eats_products_update_mapping.call(
        task_id='update_id_mapping_slug',
        kwargs={'place_slug': 'slug'},
        expect_fail=False,
    )

    place_products_mapping = read_place_products_mapping(pgsql)
    assert place_products_mapping[(place_id, 'new_product_101')] == 101
    assert place_products_mapping[(place_id, 'new_product_102')] == 102
    assert place_products_mapping[(place_id, 'new_product_103')] == 103


async def test_stq_update_place_products_brand(
        pgsql, mockserver, load_json, stq_runner,
):
    def read_from_place_products():
        cursor = pgsql['eats_products'].cursor()
        cursor.execute(
            """
                SELECT brand_id, origin_id
                FROM eats_products.place_products;
            """,
        )
        return [(row[0], row[1]) for row in cursor]

    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_MAPPING)
    def _mock_eats_core_retail_mapping(request):
        return load_json('core_retail_mapping.json')

    await stq_runner.eats_products_update_mapping.call(
        task_id='update_id_mapping_slug', kwargs={'place_slug': 'slug'},
    )
    assert sorted(read_from_place_products()) == sorted(
        [
            (utils.BRAND_ID, 'new_product_103'),
            (utils.BRAND_ID, 'new_product_101'),
            (utils.BRAND_ID, 'new_product_102'),
        ],
    )


async def test_stq_update_place(pgsql, mockserver, load_json, stq_runner):
    # Тест проверяет, что stq таска обновляет маппинг заведения в бд.
    place_mapping = read_places_mappings(pgsql)
    assert 234 not in place_mapping

    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_MAPPING)
    def _mock_eats_core_retail_mapping(request):
        return load_json('core_retail_mapping_slug234.json')

    await stq_runner.eats_products_update_mapping.call(
        task_id='update_id_mapping_slug234',
        kwargs={'place_slug': 'slug234'},
        expect_fail=False,
    )

    expected_rows = {1: (1, 'slug', 1), 234: (234, 'slug234', 2)}
    places_rows = read_places_mappings(pgsql)
    for place_id in expected_rows:
        assert place_id in places_rows
        assert expected_rows[place_id] == places_rows[place_id]


@pytest.mark.parametrize(
    'core_retail_response',
    [
        {
            'place_id': 123,
            'categories': [],
            'originals_to_mapped': [],
            'total': 0,
            'brand': {'brand_id': 12, 'slug': 'brand_12_slug'},
        },
        {
            'place_id': 123,
            'categories': [],
            'originals_to_mapped': [],
            'total': 0,
            'brand': {
                'brand_id': 12,
                'slug': 'brand_12_slug',
                'scale': 'scale1',
            },
        },
    ],
)
async def test_stq_update_brand(
        pgsql, mockserver, stq_runner, core_retail_response,
):
    # Тест проверяет, что stq таска обновляет маппинг бренда
    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_MAPPING)
    def _mock_eats_core_retail_mapping(request):
        return core_retail_response

    await stq_runner.eats_products_update_mapping.call(
        task_id='update_id_mapping_slug234',
        kwargs={'place_slug': 'slug234'},
        expect_fail=False,
    )

    brand = core_retail_response['brand']
    scale = None
    if 'scale' in brand:
        scale = brand['scale']
    expected_rows = {
        1: (1, 'brand1', 'aspect_fit'),
        brand['brand_id']: (brand['brand_id'], brand['slug'], scale),
    }
    brands_rows = read_brands(pgsql)
    assert expected_rows == brands_rows


async def test_stq_update_brand_and_place_slug(
        pgsql, mockserver, load_json, stq_runner,
):
    # Тест проверяет, что stq таска обновляет slug в таблицах brand и place.
    brands = read_brands(pgsql)
    assert 1 in brands
    assert brands[1][1] == 'brand1'

    places = read_places_mappings(pgsql)
    assert 1 in places
    assert places[1][1] == 'slug'

    new_brand_slug = 'some_new_brand_slug'
    new_place_slug = 'some_new_place_slug'

    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_MAPPING)
    def _mock_eats_core_retail_mapping(request):
        response = load_json('core_retail_mapping.json')
        response['brand']['slug'] = new_brand_slug
        return response

    await stq_runner.eats_products_update_mapping.call(
        task_id='update_id_mapping_some_new_place_slug',
        kwargs={'place_slug': 'some_new_place_slug'},
        expect_fail=False,
    )

    brands = read_brands(pgsql)
    assert 1 in brands
    assert brands[1][1] == new_brand_slug

    places = read_places_mappings(pgsql)
    assert 1 in places
    assert places[1][1] == new_place_slug


async def test_update_mapping_pause_sec_new_place(
        pgsql, mockserver, load_json, stq_runner,
):
    # Тест проверяет, что если магазина нет в БД,
    # то stq-такс на обновление маппингов выполняется
    # параметр конфига update_mapping_pause_sec
    # на это не влияет

    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_MAPPING)
    def _mock_eats_core_retail_mapping(request):
        return load_json('core_retail_mapping_slug234.json')

    await stq_runner.eats_products_update_mapping.call(
        task_id='update_id_mapping_slug234',
        kwargs={'place_slug': 'slug234'},
        expect_fail=False,
    )

    expected_rows = {234: (234, 'slug234', 2)}
    places_rows = read_places_mappings(pgsql)
    for place_id in expected_rows:
        assert place_id in places_rows
        assert expected_rows[place_id] == places_rows[place_id]


async def test_stq_empty_nomenclature_id(
        pgsql, mockserver, load_json, stq_runner,
):
    # Тест проверяет, что если у товара пришел пустой
    # nomenclature_id, то в качестве nomenclature_id в базу
    # сохраняется core_id.
    assert read_place_products_mapping(pgsql) == {}

    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_MAPPING)
    def _mock_eats_core_retail_mapping(request):
        response = load_json('core_retail_mapping.json')
        for product in response['originals_to_mapped']:
            product['nomenclature_id'] = ''
        return response

    await stq_runner.eats_products_update_mapping.call(
        task_id='update_id_mapping_slug',
        kwargs={'place_slug': 'slug'},
        expect_fail=False,
    )

    expected_products_mapping = {
        (1, '103'): 103,
        (1, '101'): 101,
        (1, '104'): 104,
        (1, '102'): 102,
    }
    products_mapping = read_place_products_mapping(pgsql)
    assert products_mapping == expected_products_mapping


@pytest.mark.parametrize('entity', ['brand', 'place', 'category'])
@pytest.mark.now((dt.datetime.now() + dt.timedelta(seconds=61)).isoformat())
async def test_stq_not_updated_if_no_modified(
        pgsql, mockserver, load_json, stq_runner, entity,
):
    # Тест проверяет, что если сущность
    # полученная в маппинге не отличается от
    # хранящейся в БД, то запись в БД не обновляется
    old_rows = _select_rows(pgsql, entity)

    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_MAPPING)
    def _mock_eats_core_retail_mapping(request):
        return load_json('core_retail_non_modified.json')

    await stq_runner.eats_products_update_mapping.call(
        task_id='update_id_mapping_slug',
        kwargs={'place_slug': 'slug'},
        expect_fail=False,
    )

    new_rows = _select_rows(pgsql, entity)
    assert old_rows == new_rows


@pytest.mark.parametrize(
    'expected_has_calls',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_SETTINGS={
                        'update_mapping_on_new_assortment_enabled': True,
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_SETTINGS={
                        'update_mapping_on_new_assortment_enabled': False,
                    },
                ),
            ],
        ),
    ],
)
async def test_run_eats_products_update_mapping(
        stq_runner, stq, expected_has_calls,
):
    # Тест проверяет что eats_products_update_mapping запускается из
    # eats_products_update_nomenclature_product_mapping в случае если это
    # разрешено в конфиге.

    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(utils.PLACE_ID), kwargs={'place_id': str(utils.PLACE_ID)},
    )

    assert expected_has_calls == stq.eats_products_update_mapping.has_calls
