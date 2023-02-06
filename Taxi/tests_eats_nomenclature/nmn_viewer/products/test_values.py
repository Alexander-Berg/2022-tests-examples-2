import json
import pathlib
import re

import pytest

from . import constants
from .. import models
from ... import utils

S3_PREFIX = constants.S3_PREFIX
ASSORTMENT_ID = constants.ASSORTMENT_ID
BRAND_ID = constants.BRAND_ID
DEFAULT_CATEGORY_ID = constants.CATEGORY_ID

S3_PATH_PATTERN = f'{S3_PREFIX}{BRAND_ID}/[a-f0-9]+/0.json'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
        'minimal_schema_data.sql',
    ],
)
async def test_minimal_schema(
        stq, stq_runner, load_json, mds_s3_storage, nmn_vwr_utils,
):
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3path, s3value = _get_single_item_from_s3(mds_s3_storage)
    assert bool(re.match(S3_PATH_PATTERN, s3path))
    assert (
        nmn_vwr_utils.sorted_json_data(json.loads(s3value.data))
        == nmn_vwr_utils.sorted_json_data(
            load_json('minimal_schema_result.json'),
        )
    )
    task_info = stq.eats_nomenclature_viewer_update_products.next_call()
    assert task_info['kwargs']['s3_path'] == str(pathlib.Path(s3path).parent)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
        'full_schema_data.sql',
    ],
)
async def test_full_schema(
        stq_runner, stq, load_json, mds_s3_storage, nmn_vwr_utils,
):
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3path, s3value = _get_single_item_from_s3(mds_s3_storage)
    assert bool(re.match(S3_PATH_PATTERN, s3path))
    assert nmn_vwr_utils.sorted_json_data(
        json.loads(s3value.data),
    ) == nmn_vwr_utils.sorted_json_data(load_json('full_schema_result.json'))
    task_info = stq.eats_nomenclature_viewer_update_products.next_call()
    assert task_info['kwargs']['s3_path'] == str(pathlib.Path(s3path).parent)


@pytest.mark.parametrize(
    'product_params,expected_fields',
    [
        # catch weight handling
        pytest.param(
            {'is_catch_weight': False, 'quantum': 0.3},
            {'quantum': None},
            id='quantum when not catch weight',
        ),
        pytest.param(
            {'is_catch_weight': True, 'quantum': 0.3},
            {'quantum': 0.3},
            id='quantum when catch weight',
        ),
        # known measure units
        pytest.param(
            {'measure_unit': 'GRM'}, {'measure/unit': 'GRM'}, id='GRM',
        ),
        pytest.param(
            {'measure_unit': 'KGRM'}, {'measure/unit': 'KGRM'}, id='KGRM',
        ),
        pytest.param(
            {'measure_unit': 'MLT'}, {'measure/unit': 'MLT'}, id='MLT',
        ),
        pytest.param({'measure_unit': 'LT'}, {'measure/unit': 'LT'}, id='LT'),
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
async def test_fields(
        stq_runner,
        nmn_vwr_utils,
        # parametrize
        product_params,
        expected_fields,
):
    product = models.Product(brand_id=BRAND_ID, **product_params)
    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(product=product, assortment_id=ASSORTMENT_ID),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3product = nmn_vwr_utils.s3_get_single_product()
    nmn_vwr_utils.verify_json_field(s3product, expected_fields)


@pytest.mark.parametrize(
    'product_params,expected_attributes',
    [
        pytest.param(
            {'package_info': 'не указано'},
            {'package_info': None},
            id='package info ignored value',
        ),
        pytest.param(
            {'is_adult': True},
            {'is_adult': {'value': False}},
            id='ignore original adult value',
        ),
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
async def test_attributes(
        stq_runner,
        nmn_vwr_utils,
        # parametrize
        product_params,
        expected_attributes,
):
    product = models.Product(brand_id=BRAND_ID, **product_params)
    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(product=product, assortment_id=ASSORTMENT_ID),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3product = nmn_vwr_utils.s3_get_single_product()
    nmn_vwr_utils.verify_json_attribute(s3product, expected_attributes)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_image_url_filtering(stq_runner, nmn_vwr_utils):
    """
    Verifies that images without processed url are ignored
    """

    image_to_display = models.Image(
        raw_url='raw_1', processed_url='processed_1',
    )
    image_to_ignore = models.Image(raw_url='raw_2', processed_url=None)

    product = models.Product(
        images=[image_to_display, image_to_ignore], brand_id=BRAND_ID,
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
    assert images == [{'url': image_to_display.processed_url, 'sort_order': 0}]


@pytest.mark.parametrize(**utils.gen_bool_params('use_product_override'))
@pytest.mark.parametrize(**utils.gen_bool_params('use_sku'))
@pytest.mark.parametrize(**utils.gen_bool_params('use_sku_override'))
@pytest.mark.parametrize(**utils.gen_bool_params('is_empty_sku_override'))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_product_attributes_override(
        stq_runner,
        nmn_vwr_utils,
        # parametrize
        use_product_override,
        use_sku,
        use_sku_override,
        is_empty_sku_override,
):
    sku = models.Sku(
        attributes=models.ProductAttributes(type='sku', brand='sku'),
    )
    sku_override = models.Sku(
        attributes=models.ProductAttributes(
            type='sku overriden', brand='sku overriden',
        ),
    )
    product = models.Product(
        brand_id=BRAND_ID,
        sku=sku if use_sku else None,
        use_sku_override=use_sku_override,
        sku_override=None if is_empty_sku_override else sku_override,
        overriden_attributes=models.ProductAttributes(
            type='overriden', brand='overriden',
        )
        if use_product_override
        else None,
    )
    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(product=product, assortment_id=ASSORTMENT_ID),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3product = nmn_vwr_utils.s3_get_single_product()
    if use_product_override:
        nmn_vwr_utils.verify_json_attribute(
            s3product,
            {
                'product_brand': {'value': product.overriden_attributes.brand},
                'product_type': {'value': product.overriden_attributes.type},
            },
        )
    elif use_sku_override and not is_empty_sku_override:
        nmn_vwr_utils.verify_json_attribute(
            s3product,
            {
                'product_brand': {'value': sku_override.attributes.brand},
                'product_type': {'value': sku_override.attributes.type},
            },
        )
    elif use_sku and not (use_sku_override and is_empty_sku_override):
        nmn_vwr_utils.verify_json_attribute(
            s3product,
            {
                'product_brand': {'value': sku.attributes.brand},
                'product_type': {'value': sku.attributes.type},
            },
        )
    else:
        nmn_vwr_utils.verify_json_attribute(
            s3product, {'product_brand': None, 'product_type': None},
        )


def _get_single_item_from_s3(mds_s3_storage):
    return list(mds_s3_storage.storage.items())[0]
