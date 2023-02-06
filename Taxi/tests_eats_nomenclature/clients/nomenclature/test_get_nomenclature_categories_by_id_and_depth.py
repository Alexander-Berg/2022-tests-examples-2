import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_nomenclature_categories_by_id_and_depth(
        taxi_eats_nomenclature, pgsql, get_active_assortment,
):
    place_id = 1
    active_assortment_id = get_active_assortment(place_id, trait_id=1)
    category_origin_id = 'category_1_origin'
    max_depth = 3

    all_categories = sql_get_categories(pgsql, active_assortment_id)
    categories_data = filter_cats_by_parent_and_depth(
        all_categories, category_origin_id, max_depth,
    )

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug'
        f'&category_id={category_origin_id}&max_depth={max_depth}',
    )
    assert response.status == 200
    assert map_response(response.json()) == categories_data


def sql_get_categories(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""SELECT
            c.origin_id as id, c2.origin_id as parent_id,
            c.name, sort_order
        FROM eats_nomenclature.categories_relations cr
        JOIN eats_nomenclature.categories c
            on c.assortment_id = {assortment_id} and c.id = cr.category_id
        LEFT JOIN eats_nomenclature.categories c2
            on c2.id = cr.parent_category_id
        """,
    )

    return [
        {'id': i[0], 'parent_id': i[1], 'name': i[2], 'sort_order': i[3]}
        for i in cursor
    ]


def filter_cats_by_parent_and_depth(categories, parent_origin_id, max_depth):
    filtered_categories = [
        (c, 1) for c in categories if c['id'] == parent_origin_id
    ]
    for category in categories:
        parent_categories = [
            fc
            for fc in filtered_categories
            if fc[0]['id'] == category['parent_id']
        ]
        if not parent_categories:
            continue
        parent_depth = parent_categories[0][1]
        if parent_depth < max_depth:
            filtered_categories.append((category, parent_depth + 1))
    return sorted([fc[0] for fc in filtered_categories], key=lambda k: k['id'])


def map_response(json):
    return sorted(
        [
            {
                'id': i['id'],
                'parent_id': i.get('parent_id'),
                'name': i['name'],
                'sort_order': i['sort_order'],
            }
            for i in json['categories']
        ],
        key=lambda k: k['id'],
    )
