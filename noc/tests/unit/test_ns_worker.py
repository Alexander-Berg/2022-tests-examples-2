from unittest.mock import patch, Mock, PropertyMock
from datetime import datetime, timedelta
import json
import copy

import pytest
import responses

from workers.tests.unit.helpers import rtnmgr_mappings, ns_mappings
from workers.ns_worker import update_rtnmgr_with_ns_applied, UpdateRTNMGRWithNSApplied


additional_mapping = {"additional.mapping": ["80.239.201.199", "149.5.244.199", "2001:2030:20::9999"]}

rtnmgr_mappings_additional_mapping = copy.deepcopy(rtnmgr_mappings)
rtnmgr_mappings_additional_mapping["data"]["mappings"].update(**additional_mapping)


rtnmgr_mappings_no_v6 = copy.deepcopy(rtnmgr_mappings)
del rtnmgr_mappings_no_v6["data"]["mappings"]["yastat.net"]


@pytest.mark.parametrize(
    "rtnmgr_mappings, ns_mappings, additional_mapping",
    [
        (rtnmgr_mappings, ns_mappings, None),
        (rtnmgr_mappings_additional_mapping, ns_mappings, additional_mapping),
        (rtnmgr_mappings_no_v6, ns_mappings, None),
    ],
)
@patch("workers.ns_worker.requests.put", new_callable=Mock)
@patch(
    "workers.ns_worker.UpdateRTNMGRWithNSApplied._ns_update_timout_not_exceed",
    # The side effect works for all test cases (there is currently three cases.
    # Every test case makes two calls of _ns_update_timout_not_exceed)
    PropertyMock(side_effect=[True, False, True, False, True, False]),
)
@responses.activate
def test_expected_status_from_ns_worker(put_status_mock, rtnmgr_mappings, ns_mappings, additional_mapping):
    UpdateRTNMGRWithNSApplied.NS_API_QUERY_INTERVAL_SECONDS = 0.0001
    responses.add(
        responses.GET, UpdateRTNMGRWithNSApplied.RTNMGR_COLLECT_MAPPINGS_URL, json=rtnmgr_mappings, status=200
    )
    responses.add(responses.GET, UpdateRTNMGRWithNSApplied.NS_API_COLLECT_MAPPINGS_URL, json=ns_mappings, status=200)

    update_rtnmgr_with_ns_applied()

    for domain, ips in json.loads(put_status_mock.call_args[1]["data"]).items():
        if additional_mapping:
            assert domain != tuple(additional_mapping.keys())[0]
            assert set(ips) != set(tuple(additional_mapping.values())[0])
        assert set(ips) == set(rtnmgr_mappings["data"]["mappings"][domain])
