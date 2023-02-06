# pylint: disable=redefined-outer-name,unused-variable
from dateutil import parser
import pytest

from taxi_billing_audit.generated.cron import run_cron
from taxi_billing_audit.internal import utils
from test_taxi_billing_audit import conftest as tst


CONST_NOW = '2019-03-01T01:10:00+03:00'
CONST_NOW_OBJ = parser.parse(CONST_NOW)
CONST_NOW_MS = utils.to_msec(CONST_NOW_OBJ)


@pytest.mark.config(BILLING_AUDIT_DOCS_VS_YT_CHECK_ENABLED=True)
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
                            150,  # shard_id
                            410150,  # chunk_id
                            5,  # pg_num
                            2,  # yt_num
                            22010171918,  # pg_hash
                            21942345495,  # yt_hash
                        ],
                    ],
                ],
            ],
            {
                (tst.YT_DIR + 'results'): [
                    [
                        'hex',
                        'hex',
                        'CHECK_DOCS_VS_YT_DIFF',
                        'FAILED',
                        {
                            'chunk_id': 410150,
                            'pg_hash': 22010171918,
                            'pg_num': 5,
                            'shard_id': 150,
                            'yt_hash': 21942345495,
                            'yt_num': 2,
                        },
                    ],
                ],
                (tst.YT_DIR + 'sessions'): [
                    [
                        'hex',
                        'DOCS_VS_YT',
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
                    ['hex', 'hex', 'CHECK_DOCS_VS_YT_DIFF', 'PASSED', {}],
                ],
                (tst.YT_DIR + 'sessions'): [
                    [
                        'hex',
                        'DOCS_VS_YT',
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
async def test_balance_vs_yt_check_in_action(
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
        ['taxi_billing_audit.crontasks.docs_vs_yt_check', '-t', '0'],
    )
    for table_name in expected_yt_tables:
        rows = mocked_yt.read_table(table_name).rows
        assert rows == expected_yt_tables[table_name]
