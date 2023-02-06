# pylint: disable=W0212
import logging

import pytest

from internal_b2b_bots.crontasks import replicate_yt_salesforce
from internal_b2b_bots.storage.yt import yt_requests

logger = logging.getLogger(__name__)

EXPECTED_MIDTERM_RESULT = [
    {
        'saleforce_user_id': 'saleforce_user_id_1',
        'full_name': 'full_name_1',
        'staff_user_login': 'staff_user_login_1',
        'type': 0,
        'contract_id': 'contract_id_1',
        'account_id': 'account_id_1',
        'contract_ya_taxi_code': 'contract_ya_taxi_code_1',
    },
    {
        'saleforce_user_id': 'saleforce_user_id_2',
        'full_name': 'full_name_2',
        'staff_user_login': 'staff_user_login_2',
        'type': 0,
        'contract_id': 'contract_id_2',
        'account_id': 'account_id_2',
        'contract_ya_taxi_code': 'contract_ya_taxi_code_2',
    },
    {
        'saleforce_user_id': 'saleforce_user_id_3',
        'full_name': 'full_name_3',
        'staff_user_login': 'staff_user_login_3',
        'type': 0,
        'contract_id': 'contract_id_3',
        'account_id': 'account_id_3',
        'contract_ya_taxi_code': 'contract_ya_taxi_code_3',
    },
    {
        'saleforce_user_id': 'saleforce_user_id_4',
        'full_name': 'full_name_4',
        'staff_user_login': 'staff_user_login_4',
        'type': 0,
        'contract_id': 'contract_id_4',
        'account_id': 'account_id_4',
        'contract_ya_taxi_code': 'contract_ya_taxi_code_4',
    },
]

EXPECTED_RESULT = [
    {
        'contract_id': 'contract_id_1',
        'contract_ya_taxi_code': 'contract_ya_taxi_code_1',
        'account_name': 'account_name_1',
        'staff_user_login': 'staff_user_login_1',
        'full_name': 'full_name_1',
    },
    {
        'contract_id': 'contract_id_2',
        'contract_ya_taxi_code': 'contract_ya_taxi_code_2',
        'account_name': 'account_name_2',
        'staff_user_login': 'staff_user_login_2',
        'full_name': 'full_name_2',
    },
    {
        'contract_id': 'contract_id_3',
        'contract_ya_taxi_code': 'contract_ya_taxi_code_3',
        'account_name': 'account_name_3',
        'staff_user_login': 'staff_user_login_3',
        'full_name': 'full_name_3',
    },
    {
        'contract_id': 'contract_id_4',
        'contract_ya_taxi_code': 'contract_ya_taxi_code_4',
        'account_name': 'account_name_4',
        'staff_user_login': 'staff_user_login_4',
        'full_name': 'full_name_4',
    },
]


@pytest.mark.yt(dyn_table_data=['yt_salesforce_data.yaml'])
async def test_map_reduce_without_pg(yt_apply, cron_context):
    yt = cron_context.yt_wrapper.hahn  # pylint: disable=C0103

    contract_table = yt.TablePath(
        name='//home/taxi-dwh/ods/salesforce_b2b/contract/contract',
        columns=[
            'contract_id',
            'contract_ya_taxi_code',
            'saleforce_user_id',
            'account_id',
        ],
    )
    user_table = yt.TablePath(
        name='//home/taxi-dwh/ods/salesforce_b2b/user/user',
        columns=['user_id', 'staff_user_login', 'full_name'],
    )
    account_table = yt.TablePath(
        name='//home/taxi-dwh/ods/salesforce_b2b/account/account',
        columns=['account_id', 'account_name'],
    )
    tmp_path = '//home/taxi/production/features/internal-b2b/tmp'

    for table in (contract_table, user_table, account_table):
        await yt.unmount_table(table, sync=True)
        await yt.mount_table(table, sync=True)

    with yt.TempTable(tmp_path) as mid_tab:
        await yt.run_map_reduce(
            mapper=yt_requests._midterm_mapper,
            reducer=yt_requests._reducer,
            source_table=[contract_table, user_table, account_table],
            destination_table=mid_tab,
            reduce_by=['saleforce_user_id'],
        )
        output = list(await yt.read_table(mid_tab))
        assert output == EXPECTED_MIDTERM_RESULT

        with yt.TempTable(tmp_path) as res_tab:
            await yt.run_map_reduce(
                mapper=yt_requests._result_mapper,
                reducer=yt_requests._result_value_reducer,
                source_table=[mid_tab, account_table],
                destination_table=res_tab,
                reduce_by=['account_id'],
            )
            result = list(await yt.read_table(res_tab))

    assert result == EXPECTED_RESULT


EXPECTED_PG_RESULT = [
    (
        'contract_id_1',
        'contract_ya_taxi_code_1',
        'account_name_1',
        'staff_user_login_1',
        'full_name_1',
        'telegram_account_1',
        '"chef_login_1"',
    ),
    (
        'contract_id_2',
        'contract_ya_taxi_code_2',
        'account_name_2',
        'staff_user_login_2',
        'full_name_2',
        'telegram_account_2',
        '"chef_login_2"',
    ),
    (
        'contract_id_3',
        'contract_ya_taxi_code_3',
        'account_name_3',
        'staff_user_login_3',
        'full_name_3',
        'telegram_account_3',
        '"chef_login_3"',
    ),
    (
        'contract_id_4',
        'contract_ya_taxi_code_4',
        'account_name_4',
        'staff_user_login_4',
        'full_name_4',
        'telegram_account_4',
        '"chef_login_4"',
    ),
]


@pytest.mark.pgsql('internal_b2b', files=('pgsql_fill_staff_table.sql',))
async def test_replicate_yt_salesforce_pg_interaction(
        patch, cron_context, pgsql,
):
    @patch('internal_b2b_bots.storage.yt.yt_requests.get_yt_rows_to_replicate')
    async def _get_yt_rows_to_replicate(context):
        return EXPECTED_RESULT

    await replicate_yt_salesforce.replicate_data(cron_context)

    cursor = pgsql['internal_b2b'].cursor()
    query = """SELECT
                    *
                    FROM internal_b2b.sf_tg_support_contracts;
                        """

    cursor.execute(query)
    data = cursor.fetchall()

    assert data == EXPECTED_PG_RESULT
