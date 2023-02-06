from noc.megaping.megaping.zmap_connector import ZmapConnector
from noc.megaping.megaping.lib import Target


def test_check_ip():
    data = {
        "AS1": Target("AS1", ["1.1.1.1", "10.10.10.10", "192.168.1.1", "192.168.1.2"]),
        "AS2": Target("AS2", ["1.1.1.2", "1.1.1.3", "1.1.1.4"]),
    }
    unmerge_map, merged_targets = ZmapConnector._merge_requests(data, max_prefixes=2)
    e = Exception()
    merged_targets["merged_origin_AS2"] = e
    result = ZmapConnector._unmerge_requests(unmerge_map, merged_targets)
    assert result == {"AS2": e, "AS1": data["AS1"]}
