# pylint: disable=redefined-outer-name,unused-variable
import logging

from dateutil import parser
import pytest

from taxi_billing_audit.generated.cron import run_cron
from taxi_billing_audit.internal import storage
from taxi_billing_audit.internal import utils
from test_taxi_billing_audit import conftest as tst
from .support import Markers


MY_LOGGER = 'taxi_billing_audit.crontasks.journal_vs_yt_check_v3'

CONST_NOW = '2019-03-01T01:10:00+03:00'
CONST_NOW_OBJ = parser.parse(CONST_NOW)
CONST_NOW_MS = utils.to_msec(CONST_NOW_OBJ)


@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_YT_V3_CHECK_ENABLED=False)
async def test_checker_disabled(
        patch, caplog, patched_secdist, mocked_yt, mocked_yql,
):
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main(
        ['taxi_billing_audit.crontasks.journal_vs_yt_check_v3', '-t', '0'],
    )

    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    expected_markers = Markers(
        disabled=True, success=False, missing=False, duplicates=False,
    )
    assert expected_markers == Markers.from_log(lines)


@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_YT_V3_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_YT_TIMEOUT_BETWEEN_REQUESTS=1)
@pytest.mark.usefixtures('patched_secdist')
@pytest.mark.usefixtures('dummy_uuid4_hex')
@pytest.mark.now(CONST_NOW_OBJ.isoformat())
@pytest.mark.parametrize(
    'yt_queries, expected_yt_tables',
    [
        (
            [
                [  # query No.1
                    [  # diff
                        [
                            150,
                            410150,
                            910150,
                            '-89.8472',
                            40,
                            '210.1528',
                            50,
                            'RUB',
                        ],
                    ],
                    [  # chunks
                        [
                            1575979608712888,
                            255,
                            3741255,
                            4670255,
                            '12.3284',
                            4,
                            'XXX',
                        ],
                    ],
                ],
            ],
            {
                (tst.YT_DIR + 'results'): [
                    [
                        'hex',
                        'hex',
                        'CHECK_ACCOUNTS_VS_YT_DIFF',
                        'FAILED',
                        {
                            'actual_amount': '-89.8472',
                            'actual_count': 40,
                            'currency': 'RUB',
                            'expected_amount': '210.1528',
                            'expected_count': 50,
                            'max_id': 910150,
                            'min_id': 410150,
                            'shard_id': 150,
                        },
                    ],
                ],
                (tst.YT_DIR + 'sessions'): [
                    [
                        'hex',
                        'JOURNAL_VS_YT_V3',
                        1551402600000000,
                        1551402600000000,
                        0,
                        'hex',
                        None,
                    ],
                ],
                (tst.YT_DIR_ACCOUNTS + 'journal_chunks_yt'): [
                    [
                        1575979608712888,
                        255,
                        3741255,
                        4670255,
                        '12.3284',
                        4,
                        'XXX',
                    ],
                ],
            },
        ),
        (
            [
                [  # query No.1
                    [],  # diff
                    [  # chunks
                        [
                            1575979608712888,
                            255,
                            3741255,
                            4670255,
                            '12.3284',
                            4,
                            'XXX',
                        ],
                    ],
                ],
            ],
            {
                (tst.YT_DIR + 'results'): [
                    ['hex', 'hex', 'CHECK_ACCOUNTS_VS_YT_DIFF', 'PASSED', {}],
                ],
                (tst.YT_DIR + 'sessions'): [
                    [
                        'hex',
                        'JOURNAL_VS_YT_V3',
                        1551402600000000,
                        1551402600000000,
                        0,
                        'hex',
                        None,
                    ],
                ],
                (tst.YT_DIR_ACCOUNTS + 'journal_chunks_yt'): [
                    [
                        1575979608712888,
                        255,
                        3741255,
                        4670255,
                        '12.3284',
                        4,
                        'XXX',
                    ],
                ],
            },
        ),
    ],
)
async def test_journal_v3_check_in_action(
        caplog, mocked_yt, mocked_yql, yt_queries, expected_yt_tables,
):
    #
    # typical YQL Session for journal_vs_yt_check:
    # 1. query data from billing_accounts/v1/audit/summary
    # 2. query data from yt
    # 3. append to the tables results and sessions
    #
    for yt_query in yt_queries:
        mocked_yql.append(
            tst.MockedRequest(
                tst.MockedResult(
                    tst.STATUS_COMPLETED,
                    [tst.MockedTable(table) for table in yt_query],
                ),
            ),
        )

    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main(
        ['taxi_billing_audit.crontasks.journal_vs_yt_check_v3', '-t', '0'],
    )
    for table_name in expected_yt_tables:
        rows = mocked_yt.read_table(table_name).rows
        assert rows == expected_yt_tables[table_name]


@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_YT_V3_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_YT_TIMEOUT_BETWEEN_REQUESTS=1)
@pytest.mark.usefixtures('patched_secdist')
@pytest.mark.usefixtures('dummy_uuid4_hex')
@pytest.mark.now(CONST_NOW_OBJ.isoformat())
async def test_journal_v3_check_sectioning(caplog, mocked_yt, mocked_yql):
    #
    # typical YQL Session for journal_vs_yt_check_v3:
    # 1. query data from yql and return table with diffs and chunks
    # 2. append to the tables results and sessions
    # 2. append to the checked chunks table
    #
    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(
                tst.STATUS_COMPLETED,
                [tst.MockedTable([]), tst.MockedTable([])],
            ),
        ),
    )
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main(
        ['taxi_billing_audit.crontasks.journal_vs_yt_check_v3', '-t', '0'],
    )
    lines = [x.getMessage() for x in caplog.records]
    assert any(storage.JOURNAL_REPLICA_PATH in x for x in lines)
    assert any(storage.JOURNAL_MONTHLY_REPLICA_PATH in x for x in lines)
