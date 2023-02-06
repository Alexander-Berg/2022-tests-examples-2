import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_all_nomenclature_categories(taxi_eats_nomenclature, pgsql):

    categories_data = get_categories(pgsql)

    response = await taxi_eats_nomenclature.get('/v1/nomenclature?slug=slug')

    assert response.status == 200

    assert map_response(response.json()) == categories_data


def map_response(json):
    categories = json['categories']
    return {
        (i['id'], i.get('parent_id') or None, i['name'], i['sort_order'])
        for i in categories
    }


def get_categories(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """SELECT c.origin_id as id, c2.origin_id as parent_id, c.name, sort_order
        FROM eats_nomenclature.categories_relations cr
        JOIN eats_nomenclature.categories c on c.id = cr.category_id
        LEFT JOIN eats_nomenclature.categories c2
            on c2.id = cr.parent_category_id
        """,
    )
    return set(cursor)
