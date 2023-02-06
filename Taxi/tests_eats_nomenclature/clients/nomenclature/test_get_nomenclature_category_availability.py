import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
@pytest.mark.parametrize('items_count, availability', [(1, True), (0, False)])
@pytest.mark.parametrize('calculate_active_in_runtime', [True, False])
async def test_get_nomenclature_category_availability(
        taxi_eats_nomenclature,
        pgsql,
        update_taxi_config,
        items_count,
        availability,
        calculate_active_in_runtime,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_TEMPORARY_CONFIGS',
        {
            'calculate-category-availability-in-runtime': (
                calculate_active_in_runtime
            ),
        },
    )

    if calculate_active_in_runtime:
        set_category_active_items_count(3, items_count, pgsql)
        set_category_active_items_count(6, 1, pgsql)
    else:
        set_category_active_items_count(1, 1, pgsql)
        set_category_active_items_count(2, items_count, pgsql)
        set_category_active_items_count(3, items_count, pgsql)
        set_category_active_items_count(6, 1, pgsql)

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
    )
    assert response.status == 200
    assert map_response(response.json()) == {
        ('category_1_origin', 'category_4_origin', True),
        ('category_2_origin', 'category_1_origin', availability),
        ('category_3_origin', 'category_2_origin', availability),
        ('category_6_origin', 'category_1_origin', True),
    }


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'modify_categories.sql',
    ],
)
@pytest.mark.parametrize('items_count, availability', [(1, True), (0, False)])
@pytest.mark.parametrize('calculate_active_in_runtime', [True, False])
async def test_get_nomenclature_parent_category_availability(
        taxi_eats_nomenclature,
        update_taxi_config,
        pgsql,
        items_count,
        availability,
        calculate_active_in_runtime,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_TEMPORARY_CONFIGS',
        {
            'calculate-category-availability-in-runtime': (
                calculate_active_in_runtime
            ),
        },
    )

    if calculate_active_in_runtime:
        set_category_active_items_count(1, 0, pgsql)
        set_category_active_items_count(2, 0, pgsql)
        set_category_active_items_count(3, items_count, pgsql)
        set_category_active_items_count(6, 0, pgsql)
    else:
        set_category_active_items_count(1, items_count, pgsql)
        set_category_active_items_count(2, items_count, pgsql)
        set_category_active_items_count(3, items_count, pgsql)
        set_category_active_items_count(6, items_count, pgsql)

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_6_origin',
    )

    assert response.status == 200

    assert map_response(response.json()) == {
        ('category_1_origin', 'category_6_origin', availability),
        ('category_2_origin', 'category_1_origin', availability),
        ('category_3_origin', 'category_2_origin', availability),
        ('category_6_origin', None, availability),
    }


def set_category_active_items_count(category_id, items_count, pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        INSERT INTO eats_nomenclature.places_categories
        (assortment_id, place_id, category_id, active_items_count)
        VALUES(1, 1, '{category_id}', '{items_count}')""",
    )


def map_response(json):
    categories = json['categories']
    return {
        (i['id'], i.get('parent_id'), i.get('available')) for i in categories
    }
