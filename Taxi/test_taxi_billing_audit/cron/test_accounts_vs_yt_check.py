# pylint: disable=redefined-outer-name,unused-variable
from dateutil import parser
import pytest

from taxi_billing_audit.generated.cron import run_cron
from taxi_billing_audit.internal import utils
from test_taxi_billing_audit import conftest as tst


CONST_NOW = '2019-03-01T01:10:00+03:00'
CONST_NOW_OBJ = parser.parse(CONST_NOW)
CONST_NOW_MS = utils.to_msec(CONST_NOW_OBJ)


@pytest.mark.config(BILLING_AUDIT_ACCOUNTS_VS_YT_CHECK_ENABLED=True)
@pytest.mark.usefixtures('patched_secdist')
@pytest.mark.usefixtures('dummy_uuid4_hex')
@pytest.mark.now(CONST_NOW_OBJ.isoformat())
@pytest.mark.parametrize(
    'yt_queries, expected_yt_tables',
    [
        (
            [
                [
                    [  # diff
                        [
                            7,  # shard_id
                            428771,  # chunk_id
                            7,  # pg_total
                            8,  # yt_total
                            64543994705,  # pg_hash
                            74215573984,  # yt_hash
                        ],
                    ],
                ],
            ],
            {
                (tst.YT_DIR + 'results'): [
                    [
                        'hex',
                        'hex',
                        'CHECK_ACCOUNTS_VS_YT',
                        'FAILED',
                        {
                            'chunk_id': 428771,
                            'pg_hash': 64543994705,
                            'pg_total': 7,
                            'shard_id': 7,
                            'yt_hash': 74215573984,
                            'yt_total': 8,
                        },
                    ],
                ],
                (tst.YT_DIR + 'sessions'): [
                    [
                        'hex',
                        'ACCOUNTS_VS_YT',
                        1551402600000000,
                        1551402600000000,
                        0,
                        'hex',
                        None,
                    ],
                ],
            },
        ),
        (
            [[[]]],  # no diff
            {
                (tst.YT_DIR + 'results'): [
                    ['hex', 'hex', 'CHECK_ACCOUNTS_VS_YT', 'PASSED', {}],
                ],
                (tst.YT_DIR + 'sessions'): [
                    [
                        'hex',
                        'ACCOUNTS_VS_YT',
                        1551402600000000,
                        1551402600000000,
                        0,
                        'hex',
                        None,
                    ],
                ],
            },
        ),
    ],
)
async def test_accounts_vs_yt_check_in_action(
        mocked_yt, mocked_yql, yt_queries, expected_yt_tables,
):
    for yt_query in yt_queries:
        mocked_yql.append(
            tst.MockedRequest(
                tst.MockedResult(
                    tst.STATUS_COMPLETED,
                    [tst.MockedTable(table) for table in yt_query],
                ),
            ),
        )

    await run_cron.main(
        ['taxi_billing_audit.crontasks.accounts_vs_yt_check', '-t', '0'],
    )
    for table_name in expected_yt_tables:
        rows = mocked_yt.read_table(table_name).rows
        assert rows == expected_yt_tables[table_name]
