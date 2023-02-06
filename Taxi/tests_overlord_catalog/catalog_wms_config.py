import re

import pytest


WMS_GOODS_DATA_CONFIG = {'goods-data': 'catalog_wms'}


GET_WMS_MENU = pytest.mark.config(
    OVERLORD_CATALOG_GOODS_DATA_SOURCE=WMS_GOODS_DATA_CONFIG,
)

# Use this one if not sure what you need.
# If you add specific config, add it here too.
GET_EVERYTHING_FROM_WMS = pytest.mark.config(
    OVERLORD_CATALOG_GOODS_DATA_SOURCE=WMS_GOODS_DATA_CONFIG,
)

GET_EVERYTHING_FROM_1C_AND_WMS = pytest.mark.parametrize(
    '',
    [
        '',
        pytest.param(
            marks=pytest.mark.config(
                OVERLORD_CATALOG_GOODS_DATA_SOURCE=WMS_GOODS_DATA_CONFIG,
            ),
        ),
    ],
)

# A helper function to distinguish 1C ids from WMS ids
# Works only if the mock WMS ids were 'wmsified', otherwise WMS mock data
# contains uuids
def is_uuid(some_id):
    pattern = re.compile(
        '^[0-9a-f]{8,8}-[0-9a-f]{4,4}-[0-9a-f]{4,4}-'
        '[0-9a-f]{4,4}-[0-9a-f]{12,12}$',
    )
    return pattern.match(some_id) is not None
