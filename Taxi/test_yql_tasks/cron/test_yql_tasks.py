# pylint: disable=redefined-outer-name
# pylint: disable=no-method-argument
# pylint: disable=unused-variable

import pytest

from test_yql_tasks import conftest
from yql_tasks.generated.cron import run_cron
from yql_tasks.internal import yql_tasks_manager


@pytest.mark.parametrize(
    'cron',
    [
        'yql_tasks.crontasks.check_not_infranaim_tickets',
        'yql_tasks.crontasks.carsharing_transactions',
        'yql_tasks.crontasks.clean_old_tables',
        'yql_tasks.crontasks.deprecated_driver_info_full',
        'yql_tasks.crontasks.download_active_driver_attributes',
        'yql_tasks.crontasks.download_active_driver_ids',
        'yql_tasks.crontasks.eda_actives',
        'yql_tasks.crontasks.eda_deduplicate',
        'yql_tasks.crontasks.infranaim_call_vs_sms_w_sla',
        'yql_tasks.crontasks.jobboards_dashbord',
        'yql_tasks.crontasks.salesforce_territories',
        'yql_tasks.crontasks.sf_actives_from_zd',
        'yql_tasks.crontasks.sla_with_no_lid',
        'yql_tasks.crontasks.tickets_order_attribution',
        'yql_tasks.crontasks.zd_tickets_to_close',
    ],
)
async def test_yql_tasks(patch, cron):
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        return conftest.MockYqlRequestOperation()

    await run_cron.main([cron, '-t', '0'])


@pytest.mark.parametrize(
    'cron', ['yql_tasks.crontasks.deprecated_driver_info_full'],
)
async def test_query_error(patch, cron):
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        return conftest.MockYqlRequestOperationError()

    with pytest.raises(yql_tasks_manager.QueryError):
        await run_cron.main([cron, '-t', '0'])


@pytest.mark.parametrize('cron', ['yql_tasks.crontasks.yt_to_oktell_calls'])
async def test_yt_to_oktell_calls(patch, cron):
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        return conftest.MockYqlRequestOperation()

    @patch('yql_tasks.internal.yql_tasks_manager._make_result_table')
    def patched_make_result_table(*args, **kwargs):
        return [{'table_path': '1'}, {'table_path': '2'}]

    await run_cron.main([cron, '-t', '0'])
