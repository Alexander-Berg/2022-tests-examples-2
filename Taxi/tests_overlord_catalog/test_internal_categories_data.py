import pytest


def _count_categories(pgsql):
    db = pgsql['overlord_catalog']
    cursor = db.cursor()
    cursor.execute(f"""SELECT COUNT(*) FROM catalog_wms.categories;""")
    return cursor.fetchall()[0][0]


@pytest.mark.pgsql(
    'overlord_catalog', files=['categories.sql', 'refresh_wms_views.sql'],
)
async def test_categories_data(pgsql, taxi_overlord_catalog):
    """ Check /internal/v1/catalog/v1/categories-data
    return three categories ordered by id """
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/categories-data',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert categories == [
        {
            'category_id': '61d24b27-0e8e-4173-a861-95c87802972f',
            'title': 'Яйца',
            'description': 'Яйца - описание',
            'image_url_template': 'eggs_template.jpg',
        },
        {
            'category_id': '73fa0267-8519-485a-9e06-5e18a9a7514c',
            'external_id': 'external-id-2',
            'title': 'Завтрак',
            'description': 'Завтрак - описание',
            'image_url_template': 'zavtrak_template.jpg',
            'deep_link': 'breakfast',
        },
        {
            'category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
            'external_id': 'external-id-1',
            'title': 'Корень 1',
            'description': 'Корневая категория',
            'image_url_template': '',
        },
    ]
    assert len(categories) == _count_categories(pgsql)


@pytest.mark.pgsql(
    'overlord_catalog', files=['wms_menu_data.sql', 'refresh_wms_views.sql'],
)
async def test_categories_data_chunked(
        pgsql, taxi_overlord_catalog, load_json,
):
    """ Check /internal/v1/catalog/v1/categories-data
    return four chunks of different categories sorted by id """
    response_len = [150, 150, 142, 0]
    categories = []
    limit = 150
    cursor = 0
    for length in response_len:
        response = await taxi_overlord_catalog.post(
            '/internal/v1/catalog/v1/categories-data',
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
        category_id = item['category_id']
        categories_ids_set.add(category_id)
        if prev_category_id:
            assert category_id > prev_category_id
        prev_category_id = category_id

    assert len(categories) == len(categories_ids_set)
    assert len(categories) == sum(response_len)
    assert len(categories) == _count_categories(pgsql)
