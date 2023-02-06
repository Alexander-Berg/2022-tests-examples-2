from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated.models import taxi_geo_booking_shift
from taxi.billing.util import dates

from billing_functions.functions import create_entries
from billing_functions.functions import generate_reversal_entries
from billing_functions.stq import converters
from test_billing_functions import equatable

_DOC_ID = 18061991
_MOCK_NOW = '2020-12-31T23:59:59.999999+03:00'
_MOCK_NOW_DT = dates.parse_datetime(_MOCK_NOW)


@pytest.mark.config(
    BILLING_FUNCTIONS_ADD_TLOG_EXTERNAL_REF='2001-01-01T00:00:00+00:00',
    BILLING_FUNCTIONS_ADD_TLOG_TARGET='2001-01-01T00:00:00+00:00',
)
@pytest.mark.json_obj_hook(
    Query=create_entries.Query,
    Template=create_entries.Query.Template,
    TLogV1Customizer=equatable.by_type(
        generate_reversal_entries.TlogV1Customizer,
    ),
    TLogV2Customizer=equatable.by_type(
        generate_reversal_entries.TlogV2Customizer,
    ),
    DriverIncomeCustomizer=equatable.by_type(
        generate_reversal_entries.DriverIncomeCustomizer,
    ),
)
@pytest.mark.now(_MOCK_NOW)
def test_make_query(stq3_context, taxi_shift_doc, load_py_json):
    query = converters.create_gb_entries_query(
        stq3_context.config,
        taxi_shift_doc.id,
        taxi_shift_doc,
        _MOCK_NOW_DT,
        af_decision_revise=None,
    )
    expected_query = load_py_json('expected_query.json')
    assert query == expected_query


@pytest.fixture(name='taxi_shift_doc')
def _make_taxi_shift(
        load_py_json,
) -> docs.TypedDoc[taxi_geo_booking_shift.TaxiGeoBookingShift]:
    doc = docs.Doc(**load_py_json('doc.json'))
    data = taxi_geo_booking_shift.TaxiGeoBookingShift.deserialize(doc.data)
    return docs.TypedDoc.from_doc(doc, data)
