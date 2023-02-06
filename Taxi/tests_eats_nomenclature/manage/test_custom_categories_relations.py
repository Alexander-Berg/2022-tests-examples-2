import pytest


HANDLER = '/v1/manage/custom_categories_groups'


@pytest.mark.parametrize('mark_added_category_as_base', [True, False])
@pytest.mark.parametrize('mark_added_category_as_restaurant', [True, False])
@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_categories_relations_merge(
        taxi_eats_nomenclature,
        load_json,
        sql_get_group,
        sql_get_categories_relations,
        # parametrize
        mark_added_category_as_base,
        mark_added_category_as_restaurant,
):
    request = load_json('request.json')
    request['is_base'] = mark_added_category_as_base
    request['is_restaurant'] = mark_added_category_as_restaurant
    response = await taxi_eats_nomenclature.post(HANDLER, json=request)
    assert response.status_code == 200

    (
        group_id,
        group_name,
        group_description,
        is_base,
        is_restaurant,
    ) = sql_get_group()
    assert (group_name, group_description, is_base, is_restaurant) == (
        'Группа категорий',
        'Описание группы категорий',
        mark_added_category_as_base,
        mark_added_category_as_restaurant,
    )

    expected_categories_relations = {
        (group_id, 'Молоко', 'Молочные продукты'),
        (group_id, 'Молоко', 'Молоко и сыры'),
        (group_id, 'Молочные продукты', None),
        (group_id, 'Молоко и сыры', None),
        (group_id, 'Фрукты', 'Фрукты и овощи'),
        (group_id, 'Фрукты и овощи', None),
        (group_id, 'Фрукты', None),
    }
    assert sql_get_categories_relations() == expected_categories_relations
