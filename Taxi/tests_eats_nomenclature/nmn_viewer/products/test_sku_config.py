import pytest

from . import constants
from .. import models
from ... import utils

ASSORTMENT_ID = constants.ASSORTMENT_ID
BRAND_ID = constants.BRAND_ID
DEFAULT_CATEGORY_ID = constants.CATEGORY_ID


@pytest.mark.parametrize(**utils.gen_bool_params('enable_sku'))
@pytest.mark.parametrize(**utils.gen_bool_params('exclude_brand'))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_sku_experiment(
        stq_runner,
        nmn_vwr_utils,
        exp_set_sku_data,
        # parametrize
        enable_sku,
        exclude_brand,
):
    await exp_set_sku_data(enable_sku, [BRAND_ID] if exclude_brand else [])

    sku = models.Sku(name='overriden')
    product = models.Product(name='original', sku=sku, brand_id=BRAND_ID)
    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(product=product, assortment_id=ASSORTMENT_ID),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3product = nmn_vwr_utils.s3_get_single_product()
    name = s3product['name']
    if not enable_sku or exclude_brand:
        assert name == product.name
    else:
        assert name == sku.name


@pytest.mark.parametrize(**utils.gen_bool_params('use_fallback'))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_image_fallback(
        pg_cursor,
        stq_runner,
        nmn_vwr_utils,
        exp_set_sku_data,
        # parametrize
        use_fallback,
):
    await exp_set_sku_data(True)

    _sql_set_brand_fallback(
        pg_cursor,
        brand_id=BRAND_ID,
        should_fallback_to_product_picture=use_fallback,
    )

    product_image = models.Image(raw_url='raw', processed_url='processed')

    sku = models.Sku()
    product = models.Product(
        sku=sku, images=[product_image], brand_id=BRAND_ID,
    )
    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(product=product, assortment_id=ASSORTMENT_ID),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3product = nmn_vwr_utils.s3_get_single_product()
    images = s3product['images']
    if use_fallback:
        assert images == [
            {'url': product_image.processed_url, 'sort_order': 0},
        ]
    else:
        assert not images


def _sql_set_brand_fallback(
        pg_cursor, brand_id, should_fallback_to_product_picture,
):
    pg_cursor.execute(
        f"""
        update eats_nomenclature.brands
        set
          fallback_to_product_picture =
            {should_fallback_to_product_picture}
        where id = {brand_id}
    """,
    )
