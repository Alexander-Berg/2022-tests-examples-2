from __future__ import annotations

import datetime

import pytest

from billing.docs import service as docs
from billing_models.generated import models
from generated.clients import billing_subventions
from testsuite.utils import ordered_object

from billing_functions.functions import calculate_subventions
from billing_functions.functions.core import events
from billing_functions.functions.core import types
from billing_functions.repositories import antifraud
from billing_functions.repositories import cities
from billing_functions.repositories import commission_agreements
from billing_functions.repositories import currency_rates
from billing_functions.repositories import migration_mode
from billing_functions.repositories import service_ids
from billing_functions.stq.pipelines._taxi_order import (
    calculate_subventions as handler,
)
from test_billing_functions import equatable

_MOCK_NOW = '2021-01-01T00:00:00.000+00:00'


@pytest.mark.parametrize(
    'test_data_json', ['test_data.json', 'old_order.json'],
)
@pytest.mark.json_obj_hook(
    Query=calculate_subventions.Query,
    Order=calculate_subventions.Query.Order,
    Driver=calculate_subventions.Query.Driver,
    Contract=calculate_subventions.Query.Contract,
    Commission=calculate_subventions.Query.Commission,
    ShiftsConfig=calculate_subventions.Query.ShiftsConfig,
    Subventions=equatable.codegen(models.Subventions),
    Doc=docs.Doc,
    # raw agreement
    HiringInfo=commission_agreements.Query.HiringInfo,
    Agreement=commission_agreements.Agreement,
    RateFlat=commission_agreements.RateFlat,
    RateAbsolute=commission_agreements.RateAbsolute,
    RateAsymptotic=commission_agreements.RateAsymptotic,
    CancellationSettings=commission_agreements.CancellationSettings,
    CancellationInterval=commission_agreements.CancellationInterval,
    BrandingDiscount=commission_agreements.BrandingDiscount,
    CostInfoBoundaries=commission_agreements.CostInfoBoundaries,
    CostInfoAbsolute=commission_agreements.CostInfoAbsolute,
)
@pytest.mark.config(
    PROCESS_SHIFT_ENDED_MIN_MSK_TIME='04:00',
    BILLING_FUNCTIONS_MULTIPLY_INSTANT_PAYMENTS_BY_COUNTER_SINCE=(
        '2020-12-22T11:48:39+03:00'
    ),
    BILLING_FUNCTIONS_ENABLE_GOAL_AF_PRECHECK_SINCE={
        '__default__': '2019-12-31T21:00:00+00:00',
    },
)
@pytest.mark.now(_MOCK_NOW)
async def test(
        test_data_json,
        *,
        stq3_context,
        load_py_json,
        mock_billing_subventions_x,
):
    test_data = load_py_json(test_data_json)
    mock_billing_subventions_x(
        test_data['bsx_v1_rules_match_responses'],
        test_data['bsx_v2_rules_match_responses'],
    )

    raw_doc = test_data['taxi_order']
    data = models.TaxiOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)
    results = models.Subventions(
        is_eligible=False, skip_reason='not_implemented',
    )

    actual_query = None

    async def _function(
            antifraud_repo: antifraud.Repository,
            service_ids_repo: service_ids.Repository,
            currency_rates_repo: currency_rates.Repository,
            cities_repo: cities.Repository,
            migration_repo: migration_mode.Repository,
            bs_client: billing_subventions.BillingSubventionsClient,
            shift_scheduler: events.Scheduler,
            query: calculate_subventions.Query,
    ) -> models.Subventions:
        del antifraud_repo  # unused
        del service_ids_repo  # unused
        del currency_rates_repo  # unused
        del cities_repo  # unused
        del migration_repo  # unused
        del bs_client  # unused
        del shift_scheduler  # unused
        nonlocal actual_query
        actual_query = query
        return results

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == results
    if 'expected_v1_rules_match_requests' in test_data:
        actual = mock_billing_subventions_x.v1_rules_match_requests
        ordered_object.assert_eq(
            actual,
            test_data['expected_v1_rules_match_requests'],
            ['', 'reference_time'],
        )
    if 'expected_v2_rules_match_requests' in test_data:
        actual = mock_billing_subventions_x.v2_rules_match_requests
        assert actual == test_data['expected_v2_rules_match_requests']


@pytest.mark.parametrize(
    'expected_shift_scheduler_type',
    [
        pytest.param(
            events.Scheduler,
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION={
                    'by_zone': {
                        '__default__': {
                            'enabled': [
                                {'since': '1991-06-18T07:15:00+03:00'},
                            ],
                        },
                    },
                },
            ),
        ),
        pytest.param(
            handler.CompareWithExistingDocScheduler,
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION={
                    'by_zone': {
                        '__default__': {
                            'test': [{'since': '1991-06-18T07:15:00+03:00'}],
                        },
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.config(PROCESS_SHIFT_ENDED_MIN_MSK_TIME='04:00')
@pytest.mark.json_obj_hook(Doc=docs.Doc)
async def test_choose_doc_scheduler(
        expected_shift_scheduler_type,
        *,
        stq3_context,
        load_py_json,
        mock_billing_subventions_x,
):

    mock_billing_subventions_x(
        [{'match': []}, {'match': []}], [{'matches': []}],
    )
    raw_doc = load_py_json('taxi_order.json')
    data = models.TaxiOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_shift_scheduler = None

    async def _function(
            antifraud_repo: antifraud.Repository,
            service_ids_repo: service_ids.Repository,
            currency_rates_repo: currency_rates.Repository,
            cities_repo: cities.Repository,
            migration_repo: migration_mode.Repository,
            bs_client: billing_subventions.BillingSubventionsClient,
            shift_scheduler: events.Scheduler,
            query: calculate_subventions.Query,
    ) -> models.Subventions:
        del antifraud_repo  # unused
        del service_ids_repo  # unused
        del currency_rates_repo  # unused
        del migration_repo  # unused
        del cities_repo  # unused
        del bs_client  # unused
        del query  # unused
        nonlocal actual_shift_scheduler
        actual_shift_scheduler = shift_scheduler
        return models.Subventions(
            is_eligible=False, skip_reason='not_implemented',
        )

    await handler.handle(stq3_context, doc, _function)
    assert isinstance(actual_shift_scheduler, expected_shift_scheduler_type)


async def test_compare_with_existing_doc_scheduler(mock_docs_component):
    some_dt = datetime.datetime.now(tz=datetime.timezone.utc)
    mock_docs_component.items.append(
        docs.Doc(
            id=1,
            kind='kind',
            topic='topic',
            entry_ids=[],
            external_ref='external_ref',
            event_at=some_dt,
            process_at=some_dt,
            revision=1,
            status='status',
            data={'a': 1, 'b': {'c': 2}},
        ),
    )
    scheduler = handler.CompareWithExistingDocScheduler(
        types.TRUE, mock_docs_component,
    )
    doc_id = await scheduler.schedule(
        'queue',
        docs.CreateDocRequest(
            kind='kind',
            topic='topic',
            external_ref='external_ref',
            event_at=some_dt,
            process_at=some_dt,
            status='status',
            tags=[],
            data={'a': 2, 'b': {'c': 1}},
        ),
        'jitter_seed',
    )
    assert doc_id.value == 1
