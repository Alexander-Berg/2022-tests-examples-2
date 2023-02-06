import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_product_barcodes_merging(pgsql, brand_task_enqueue):
    # check current data
    assert get_place_product_barcodes(pgsql) == [
        (1, 3),
        (2, 1),
        (3, 2),
        (4, 1),
        (5, 3),
    ]

    # upload new nomenclature
    await brand_task_enqueue()

    # check merged data
    assert get_place_product_barcodes(pgsql) == [
        (1, 3),
        (2, 1),
        (3, 2),
        (4, 1),
        (5, 3),
        (6, 4),
    ]


def get_place_product_barcodes(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """SELECT product_id, barcode_id
        FROM eats_nomenclature.product_barcodes
        ORDER BY product_id, barcode_id""",
    )
    return list(cursor)
