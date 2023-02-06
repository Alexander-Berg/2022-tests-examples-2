from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated.models import taxi_geo_booking_shift

from billing_functions.functions import check_in_antifraud
from billing_functions.generated.stq3 import stq_context
from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._taxi_geo_booking_shift import (
    check_in_antifraud as handler,
)
from test_billing_functions import equatable

TEST_DOC_ID = 18061991


@pytest.mark.json_obj_hook(
    Query=check_in_antifraud.CheckDriverQuery,
    Driver=check_in_antifraud.CheckDriverQuery.Driver,
    Rule=check_in_antifraud.CheckDriverQuery.Rule,
    Antifraud=equatable.codegen(check_in_antifraud.Result),
    Results=pipeline.Results,
    Doc=docs.Doc,
)
@pytest.mark.parametrize(
    'test_data_json',
    ['delay.json', 'pay.json', 'block.json', 'zero_payment.json'],
)
async def test_doc_is_converted_to_check_driver_request(
        test_data_json, *, load_py_json, stq3_context,
):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['doc']
    data = taxi_geo_booking_shift.TaxiGeoBookingShift.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _func(
            context: stq_context.Context, query: check_in_antifraud.Query,
    ) -> check_in_antifraud.Result:
        del context  # unused
        nonlocal actual_query
        actual_query = query
        return check_in_antifraud.Result(
            antifraud_id='some_af_id', decision=test_data['af_decision'],
        )

    actual_results = await handler.handle(stq3_context, doc, _func)
    assert actual_results == test_data['expected_results']
    assert actual_query == test_data['expected_query']
