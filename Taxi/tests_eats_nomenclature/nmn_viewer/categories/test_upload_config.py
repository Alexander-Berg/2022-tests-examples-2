import pytest

from . import constants
from .. import models
from ... import utils

S3_PREFIX = constants.S3_PREFIX
ASSORTMENT_ID = constants.ASSORTMENT_ID
BRAND_ID = constants.BRAND_ID


@pytest.mark.parametrize(**utils.gen_bool_params('enable_upload'))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'brand_place.sql', 'assortment.sql'],
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

    category = models.Category(assortment_id=ASSORTMENT_ID)
    category.add_product(models.Product(brand_id=BRAND_ID))
    nmn_vwr_utils.sql.save(category)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    assert bool(mds_s3_storage.storage) == enable_upload
    assert (
        stq.eats_nomenclature_viewer_update_categories.has_calls
        == enable_upload
    )
