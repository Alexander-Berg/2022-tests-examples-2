import pytest


@pytest.mark.parametrize(
    'search_field, search_by_id_or_public_id, has_public_id, expect_found',
    [
        ('id', False, False, True),
        ('public_id', False, False, True),
        ('origin_id', False, False, True),
        ('id', False, True, False),
        ('public_id', False, True, True),
        ('origin_id', False, True, True),
        ('id', True, False, True),
        ('public_id', True, False, True),
        ('origin_id', True, False, False),
        ('id', True, True, True),
        ('public_id', True, True, True),
        ('origin_id', True, True, False),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_nomenclature_categories_by_id(
        taxi_eats_nomenclature,
        pgsql,
        update_taxi_config,
        add_category_public_id_by_name,
        get_active_assortment,
        search_field,
        search_by_id_or_public_id,
        has_public_id,
        expect_found,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY',
        {'search_by_id_or_public_id': search_by_id_or_public_id},
    )

    place_id = 1
    active_assortment_id = get_active_assortment(place_id, trait_id=1)

    category_id = 1
    category_public_id = category_id
    category_origin_id = 'category_1_origin'
    if has_public_id:
        category_public_id = 111
        add_category_public_id_by_name(category_public_id, 'category_1')

    request_category_id = category_id
    if search_field == 'public_id':
        request_category_id = category_public_id
    if search_field == 'origin_id':
        request_category_id = category_origin_id

    all_categories = sql_get_categories(pgsql, active_assortment_id)
    categories_data = filter_categories_by_parent(all_categories, category_id)

    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug=slug&category_id={request_category_id}',
    )
    assert response.status == 200
    if expect_found:
        assert (
            map_response(response.json())
            == map_sql_categories_for_response(
                pgsql, active_assortment_id, categories_data, category_id,
            )
        )
    else:
        assert map_response(response.json()) == []


def sql_get_categories(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""select
            c.id as id,
            coalesce(c.public_id, c.id) as public_id,
            c2.id as parent_id,
            coalesce(c2.public_id, c2.id) as parent_public_id,
            c.name,
            sort_order
        from eats_nomenclature.categories_relations cr
        join eats_nomenclature.categories c
            on c.assortment_id = {assortment_id} and c.id = cr.category_id
        left join eats_nomenclature.categories c2
            on c2.id = cr.parent_category_id
        """,
    )

    return [
        {
            'id': i[0],
            'public_id': i[1],
            'parent_id': i[2],
            'parent_public_id': i[3],
            'name': i[4],
            'sort_order': i[5],
        }
        for i in cursor
    ]


def filter_categories_by_parent(categories, parent_id):
    filtered_categories = [c for c in categories if c['id'] == parent_id]
    for category in categories:
        if [
                fc
                for fc in filtered_categories
                if fc['id'] == category['parent_id']
        ]:
            filtered_categories.append(category)

    return sorted(filtered_categories, key=lambda k: k['id'])


def map_response(json):
    return sorted(
        [
            {
                'id': i['id'],
                'public_id': i['public_id'],
                'parent_id': i.get('parent_id'),
                'parent_public_id': i.get('parent_public_id'),
                'name': i['name'],
                'sort_order': i['sort_order'],
            }
            for i in json['categories']
        ],
        key=lambda k: k['id'],
    )


def map_sql_categories_for_response(
        pgsql, assortment_id, categories, found_category_id,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select coalesce(public_id, id), origin_id
        from eats_nomenclature.categories
        where assortment_id = {assortment_id}
        """,
    )
    public_id_to_origin_id = {i[0]: i[1] for i in cursor}

    for category in categories:
        category_id = category['id']
        category['id'] = public_id_to_origin_id[category['public_id']]
        category['parent_id'] = (
            public_id_to_origin_id[category['parent_public_id']]
            if category['parent_id']
            else None
        )
        # if found, parent_public_id is deleted
        if category_id == found_category_id:
            category['parent_public_id'] = None
    return categories
