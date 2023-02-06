import pytest

from billing.docs import service as docs
from billing_models.generated import models
from generated.clients import subvention_communications as subv_comms

from billing_functions.functions import notify_geo_booking
from billing_functions.stq.pipelines._taxi_geo_booking_shift import notify


@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    Query=notify_geo_booking.Query,
    Driver=notify_geo_booking.Driver,
)
@pytest.mark.parametrize('test_data_json', ['enabled.json'])
async def test_taxi_geo_booking_shift_notify(
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
            sc_client: subv_comms.SubventionCommunicationsClient,
            query: notify_geo_booking.Query,
    ):
        del sc_client  # unused
        nonlocal actual_query
        actual_query = query

    actual_results = await notify.handle(
        stq3_context, taxi_geo_booking_shift_doc, _function,
    )
    assert actual_query == test_data['expected_query']
    assert actual_results is None
