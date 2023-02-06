# pylint: disable=redefined-outer-name,unused-variable
import pytest

from taxi_billing_audit.generated.cron import run_cron
from test_taxi_billing_audit import conftest as tst


CRON_PATH = 'taxi_billing_audit.crontasks.taxi_failed_refunds_check'


@pytest.mark.config(BILLING_AUDIT_TAXI_FAILED_REFUNDS_CHECK_ENABLED=True)
async def test_checker_without_issues(
        patch, patched_secdist, mocked_yt, mocked_yql, check_result,
):
    mock_query_result(mocked_yql, data=[])
    await run_cron.main([CRON_PATH, '-t', '0'])
    check_result({'orders': []}, expected_outcome='PASSED')


@pytest.mark.config(BILLING_AUDIT_TAXI_FAILED_REFUNDS_CHECK_ENABLED=True)
async def test_checker_with_issues(
        patch, patched_secdist, mocked_yt, mocked_yql, check_result,
):
    mock_query_result(
        mocked_yql,
        data=[
            ['abc1', 'RUB', 1234500],
            ['abc2', 'GEL', 1234500],
            ['abc3', 'RUB', 34500],
            ['abc4', 'RUB', 1234500],
        ],
    )
    await run_cron.main([CRON_PATH, '-t', '0'])
    check_result(
        {
            'orders': [
                {'id': 'abc1', 'currency': 'RUB', 'refund_sum': 123.45},
                {'id': 'abc2', 'currency': 'GEL', 'refund_sum': 123.45},
                {'id': 'abc3', 'currency': 'RUB', 'refund_sum': 3.45},
                {'id': 'abc4', 'currency': 'RUB', 'refund_sum': 123.45},
            ],
        },
        expected_outcome='FAILED',
    )


def mock_query_result(mocked_yql, data):
    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable(data)]),
        ),
    )
