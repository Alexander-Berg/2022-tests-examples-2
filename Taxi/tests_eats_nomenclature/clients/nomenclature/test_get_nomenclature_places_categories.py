import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_nomenclature_places_categories(
        pgsql, taxi_eats_nomenclature, update_taxi_config,
):
    add_place_category(pgsql, 1, 0, '11111111')
    add_place_category(pgsql, 2, 1, '22222222')
    add_place_category(pgsql, 3, 1, '33333333')
    add_place_category(pgsql, 4, 1, '44444444')
    add_place_category(pgsql, 5, 0, '55555555')
    add_place_category(pgsql, 6, 1, '66666666')

    request = {
        'places_categories': [
            {
                'place_id': 1,
                'categories': [
                    '11111111',
                    '22222222',
                    '33333333',
                    '44444444',
                    '55555555',
                ],
            },
        ],
    }

    response = await taxi_eats_nomenclature.post(
        '/v1/places/categories', json=request,
    )

    expected_response = [
        {'place_id': 1, 'categories': ['22222222', '33333333', '44444444']},
    ]

    assert response.status == 200

    assert response.json()['places_categories'] == expected_response


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_place_without_brand(
        pgsql, taxi_eats_nomenclature, sql_delete_brand_place,
):
    place_id = 1
    add_place_category(pgsql, 1, 0, '11111111')
    add_place_category(pgsql, 2, 1, '22222222')
    add_place_category(pgsql, 3, 1, '33333333')
    add_place_category(pgsql, 4, 1, '44444444')
    add_place_category(pgsql, 5, 0, '55555555')
    add_place_category(pgsql, 6, 1, '66666666')

    sql_delete_brand_place(place_id)

    request = {
        'places_categories': [
            {
                'place_id': place_id,
                'categories': [
                    '11111111',
                    '22222222',
                    '33333333',
                    '44444444',
                    '55555555',
                ],
            },
        ],
    }

    response = await taxi_eats_nomenclature.post(
        '/v1/places/categories', json=request,
    )

    assert response.status == 200

    assert response.json()['places_categories'] == []


def add_place_category(pgsql, category_id, items_count, public_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        INSERT INTO eats_nomenclature.categories_dictionary
        (id, name)
        VALUES('{public_id}', '{public_id}_name')""",
    )
    cursor.execute(
        f"""
        INSERT INTO eats_nomenclature.places_categories
        (assortment_id, place_id, category_id, active_items_count, public_id)
        VALUES(1, 1, '{category_id}', '{items_count}', '{public_id}')""",
    )
