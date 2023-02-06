import json
import os

from market_platform_eff_etl.layer.greenplum.ods.datacamp.cpa_offer_service.impl import EXTRACTORS
from test_market_platform_eff_etl.layer.greenplum.ods.common import execute_extractors


def test_whole_object():
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, 'data/input.json'), 'r') as f:
        parsed = execute_extractors(json.load(f), EXTRACTORS)
    expected = {
        "utc_event_processed_dttm": "2022-03-01 00:20:34",
        "synthetic_id": 1646094034984404848,
        "ssku": "059199.833331",
        "b2b_partner_business_id": 921851,
        "b2b_partner_id": 465852,
        "b2b_partner_type_id": None,
        "b2b_partner_1p_id": "059199"
    }

    assert parsed == expected
