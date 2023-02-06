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


def rules(*items) -> List[pytest.mark.config]:
    return [
        pytest.mark.config(
            BILLING_AUDIT_CHECK_TLOG={'rules': items},
            BILLING_AUDIT_JUGGLER_SETTINGS={'host': JUGGLER_HOST},
        ),
    ]


@pytest.mark.parametrize('cluster', ['hahn', 'arnold'])
@pytest.mark.parametrize(
    'metrics, expected_juggler_requests',
    [
        pytest.param(
            [
                # hour,
                # product,
                # currency,
                # current_amount,
                # historical_amount,
                # current_max_amount,
                # current_min_amount,
                # current_count,
                # historical_count
                ['1h', 'order', 'RUB', '1000', '500', '10', '-5', 300, 400],
                ['1d', 'subsidy', 'USD', '2000', '2400', '30', '5', 100, 50],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='OK',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-max_absolute_value_1h',
                    status='OK',
                ),
                EVENT(
                    description='(subsidy,USD) x>20',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-max_absolute_value_1d',
                    status='WARN',
                ),
            ),
            marks=rules({'max_absolute_value': 20}),
            id='global max_absolute_value',
        ),
        pytest.param(
            [['1d', 'subsidy', 'USD', '0', '0', '30', '5', 100, 50]],
            JUGGLER_REQUESTS(
                EVENT(
                    description='OK',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-weekly_amount_change_1d',
                    status='OK',
                ),
            ),
            marks=rules({'max_1d_weekly_amount_change': 0.1}),
            id='zero amount',
        ),
        pytest.param(
            [['1d', 'subsidy', 'USD', '2000', '2000', '30', '5', 0, 0]],
            JUGGLER_REQUESTS(
                EVENT(
                    description='OK',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-weekly_count_change_1d',
                    status='OK',
                ),
            ),
            marks=rules({'max_1d_weekly_count_change': 0.1}),
            id='zero count',
        ),
        pytest.param(
            [
                ['1h', 'order', 'RUB', '1000', '500', '10', '-5', 300, 400],
                ['1h', 'order', 'USD', '1000', '500', '10', '-5', 300, 400],
                ['1d', 'subsidy', 'USD', '2000', '2400', '30', '5', 100, 50],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(order,RUB) x>5, (order,USD) x>5',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-max_absolute_value_1h',
                    status='WARN',
                ),
            ),
            marks=rules({'max_absolute_value': 5, 'product': 'order'}),
            id='product max_absolute_value',
        ),
        pytest.param(
            [
                ['1h', 'order', 'RUB', '1000', '500', '10', '-5', 300, 400],
                ['1h', 'order', 'USD', '1000', '500', '10', '-5', 300, 400],
                ['1d', 'subsidy', 'USD', '2000', '2400', '30', '5', 100, 50],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(order,USD) x>5',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-max_absolute_value_1h',
                    status='WARN',
                ),
                EVENT(
                    description='(subsidy,USD) x>5',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-max_absolute_value_1d',
                    status='WARN',
                ),
            ),
            marks=rules({'max_absolute_value': 5, 'currency': 'USD'}),
            id='currency max_absolute_value',
        ),
        pytest.param(
            [
                ['1h', 'order', 'RUB', '1000', '500', '10', '-5', 300, 400],
                ['1h', 'order', 'USD', '1000', '500', '10', '-5', 300, 400],
                ['1d', 'subsidy', 'USD', '2000', '2400', '30', '5', 100, 50],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(order,USD) x>5',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-max_absolute_value_1h',
                    status='WARN',
                ),
            ),
            marks=rules(
                {
                    'max_absolute_value': 5,
                    'currency': 'USD',
                    'product': 'order',
                },
            ),
            id='currency+product max_absolute_value',
        ),
        pytest.param(
            [
                ['1h', 'order', 'RUB', '400', '1000', '10', '-5', 300, 400],
                ['1h', 'order', 'USD', '2100', '1000', '10', '-5', 300, 400],
                ['1h', 'order', 'CAD', '600', '1000', '10', '-5', 300, 400],
                ['1h', 'order', 'GBP', '1400', '1000', '10', '-5', 300, 400],
                ['1d', 'order', 'RUB', '400', '1000', '10', '-5', 300, 400],
                ['1d', 'order', 'USD', '2100', '1000', '10', '-5', 300, 400],
                ['1d', 'order', 'CAD', '600', '1000', '10', '-5', 300, 400],
                ['1d', 'order', 'GBP', '1400', '1000', '10', '-5', 300, 400],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(order,RUB) tol=0.50, (order,USD) tol=0.50',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-weekly_amount_change_1d',
                    status='WARN',
                ),
            ),
            marks=rules({'max_1d_weekly_amount_change': 0.5}),
            id='1d max_1d_weekly_amount_change',
        ),
        pytest.param(
            [
                ['1h', 'order', 'RUB', '400', '1000', '10', '-5', 300, 400],
                ['1h', 'order', 'USD', '2100', '1000', '10', '-5', 300, 400],
                ['1h', 'order', 'CAD', '600', '1000', '10', '-5', 300, 400],
                ['1h', 'order', 'GBP', '1400', '1000', '10', '-5', 300, 400],
                ['1d', 'order', 'RUB', '400', '1000', '10', '-5', 300, 400],
                ['1d', 'order', 'USD', '2100', '1000', '10', '-5', 300, 400],
                ['1d', 'order', 'CAD', '600', '1000', '10', '-5', 300, 400],
                ['1d', 'order', 'GBP', '1400', '1000', '10', '-5', 300, 400],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(order,RUB) tol=0.50, (order,USD) tol=0.50',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-weekly_amount_change_1h',
                    status='WARN',
                ),
            ),
            marks=rules({'max_1h_weekly_amount_change': 0.5}),
            id='1h max_1d_weekly_amount_change',
        ),
        pytest.param(
            [
                ['1h', 'order', 'RUB', '400', '1000', '10', '-5', 400, 1000],
                ['1h', 'order', 'USD', '1600', '1000', '10', '-5', 2100, 1000],
                ['1h', 'order', 'CAD', '600', '1000', '10', '-5', 600, 1000],
                ['1h', 'order', 'GBP', '1400', '1000', '10', '-5', 1400, 1000],
                ['1d', 'order', 'RUB', '400', '1000', '10', '-5', 400, 1000],
                ['1d', 'order', 'USD', '1600', '1000', '10', '-5', 2100, 1000],
                ['1d', 'order', 'CAD', '600', '1000', '10', '-5', 600, 1000],
                ['1d', 'order', 'GBP', '1400', '1000', '10', '-5', 1400, 1000],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(order,RUB) tol=0.50, (order,USD) tol=0.50',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-weekly_count_change_1d',
                    status='WARN',
                ),
            ),
            marks=rules({'max_1d_weekly_count_change': 0.5}),
            id='1d max_1d_weekly_count_change',
        ),
        pytest.param(
            [
                ['1h', 'order', 'RUB', '400', '1000', '10', '-5', 400, 1000],
                ['1h', 'order', 'USD', '1600', '1000', '10', '-5', 2100, 1000],
                ['1h', 'order', 'CAD', '600', '1000', '10', '-5', 600, 1000],
                ['1h', 'order', 'GBP', '1400', '1000', '10', '-5', 1400, 1000],
                ['1d', 'order', 'RUB', '400', '1000', '10', '-5', 10, 10],
                ['1d', 'order', 'USD', '1600', '1000', '10', '-5', 5, 10],
                ['1d', 'order', 'CAD', '600', '1000', '10', '-5', 600, 1000],
                ['1d', 'order', 'GBP', '1400', '1000', '10', '-5', 1400, 1000],
            ],
            JUGGLER_REQUESTS(
                EVENT(
                    description='(order,RUB) tol=0.50, (order,USD) tol=0.50',
                    service='taxi-billing-tlog-{cluster}'
                    '-anomaly-weekly_avg_amount_change_1d',
                    status='WARN',
                ),
            ),
            marks=rules({'max_1d_weekly_avg_amount_change': 0.5}),
            id='1d max_1d_weekly_avg_amount_change',
        ),
    ],
)
@pytest.mark.now('2019-03-01T01:10:00+03:00')
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
            f'taxi_billing_audit.crontasks.tlog_anomaly_check_{cluster}',
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
