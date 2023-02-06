# pylint: disable=invalid-name,redefined-builtin,too-many-lines
import typing as tp

from dateutil import parser
import pytest
import pytz

from taxi.billing.util import dates

from taxi_billing_accounts.audit import actions
from test_taxi_billing_accounts import conftest as tst


CONST_NOW = '2019-12-20T21:00:00'
CONST_NOW_OBJ = parser.parse(CONST_NOW).astimezone(pytz.utc)
CONST_NOW_MS = dates.microseconds_from_timestamp(CONST_NOW_OBJ)


@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'balance_at@0.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'balance_at@1.sql', 'entities@1.sql', 'accounts@1.sql'),
)
@pytest.mark.config(
    BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_BALANCES_ENABLED=True,
    BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_BALANCES_ITER_COUNT=2,
    BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_DELAY=0,
    BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_BALANCES_LAG_DAYS=90,
)
@pytest.mark.now(CONST_NOW_OBJ.isoformat())
@pytest.mark.parametrize(
    'yt_responses, yt_expected_result',
    [
        (
            [[]],
            [
                [
                    1576864800000000,
                    0,
                    300010000,
                    '45.0000',
                    10,
                    1547118671000000,
                ],
                [
                    1576864800000000,
                    0,
                    300020000,
                    '45.1000',
                    10,
                    1547122332000000,
                ],
                [
                    1576864800000000,
                    0,
                    300100000,
                    '0.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300110000,
                    '1.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300120000,
                    '2.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300130000,
                    '3.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300140000,
                    '4.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300150000,
                    '5.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300160000,
                    '6.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300170000,
                    '7.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300180000,
                    '8.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300190000,
                    '9.1100',
                    1,
                    1547125993000000,
                ],
                [
                    1576864800000000,
                    0,
                    300200000,
                    '54.9990',
                    10,
                    1547129654000000,
                ],
                [
                    1576864800000000,
                    4,
                    330110004,
                    '1.0000',
                    1,
                    1546341071000000,
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
    task = actions.AggregatePGBalanceData(context=accounts_audit_cron_app)
    await task.aggregate()
    actual = mocked_yt.read_table(tst.YT_DIR + 'balance_chunks_pg').rows
    #  sort by shard number (sorting is stable)
    actual = sorted(actual, key=lambda row: row[1])
    assert actual == yt_expected_result
