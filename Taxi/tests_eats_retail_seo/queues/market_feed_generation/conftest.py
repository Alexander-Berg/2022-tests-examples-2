import pytest

from ... import constants
from ... import models


@pytest.fixture
def load_result_market_feed(generate_feed_s3_path, mds_s3_storage):
    def do_load(brand: models.Brand):
        s3_path = generate_feed_s3_path(
            constants.S3_DIRS[constants.MARKET_FEED_TYPE], brand,
        )
        return mds_s3_storage.storage[s3_path].data.decode('utf-8')

    return do_load
