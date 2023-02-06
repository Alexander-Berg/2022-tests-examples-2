import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_dequeue_stq_and_process_nomenclature(
        pgsql, sql_upsert_place, brand_task_enqueue,
):
    sql_upsert_place(place_id=1, place_slug='lavka_krasina')
    await brand_task_enqueue()

    cursor = pgsql['eats_nomenclature'].cursor()

    cursor.execute(
        """SELECT id, slug
        FROM eats_nomenclature.places""",
    )
    assert list(cursor) == [(1, 'lavka_krasina')]

    cursor.execute(
        """SELECT count(*)
        FROM eats_nomenclature.brands""",
    )
    assert list(cursor)[0][0] == 1

    cursor.execute(
        """SELECT count(*)
        FROM eats_nomenclature.brand_places""",
    )
    assert list(cursor)[0][0] == 1

    # partner assortment and assortment with trait_id = 2
    cursor.execute(
        """SELECT count(*)
        FROM eats_nomenclature.place_assortments""",
    )
    assert list(cursor)[0][0] == 2

    # 3 old assortments;
    # 1 new assortment for nomenclature_processing,
    # because it creates only default assortment;
    # 2 new assortments for brand_processing,
    # because it creates assortments for all trait_ids
    cursor.execute(
        """SELECT count(*)
        FROM eats_nomenclature.assortments""",
    )
    assert list(cursor)[0][0] == 5
