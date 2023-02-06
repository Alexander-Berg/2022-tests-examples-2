import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_product_pictures_merging(pgsql, brand_task_enqueue):
    # check current data
    assert get_product_pictures(pgsql) == [(1, 1), (2, 2), (4, 3), (4, 4)]

    # upload new nomenclature
    await brand_task_enqueue()

    # check merged data
    assert get_product_pictures(pgsql) == [
        (1, 1),
        (2, 2),
        (4, 4),
        (5, 5),
        (6, 6),
    ]


def get_product_pictures(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """SELECT product_id, picture_id
        FROM eats_nomenclature.product_pictures
        ORDER BY product_id, picture_id""",
    )
    return list(cursor)
