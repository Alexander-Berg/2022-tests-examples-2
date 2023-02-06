import datetime as dt
import decimal
from typing import Collection

import pytest

from billing.accounts import service as aservice
from billing.docs import service as dservice

from billing_functions.stq import single_doc
from test_billing_functions.stq import stq as stq_utils


@pytest.mark.parametrize(
    'taxi_shift_json, af_decision_json, '
    'expected_initial_amount, expected_final_amount',
    [
        pytest.param(
            'taxi_order_pay.json',
            'af_decision_pay.json',
            decimal.Decimal('1596.50000'),
            decimal.Decimal('1596.50000'),
            id='pay after pay',
        ),
        pytest.param(
            'taxi_order_block.json',
            'af_decision_pay.json',
            decimal.Decimal('675.06'),
            decimal.Decimal('1596.50000'),
            id='pay after block',
        ),
        pytest.param(
            'taxi_order_pay.json',
            'af_decision_block.json',
            decimal.Decimal('1596.50000'),
            decimal.Decimal('675.06'),
            id='block after pay',
        ),
        pytest.param(
            'taxi_order_block.json',
            'af_decision_block.json',
            decimal.Decimal('675.06'),
            decimal.Decimal('675.06'),
            id='block after block',
        ),
    ],
)
@pytest.mark.now('2021-01-01T00:00:00+03:00')
@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={'subvention/netted': 111},
    BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION={
        'by_zone': {
            '__default__': {
                'enabled': [{'since': '1991-06-18T07:15:00+03:00'}],
            },
        },
    },
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='old',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='both',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='new',
            ),
        ),
    ],
)
async def test_scenarios(
        stq3_context,
        stq,
        mock_billing_components,
        load_json,
        mock_tlog,
        *,
        taxi_shift_json,
        af_decision_json,
        expected_initial_amount,
        expected_final_amount,
):
    components = mock_billing_components(
        now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
    )

    await _process_doc(
        load_json, stq3_context, components, json_file=taxi_shift_json,
    )
    initial_amount = _get_total_amount(components.journal.items)

    await _process_doc(
        load_json, stq3_context, components, json_file=af_decision_json,
    )
    final_amount = _get_total_amount(components.journal.items)

    assert initial_amount == expected_initial_amount
    assert final_amount == expected_final_amount


def _get_total_amount(
        entries: Collection[aservice.AppendedEntry],
) -> decimal.Decimal:
    return sum((entry.amount for entry in entries), decimal.Decimal())


async def _process_doc(load_py_json, stq3_context, components, json_file: str):
    doc_json = load_py_json(json_file)
    doc = dservice.Doc(**doc_json)
    components.docs.items.append(doc)
    await single_doc.task(stq3_context, stq_utils.task_info(), doc.id)
