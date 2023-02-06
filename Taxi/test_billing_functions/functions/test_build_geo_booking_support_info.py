import pytest

from billing_models.generated import models

from billing_functions.functions import build_geo_booking_support_info
from test_billing_functions import equatable


@pytest.mark.parametrize('test_data_json', ['paid.json', 'blocked.json'])
@pytest.mark.json_obj_hook(
    Query=build_geo_booking_support_info.Query,
    GeoBookingSupportInfo=equatable.codegen(models.GeoBookingSupportInfo),
    GeoBookingSupportInfoData=models.GeoBookingSupportInfoData,
    SupportInfoGeoBookingRule=models.SupportInfoGeoBookingRule,
    SupportInfoIncome=models.SupportInfoIncome,
    SupportInfoPayout=models.SupportInfoPayout,
    CalculatedValue=models.CalculatedValue,
    Calculation=models.Calculation,
    Money=models.Money,
)
def test_build_geo_booking_support_info(test_data_json, load_py_json):
    test_data = load_py_json(test_data_json)
    support_info = build_geo_booking_support_info.execute(test_data['query'])
    assert support_info == test_data['expected_support_info']
