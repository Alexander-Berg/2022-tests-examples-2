from unittest.mock import patch

import pytest
from market_b2c_etl.layer.yt.cdm.b2c import YTDmOrderItem
from test_market_b2c_etl.layer.greenplum.ods.common.test_extractors import (
    execute_extractors,
)


def patch_apply():
    def apply(fn, field):
        return lambda data: fn(data[field])

    return patch("dmp_suite.market.olap.extractors.apply", apply)


def test_precense_of_fields(unit_test_settings):
    with unit_test_settings(), patch_apply():
        from market_b2c_etl.layer.yt.olap.cube_gp_order_item.table import (
            CubeOrderItem,
        )
        from market_b2c_etl.layer.yt.olap.cube_gp_order_item.names_mapping import (
            EXTRACTORS,
        )

        cube_order_item_dict_fields = set(CubeOrderItem.field_names())
        dummy_dm_order_item_record = {
            field: None
            for field in YTDmOrderItem.field_names()
        }

        for target_field in EXTRACTORS:
            assert target_field in cube_order_item_dict_fields, "the target table doesn't have a given field"

        try:
            execute_extractors(dummy_dm_order_item_record, EXTRACTORS)
        except:
            pytest.fail("Some extractor failed")
