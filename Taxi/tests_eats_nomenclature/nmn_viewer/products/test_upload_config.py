import json
import re

import pytest

from . import constants
from .. import models
from ... import utils

S3_PREFIX = constants.S3_PREFIX
ASSORTMENT_ID = constants.ASSORTMENT_ID
BRAND_ID = constants.BRAND_ID
DEFAULT_CATEGORY_ID = constants.CATEGORY_ID


@pytest.mark.parametrize(**utils.gen_bool_params('enable_upload'))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_config_upload_state(
        stq,
        stq_runner,
        mds_s3_storage,
        nmn_vwr_utils,
        # parametrize
        enable_upload,
):
    nmn_vwr_utils.config_set_upload_state(enable_upload)

    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(
            product=models.Product(BRAND_ID), assortment_id=ASSORTMENT_ID,
        ),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    assert bool(mds_s3_storage.storage) == enable_upload
    assert (
        stq.eats_nomenclature_viewer_update_products.has_calls == enable_upload
    )


@pytest.mark.parametrize(**utils.gen_bool_params('use_partner_assortment'))
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'brand_place.sql'],
)
async def test_assortment_trait(
        stq_runner,
        mds_s3_storage,
        pg_cursor,
        nmn_vwr_utils,
        # parametrize
        use_partner_assortment,
):
    """
    Verifies that file is only uploaded
    when trait id is not set (i.e. partner assortment)
    """

    assortment_name = None if use_partner_assortment else 'custom_assortment'

    assortment_id, trait_id = _sql_add_assortment(
        pg_cursor, assortment_name=assortment_name,
    )
    category = models.Category(assortment_id=assortment_id)
    category.add_product(models.Product(BRAND_ID))
    nmn_vwr_utils.sql.save(category)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
    )

    assert bool(mds_s3_storage.storage) == use_partner_assortment


@pytest.mark.parametrize(
    'chunk_size, product_count, expected_chunk_count',
    [
        pytest.param(3, 2, 1, id='single chunk, undersized'),
        pytest.param(2, 6, 3, id='multiple chunks, no remainder'),
        pytest.param(2, 5, 3, id='multiple chunks, has remainder'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_file_chunks(
        stq_runner,
        mds_s3_storage,
        nmn_vwr_utils,
        update_taxi_config,
        # parametrize
        chunk_size,
        product_count,
        expected_chunk_count,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_UPLOAD_TO_VIEWER_SETTINGS',
        {'products_in_file_count': chunk_size},
    )

    db_product_ids = sorted(
        [
            f'00000000-0000-0000-0000-00000000000{i}'
            for i in range(0, product_count)
        ],
    )

    for i in db_product_ids:
        nmn_vwr_utils.sql.save_category_product(
            models.CategoryProduct(
                product=models.Product(BRAND_ID, public_id=i),
                assortment_id=ASSORTMENT_ID,
            ),
            category_id=DEFAULT_CATEGORY_ID,
        )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3_paths = sorted([])
    s3_product_ids = sorted([])
    for path, value in mds_s3_storage.storage.items():
        s3_paths += [path]
        s3_products = json.loads(value.data)['products']
        assert len(s3_products) <= chunk_size
        s3_product_ids += [i['id'] for i in s3_products]

    assert s3_product_ids == db_product_ids
    assert len(s3_paths) == expected_chunk_count

    path_pattern = f'{S3_PREFIX}{BRAND_ID}/([a-f0-9]+)/([0-9]).json'
    s3_file_uuid = re.match(path_pattern, s3_paths[0]).group(1)
    for i, s3_path in enumerate(s3_paths):
        match = re.match(path_pattern, s3_path)
        assert bool(match)
        assert match.group(1) == s3_file_uuid
        assert match.group(2) == str(i)


def _sql_add_assortment(pg_cursor, assortment_name=None):
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
            f"""
            insert into eats_nomenclature.assortment_traits(
                brand_id,
                assortment_name
            )
            values ({assortment_id}, '{assortment_name}')
            returning id
        """,
        )
        trait_id = pg_cursor.fetchone()[0]
    else:
        trait_id = None

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.place_assortments(
            place_id,
            assortment_id,
            in_progress_assortment_id,
            trait_id
        )
        values
            (1, null, {assortment_id}, {trait_id if trait_id else 'null'})
    """,
    )

    return assortment_id, trait_id
