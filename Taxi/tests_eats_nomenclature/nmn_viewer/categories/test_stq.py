import pytest

from . import constants
from .. import models

S3_PREFIX = constants.S3_PREFIX
BRAND_ID = constants.BRAND_ID
PLACE_ID = constants.PLACE_ID


@pytest.mark.parametrize(
    'db_assortment_name, expected_assortment_name',
    [(None, 'partner'), ('custom', 'custom')],
)
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'brand_place.sql'],
)
async def test_assortment_name(
        stq,
        stq_runner,
        nmn_vwr_utils,
        pg_cursor,
        # parametrize
        db_assortment_name,
        expected_assortment_name,
):
    assortment_id, trait_id = _sql_add_assortment(
        pg_cursor,
        brand_id=BRAND_ID,
        place_id=PLACE_ID,
        assortment_name=db_assortment_name,
    )

    category = models.Category(assortment_id=assortment_id)
    category.add_product(models.Product(brand_id=BRAND_ID))
    nmn_vwr_utils.sql.save(category)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
    )

    task_info = stq.eats_nomenclature_viewer_update_categories.next_call()
    assert task_info['kwargs']['assortment_name'] == expected_assortment_name


def _sql_add_assortment(pg_cursor, brand_id, place_id, assortment_name):
    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.assortments
        default values
        returning id
    """,
    )
    assortment_id = pg_cursor.fetchone()[0]

    if assortment_name:
        pg_cursor.execute(
            """
            insert into eats_nomenclature.assortment_traits(
                brand_id,
                assortment_name
            )
            values (%s, %s)
            returning id
        """,
            (brand_id, assortment_name),
        )
        trait_id = pg_cursor.fetchone()[0]
    else:
        trait_id = None

    pg_cursor.execute(
        """
        insert into eats_nomenclature.place_assortments(
            place_id,
            assortment_id,
            in_progress_assortment_id,
            trait_id
        )
        values
            (%s, null, %s, %s)
    """,
        (place_id, assortment_id, trait_id),
    )

    return assortment_id, trait_id
