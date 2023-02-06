import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_category_products_merging(
        pgsql,
        get_active_assortment,
        get_in_progress_assortment,
        brand_task_enqueue,
):
    place_id = 1
    active_assortment_id = get_active_assortment(place_id)

    # check current data
    assert get_category_products(pgsql, active_assortment_id) == {
        (1, 'category_1', 1, 100),
        (1, 'category_1', 2, 50),
        (1, 'category_3', 3, 10),
        (1, 'category_3', 4, 100),
        (1, 'category_3', 5, 20),
    }

    # upload new nomenclature
    await brand_task_enqueue()

    in_progress_assortment_id = get_in_progress_assortment(place_id)

    # check merged data
    assert get_category_products(pgsql, in_progress_assortment_id) == {
        (in_progress_assortment_id, 'category_6', 6, 0),
        (in_progress_assortment_id, 'category_3', 5, 60),
        (in_progress_assortment_id, 'category_3', 4, 100),
    }


def get_category_products(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select cp.assortment_id, c.name, cp.product_id, cp.sort_order
        from eats_nomenclature.categories_products cp
        join eats_nomenclature.categories c
            on c.assortment_id = cp.assortment_id and c.id = cp.category_id
        where c.assortment_id = {assortment_id}
        """,
    )
    return set(cursor)
