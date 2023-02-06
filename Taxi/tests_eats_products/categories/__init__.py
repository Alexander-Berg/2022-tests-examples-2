import copy

from tests_eats_products import conftest

DEFAULT_PRODUCTS = {
    'item_id_1': conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        name='Огурцы',
        origin_id='item_id_1',
        measure=(1, 'KGRM'),
        price=4.1,
        description='Описание Огурцы',
        images=[('url_1', 0), ('url_2', 0)],
        in_stock=10,
        is_catch_weight=True,
    ),
    'item_id_2': conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
        name='Помидоры',
        origin_id='item_id_2',
        measure=(1, 'KGRM'),
        price=6.5,
        description='Описание Помидоры',
        images=[('url_1', 0), ('url_2', 0)],
        in_stock=20,
        is_catch_weight=True,
    ),
    'item_id_3': conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
        name='Яблоки',
        origin_id='item_id_3',
        measure=(1, 'KGRM'),
        price=3,
        old_price=5,
        description='Описание Яблоки',
        images=[('url_1', 0), ('url_2', 0)],
        is_catch_weight=True,
    ),
    'item_id_4': conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
        name='Апельсины',
        origin_id='item_id_4',
        price=4,
        description='Описание Апельсины',
        images=[('url_1', 0), ('url_2', 0)],
        in_stock=25,
        is_catch_weight=True,
    ),
    'item_id_5': conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
        name='Бананы',
        origin_id='item_id_5',
        price=3,
        description='Описание Бананы',
        measure=(1500, 'GRM'),
        images=[('url_1', 0), ('url_2', 0)],
        in_stock=30,
        is_catch_weight=True,
    ),
    'item_id_6': conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Молоко',
        origin_id='item_id_6',
        measure=(1, 'LT'),
        price=10,
        description='Описание Молоко',
        images=[('url_1', 0), ('url_2', 0)],
        is_catch_weight=True,
    ),
    'item_id_7': conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
        name='Творог',
        origin_id='item_id_7',
        is_available=False,
        is_catch_weight=True,
    ),
    'item_id_8': conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b008',
        name='Батон',
        origin_id='item_id_8',
        is_available=False,
        is_catch_weight=True,
    ),
}


def _make_category_101():
    return conftest.CategoryMenuGoods(
        public_id='101',
        name='Овощи и фрукты',
        origin_id='1',
        sort_order=3,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )


def _make_category_102():
    category = conftest.CategoryMenuGoods(
        public_id='102',
        name='Молочные продукты',
        origin_id='2',
        sort_order=4,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )

    category.add_product(DEFAULT_PRODUCTS['item_id_6'], 3)

    return category


def _make_category_103():
    category = conftest.CategoryMenuGoods(
        public_id='103',
        name='Хлеб',
        origin_id='3',
        sort_order=5,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )

    category.add_product(DEFAULT_PRODUCTS['item_id_8'], 5)

    return category


def _make_category_104():
    return conftest.CategoryMenuGoods(
        public_id='104',
        name='Здоровье',
        origin_id='4',
        sort_order=6,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )


def _make_category_105():
    category = conftest.CategoryMenuGoods(
        public_id='105',
        name='Овощи',
        origin_id='5',
        sort_order=4,
        images=[('image_url_1', 1), ('image_url_2', 0)],
        is_available=False,
    )

    category.add_product(DEFAULT_PRODUCTS['item_id_1'], 1)
    category.add_product(DEFAULT_PRODUCTS['item_id_2'], 2)

    root_category = _make_category_101()
    root_category.add_child_category(category)

    return category


def _make_category_106(discount=False):
    category = conftest.CategoryMenuGoods(
        public_id='106',
        name='Фрукты',
        origin_id='6',
        sort_order=2,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )
    product_3 = copy.deepcopy(DEFAULT_PRODUCTS['item_id_3'])
    product_4 = copy.deepcopy(DEFAULT_PRODUCTS['item_id_4'])
    product_5 = copy.deepcopy(DEFAULT_PRODUCTS['item_id_5'])

    if discount:
        product_3.price = 299
        product_3.old_price = 300
        product_4.price = 120
        product_4.old_price = 130
        product_5.price = 100
        product_5.old_price = 150

    category.add_product(product_3, 3)
    category.add_product(product_4, 1)
    category.add_product(product_5, 2)

    root_category = _make_category_101()
    root_category.add_child_category(category)

    return category


def _make_category_107():
    category = conftest.CategoryMenuGoods(
        public_id='107',
        name='Маски',
        origin_id='7',
        sort_order=7,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )

    root_category = _make_category_104()
    root_category.add_child_category(category)

    return category


def _make_category_108():
    category = conftest.CategoryMenuGoods(
        public_id='108',
        name='Фрукты',
        origin_id='8',
        sort_order=2,
        images=[('image_url_1', 1), ('image_url_2', 2), ('image_url_3', 3)],
    )

    category.add_product(
        conftest.ProductMenuGoods(
            public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b009',
            name='Яблоки',
            origin_id='item_id_9',
            description='Описание Яблоки',
            images=[('url_1', 100), ('url_2', 200)],
        ),
    )

    root_category = _make_category_101()
    root_category.add_child_category(category)

    return category


def make_category(category_id, **kwargs):
    return globals()[f'_make_category_{category_id}'](**kwargs)
