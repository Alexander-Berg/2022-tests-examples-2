import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_category_pictures_merging(
        pgsql,
        get_active_assortment,
        get_in_progress_assortment,
        brand_task_enqueue,
):
    place_id = 1
    active_assortment_id = get_active_assortment(place_id)

    # check current data
    assert get_category_pictures(pgsql, active_assortment_id) == {
        (active_assortment_id, 'category_1', 1),
        (active_assortment_id, 'category_1', 2),
        (active_assortment_id, 'category_2', 2),
        (active_assortment_id, 'category_3', 3),
        (active_assortment_id, 'category_4', 4),
        (active_assortment_id, 'category_5', 5),
    }

    # upload new nomenclature
    await brand_task_enqueue()

    in_progress_assortment_id = get_in_progress_assortment(place_id)

    # check merged data
    assert get_category_pictures(pgsql, in_progress_assortment_id) == {
        (in_progress_assortment_id, 'category_6', 6),
        (in_progress_assortment_id, 'category_3', 3),
    }


def get_category_pictures(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select cp.assortment_id, c.name, cp.picture_id
        from eats_nomenclature.category_pictures cp
        join eats_nomenclature.categories c
            on c.assortment_id = cp.assortment_id and c.id = cp.category_id
        where cp.assortment_id = {assortment_id}
        """,
    )
    return set(cursor)
