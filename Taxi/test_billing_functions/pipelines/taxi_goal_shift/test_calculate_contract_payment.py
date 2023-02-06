from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models
from taxi.billing.util import dates

from billing_functions.functions import calculate_contract_payment
import billing_functions.repositories.cities as cities_module
import billing_functions.repositories.currency_rates as currency_rates_module
from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._taxi_goal_shift import (
    calculate_contract_payment as handler,
)
from test_billing_functions import equatable

_MOCK_NOW = '2021-03-01T00:00:00.000000+03:00'
_MOCK_NOW_DT = dates.parse_datetime(_MOCK_NOW)


@pytest.mark.parametrize(
    'test_data_json',
    [
        'pay_per_contract.json',
        'test_pay_per_contract.json',
        'pay_whole_sum.json',
    ],
)
@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    Data=lambda **kwargs: models.TaxiGoalShift.deserialize(kwargs),
    Query=calculate_contract_payment.Query,
    Contract=calculate_contract_payment.Query.Contract,
    Results=pipeline.Results,
    Money=models.Money,
    ShiftContractPayment=equatable.codegen(models.ShiftContractPayment),
)
@pytest.mark.now(_MOCK_NOW)
@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={'subvention/paid': 111},
    BILLING_FUNCTIONS_NETTING_CONFIG={
        'rus': [
            {
                'since': '1990-12-31T21:00:00+03:00',
                'zones': ['*'],
                'kinds': ['mfg'],
                'netting': 'full',
            },
        ],
    },
)
async def test(
        test_data_json, *, stq3_context, load_py_json, mock_billing_components,
):
    mock_billing_components(now=_MOCK_NOW_DT)
    test_data = load_py_json(test_data_json)

    actual_query = None

    async def _function(
            cities: cities_module.Repository,
            currency_rates: currency_rates_module.Repository,
            query: calculate_contract_payment.Query,
    ) -> models.ShiftContractPayment:
        del cities  # unused
        del currency_rates  # unused
        nonlocal actual_query
        actual_query = query
        return models.ShiftContractPayment(
            contract_id=1,
            service_id=111,
            currency_rate='1',
            is_netting=False,
            donate_multiplier='1.02',
            value=models.Money('100', 'RUB'),
        )

    actual_results = await handler.handle(
        stq3_context, test_data['doc'], _function,
    )
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['expected_results']
