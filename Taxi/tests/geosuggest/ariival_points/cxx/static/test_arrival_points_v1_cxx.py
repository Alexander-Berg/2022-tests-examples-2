from ctaxi_pyml.geosuggest.arrival_points import v2 as cxx
from ctaxi_pyml.common import geo as cxx_geo


def test_storage():
    storage = cxx.ArrivalPointsStorage()
    candidates = []
    candidates.append(cxx.ArrivalPoint('0', cxx_geo.GeoPoint(1, 2), 3))
    address = cxx.Address('org_id', 4, candidates)
    storage.add(address)

    assert storage.addresses['org_id'].popularity == 4
    assert len(storage.addresses['org_id'].candidates) == 1
    assert storage.addresses['org_id'].candidates[0].id == '0'
