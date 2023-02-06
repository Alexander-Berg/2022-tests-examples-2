import datetime as dt

from taxi_billing_audit.generated.cron import run_cron
from test_taxi_billing_audit import conftest as tst


CRON_PATH = 'taxi_billing_audit.crontasks.journal_vs_pmt_history_check'


async def test_checker_without_issues(
        patched_secdist, mocked_yql, mocked_yt_wrapper, check_result,
):
    mock_query_result(mocked_yql, data=[])
    mock_query_result(mocked_yql, data=[])
    mocked_yt_wrapper.read_table.append(
        [{'FIRST_EXPORT_DATE': '2020-12-12', 'MIN_CREATION_DATE': '2020-12'}],
    )
    mocked_yt_wrapper.exists.append(False)
    mocked_yt_wrapper.exists.append(False)
    await run_cron.main([CRON_PATH, '-t', '0'])
    check_result(
        {'payments': [], 'query_url': 'https://localhost/FakeOperation/001'},
        expected_outcome='PASSED',
    )


async def test_checker_with_issues_below_threshold(
        patched_secdist, mocked_yt_wrapper, mocked_yql, check_result,
):
    mock_query_result(mocked_yql, data=[])
    mock_query_result(
        mocked_yql,
        data=[
            ['1', '2', 'a', 'b', 1, dt.datetime(2020, 1, 1)],
            ['10', '20', 'aa', 'bb', 2, dt.datetime(2020, 1, 2)],
        ],
    )
    mocked_yt_wrapper.read_table.append(
        [{'FIRST_EXPORT_DATE': '2020-12-12', 'MIN_CREATION_DATE': '2020-12'}],
    )
    mocked_yt_wrapper.exists.append(False)
    mocked_yt_wrapper.exists.append(False)
    await run_cron.main([CRON_PATH, '-t', '0'])
    check_result(
        {
            'payments': [
                {
                    'payment_id': 1,
                    'clid': '1',
                    'billing_client_id': '2',
                    'park_id': 'a',
                    'driver_profile_id': 'b',
                },
                {
                    'payment_id': 2,
                    'clid': '10',
                    'billing_client_id': '20',
                    'park_id': 'aa',
                    'driver_profile_id': 'bb',
                },
            ],
            'query_url': 'https://localhost/FakeOperation/001',
        },
        expected_outcome='FAILED',
    )


def mock_query_result(mocked_yql, data):
    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable(data)]),
        ),
    )
