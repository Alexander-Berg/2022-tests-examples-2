import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_category_relations_merging(
        pgsql,
        get_active_assortment,
        get_in_progress_assortment,
        brand_task_enqueue,
):
    place_id = 1
    active_assortment_id = get_active_assortment(place_id)

    # check current data
    assert get_category_relations(pgsql, active_assortment_id) == {
        (active_assortment_id, 'category_1', 100, None),
        (active_assortment_id, 'category_2', 100, None),
        (active_assortment_id, 'category_3', 100, 'category_2'),
        (active_assortment_id, 'category_4', 100, None),
    }

    # upload new nomenclature
    await brand_task_enqueue()

    in_progress_assortment_id = get_in_progress_assortment(place_id)

    # check merged data
    assert get_category_relations(pgsql, in_progress_assortment_id) == {
        (in_progress_assortment_id, 'category_6', 100, None),
        (in_progress_assortment_id, 'category_3', 100, 'category_6'),
    }


def get_category_relations(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select cr.assortment_id, c.name, cr.sort_order, parc.name
        from eats_nomenclature.categories_relations cr
        join eats_nomenclature.categories c
            on c.assortment_id = cr.assortment_id and c.id = cr.category_id
        left join eats_nomenclature.categories parc
            on parc.assortment_id = cr.assortment_id
                and parc.id = cr.parent_category_id
        where cr.assortment_id = {assortment_id}
        """,
    )
    return set(cursor)
