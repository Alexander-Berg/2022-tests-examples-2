import pytest


ADD_GROUP_HANDLER = '/v1/manage/custom_categories_groups'
UPDATE_GROUP_HANDLER = '/v1/manage/custom_categories_groups/update'


@pytest.mark.parametrize('mark_category_as_base', [True, False])
@pytest.mark.parametrize('mark_category_as_restaurant', [True, False])
@pytest.mark.parametrize('diff_only_is_base', [True, False])
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_products.sql', 'fill_tags.sql'],
)
async def test_merge(
        taxi_eats_nomenclature,
        load_json,
        sql_get_group_public_id,
        sql_get_pictures,
        sql_get_group,
        sql_get_categories_relations,
        sql_get_categories,
        sql_get_categories_products,
        sql_get_cat_prod_types,
        sql_get_category_tags,
        # parametrize
        mark_category_as_base,
        mark_category_as_restaurant,
        diff_only_is_base,
):
    request = load_json('request.json')
    # Add category that will be removed from custom group.
    request['categories'].append(
        {
            'external_id': 7,
            'image': {'url': 'url_1'},
            'name': 'Овощи',
            'parents': [],
            'product_ids': [],
            'product_type_ids': [],
            'tags': [],
            'sort_order': 400,
        },
    )
    request['is_base'] = not mark_category_as_base
    request['is_restaurant'] = not mark_category_as_restaurant

    await taxi_eats_nomenclature.post(ADD_GROUP_HANDLER, json=request)
    added_group_id = sql_get_group_public_id()

    if diff_only_is_base:
        update_request = load_json('update_is_base_only_request.json')
    else:
        update_request = load_json('update_request.json')
    update_request['is_base'] = mark_category_as_base
    update_request['is_restaurant'] = mark_category_as_restaurant
    response = await taxi_eats_nomenclature.post(
        UPDATE_GROUP_HANDLER + f'?custom_categories_group_id={added_group_id}',
        json=update_request,
    )

    assert response.status_code == 200

    assert sql_get_pictures() == get_expected_pictures()
    (
        group_id,
        group_name,
        group_description,
        is_base,
        is_restaurant,
    ) = sql_get_group()
    assert (
        (group_name, group_description, is_base, is_restaurant)
        == get_expected_group(
            mark_category_as_base,
            mark_category_as_restaurant,
            diff_only_is_base,
        )
    )
    assert sql_get_categories_relations() == get_expected_cat_relations(
        group_id,
    )
    assert sql_get_categories() == get_expected_categories()
    assert sql_get_categories_products() == get_expected_cat_products()
    assert sql_get_cat_prod_types() == get_expected_cat_product_types()
    assert sql_get_category_tags() == get_expected_category_tags()


@pytest.mark.parametrize('has_diff', [True, False])
async def test_empty_is_restaurant_in_request(
        taxi_eats_nomenclature,
        sql_get_group_public_id,
        sql_get_group,
        # parametrize
        has_diff,
):
    expected_is_restaurant = True
    request = {
        'categories': [
            {
                'description': 'Молоко (описание)',
                'external_id': 1,
                'name': 'Молоко',
                'parents': [],
                'product_ids': [],
                'product_type_ids': [],
                'sort_order': 100,
                'tags': [],
                'image': {'url': 'url_2'},
            },
        ],
        'description': 'Описание группы категорий',
        'group_name': 'Группа категорий',
        'is_base': True,
        'is_restaurant': expected_is_restaurant,
    }

    await taxi_eats_nomenclature.post(ADD_GROUP_HANDLER, json=request)
    added_group_id = sql_get_group_public_id()

    del request['is_restaurant']
    if has_diff:
        request['description'] = 'Новое описание группы категорий'
        request['group_name'] = 'Новое название группы категорий'

    response = await taxi_eats_nomenclature.post(
        UPDATE_GROUP_HANDLER + f'?custom_categories_group_id={added_group_id}',
        json=request,
    )

    assert response.status_code == 200

    (_, _, _, _, is_restaurant) = sql_get_group()
    assert is_restaurant == expected_is_restaurant


def get_expected_pictures():
    return {
        ('url_1', None, True),
        ('url_2', 'processed_url_2', False),
        ('url_3', None, False),
        ('url_4', None, True),
        ('url_5', None, True),
        ('url_new_1', None, True),
        ('url_new_2', None, True),
    }


def get_expected_group(is_base, is_restaurant, diff_only_is_base):
    return (
        (
            'Группа категорий',
            'Описание группы категорий',
            is_base,
            is_restaurant,
        )
        if diff_only_is_base
        else (
            'Новое название группы категорий',
            'Новое описание группы категорий',
            is_base,
            is_restaurant,
        )
    )


def get_expected_cat_relations(group_id):
    return {
        (group_id, 'Молоко', 'Молочные продукты NEW'),
        (group_id, 'Молочные продукты NEW', None),
        (group_id, 'Фрукты', 'Фрукты и овощи'),
        (group_id, 'Фрукты', 'Новая категория'),
        (group_id, 'Фрукты и овощи', None),
        (group_id, 'Новая категория', None),
        (group_id, 'Фрукты NEW', None),
    }


def get_expected_categories():
    return [
        {
            'name': 'Молоко',
            'picture_url': 'url_new_1',
            'picture_processed_url': None,
            'sort_order': 200,
            'description': 'Молоко (новое описание)',
        },
        {
            'name': 'Молочные продукты NEW',
            'picture_url': 'url_new_2',
            'picture_processed_url': None,
            'sort_order': 300,
            'description': '',
        },
        {
            'name': 'Новая категория',
            'picture_url': 'url_1',
            'picture_processed_url': None,
            'sort_order': 100,
            'description': 'Новая категория (описание)',
        },
        {
            'name': 'Овощи',
            'picture_url': 'url_1',
            'picture_processed_url': None,
            'sort_order': 400,
            'description': '',
        },
        {
            'name': 'Фрукты',
            'picture_url': 'url_4',
            'picture_processed_url': None,
            'sort_order': 300,
            'description': '',
        },
        {
            'name': 'Фрукты NEW',
            'picture_url': 'url_1',
            'picture_processed_url': None,
            'sort_order': 400,
            'description': '',
        },
        {
            'name': 'Фрукты и овощи',
            'picture_url': 'url_5',
            'picture_processed_url': None,
            'sort_order': 100,
            'description': 'Фрукты и овощи (описание)',
        },
    ]


def get_expected_cat_products():
    return {
        ('Молоко', 1),
        ('Молоко', 3),
        ('Фрукты', 3),
        ('Фрукты', 5),
        ('Фрукты и овощи', 5),
        ('Новая категория', 1),
        ('Фрукты NEW', 1),
    }


def get_expected_cat_product_types():
    return {
        ('Молоко', 1),
        ('Фрукты', 1),
        ('Фрукты', 2),
        ('Новая категория', 3),
        ('Фрукты NEW', 3),
    }


def get_expected_category_tags():
    return {
        ('Молоко', 'Тег 1'),
        ('Молочные продукты NEW', 'Тег 1'),
        ('Фрукты', 'Тег 1'),
        ('Новая категория', 'Тег 2'),
    }
