from __future__ import annotations

import decimal

from billing.docs import service as docs
from billing_models.generated.models import taxi_goal_shift
from taxi import billing
from taxi.billing.util import dates

from billing_functions.functions import check_in_antifraud
from billing_functions.stq.pipelines._taxi_goal_shift import (
    check_in_antifraud as handler,
)

TEST_DOC_ID = 18061991


async def test_pass_if_zero_subvention(load_json, stq3_context):
    doc = _make_taxi_shift(load_json('taxi_shift_goal.json'))
    assert doc.data.payment
    doc.data.payment.amount = '0.0'
    results = await handler.handle(stq3_context, doc)
    assert results.next_status == 'fetch_park_commission_rule'


async def test_pass_if_zero_subvention_per_contractd(load_json, stq3_context):
    doc = _make_taxi_shift(load_json('taxi_shift_goal.json'))
    assert doc.data.payment
    doc.data.pay_per_contract = 'yes'
    doc.data.payment.amount_per_contract = '0.0'
    results = await handler.handle(stq3_context, doc)
    assert results.next_status == 'fetch_park_commission_rule'


async def test_goal_doc_is_converted_to_check_driver_request(load_json):
    doc = load_json('taxi_shift_goal.json')
    actual_query = check_in_antifraud.make_goal_query_from_taxi_shift(
        _make_taxi_shift(doc),
    )
    assert actual_query == check_in_antifraud.CheckDriverQuery(
        doc_id=TEST_DOC_ID,
        subvention=billing.Money(decimal.Decimal(100), 'RUB'),
        driver_info=check_in_antifraud.CheckDriverQuery.Driver(
            unique_driver_id='some_unique_driver_id',
            driver_license_personal_id='some_driver_license_personal_id',
            driver_profile_id='some_driver_profile_id',
            park_id='some_park_id',
        ),
        rule_info=check_in_antifraud.CheckDriverQuery.Rule(
            type='goal',
            days_span=3,
            min_num_orders=10,
            period_end=dates.parse_datetime('2020-07-05T00:00:00+03:00'),
            time_zone='Europe/Moscow',
        ),
        subvention_ref='some_subvention_ref',
        payment=billing.Money(decimal.Decimal(100), 'RUB'),
        shift_orders=None,
    )


def _make_taxi_shift(
        raw_doc: dict,
) -> docs.TypedDoc[taxi_goal_shift.TaxiGoalShift]:
    return docs.TypedDoc(
        id=raw_doc['doc_id'],
        kind=raw_doc['kind'],
        topic=raw_doc['external_obj_id'],
        external_ref=raw_doc['external_event_ref'],
        event_at=raw_doc['event_at'],
        process_at=raw_doc['process_at'],
        status=raw_doc['status'],
        data=taxi_goal_shift.TaxiGoalShift.deserialize(raw_doc['data']),
        entry_ids=[],
        revision=1,
    )
