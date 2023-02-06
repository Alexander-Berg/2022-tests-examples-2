import pytest


def _count_groups(pgsql):
    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(f"""SELECT COUNT(*) FROM products.category_groups;""")
    return cursor.fetchall()[0][0]


@pytest.mark.pgsql(
    'grocery_products', files=['groups.sql', 'refresh_views.sql'],
)
async def test_groups_data(pgsql, taxi_grocery_products):
    """ Check /internal/v1/products/v1/groups-data
    return three groups ordered by id """
    response = await taxi_grocery_products.post(
        '/internal/v1/products/v1/groups-data',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    groups = response.json()['groups']
    assert groups == [
        {
            'category_group_id': 'category-group-1',
            'item_meta': '{ "meta-1": "meta-1" }',
            'title_tanker_key': 'title_tanker_key-1',
        },
        {
            'category_group_id': 'category-group-3',
            'item_meta': '{ "meta-3": "meta-3" }',
            'title_tanker_key': 'title_tanker_key-3',
            'short_title_tanker_key': 'short_title_tanker_key-3',
        },
        {
            'category_group_id': 'category-group-z',
            'item_meta': '{ "meta-z": "meta-z" }',
            'title_tanker_key': 'title_tanker_key-z',
        },
    ]
    assert len(groups) == _count_groups(pgsql)


@pytest.mark.pgsql(
    'grocery_products', files=['groups.sql', 'refresh_views.sql'],
)
async def test_groups_data_chunked(pgsql, taxi_grocery_products, load_json):
    """ Check /internal/v1/products/v1/groups-data
    return three chunks of different groups sorted by id """
    response_len = [2, 1, 0]
    groups = []
    limit = 2
    cursor = 0
    for length in response_len:
        response = await taxi_grocery_products.post(
            '/internal/v1/products/v1/groups-data',
            json={'limit': limit, 'cursor': cursor},
        )

        assert response.status_code == 200
        if length == 0:
            assert cursor == response.json()['cursor']
        else:
            cursor = response.json()['cursor']
        assert len(response.json()['groups']) == length
        groups.extend(response.json()['groups'])

    groups_ids_set = set()
    prev_group_id = None
    for item in groups:
        group_id = item['category_group_id']
        groups_ids_set.add(group_id)
        if prev_group_id:
            assert group_id > prev_group_id
        prev_group_id = group_id

    assert len(groups) == len(groups_ids_set)
    assert len(groups) == sum(response_len)
    assert len(groups) == _count_groups(pgsql)
