from taxi_etl.layer.yt.ods.billing.common.impl import (
    get_executor_profile_id,
    get_park_taximeter_id,
)


def test_get_executor_profile_id():
    assert get_executor_profile_id('taximeter_driver_id/123/456') == '456'
    assert get_executor_profile_id('taximeter_driver_id/123/456/789') == '456/789'
    assert get_executor_profile_id('taximeter_driver_id_1/123/456/789') is None
    assert get_executor_profile_id('') is None


def test_get_park_taximeter_id():
    assert get_park_taximeter_id('taximeter_driver_id/123/456') == '123'
    assert get_park_taximeter_id('taximeter_driver_id_1/123/456/789') is None
    assert get_park_taximeter_id('') is None
