# pylint: disable=too-many-lines
import copy
import dataclasses
import decimal
from typing import List
from typing import Optional

import pytest

from tests_eats_products import categories as cats
from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PERIODIC_NAME = 'products-scoring-update-periodic'

# YT tables for products
YT_TABLE_SCHEMAS = 'yt_products_scoring_schema.yaml'
YT_TABLE_V1 = 'yt_table_v1'
YT_TABLE_V1_PATH = '//yt/products_scoring_v1'
YT_TABLE_V1_DATA = 'yt_products_scoring_data_v1.yaml'
YT_TABLE_V2 = 'yt_table_v2'
YT_TABLE_V2_PATH = '//yt/products_scoring_v2'
YT_TABLE_V2_DATA = 'yt_products_scoring_data_v2.yaml'
YT_TABLE_V3 = 'yt_table_v3'
YT_TABLE_V3_PATH = '//yt/products_scoring_v3'
YT_TABLE_V3_DATA = 'yt_products_scoring_data_v3.yaml'

# YT tables for categories
YT_TABLE_CATEGORIES_SCHEMAS = 'yt_categories_scoring_schema.yaml'
YT_TABLE_CATEGORIES_V1 = 'yt_categories_table_v1'
YT_TABLE_CATEGORIES_V1_PATH = '//yt/categories_scoring_v1'
YT_TABLE_CATEGORIES_V1_DATA = 'yt_categories_scoring_data_v1.yaml'
YT_TABLE_CATEGORIES_V2 = 'yt_categories_table_v2'
YT_TABLE_CATEGORIES_V2_PATH = '//yt/categories_scoring_v2'
YT_TABLE_CATEGORIES_V2_DATA = 'yt_categories_scoring_data_v2.yaml'
YT_TABLE_CATEGORIES_V3 = 'yt_categories_table_v3'
YT_TABLE_CATEGORIES_V3_PATH = '//yt/categories_scoring_v3'
YT_TABLE_CATEGORIES_V3_DATA = 'yt_categories_scoring_data_v3.yaml'

# mixed YT tables
YT_TABLE_MIXED_SCHEMAS = 'yt_mixed_scoring_schema.yaml'

# expected from YT tables by brands for products
EXPECTED_REDIS_PRODUCTS_V1_B1 = {
    b'item_id_11': b'0.0001590155712940198',
    b'item_id_12': b'0.000012231967022616907',
    b'item_id_13': b'0.000000000000000000001',
    b'item_id_14': b'66.66',
    b'item_id_15': b'55.55',
}
EXPECTED_REDIS_PRODUCTS_V1_B2 = {
    b'item_id_21': b'99.99',
    b'item_id_22': b'88.88',
    b'item_id_23': b'77.77',
    b'item_id_24': b'66.66',
    b'item_id_25': b'0.00007339180213570144',
}
EXPECTED_REDIS_PRODUCTS_V2_B1 = {
    b'item_id_11': b'0.00003669590106785072',
    b'item_id_12': b'66.66',
    b'item_id_13': b'77.77',
    b'item_id_14': b'88.88',
    b'item_id_15': b'99.99',
}
EXPECTED_REDIS_PRODUCTS_V2_B2 = {
    b'item_id_21': b'55.55',
    b'item_id_22': b'66.66',
    b'item_id_23': b'77.77',
    b'item_id_24': b'88.88',
    b'item_id_25': b'0.000012231967022616907',
}

# expected from YT tables by brands for categories
EXPECTED_REDIS_CATEGORIES_V1_B1 = {
    b'11': b'0.0001590155712940198',
    b'12': b'0.000012231967022616907',
    b'13': b'0.000000000000000000001',
}
EXPECTED_REDIS_CATEGORIES_V1_B2 = {
    b'21': b'0.000324',
    b'22': b'88.88',
    b'23': b'77.77',
}
EXPECTED_REDIS_CATEGORIES_V2_B1 = {
    b'11': b'0.00003669590106785072',
    b'12': b'66.66',
    b'13': b'77.77',
}
EXPECTED_REDIS_CATEGORIES_V2_B2 = {
    b'21': b'55.55',
    b'22': b'66.66',
    b'23': b'77.77',
}

# Redis format
# scores:brands:<yt_table_name>:<brand_id> <item_id> <value>
REDIS_BRANDS_PREFIX_KEY = 'scores:brands'
# scores:updated:products <yt_table_name> <revision>
REDIS_UPDATED_PRODUCTS_KEY = 'scores:updated:products'
# scores:updated:categories <yt_table_name> <revision>
REDIS_UPDATED_CATEGORIES_KEY = 'scores:updated:categories'

PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED = (
    'eats_products::products-scoring-update-periodic-finished'
)

PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}


def build_yt_products_scoring(yt_table_name, yt_table_path):
    return {
        'period_minutes': 20,
        'batch_size': 1000,
        'rows_limit': 1000000,
        'tables': [{'name': yt_table_name, 'yt_path': yt_table_path}],
        'categories_tables': [],
    }


def build_yt_categories_scoring(yt_table_name, yt_table_path):
    return {
        'period_minutes': 20,
        'batch_size': 1000,
        'rows_limit': 1000000,
        'tables': [],
        'categories_tables': [
            {'name': yt_table_name, 'yt_path': yt_table_path},
        ],
    }


def build_yt_table_schema(yt_table_path):
    return {
        'path': yt_table_path,
        'attributes': {
            'optimize_for': 'lookup',
            'dynamic': False,
            'schema': [
                {'name': 'brand_id', 'type': 'int64'},
                {'name': 'item_id', 'type': 'string'},
                {'name': 'score', 'type': 'double'},
            ],
        },
    }


def build_redis_key(yt_table_name, brand_id):
    return REDIS_BRANDS_PREFIX_KEY + ':' + yt_table_name + ':' + str(brand_id)


def compare_items_scoring(dict_items_lhs, dict_items_rhs, epsilon=0.000001):
    len_items = len(dict_items_lhs)
    assert len_items == len(dict_items_rhs)
    sort_list_items_lhs = sorted(dict_items_lhs.items())
    sort_list_items_rhs = sorted(dict_items_rhs.items())
    # iterate by lists of tuples
    for i in range(len_items):
        assert len(sort_list_items_lhs[i]) == len(sort_list_items_rhs[i])
        # check item id
        assert sort_list_items_lhs[i][0] == sort_list_items_rhs[i][0]
        # check score
        score_lhs = decimal.Decimal(sort_list_items_lhs[i][1].decode('utf-8'))
        score_rhs = decimal.Decimal(sort_list_items_rhs[i][1].decode('utf-8'))
        assert abs(score_lhs - score_rhs) <= epsilon


@dataclasses.dataclass
class NomenclatureCategory:
    category_id: int
    name: str
    sort_order: int
    parent_id: Optional[int] = None
    is_custom: bool = False


@dataclasses.dataclass
class ProductsCategory:
    category_id: int
    name: str
    show_in: List
    parent_id: Optional[int] = None

    @property
    def category_uid(self):
        return str(self.category_id)


def build_nomenclature_categories(nomenclature_categories):
    def build_core_category(category_id):
        return 'category_id_' + str(category_id)

    categories_data = []
    for category in nomenclature_categories:
        category_data = {
            'available': True,
            'id': build_core_category(category.category_id),
            'images': [{'url': 'img_url', 'sort_order': 0, 'hash': '0'}],
            'items': [],
            'name': category.name,
            'public_id': category.category_id,
            'sort_order': category.sort_order,
            'is_custom': category.is_custom,
        }
        if category.parent_id is not None:
            category_data['parent_id'] = build_core_category(
                category.parent_id,
            )
            category_data['parent_public_id'] = category.parent_id
        categories_data.append(category_data)
    return {'categories': categories_data}


def build_products_categories(products_categories):
    categories_data = []
    for category in products_categories:
        category_data = {
            'available': True,
            'gallery': [{'url': 'img_url/{w}x{h}', 'type': 'tile'}],
            'id': category.category_id,
            'uid': category.category_uid,
            'items': [],
            'name': category.name,
            'parentId': category.parent_id,
            'schedule': None,
            'show_in': category.show_in,
        }
        if category.parent_id:
            category_data['parent_uid'] = str(category.parent_id)
        categories_data.append(category_data)
    return {'categories': categories_data}


@pytest.mark.yt(
    schemas=[YT_TABLE_SCHEMAS],
    static_table_data=[YT_TABLE_V1_DATA, YT_TABLE_V2_DATA],
)
@pytest.mark.parametrize(
    'batch_size',
    [
        pytest.param(2, id='yt batch size 2'),
        pytest.param(100, id='yt batch size 100'),
    ],
)
async def test_products_scoring(
        taxi_eats_products,
        taxi_config,
        testpoint,
        redis_store,
        yt_apply,
        batch_size,
):
    # Тест проверяет, что данные читаются из двух таблиц YT,
    # заданных в конфигурации и записываются в Redis.
    # Дополнительно проверяется работа порционного чтения из YT.

    config = build_yt_products_scoring(YT_TABLE_V1, YT_TABLE_V1_PATH)
    config['tables'].append({'name': YT_TABLE_V2, 'yt_path': YT_TABLE_V2_PATH})
    config['batch_size'] = batch_size
    taxi_config.set(EATS_PRODUCTS_YT_PRODUCTS_SCORING=config)

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    expected_redis_data_updated = {
        bytes(YT_TABLE_V1, 'utf-8'),
        bytes(YT_TABLE_V2, 'utf-8'),
    }

    assert redis_store.exists(REDIS_UPDATED_PRODUCTS_KEY)
    redis_hgetall_updated = redis_store.hgetall(REDIS_UPDATED_PRODUCTS_KEY)
    assert sorted(redis_hgetall_updated.keys()) == sorted(
        expected_redis_data_updated,
    )

    # YT_TABLE_V1
    brand_id = 1
    assert redis_store.exists(build_redis_key(YT_TABLE_V1, brand_id))
    redis_hgetall_table_v1_brand_1 = redis_store.hgetall(
        build_redis_key(YT_TABLE_V1, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v1_brand_1, EXPECTED_REDIS_PRODUCTS_V1_B1,
    )
    brand_id = 2
    assert redis_store.exists(build_redis_key(YT_TABLE_V1, brand_id))
    redis_hgetall_table_v1_brand_2 = redis_store.hgetall(
        build_redis_key(YT_TABLE_V1, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v1_brand_2, EXPECTED_REDIS_PRODUCTS_V1_B2,
    )

    # YT_TABLE_V2
    brand_id = 1
    assert redis_store.exists(build_redis_key(YT_TABLE_V2, brand_id))
    redis_hgetall_table_v2_brand_1 = redis_store.hgetall(
        build_redis_key(YT_TABLE_V2, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v2_brand_1, EXPECTED_REDIS_PRODUCTS_V2_B1,
    )
    brand_id = 2
    assert redis_store.exists(build_redis_key(YT_TABLE_V2, brand_id))
    redis_hgetall_table_v2_brand_2 = redis_store.hgetall(
        build_redis_key(YT_TABLE_V2, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v2_brand_2, EXPECTED_REDIS_PRODUCTS_V2_B2,
    )


@pytest.mark.yt(
    schemas=[YT_TABLE_SCHEMAS],
    static_table_data=[YT_TABLE_V1_DATA, YT_TABLE_V2_DATA],
)
async def test_products_scoring_yt_limit(
        taxi_eats_products, taxi_config, testpoint, redis_store, yt_apply,
):
    # Тест проверяет, что данные читаются из таблицы YT,
    # и записываются в Redis с учетом указанного в конфигурации лимита.

    config = build_yt_products_scoring(YT_TABLE_V1, YT_TABLE_V1_PATH)
    config['rows_limit'] = 6
    taxi_config.set(EATS_PRODUCTS_YT_PRODUCTS_SCORING=config)

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    expected_redis_data_updated = {bytes(YT_TABLE_V1, 'utf-8')}

    assert redis_store.exists(REDIS_UPDATED_PRODUCTS_KEY)
    redis_hgetall_updated = redis_store.hgetall(REDIS_UPDATED_PRODUCTS_KEY)
    assert redis_hgetall_updated.keys() == expected_redis_data_updated

    expected_redis_data_table_v1_b1 = {
        b'item_id_11': b'0.0001590155712940198',
        b'item_id_12': b'0.000012231967022616907',
        b'item_id_13': b'0.000000000000000000001',
        b'item_id_14': b'66.66',
        b'item_id_15': b'55.55',
    }
    expected_redis_data_table_v1_b2 = {b'item_id_21': b'99.99'}

    brand_id = 1
    assert redis_store.exists(build_redis_key(YT_TABLE_V1, brand_id))
    redis_hgetall_table_v1_brand_1 = redis_store.hgetall(
        build_redis_key(YT_TABLE_V1, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v1_brand_1, expected_redis_data_table_v1_b1,
    )
    brand_id = 2
    assert redis_store.exists(build_redis_key(YT_TABLE_V1, brand_id))
    redis_hgetall_table_v1_brand_2 = redis_store.hgetall(
        build_redis_key(YT_TABLE_V1, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v1_brand_2, expected_redis_data_table_v1_b2,
    )


@pytest.mark.yt(
    schemas=[YT_TABLE_SCHEMAS],
    static_table_data=[YT_TABLE_V1_DATA, YT_TABLE_V2_DATA],
)
async def test_products_scoring_disable(
        taxi_eats_products, taxi_config, testpoint, redis_store, yt_apply,
):
    # Тест проверяет, что данные не читаются из таблицы YT,
    # если она не указана в настройках.

    config = build_yt_products_scoring(YT_TABLE_V1, YT_TABLE_V1_PATH)
    config['tables'] = []
    taxi_config.set(EATS_PRODUCTS_YT_PRODUCTS_SCORING=config)

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert not redis_store.exists(REDIS_UPDATED_PRODUCTS_KEY)


@pytest.mark.yt(
    schemas=[build_yt_table_schema(YT_TABLE_V1_PATH)],
    static_table_data=[{'path': YT_TABLE_V1_PATH, 'values': []}],
)
@pytest.mark.config(
    EATS_PRODUCTS_YT_PRODUCTS_SCORING=build_yt_products_scoring(
        YT_TABLE_V1, YT_TABLE_V1_PATH,
    ),
)
async def test_products_scoring_empty_yt_table(
        taxi_eats_products, testpoint, redis_store, yt_apply,
):
    # Тест проверяет работу с пустой таблицей YT.

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert not redis_store.exists(REDIS_UPDATED_PRODUCTS_KEY)


YT_TABLE_V222 = 'yt_table_v222'
YT_TABLE_V222_PATH = '//yt/products_scoring_v222'
YT_TABLE_V333_PATH = '//yt/products_scoring_v333'


@pytest.mark.yt(
    schemas=[build_yt_table_schema(YT_TABLE_V333_PATH)],
    static_table_data=[{'path': YT_TABLE_V333_PATH, 'values': []}],
)
@pytest.mark.config(
    EATS_PRODUCTS_YT_PRODUCTS_SCORING=build_yt_products_scoring(
        YT_TABLE_V222, YT_TABLE_V222_PATH,
    ),
)
async def test_products_scoring_not_exist_yt_table(
        taxi_eats_products, testpoint, redis_store, yt_apply,
):
    # Тест проверяет работу с несуществующей таблицей YT,
    # заданной в конфигурации.

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert not redis_store.exists(REDIS_UPDATED_PRODUCTS_KEY)


@pytest.mark.yt(
    schemas=[
        {
            'path': YT_TABLE_V1_PATH,
            'attributes': {
                'schema': [
                    {'name': 'item_id', 'type': 'string'},
                    {'name': 'brand_id', 'type': 'int64'},
                ],
            },
        },
    ],
    static_table_data=[
        {
            'path': YT_TABLE_V1_PATH,
            'values': [{'item_id': 'id_1', 'brand_id': 1}],
        },
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_YT_PRODUCTS_SCORING=build_yt_products_scoring(
        YT_TABLE_V1, YT_TABLE_V1_PATH,
    ),
)
async def test_products_scoring_bad_yt_table(
        taxi_eats_products, testpoint, redis_store, yt_apply,
):
    # Тест проверяет работу с таблицей YT с неподдерживаемым форматом.

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert not redis_store.exists(REDIS_UPDATED_PRODUCTS_KEY)


@pytest.mark.yt(
    schemas=[build_yt_table_schema(YT_TABLE_V3_PATH)],
    static_table_data=[YT_TABLE_V3_DATA],
)
@pytest.mark.config(
    EATS_PRODUCTS_YT_PRODUCTS_SCORING=build_yt_products_scoring(
        YT_TABLE_V3, YT_TABLE_V3_PATH,
    ),
)
@utils.PARAMETRIZE_CATEGORY_PRODUCTS_VERSION
@pytest.mark.parametrize(
    'products_response',
    [
        pytest.param('products_response_default_sort.json', id='no_exp'),
        pytest.param(
            'products_response_scoring_sort.json',
            marks=experiments.products_scoring(),
            id='exp_on',
        ),
        pytest.param(
            'products_response_default_sort.json',
            marks=experiments.products_scoring(enabled=False),
            id='exp_off',
        ),
    ],
)
async def test_products_scoring_sort(
        taxi_eats_products,
        mock_nomenclature_for_v2_menu_goods,
        testpoint,
        yt_apply,
        load_json,
        products_response,
        add_place_products_mapping,
        category_products_version,
):
    # Тест проверяет, что товары сортируются согласно заданному скорингу
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_3',
                core_id=3,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            ),
            conftest.ProductMapping(
                origin_id='item_id_4',
                core_id=4,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            ),
            conftest.ProductMapping(
                origin_id='item_id_5',
                core_id=5,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
            ),
            conftest.ProductMapping(
                origin_id='item_id_6',
                core_id=6,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b600',
            ),
            conftest.ProductMapping(
                origin_id='item_id_7',
                core_id=7,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
            ),
            conftest.ProductMapping(
                origin_id='item_id_9',
                core_id=9,
                public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b900',
            ),
        ],
    )

    category_1 = conftest.CategoryMenuGoods(
        public_id='101',
        name='Овощи и фрукты',
        origin_id='1',
        sort_order=3,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )
    category_5 = conftest.CategoryMenuGoods(
        public_id='105',
        name='Овощи',
        origin_id='5',
        sort_order=5,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )
    category_5.add_child_category(
        conftest.CategoryMenuGoods(
            public_id='109',
            name='Томаты',
            origin_id='9',
            sort_order=9,
            images=[('image_url_1', 1), ('image_url_2', 0)],
        ),
    )
    category_6 = conftest.CategoryMenuGoods(
        public_id='106',
        name='Фрукты',
        origin_id='6',
        sort_order=6,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )

    category_6.add_product(cats.DEFAULT_PRODUCTS['item_id_3'], 6)
    category_6.add_product(cats.DEFAULT_PRODUCTS['item_id_4'], 1)
    category_6.add_product(cats.DEFAULT_PRODUCTS['item_id_5'], 3)

    category_1.add_child_category(category_5)
    category_1.add_child_category(category_6)

    place = conftest.PlaceMenuGoods(place_id=1, slug='slug', brand_id=1)
    place.add_root_category(category_1)
    mock_nomenclature_for_v2_menu_goods.set_place(place)

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 101
    products_request['maxDepth'] = 3

    expected_response = {'meta': None, 'payload': load_json(products_response)}

    response = (
        await mock_nomenclature_for_v2_menu_goods.invoke_menu_goods_basic(
            products_request,
            integration_version=category_products_version,
            use_version_for_all=False,
        )
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.yt(
    schemas=[YT_TABLE_CATEGORIES_SCHEMAS],
    static_table_data=[
        YT_TABLE_CATEGORIES_V1_DATA,
        YT_TABLE_CATEGORIES_V2_DATA,
    ],
)
@pytest.mark.parametrize(
    'batch_size',
    [
        pytest.param(2, id='yt batch size 2'),
        pytest.param(100, id='yt batch size 100'),
    ],
)
async def test_categories_scoring(
        taxi_eats_products,
        taxi_config,
        testpoint,
        redis_store,
        yt_apply,
        batch_size,
):
    # Тест проверяет, что данные скоринга категорий читаются из двух
    # таблиц YT, заданных в конфигурации и записываются в Redis.

    config = build_yt_categories_scoring(
        YT_TABLE_CATEGORIES_V1, YT_TABLE_CATEGORIES_V1_PATH,
    )
    config['categories_tables'].append(
        {
            'name': YT_TABLE_CATEGORIES_V2,
            'yt_path': YT_TABLE_CATEGORIES_V2_PATH,
        },
    )
    config['batch_size'] = batch_size
    taxi_config.set(EATS_PRODUCTS_YT_PRODUCTS_SCORING=config)

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    # updated tables
    expected_redis_data_updated = {
        bytes(YT_TABLE_CATEGORIES_V1, 'utf-8'),
        bytes(YT_TABLE_CATEGORIES_V2, 'utf-8'),
    }

    assert redis_store.exists(REDIS_UPDATED_CATEGORIES_KEY)
    redis_hgetall_updated = redis_store.hgetall(REDIS_UPDATED_CATEGORIES_KEY)
    assert sorted(redis_hgetall_updated.keys()) == sorted(
        expected_redis_data_updated,
    )

    # data from table YT_TABLE_CATEGORIES_V1
    brand_id = 1
    assert redis_store.exists(
        build_redis_key(YT_TABLE_CATEGORIES_V1, brand_id),
    )
    redis_hgetall_table_v1_brand_1 = redis_store.hgetall(
        build_redis_key(YT_TABLE_CATEGORIES_V1, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v1_brand_1, EXPECTED_REDIS_CATEGORIES_V1_B1,
    )

    brand_id = 2
    assert redis_store.exists(
        build_redis_key(YT_TABLE_CATEGORIES_V1, brand_id),
    )
    redis_hgetall_table_v1_brand_2 = redis_store.hgetall(
        build_redis_key(YT_TABLE_CATEGORIES_V1, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v1_brand_2, EXPECTED_REDIS_CATEGORIES_V1_B2,
    )

    # data from table YT_TABLE_CATEGORIES_V2
    brand_id = 1
    assert redis_store.exists(
        build_redis_key(YT_TABLE_CATEGORIES_V2, brand_id),
    )
    redis_hgetall_table_v2_brand_1 = redis_store.hgetall(
        build_redis_key(YT_TABLE_CATEGORIES_V2, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v2_brand_1, EXPECTED_REDIS_CATEGORIES_V2_B1,
    )
    brand_id = 2
    assert redis_store.exists(
        build_redis_key(YT_TABLE_CATEGORIES_V2, brand_id),
    )
    redis_hgetall_table_v2_brand_2 = redis_store.hgetall(
        build_redis_key(YT_TABLE_CATEGORIES_V2, brand_id),
    )
    compare_items_scoring(
        redis_hgetall_table_v2_brand_2, EXPECTED_REDIS_CATEGORIES_V2_B2,
    )


@pytest.mark.yt(
    schemas=[YT_TABLE_CATEGORIES_SCHEMAS],
    static_table_data=[YT_TABLE_CATEGORIES_V3_DATA],
)
@pytest.mark.config(
    EATS_PRODUCTS_YT_PRODUCTS_SCORING=build_yt_categories_scoring(
        YT_TABLE_CATEGORIES_V3, YT_TABLE_CATEGORIES_V3_PATH,
    ),
)
@pytest.mark.parametrize(
    'nomenclature_response, expected_products_response',
    [
        pytest.param(
            build_nomenclature_categories(
                [
                    NomenclatureCategory(0, 'Фрукты', 0),
                    NomenclatureCategory(1, 'Овощи', 1),
                    NomenclatureCategory(2, 'Молоко', 2),
                    NomenclatureCategory(10, 'Кастом', 3, None, True),
                ],
            ),
            build_products_categories(
                [
                    ProductsCategory(10, 'Кастом', ['banner_carousel']),
                    ProductsCategory(0, 'Фрукты', ['categories_carousel']),
                    ProductsCategory(1, 'Овощи', ['categories_carousel']),
                    ProductsCategory(2, 'Молоко', ['categories_carousel']),
                ],
            ),
            id='no_exp',
        ),
        pytest.param(
            build_nomenclature_categories(
                [
                    NomenclatureCategory(0, 'Фрукты', 0),
                    NomenclatureCategory(1, 'Овощи', 1),
                    NomenclatureCategory(2, 'Молоко', 2),
                ],
            ),
            build_products_categories(
                [
                    ProductsCategory(0, 'Фрукты', ['categories_carousel']),
                    ProductsCategory(1, 'Овощи', ['categories_carousel']),
                    ProductsCategory(2, 'Молоко', ['categories_carousel']),
                ],
            ),
            marks=experiments.categories_scoring(enabled=False),
            id='exp_off',
        ),
        pytest.param(
            build_nomenclature_categories(
                [
                    NomenclatureCategory(0, 'Фрукты', 0),
                    NomenclatureCategory(1, 'Овощи', 1),
                    NomenclatureCategory(2, 'Молоко', 2),
                ],
            ),
            build_products_categories(
                [
                    ProductsCategory(2, 'Молоко', ['categories_carousel']),
                    ProductsCategory(1, 'Овощи', ['categories_carousel']),
                    ProductsCategory(0, 'Фрукты', ['categories_carousel']),
                ],
            ),
            marks=experiments.categories_scoring(),
            id='exp_on_default',
        ),
        pytest.param(
            build_nomenclature_categories(
                [
                    NomenclatureCategory(0, 'Фрукты', 0),
                    NomenclatureCategory(1, 'Овощи', 1),
                    NomenclatureCategory(2, 'Молочные продукты', 2),
                    NomenclatureCategory(3, 'Сливки', 0, 2),
                    NomenclatureCategory(4, 'Творог', 1, 2),
                ],
            ),
            build_products_categories(
                [
                    ProductsCategory(
                        2, 'Молочные продукты', ['categories_carousel'],
                    ),
                    ProductsCategory(1, 'Овощи', ['categories_carousel']),
                    ProductsCategory(0, 'Фрукты', ['categories_carousel']),
                    ProductsCategory(4, 'Творог', ['categories_carousel'], 2),
                    ProductsCategory(3, 'Сливки', ['categories_carousel'], 2),
                ],
            ),
            marks=experiments.categories_scoring(),
            id='exp_on_with_depth',
        ),
        pytest.param(
            build_nomenclature_categories(
                [
                    NomenclatureCategory(10, 'Категория без скоринга', 0),
                    NomenclatureCategory(1, 'Овощи', 1),
                    NomenclatureCategory(2, 'Молоко', 2),
                ],
            ),
            build_products_categories(
                [
                    ProductsCategory(2, 'Молоко', ['categories_carousel']),
                    ProductsCategory(1, 'Овощи', ['categories_carousel']),
                    ProductsCategory(
                        10, 'Категория без скоринга', ['categories_carousel'],
                    ),
                ],
            ),
            marks=experiments.categories_scoring(),
            id='exp_on_missing_scores',
        ),
        pytest.param(
            build_nomenclature_categories(
                [
                    NomenclatureCategory(0, 'Фрукты', 0),
                    NomenclatureCategory(1, 'Овощи', 1),
                    NomenclatureCategory(
                        5, 'Кастомная категория', -1, None, True,
                    ),
                    NomenclatureCategory(2, 'Молоко', 2),
                    NomenclatureCategory(
                        6, 'Кастомная категория 2', 2, None, True,
                    ),
                ],
            ),
            build_products_categories(
                [
                    ProductsCategory(
                        5, 'Кастомная категория', ['banner_carousel'],
                    ),
                    ProductsCategory(
                        6, 'Кастомная категория 2', ['banner_carousel'],
                    ),
                    ProductsCategory(2, 'Молоко', ['categories_carousel']),
                    ProductsCategory(1, 'Овощи', ['categories_carousel']),
                    ProductsCategory(0, 'Фрукты', ['categories_carousel']),
                ],
            ),
            marks=experiments.categories_scoring(),
            id='exp_on_custom_categories',
        ),
        pytest.param(
            build_nomenclature_categories(
                [
                    NomenclatureCategory(5, 'Фрукты', 2),
                    NomenclatureCategory(6, 'Овощи', 0),
                    NomenclatureCategory(7, 'Молоко', 1),
                ],
            ),
            build_products_categories(
                [
                    ProductsCategory(7, 'Молоко', ['categories_carousel']),
                    ProductsCategory(6, 'Овощи', ['categories_carousel']),
                    ProductsCategory(5, 'Фрукты', ['categories_carousel']),
                ],
            ),
            marks=experiments.categories_scoring(),
            id='exp_on_equal_scoring',
        ),
    ],
)
async def test_categories_scoring_sort(
        taxi_eats_products,
        mockserver,
        testpoint,
        yt_apply,
        load_json,
        nomenclature_response,
        expected_products_response,
):
    # Тест проверяет, что категории сортируются согласно заданному скорингу

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['maxDepth'] = 3

    expected_response = {'meta': None, 'payload': expected_products_response}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return nomenclature_response

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.yt(
    schemas=[YT_TABLE_MIXED_SCHEMAS],
    static_table_data=[YT_TABLE_V1_DATA, YT_TABLE_CATEGORIES_V2_DATA],
)
async def test_products_and_categories_scoring(
        taxi_eats_products, taxi_config, testpoint, redis_store, yt_apply,
):
    # Тест проверяет, что данные скоринга и для продуктов, и для категорий
    # читаются из таблиц YT, заданных в конфигурации, и записываются в Redis.

    config = {
        'period_minutes': 20,
        'batch_size': 1000,
        'rows_limit': 1000000,
        'tables': [{'name': YT_TABLE_V1, 'yt_path': YT_TABLE_V1_PATH}],
        'categories_tables': [
            {
                'name': YT_TABLE_CATEGORIES_V2,
                'yt_path': YT_TABLE_CATEGORIES_V2_PATH,
            },
        ],
    }
    taxi_config.set(EATS_PRODUCTS_YT_PRODUCTS_SCORING=config)

    @testpoint(PRODUCTS_SCORING_UPDATE_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    # updated products
    expected_updated_products = {bytes(YT_TABLE_V1, 'utf-8')}
    assert redis_store.exists(REDIS_UPDATED_PRODUCTS_KEY)
    hgetall_updated_products = redis_store.hgetall(REDIS_UPDATED_PRODUCTS_KEY)
    assert sorted(hgetall_updated_products.keys()) == sorted(
        expected_updated_products,
    )

    # updated categories
    expected_updated_categories = {bytes(YT_TABLE_CATEGORIES_V2, 'utf-8')}
    assert redis_store.exists(REDIS_UPDATED_CATEGORIES_KEY)
    hgetall_updated_categories = redis_store.hgetall(
        REDIS_UPDATED_CATEGORIES_KEY,
    )
    assert sorted(hgetall_updated_categories.keys()) == sorted(
        expected_updated_categories,
    )

    # products data
    brand_id = 1
    assert redis_store.exists(build_redis_key(YT_TABLE_V1, brand_id))
    hgetall_products_brand_1 = redis_store.hgetall(
        build_redis_key(YT_TABLE_V1, brand_id),
    )
    compare_items_scoring(
        hgetall_products_brand_1, EXPECTED_REDIS_PRODUCTS_V1_B1,
    )

    brand_id = 2
    assert redis_store.exists(build_redis_key(YT_TABLE_V1, brand_id))
    hgetall_products_brand_2 = redis_store.hgetall(
        build_redis_key(YT_TABLE_V1, brand_id),
    )
    compare_items_scoring(
        hgetall_products_brand_2, EXPECTED_REDIS_PRODUCTS_V1_B2,
    )

    # categories data
    brand_id = 1
    assert redis_store.exists(
        build_redis_key(YT_TABLE_CATEGORIES_V2, brand_id),
    )
    hgetall_categories_brand_1 = redis_store.hgetall(
        build_redis_key(YT_TABLE_CATEGORIES_V2, brand_id),
    )
    compare_items_scoring(
        hgetall_categories_brand_1, EXPECTED_REDIS_CATEGORIES_V2_B1,
    )

    brand_id = 2
    assert redis_store.exists(
        build_redis_key(YT_TABLE_CATEGORIES_V2, brand_id),
    )
    hgetall_categories_brand_2 = redis_store.hgetall(
        build_redis_key(YT_TABLE_CATEGORIES_V2, brand_id),
    )
    compare_items_scoring(
        hgetall_categories_brand_2, EXPECTED_REDIS_CATEGORIES_V2_B2,
    )
