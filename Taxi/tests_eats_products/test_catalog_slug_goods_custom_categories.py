# pylint: disable=too-many-lines
from typing import Optional

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}


async def get_goods_response(taxi_eats_products, headers=None):
    return await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=BASE_REQUEST, headers=headers or {},
    )


@pytest.mark.parametrize('nmn_integration_version', ['v1', 'v2'])
async def test_custom_categories_sorting(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='1',
        name='partner',
        origin_id='category_origin_id',
        sort_order=5,
    )
    root_cat_100 = conftest.CategoryMenuGoods(
        public_id='100',
        name='custom_cat',
        origin_id='category_origin_id',
        sort_order=-3,
        category_type='custom_promo',
    )
    cat_200 = conftest.CategoryMenuGoods(
        public_id='200',
        name='custom_cat',
        origin_id='category_origin_id',
        sort_order=-2,
        category_type='custom_promo',
    )
    root_cat_100.add_child_category(cat_200)
    root_cat_300 = conftest.CategoryMenuGoods(
        public_id='300',
        name='custom_cat',
        origin_id='category_origin_id',
        sort_order=11,
        category_type='custom_promo',
    )
    cat_8 = conftest.CategoryMenuGoods(
        public_id='8',
        name='partner',
        origin_id='category_origin_id',
        sort_order=6,
    )
    root_cat_3 = conftest.CategoryMenuGoods(
        public_id='3',
        name='base',
        origin_id='category_origin_id',
        sort_order=8,
        category_type='custom_base',
    )
    root_cat_4 = conftest.CategoryMenuGoods(
        public_id='4',
        name='base',
        origin_id='category_origin_id',
        sort_order=9,
        category_type='custom_base',
    )
    root_cat_1.add_child_category(cat_8)
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(root_cat_1)
    place.add_root_category(root_cat_100)
    place.add_root_category(root_cat_300)
    place.add_root_category(root_cat_3)
    place.add_root_category(root_cat_4)
    mock_nomenclature_context.set_place(place)
    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        BASE_REQUEST, integration_version=nmn_integration_version,
    )
    assert response.status_code == 200

    # Check categories mapping.
    categories = [
        (c['id'], c['parentId'])
        for c in response.json()['payload']['categories']
    ]
    assert categories == [
        (100, None),
        (3, None),
        (4, None),
        (300, None),
        (1, None),
        (200, 100),
        (8, 1),
    ]


OTHER_CATEGORIES = [6, 5, 1, 2, 800, 700, 600, 8, 7, 3, 4, 1000, 900]


@pytest.mark.parametrize(
    ('first_result', 'second_result'),
    [
        pytest.param(
            [500, 400, 300, 200, 100] + OTHER_CATEGORIES,
            [500, 400, 300, 200, 100] + OTHER_CATEGORIES,
            marks=(experiments.CUSTOM_CATEGORIES_RANDOMIZATION_DISABLED),
        ),
        pytest.param(
            [100, 400, 300, 500, 200] + OTHER_CATEGORIES,
            [200, 300, 100, 400, 500] + OTHER_CATEGORIES,
            marks=(experiments.CUSTOM_CATEGORIES_RANDOMIZATION_ENABLED),
        ),
    ],
)
@pytest.mark.now('2019-01-01T00:00:00+0300')
async def test_custom_categories_sorting_randomization(
        taxi_eats_products,
        mockserver,
        mocked_time,
        first_result,
        second_result,
):
    """
    Тест проверяет рандомизацию кастомных категорий, кроме мастер-дерева,
    и кроме дочерних категорий для кастомных.

    Пояснение результата
    [500, 400, 300, 200, 100, 6, 5, 1, 2, 800, 700, 600, 8, 7, 3, 4, 1000, 900]

    - сначала идут топ-левел категории (и обычные и кастомные)
    - сначала идут кастомные и категории мастер-дерева, потому что у них
      отрицательный sort-order
    - потом идут остальные
    """

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        current_sort_order = 0

        def make_category(
                public_id: int,
                parent_public_id: Optional[int] = None,
                custom: bool = False,
                base: bool = True,
        ):
            nonlocal current_sort_order
            category_json = {
                'id': f'nmn-{public_id}',
                'public_id': public_id,
                'name': f'Category {public_id}',
                'available': True,
                'is_custom': custom,
                'is_base': base,
                'images': [],
                'items': [],
            }

            if custom:
                # Подражаем поведению прода - кастомные категории
                # имеют отрицательный sort-order
                category_json['sort_order'] = -current_sort_order
            else:
                category_json['sort_order'] = current_sort_order
            current_sort_order += 1

            if parent_public_id:
                category_json['parent_id'] = f'nmn-{parent_public_id}'
                category_json['parent_public_id'] = parent_public_id
            return category_json

        categories = []

        master_tree_category = {'custom': True, 'base': True}
        custom_category = {'custom': True, 'base': False}

        # Обычные категории
        categories.append(make_category(1))
        categories.append(make_category(2))
        categories.append(make_category(3, 2))
        categories.append(make_category(4, 2))

        # Категории мастер-дерева
        categories.append(make_category(5, **master_tree_category))
        categories.append(make_category(6, **master_tree_category))
        categories.append(make_category(7, 6, **master_tree_category))
        categories.append(make_category(8, 6, **master_tree_category))

        # Кастомные категории верхнего уровня - только их надо рандомизировать
        categories.append(make_category(100, **custom_category))
        categories.append(make_category(200, **custom_category))
        categories.append(make_category(300, **custom_category))
        categories.append(make_category(400, **custom_category))
        categories.append(make_category(500, **custom_category))

        # Кастомные категории - дети
        categories.append(make_category(600, 100, **custom_category))
        categories.append(make_category(700, 200, **custom_category))
        categories.append(make_category(800, 300, **custom_category))

        # Кастомные категории - дети детей
        categories.append(make_category(900, 600, **custom_category))
        categories.append(make_category(1000, 600, **custom_category))

        return {'categories': categories}

    def categories_ids(response):
        return [c['id'] for c in response.json()['payload']['categories']]

    response = await get_goods_response(taxi_eats_products)
    assert categories_ids(response) == first_result

    # Спим одну минуту - остаемся в том же интервале
    mocked_time.sleep(60 * 1)
    await taxi_eats_products.invalidate_caches()

    response = await get_goods_response(taxi_eats_products)
    assert categories_ids(response) == first_result

    # Гарантированно попадаем в другой временной интервал (он равен 60 минутам)
    mocked_time.sleep(60 * 59)
    await taxi_eats_products.invalidate_caches()

    response = await get_goods_response(taxi_eats_products)
    assert categories_ids(response) == second_result
