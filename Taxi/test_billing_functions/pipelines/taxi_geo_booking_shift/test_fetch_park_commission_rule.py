import pytest

from billing.docs import service as docs
from billing_models.generated import models
from generated.clients import driver_work_modes as dwm_client

from billing_functions.functions import fetch_park_commission_rules
from billing_functions.stq.pipelines._taxi_geo_booking_shift import (
    fetch_park_commission_rule as pipline_handler,
)
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    Query=fetch_park_commission_rules.Query,
    ParkCommissionRules=equatable.codegen(models.ParkCommissionRules),
    ParkCommissionRule=models.BaseParkCommissionRule,
)
@pytest.mark.parametrize('test_data_json', ['test_data.json'])
async def test_taxi_geo_booking_shift_fetch_park_commission_rule(
        test_data_json, stq3_context, load_py_json,
):
    raw_doc = load_py_json('taxi_geo_booking_shift.json')
    data = models.taxi_geo_booking_shift.TaxiGeoBookingShift.deserialize(
        raw_doc.data,
    )
    taxi_geo_booking_shift_doc = docs.TypedDoc.from_doc(raw_doc, data)
    test_data = load_py_json(test_data_json)
    actual_query = None

    async def _function(
            driver_work_modes_client: dwm_client.DriverWorkModesClient,
            query: fetch_park_commission_rules.Query,
    ) -> models.ParkCommissionRules:
        del driver_work_modes_client  # unused
        nonlocal actual_query
        actual_query = query
        return test_data['park_commission_rules']

    actual_results = await pipline_handler.handle(
        stq3_context, taxi_geo_booking_shift_doc, _function,
    )
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['park_commission_rules']
