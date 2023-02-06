import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_barcode_merging(pgsql, brand_task_enqueue):
    # check current data
    assert get_barcodes(pgsql) == [
        (1, '123ETR45611', '123ETR456', 1, 1),
        (2, '999UUU42', '999UUU', 4, 2),
        (3, 'XXX00093', 'XXX000', 9, 3),
    ]

    # upload new nomenclature
    await brand_task_enqueue()

    # check merged data
    assert get_barcodes(pgsql) == [
        (1, '123ETR45611', '123ETR456', 1, 1),
        (2, '999UUU42', '999UUU', 4, 2),
        (3, 'XXX00093', 'XXX000', 9, 3),
        (4, '987654321098252', '987654321098', 25, 2),
    ]


def get_barcodes(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """SELECT id, unique_key, value, barcode_type_id,
            barcode_weight_encoding_id
        FROM eats_nomenclature.barcodes""",
    )
    return list(cursor)
