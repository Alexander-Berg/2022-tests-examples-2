import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql', 'fill_vendors.sql'],
)
async def test_product_merging(pgsql, brand_task_enqueue):
    # check current data
    assert get_product(pgsql) == {
        (
            1,
            None,
            True,
            1,
            0.2,
            False,
            'item_origin_1',
            'abc',
            'item_1',
            1,
            1000,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            777,
        ),
        (
            2,
            None,
            True,
            2,
            1.0,
            True,
            'item_origin_2',
            'def',
            'item_2',
            1,
            1000,
            True,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            777,
        ),
        (
            3,
            None,
            True,
            2,
            1.0,
            True,
            'item_origin_3',
            'ghi',
            'item_3',
            None,
            None,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            777,
        ),
        (
            4,
            None,
            False,
            3,
            1.0,
            True,
            'item_origin_4',
            'jkl',
            'item_4',
            1,
            50,
            True,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            777,
        ),
        (
            5,
            None,
            True,
            3,
            0.5,
            True,
            'item_origin_5',
            'mno',
            'item_5',
            1,
            300,
            True,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            777,
        ),
    }

    # upload new nomenclature
    await brand_task_enqueue()

    # check merged data
    assert get_product(pgsql) == {
        (
            1,
            None,
            True,
            1,
            0.2,
            False,
            'item_origin_1',
            'abc',
            'item_1',
            1,
            1000,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            777,
        ),
        (
            2,
            None,
            True,
            2,
            1.0,
            True,
            'item_origin_2',
            'def',
            'item_2',
            1,
            1000,
            True,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            777,
        ),
        (
            3,
            None,
            True,
            2,
            1.0,
            True,
            'item_origin_3',
            'ghi',
            'item_3',
            None,
            None,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            777,
        ),
        (
            4,
            None,
            False,
            3,
            1.0,
            True,
            'item_origin_4',
            'item 4 description',
            'item_4',
            1,
            50,
            True,
            2,
            100,
            'item 4 composition',
            'item 4 nutritional vale',
            'item 4 purpose',
            'item 4 storage requirements',
            'item 4 expires in',
            'item 4 package info',
            777,
        ),
        (
            5,
            None,
            True,
            3,
            0.5,
            True,
            'item_origin_5',
            'item 5 description',
            'item_5',
            1,
            300,
            True,
            2,
            100,
            'item 5 composition',
            'item 5 nutritional vale',
            'item 5 purpose',
            'item 5 storage requirements',
            'item 5 expires in',
            'item 5 package info',
            777,
        ),
        (
            6,
            None,
            True,
            1,
            1.0,
            True,
            'item_origin_6',
            'item 6 description',
            'item_6',
            1,
            1000,
            True,
            2,
            100,
            'item 6 composition',
            'item 6 nutritional vale',
            'item 6 purpose',
            'item 6 storage requirements',
            'item 6 expires in',
            '????????????????',
            777,
        ),
    }
    product_id_to_marking_type_ = _get_product_id_to_marking_type_value_(pgsql)
    assert product_id_to_marking_type_ == {
        1: 'default',
        4: 'tobacco',
        6: 'wine',
    }


def get_product(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """SELECT id, sku_id, is_choosable, shipping_type_id,
                quantum, is_catch_weight, origin_id, description,
                name, measure_unit_id, measure_value, adult, volume_unit_id,
                volume_value, composition, nutritional_value, purpose,
                storage_requirements, expires_in, package_info, brand_id
        FROM eats_nomenclature.products""",
    )
    return set(cursor)


def _get_product_id_to_marking_type_value_(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """select p.id, mt.value
        from eats_nomenclature.products p
        join eats_nomenclature.marking_types mt
            on p.marking_type_id = mt.id
        order by p.id""",
    )
    return {row[0]: row[1] for row in cursor}
