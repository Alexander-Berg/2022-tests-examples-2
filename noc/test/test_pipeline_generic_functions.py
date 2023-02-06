from noc.grad.grad.lib.functions import call_sendgen
from noc.grad.grad.lib.pipeline_generic_functions import rename_keys, group_by_count


def test_rename_keys():
    in_data = [[1628407800, {'index': '1', 'host': 'sas1-i8'}, {'load1': 123, 'load5': 2.0}]]
    res = call_sendgen(rename_keys, filter={"index": "component"}, send=in_data)
    assert res == [[1628407800, {'host': 'sas1-i8', 'component': '1'}, {'load1': 123, 'load5': 2.0}]]


def test_group_by_count():
    in_data = [
        [1635945607, {"ap_name": "oko-1", "host": "oko-iap-wlc"}, {"iap_uptime": 17947010.0}],
        [1635945607, {"ap_name": "oko-2", "host": "oko-iap-wlc"}, {"iap_uptime": 17947005.0}],
        [1635945607, {"ap_name": "oko-2", "host": "oko-iap-wlc"}, {"iap_uptime": 17947003.0}],
    ]
    res = call_sendgen(group_by_count, keys=["host"], new_sensor="olo", send=in_data.copy())
    assert res == in_data.copy() + [[1635945607, {"host": "oko-iap-wlc"}, {"olo": 3}]]
    res = call_sendgen(group_by_count, keys=["ap_name"], new_sensor="olo", send=in_data.copy())
    assert res == in_data.copy() + [
        [1635945607, {"ap_name": "oko-1"}, {"olo": 1}],
        [1635945607, {"ap_name": "oko-2"}, {"olo": 2}],
    ]
