import pytest


def _count_layouts(pgsql):
    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(f"""SELECT COUNT(*) FROM products.layouts;""")
    return cursor.fetchall()[0][0]


@pytest.mark.pgsql(
    'grocery_products', files=['layouts.sql', 'refresh_views.sql'],
)
async def test_layouts_data(pgsql, taxi_grocery_products, load_json):
    """ Check /internal/v1/products/v1/layouts-data
    return three layouts ordered by id """
    response = await taxi_grocery_products.post(
        '/internal/v1/products/v2/layouts-data',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    layouts = response.json()['layouts']
    assert layouts == load_json('internal_layouts_data_expected_response.json')
    assert len(layouts) == _count_layouts(pgsql)


@pytest.mark.pgsql(
    'grocery_products', files=['layouts.sql', 'refresh_views.sql'],
)
async def test_layouts_data_chunked(pgsql, taxi_grocery_products):
    """ Check /internal/v1/products/v2/layouts-data
    return three chunks of different layouts sorted by id """
    response_len = [2, 1, 0]
    layouts = []
    limit = 2
    cursor = 0
    for length in response_len:
        response = await taxi_grocery_products.post(
            '/internal/v1/products/v2/layouts-data',
            json={'limit': limit, 'cursor': cursor},
        )

        assert response.status_code == 200
        if length == 0:
            assert cursor == response.json()['cursor']
        else:
            cursor = response.json()['cursor']
        assert len(response.json()['layouts']) == length
        layouts.extend(response.json()['layouts'])

    layouts_ids_set = set()
    prev_layout_id = None
    for item in layouts:
        layout_id = item['layout_id']
        layouts_ids_set.add(layout_id)
        if prev_layout_id:
            assert layout_id > prev_layout_id
        prev_layout_id = layout_id

    assert len(layouts) == len(layouts_ids_set)
    assert len(layouts) == sum(response_len)
    assert len(layouts) == _count_layouts(pgsql)
