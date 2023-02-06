import json
import re

import pytest

from . import constants
from .. import models

S3_PREFIX = constants.S3_PREFIX
ASSORTMENT_ID = constants.ASSORTMENT_ID
BRAND_ID = constants.BRAND_ID
PLACE_ID = constants.PLACE_ID

S3_PATH_PATTERN = f'{S3_PREFIX}{BRAND_ID}/[a-f0-9]+.json'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment.sql',
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

    task_info = stq.eats_nomenclature_viewer_update_categories.next_call()
    assert task_info['kwargs']['s3_path'] == s3path
    assert task_info['kwargs']['brand_id'] == BRAND_ID
    assert task_info['kwargs']['place_ids'] == [PLACE_ID]
    assert task_info['kwargs']['assortment_name'] == 'partner'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment.sql',
        'full_schema_data.sql',
    ],
)
async def test_full_schema(
        stq, stq_runner, load_json, mds_s3_storage, nmn_vwr_utils,
):
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3path, s3value = _get_single_item_from_s3(mds_s3_storage)
    assert bool(re.match(S3_PATH_PATTERN, s3path))
    assert nmn_vwr_utils.sorted_json_data(
        json.loads(s3value.data),
    ) == nmn_vwr_utils.sorted_json_data(load_json('full_schema_result.json'))

    task_info = stq.eats_nomenclature_viewer_update_categories.next_call()
    assert task_info['kwargs']['s3_path'] == s3path
    assert task_info['kwargs']['brand_id'] == BRAND_ID
    assert task_info['kwargs']['place_ids'] == [PLACE_ID]
    assert task_info['kwargs']['assortment_name'] == 'partner'


@pytest.mark.parametrize(
    'category_params,expected_fields',
    [
        # category types
        pytest.param(
            {'is_custom': False, 'is_base': True},
            {'type': 'partner'},
            id='partner with is_base',
        ),
        pytest.param(
            {'is_custom': False, 'is_base': False},
            {'type': 'partner'},
            id='partner without is_base',
        ),
        # TODO: uncomment once the export is migrated to a separate queue
        # pytest.param({'is_custom': True, 'is_base': True},
        #  {'type': 'custom_base'}, id='custom base'),
        # pytest.param({'is_custom': True, 'is_base': False},
        #  {'type': 'custom_promo'}, id='custom promo'),
        # pytest.param({'is_custom': True, 'is_restaurant': True},
        # {'type': 'custom_restaurant'}, id='custom restaurant'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'brand_place.sql', 'assortment.sql'],
)
async def test_fields(
        stq_runner,
        nmn_vwr_utils,
        # parametrize
        category_params,
        expected_fields,
):
    category = models.Category(assortment_id=ASSORTMENT_ID, **category_params)
    category.add_product(models.Product(brand_id=BRAND_ID))
    nmn_vwr_utils.sql.save(category)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3category = nmn_vwr_utils.s3_get_single_category()
    nmn_vwr_utils.verify_json_field(s3category, expected_fields)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'brand_place.sql', 'assortment.sql'],
)
async def test_image_url_filtering(stq_runner, nmn_vwr_utils):
    """
    Verifies that images without processed url are ignored
    """

    image_to_display = models.Image(
        raw_url='raw_1', processed_url='processed_1',
    )
    image_to_ignore = models.Image(raw_url='raw_2', processed_url=None)

    category = models.Category(
        assortment_id=ASSORTMENT_ID,
        images=[image_to_display, image_to_ignore],
    )
    category.add_product(models.Product(brand_id=BRAND_ID))
    nmn_vwr_utils.sql.save(category)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3category = nmn_vwr_utils.s3_get_single_category()
    images = s3category['images']
    assert images == [{'url': image_to_display.processed_url, 'sort_order': 0}]


def _get_single_item_from_s3(mds_s3_storage):
    return list(mds_s3_storage.storage.items())[0]
