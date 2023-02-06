# pylint: disable=redefined-outer-name,unused-variable
import pytest

from taxi_billing_audit.generated.cron import run_cron
from test_taxi_billing_audit import conftest as tst


CRON_PATH = 'taxi_billing_audit.crontasks.compensation_refunds_check'


@pytest.mark.config(BILLING_AUDIT_COMPENSATION_REFUNDS_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_COMPENSATION_REFUNDS_THRESHOLD=4)
async def test_checker_without_issues(
        patch, patched_secdist, mocked_yt, mocked_yql, check_result,
):
    mock_query_result(mocked_yql, data=[])
    await run_cron.main([CRON_PATH, '-t', '0'])
    check_result({'orders': []}, expected_outcome='PASSED')


@pytest.mark.config(BILLING_AUDIT_COMPENSATION_REFUNDS_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_COMPENSATION_REFUNDS_THRESHOLD=4)
async def test_checker_with_issues_below_threshold(
        patch, patched_secdist, mocked_yt, mocked_yql, check_result,
):
    mock_query_result(
        mocked_yql,
        data=[
            ['abc1', 'RUB', 670000000],
            ['abc2', 'RUB', 335000000],
            ['abc3', 'GEL', 7000000],
            ['abc4', 'GEL', 3500000],
        ],
    )
    await run_cron.main([CRON_PATH, '-t', '0'])
    check_result(
        {
            'orders': [
                {'id': 'abc1', 'currency': 'RUB', 'lacking_refunds': '67000'},
                {'id': 'abc2', 'currency': 'RUB', 'lacking_refunds': '33500'},
                {'id': 'abc3', 'currency': 'GEL', 'lacking_refunds': '700'},
                {'id': 'abc4', 'currency': 'GEL', 'lacking_refunds': '350'},
            ],
        },
        expected_outcome='PASSED',
    )


@pytest.mark.config(BILLING_AUDIT_COMPENSATION_REFUNDS_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_COMPENSATION_REFUNDS_THRESHOLD=3)
async def test_checker_with_issues_above_threshold(
        patch, patched_secdist, mocked_yt, mocked_yql, check_result,
):
    mock_query_result(
        mocked_yql,
        data=[
            ['abc1', 'RUB', 670000000],
            ['abc2', 'RUB', 335000000],
            ['abc3', 'GEL', 7000000],
            ['abc4', 'GEL', 3500000],
        ],
    )
    await run_cron.main([CRON_PATH, '-t', '0'])
    check_result(
        {
            'orders': [
                {'id': 'abc1', 'currency': 'RUB', 'lacking_refunds': '67000'},
                {'id': 'abc2', 'currency': 'RUB', 'lacking_refunds': '33500'},
                {'id': 'abc3', 'currency': 'GEL', 'lacking_refunds': '700'},
                {'id': 'abc4', 'currency': 'GEL', 'lacking_refunds': '350'},
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
