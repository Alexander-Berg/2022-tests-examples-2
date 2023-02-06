import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_nomenclature_products_pictures(
        taxi_eats_nomenclature, pgsql,
):
    pictures = get_pictures(pgsql)

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
    )

    assert response.status == 200

    assert map_response(response.json()) == pictures


def map_response(json):
    categories = json['categories']
    pictures = []
    for category in categories:
        for item in category['items']:
            for picture in item['images']:
                pictures.append(picture)

    return {(p['url'], p.get('hash') or None) for p in pictures}


def get_pictures(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select pic.processed_url, pic.hash
        from eats_nomenclature.product_pictures ppic
        join eats_nomenclature.pictures pic on pic.id = ppic.picture_id
        where pic.processed_url is not null
        order by url
        """,
    )
    return set(cursor)
