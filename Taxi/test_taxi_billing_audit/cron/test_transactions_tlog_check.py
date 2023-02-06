import datetime as dt
from typing import Optional

import pytest

from taxi_billing_audit.generated.cron import run_cron
from test_taxi_billing_audit import conftest as tst


def diff(order_id: str, missed_in: Optional[str]) -> list:
    # tlog_payment_is_missing: bool
    # transactions_payment_is_missing: bool
    # payments_differ: Optional[bool]
    # tr_order_id: str
    # tr_due: dt.datetime
    # tr_currency: str
    # tr_external_payment_id: str
    # tr_product: str
    # tr_detailed_product: str
    # tr_transaction_type: str
    # tr_amount: float
    # tr_event_time: dt.datetime
    # tr_terminal_id: int
    # tlog_order_id: str
    # tlog_due: dt.datetime
    # tlog_currency: str
    # tlog_external_payment_id: str
    # tlog_product: str
    # tlog_detailed_product: str
    # tlog_transaction_type: str
    # tlog_amount: float
    # tlog_event_time: dt.datetime
    # tlog_terminal_id: int
    result: list = [
        missed_in == 'tlog',
        missed_in == 'transactions',
        True if missed_in is None else None,
    ]
    payment = [
        order_id,
        dt.datetime.now(),
        'CCY',
        'epi',
        'p',
        'dp',
        'tt',
        'a',
        'et',
        'tid',
    ]
    if missed_in == 'tlog':
        result.extend(payment)
        result.extend([None] * len(payment))
    if missed_in == 'transactions':
        result.extend([None] * len(payment))
        result.extend(payment)
    if missed_in is None:
        result.extend(payment)
        result.extend(payment)
    return result


@pytest.mark.config(
    BILLING_AUDIT_TRANSACTIONS_VS_TLOG={
        'cursor_overlap_hours': 0,
        'interval_end_lag_hours': 0,
        'diff_size_limit': 1000,
        'min_interval_duration_hours': 0,
        'payment_types': ['card'],
        'tlog_products': ['p'],
    },
)
@pytest.mark.parametrize(
    'diffs, expected_details, expected_outcome',
    [
        pytest.param(
            [
                diff('oid1', missed_in='tlog'),
                diff('oid2', missed_in='transactions'),
                diff('oid3', missed_in=None),
            ],
            {
                'payments': [
                    {
                        'diff_type': 'missed_in_tlog',
                        'external_payment_id': 'epi',
                        'order_id': 'oid1',
                    },
                    {
                        'diff_type': 'missed_in_transactions',
                        'external_payment_id': 'epi',
                        'order_id': 'oid2',
                    },
                    {
                        'diff_type': 'values_differ',
                        'external_payment_id': 'epi',
                        'order_id': 'oid3',
                    },
                ],
            },
            'FAILED',
        ),
        pytest.param([], {'payments': []}, 'PASSED'),
    ],
)
@pytest.mark.now('2019-03-01T01:10:00+03:00')
async def test_simple(
        mocked_yql,
        mocked_yt_wrapper,
        patched_secdist,
        check_result,
        *,
        diffs,
        expected_details,
        expected_outcome,
):
    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable(diffs)]),
        ),
    )

    mocked_yt_wrapper.exists.extend([True, False])

    await run_cron.main(
        ['taxi_billing_audit.crontasks.transactions_tlog_check', '-t', '0'],
    )

    check_result(expected_details, expected_outcome)
