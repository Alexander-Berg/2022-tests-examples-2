import datetime as dt
import re

import pytest
import pytz

from . import constants
from ... import utils

S3_NMN_PATH = 'data.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.parametrize(**utils.gen_bool_params('enable_upload'))
@pytest.mark.s3(files={S3_NMN_PATH: 'data_template.json'})
@pytest.mark.pgsql('eats_nomenclature', files=['brand_place.sql'])
async def test_config_upload_state(
        stq,
        stq_runner,
        mds_s3_storage,
        test_utils,
        # parametrize
        enable_upload,
):
    test_utils.config_set_upload_state(enable_upload)

    await stq_runner.eats_nomenclature_brand_processing.call(
        task_id='1',
        args=[],
        kwargs={
            'brand_id': '1',
            's3_path': S3_NMN_PATH,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    s3_items = [
        i
        for i in mds_s3_storage.storage.items()
        if re.match(constants.S3_PATH_PATTERN, i[0])
    ]

    assert bool(s3_items) == enable_upload
    assert (
        stq.eats_nomenclature_viewer_update_vendor_data.has_calls
        == enable_upload
    )
