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
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
@pytest.mark.config(
    BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_ACCOUNTS_ENABLED=True,
    BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_ACCOUNTS_DELAY=0,
    BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_ACCOUNTS_LAG_HOURS=24,
)
@pytest.mark.now(CONST_NOW_OBJ.isoformat())
@pytest.mark.parametrize(
    'yt_responses, yt_expected_result',
    [
        pytest.param(
            [[]],
            [
                [
                    1,
                    425320,
                    17623937391,
                    2,
                    1576864800000000,
                    1531153912758819,
                ],
                [
                    1,
                    426065,
                    22564500192,
                    2,
                    1576864800000000,
                    1533834341651410,
                ],
                [
                    2,
                    426347,
                    19622306664,
                    2,
                    1576864800000000,
                    1534851636726458,
                ],
                [
                    2,
                    426350,
                    15037134424,
                    2,
                    1576864800000000,
                    1534861678697092,
                ],
                [1, 428601, 8974889229, 1, 1576864800000000, 1542964357281163],
            ],
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_ACCOUNTS_INTERVAL=0,
            ),
        ),
        pytest.param(
            [[]],
            [
                [
                    1,
                    425320,
                    17623937391,
                    2,
                    1576864800000000,
                    1531153912758819,
                ],
                [
                    1,
                    426065,
                    12577443250,
                    1,
                    1576864800000000,
                    1533834341406741,
                ],
                [
                    2,
                    426347,
                    19622306664,
                    2,
                    1576864800000000,
                    1534851636726458,
                ],
                [
                    2,
                    426350,
                    15037134424,
                    2,
                    1576864800000000,
                    1534861678697092,
                ],
                [1, 428601, 8974889229, 1, 1576864800000000, 1542964357281163],
            ],
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_ACCOUNTS_INTERVAL=426348,  # noqa: E501
                BILLING_ACCOUNTS_PG_PREPARE_AUDIT_DATA_ACCOUNTS_ITER_COUNT=10,
            ),
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
    task = actions.AggregatePGAccountsData(context=accounts_audit_cron_app)
    await task.aggregate()
    actual = mocked_yt.read_table(tst.YT_DIR + 'accounts_chunks_pg').rows
    #  sort by shard number (sorting is stable)
    actual = sorted(actual, key=lambda row: row[1])
    assert actual == yt_expected_result
