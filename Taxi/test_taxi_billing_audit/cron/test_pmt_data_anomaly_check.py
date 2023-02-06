import copy
import functools
from typing import List

import pytest

from taxi_billing_audit.generated.cron import run_cron
from test_taxi_billing_audit import conftest as tst
from test_taxi_billing_audit.cron import common


JUGGLER_HOST = 'test'
EVENT = functools.partial(common.juggler_raw_event, host=JUGGLER_HOST)
JUGGLER_REQUESTS = common.juggler_requests


def rules(
        *items, diff_delay_threshold_minutes: int = 0,
) -> List[pytest.mark.config]:
    return [
        pytest.mark.config(
            BILLING_AUDIT_CHECK_PMT_DATA={
                'diff_delay_threshold_minutes': diff_delay_threshold_minutes,
                'rules': items,
            },
            BILLING_AUDIT_JUGGLER_SETTINGS={'host': JUGGLER_HOST},
        ),
    ]


@pytest.mark.parametrize('cluster', ['hahn', 'arnold'])
@pytest.mark.parametrize(
    'metrics, expected_juggler_requests',
    [
        pytest.param(
            [
                # PAYMENT_CURR_CODE,
                # PAYSYS_TYPE_CODE,
                # CURRENT_MIN_PMT_HIST_DATE,
                # CURRENT_MAX_PMT_HIST_DATE,
                # HISTORICAL_MIN_PMT_HIST_DATE,
                # HISTORICAL_MAX_PMT_HIST_DATE,
                # CURRENT_AMOUNT,
                # HISTORICAL_AMOUNT,
                # CURRENT_COUNT,
                # HISTORICAL_COUNT
                [
                    'RUB',
                    'YA_PROMOCODES',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '3000',
                    100,
                    100,
                ],
                [
                    'USD',
                    'PAYBOX',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1500',
                    100,
                    100,
                ],
                [
                    'USD',
                    'PAYTURE',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1001',
                    100,
                    100,
                ],
                [
                    'KZT',
                    'VTB',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1500',
                    100,
                    100,
                ],
                [
                    'CAD',
                    'VTB',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1001',
                    100,
                    100,
                ],
                [
                    'RUB',
                    '__total__',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '0',
                    '0',
                    100,
                    100,
                ],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(YA_PROMOCODES,RUB) tol=0.50, '
                    '(PAYBOX,USD) tol=0.10, (VTB,KZT) tol=0.10',
                    service='taxi-billing-pmt_data-{cluster}'
                    '-anomaly-weekly_amount_change',
                    status='WARN',
                ),
            ),
            marks=rules(
                {'max_weekly_amount_change': 0.5},
                {'max_weekly_amount_change': 0.1, 'currency': 'USD'},
                {'max_weekly_amount_change': 0.1, 'paysys_type_code': 'VTB'},
            ),
            id='max_weekly_amount_change',
        ),
        pytest.param(
            [
                [
                    'RUB',
                    'YA_PROMOCODES',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1000',
                    100,
                    120,
                ],
                [
                    'RUB',
                    '__total__',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1000',
                    0,
                    0,
                ],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(YA_PROMOCODES,RUB) tol=0.10',
                    service='taxi-billing-pmt_data-{cluster}'
                    '-anomaly-weekly_count_change',
                    status='WARN',
                ),
            ),
            marks=rules({'max_weekly_count_change': 0.1}),
            id='max_weekly_count_change',
        ),
        pytest.param(
            [
                [
                    'RUB',
                    'YA_PROMOCODES',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1000',
                    100,
                    120,
                ],
                [
                    'RUB',
                    '__total__',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1000',
                    0,
                    0,
                ],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(YA_PROMOCODES,RUB) tol=0.10',
                    service='taxi-billing-pmt_data-{cluster}'
                    '-anomaly-weekly_avg_amount_change',
                    status='WARN',
                ),
            ),
            marks=rules({'max_weekly_avg_amount_change': 0.1}),
            id='max_weekly_avg_amount_change',
        ),
        pytest.param(
            [
                [
                    'RUB',
                    'YA_PROMOCODES',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1500',
                    100,
                    120,
                ],
                [
                    'RUB',
                    '__total__',
                    '2019-03-01T12:10:00Z',
                    '2019-03-01T17:10:00Z',
                    '2019-03-01T12:15:00Z',
                    '2019-03-01T17:18:00Z',
                    '1000',
                    '1500',
                    100,
                    120,
                ],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='OK',
                    service='taxi-billing-pmt_data-{cluster}'
                    '-anomaly-weekly_count_change',
                    status='OK',
                ),
            ),
            marks=rules(
                {'max_weekly_count_change': 0.1},
                diff_delay_threshold_minutes=600,
            ),
            id='diff_delay_threshold_minutes not reached',
        ),
        pytest.param(
            [
                [
                    'RUB',
                    'YA_PROMOCODES',
                    None,
                    '2019-03-01T17:10:00Z',
                    None,
                    '2019-03-01T17:18:00Z',
                    '0',
                    '1500',
                    0,
                    120,
                ],
                [
                    'RUB',
                    '__total__',
                    '2019-03-01T12:10:00Z',
                    None,
                    '2019-03-01T12:15:00Z',
                    None,
                    '1000',
                    '0',
                    100,
                    0,
                ],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='OK',
                    service='taxi-billing-pmt_data-{cluster}'
                    '-anomaly-weekly_count_change',
                    status='OK',
                ),
            ),
            marks=rules(
                {'max_weekly_count_change': 0.1},
                diff_delay_threshold_minutes=600,
            ),
            id='null dates',
        ),
        pytest.param(
            [],
            common.no_juggler_requests(),
            marks=rules({'max_weekly_count_change': 0.1}),
            id='no data',
        ),
    ],
)
@pytest.mark.now('2019-03-01T18:10:00+00:00')
async def test_rules(
        patch,
        mocked_yql,
        patched_secdist,
        *,
        cluster,
        metrics,
        expected_juggler_requests,
):
    actual_juggler_requests = []

    @patch('taxi.clients.juggler_api.JugglerAPIClient._push_request')
    async def _juggler(json, **kwargs):
        nonlocal actual_juggler_requests
        actual_juggler_requests.append(json)

    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable(metrics)]),
        ),
    )

    await run_cron.main(
        [
            f'taxi_billing_audit.crontasks.pmt_data_anomaly_check_{cluster}',
            '-t',
            '0',
        ],
    )

    expected_juggler_requests = copy.deepcopy(expected_juggler_requests)
    for request in expected_juggler_requests:
        for expected_event in request['events']:
            expected_event['service'] = expected_event['service'].format(
                cluster=cluster,
            )
    assert actual_juggler_requests == expected_juggler_requests
