# pylint: disable=invalid-name,redefined-builtin,too-many-lines
import asyncio
import datetime as dt
import logging
import typing as tp

from dateutil import parser
import pytest
import pytz

from taxi.billing.util import dates
from taxi.maintenance import run

from taxi_billing_accounts.audit import actions
from taxi_billing_accounts.audit.tasks import aggregate_journal_data_v2
from test_taxi_billing_accounts import conftest as tst


MY_LOGGER = 'taxi_billing_accounts.audit.tasks.aggregate_journal_data_v2'


CONST_NOW = '2018-12-20T21:00:00'
CONST_NOW_OBJ = parser.parse(CONST_NOW).astimezone(pytz.utc)
CONST_NOW_MS = dates.microseconds_from_timestamp(CONST_NOW_OBJ)


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
@pytest.mark.config(BILLING_ACCOUNTS_PREPARE_AUDIT_DATA_V2_ENABLED=False)
async def test_cron_can_run(accounts_audit_cron_app, caplog, loop):
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    success = False
    context = run.StuffContext(
        lock=None,
        task_id='123',
        start_time=dt.datetime.now(),
        data=accounts_audit_cron_app,
    )
    await aggregate_journal_data_v2.do_stuff(context=context, loop=loop)
    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    for x in lines:
        if 'Task disabled by fallback config' in x:
            success = True
    assert success


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'journal@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'balance_at@1.sql',
        'rollups@1.sql',
        'entities@1.sql',
        'accounts@1.sql',
        'journal@1.sql',
    ),
)
@pytest.mark.config(BILLING_ACCOUNTS_PREPARE_AUDIT_DATA_V2_ENABLED=True)
@pytest.mark.config(BILLING_ACCOUNTS_PREPARE_AUDIT_DATA_CHUNK_SIZE=2)
@pytest.mark.config(BILLING_ACCOUNTS_PREPARE_AUDIT_DATA_CHUNK_COUNT=100)
@pytest.mark.config(BILLING_ACCOUNTS_PREPARE_AUDIT_DATA_DELAY=0)
@pytest.mark.now(CONST_NOW_OBJ.isoformat())
@pytest.mark.parametrize(
    'yt_responses, yt_expected_result',
    [
        (
            [[]],
            [
                [
                    CONST_NOW_MS,
                    0,
                    22220010000,
                    22220020000,
                    '2.0000',
                    2,
                    'XXX',
                ],
                [
                    CONST_NOW_MS,
                    0,
                    22220030000,
                    22220040000,
                    '2.0000',
                    2,
                    'XXX',
                ],
                [
                    CONST_NOW_MS,
                    0,
                    22220050000,
                    22220060000,
                    '2.0000',
                    2,
                    'XXX',
                ],
                [
                    CONST_NOW_MS,
                    4,
                    22220010004,
                    22220020004,
                    '6.0000',
                    2,
                    'RUB',
                ],
                [
                    CONST_NOW_MS,
                    4,
                    22220030004,
                    22220040004,
                    '12.0000',
                    2,
                    'RUB',
                ],
                [
                    CONST_NOW_MS,
                    4,
                    22220050004,
                    22220060004,
                    '12.0000',
                    2,
                    'RUB',
                ],
            ],
        ),
        (
            [
                [
                    [0, 22220060000, 1545317143000000],
                    [4, 22220060004, 1545317143000000],
                ],
            ],
            [],
        ),
    ],
)
async def test_cron_usage(
        accounts_audit_cron_app,
        caplog,
        loop: asyncio.AbstractEventLoop,
        yt_responses: tp.List,
        yt_expected_result,
        mocked_yql: tp.List,
        mocked_yt: tst.MockedDB,
        patch,
):
    @patch('random.shuffle')
    def shuffle(array: tp.List):  # pylint: disable=unused-variable
        # no shuffle and fixed random for same results
        pass

    for response in yt_responses:
        mocked_yql.append(  # get_latest_start_date
            tst.MockedRequest(
                tst.MockedResult(
                    tst.YT_STATUS_COMPLETED, [tst.MockedTable(response)],
                ),
            ),
        )
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    task = actions.AggregateJournalDataV2(
        context=accounts_audit_cron_app, loop=loop,
    )
    await task.aggregate()
    actual = mocked_yt.read_table(tst.YT_DIR + 'journal_chunks_pg').rows
    #  sort by shard number (sorting is stable)
    actual = sorted(actual, key=lambda row: row[1])
    assert actual == yt_expected_result
