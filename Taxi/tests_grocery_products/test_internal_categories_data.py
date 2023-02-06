import pytest


def _count_categories(pgsql):
    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(f"""SELECT COUNT(*) FROM products.virtual_categories;""")
    return cursor.fetchall()[0][0]


@pytest.mark.pgsql(
    'grocery_products', files=['categories.sql', 'refresh_views.sql'],
)
async def test_categories_data(pgsql, taxi_grocery_products):
    """ Check /internal/v1/products/v1/categories-data
    return three categories ordered by id """
    response = await taxi_grocery_products.post(
        '/internal/v1/products/v1/categories-data',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert categories == [
        {
            'alias': 'alias-1',
            'item_meta': '{ "meta-1": "meta-1" }',
            'subcategories': [
                {'category_id': 'subcategory-1-1'},
                {'category_id': 'subcategory-1-2'},
                {'category_id': 'subcategory-1-3'},
            ],
            'title_tanker_key': 'title_tanker_key-1',
            'virtual_category_id': 'virtual-category-1',
        },
        {
            'alias': 'alias-3',
            'item_meta': '{ "meta-3": "meta-3" }',
            'short_title_tanker_key': 'short_title_tanker_key-3',
            'subcategories': [
                {'category_id': 'subcategory-31'},
                {'category_id': 'subcategory-32'},
            ],
            'title_tanker_key': 'title_tanker_key-3',
            'virtual_category_id': 'virtual-category-3',
            'deep_link': 'category-deep-link',
        },
        {
            'alias': 'alias-4',
            'item_meta': '{ "meta-4": "meta-4" }',
            'short_title_tanker_key': 'short_title_tanker_key-4',
            'subcategories': [],
            'title_tanker_key': 'title_tanker_key-4',
            'virtual_category_id': 'virtual-category-4',
            'special_category': 'promo-caas',
        },
        {
            'alias': 'alias-z',
            'item_meta': '{ "meta-z": "meta-z" }',
            'subcategories': [
                {'category_id': 'subcategory-z'},
                {'category_id': 'subcategory-a'},
                {'category_id': 'subcategory-b'},
            ],
            'title_tanker_key': 'title_tanker_key-z',
            'virtual_category_id': 'virtual-category-z',
        },
    ]
    assert len(categories) == _count_categories(pgsql)


@pytest.mark.pgsql(
    'grocery_products', files=['categories.sql', 'refresh_views.sql'],
)
async def test_categories_data_chunked(
        pgsql, taxi_grocery_products, load_json,
):
    """ Check /internal/v1/products/v1/categories-data
    return three chunks of different categories sorted by id """
    response_len = [2, 2, 0]
    categories = []
    limit = 2
    cursor = 0
    for length in response_len:
        response = await taxi_grocery_products.post(
            '/internal/v1/products/v1/categories-data',
            json={'limit': limit, 'cursor': cursor},
        )

        assert response.status_code == 200
        if length == 0:
            assert cursor == response.json()['cursor']
        else:
            cursor = response.json()['cursor']
        assert len(response.json()['categories']) == length
        categories.extend(response.json()['categories'])

    categories_ids_set = set()
    prev_category_id = None
    for item in categories:
        category_id = item['virtual_category_id']
        categories_ids_set.add(category_id)
        if prev_category_id:
            assert category_id > prev_category_id
        prev_category_id = category_id

    assert len(categories) == len(categories_ids_set)
    assert len(categories) == sum(response_len)
    assert len(categories) == _count_categories(pgsql)


# удалить после LAVKAFRONT-3463, берем атрибут 'special_category'
# из конфига
@pytest.mark.pgsql(
    'grocery_products', files=['categories.sql', 'refresh_views.sql'],
)
@pytest.mark.config(
    GROCERY_PRODUCTS_SPECIAL_CATEGORY_MAP={
        'virtual-category-1': 'custom-special-category',
    },
)
async def test_special_category_by_config(taxi_grocery_products):
    """ Check /internal/v1/products/v1/categories-data
    return three categories ordered by id """
    response = await taxi_grocery_products.post(
        '/internal/v1/products/v1/categories-data',
        json={'limit': 1, 'cursor': 0},
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert categories[0]['virtual_category_id'] == 'virtual-category-1'
    assert categories[0]['special_category'] == 'custom-special-category'
