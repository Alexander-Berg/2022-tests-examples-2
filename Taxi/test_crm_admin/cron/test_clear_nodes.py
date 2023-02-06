import pytest
import yt.wrapper as yt

from crm_admin.generated.cron import run_cron


@pytest.mark.now('2021-06-01 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table\d+$',
            'action': 'merge',
            'merge_dst': '//home/clear_node/heap',
            'delay': 24 * 30,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table\d+$',
            'action': 'merge',
            'merge_dst': '//home/clear_node/heap',
            'delay': 24 * 30,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'regular',
                'campaign_status': 'SCHEDULED',
            },
        },
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table\d+_merge$',
            'action': 'merge',
            'merge_dst': '//home/clear_node/heap',
            'delay': 24 * 30,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)_merge$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
    ],
)
@pytest.mark.yt(
    static_table_data=[
        'yt_gc_table1_sample.yaml',
        'yt_gc_table2_sample.yaml',
        'yt_gc_table3_sample.yaml',
        'yt_gc_table1_merge_sample.yaml',
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_merge(yt_apply, yt_client, cron_context, patch):
    tables_merged = [
        {'campaign_id': 1, 'data': {'id': '1', 'value': 'one'}},
        {'campaign_id': 1, 'data': {'id': '2', 'value': 'two'}},
        {'campaign_id': 2, 'data': {'id': '2', 'date': 'today'}},
        {'campaign_id': 2, 'data': {'id': '3', 'date': 'yesturday'}},
        {'campaign_id': 1, 'data': 'one'},
        {'campaign_id': 2, 'data': 'two'},
    ]
    dst_table = '//home/clear_node/heap'

    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])

    assert list(yt_client.read_table(dst_table)) == tables_merged

    for table in ['table1', 'table2']:
        assert not yt_client.exists('//home/clear_node/' + table)

    assert yt_client.exists('//home/clear_node/table3')


@pytest.mark.now('2021-06-01 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table(?P<campaign_id>\d+)',
            'action': 'remove',
            'delay': 24 * 30,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table(?P<campaign_id>\d+)',
            'action': 'remove',
            'delay': 24 * 30,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'regular',
                'campaign_status': 'SCHEDULED',
            },
        },
    ],
)
@pytest.mark.yt(
    static_table_data=[
        'yt_gc_table1_sample.yaml',
        'yt_gc_table2_sample.yaml',
        'yt_gc_table3_sample.yaml',
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_remove_campaigns(
        yt_apply, yt_client, cron_context, patch,
):
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])

    for table in ['table1', 'table2']:
        assert not yt_client.exists('//home/clear_node/' + table)

    assert yt_client.exists('//home/clear_node/table3')


@pytest.mark.now('3000-06-01 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table(?P<campaign_id>\d+)',
            'action': 'remove',
            'delay': 24 * 30,
        },
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table(?P<campaign_id>\d+)',
            'action': 'remove',
            'delay': 24 * 30,
        },
    ],
)
@pytest.mark.yt(
    static_table_data=[
        'yt_gc_table1_sample.yaml',
        'yt_gc_table2_sample.yaml',
        'yt_gc_table3_sample.yaml',
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_remove_impersonal(
        yt_apply, yt_client, cron_context, patch,
):
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])

    for table in ['table1', 'table2', 'table3']:
        assert not yt_client.exists('//home/clear_node/' + table)


@pytest.mark.now('2021-06-01 18:30:00')
@pytest.mark.config(CRM_ADMIN_CLEAR_NODES=[])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_empty(yt_apply, yt_client, cron_context, patch):
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])


@pytest.mark.now('2021-06-01 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table\d+_merge$',
            'action': 'merge',
            'merge_dst': '//home/clear_node/heap',
            'delay': 24 * 30,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)_merge$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
    ],
)
@pytest.mark.yt(static_table_data=['yt_gc_table1_sample.yaml'])
async def test_clear_nodes_segment_wo_campaign(
        yt_apply, yt_client, cron_context, patch,
):
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])


@pytest.mark.now('2021-03-01 01:00:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table1$',
            'action': 'remove',
            'delay': 0,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
    ],
)
@pytest.mark.yt(static_table_data=['yt_gc_table1_sample.yaml'])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_timezone_1(
        yt_apply, yt_client, cron_context, patch,
):
    assert yt_client.exists('//home/clear_node/table1')
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])
    assert not yt_client.exists('//home/clear_node/table1')


@pytest.mark.now('2021-03-01 00:50:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table1$',
            'action': 'remove',
            'delay': 0,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
    ],
)
@pytest.mark.yt(static_table_data=['yt_gc_table1_sample.yaml'])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_timezone_2(
        yt_apply, yt_client, cron_context, patch,
):
    assert yt_client.exists('//home/clear_node/table1')
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])
    assert yt_client.exists('//home/clear_node/table1')


@pytest.mark.now('2021-04-01 01:00:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table2$',
            'action': 'remove',
            'delay': 0,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'regular',
                'campaign_status': 'SCHEDULED',
            },
        },
    ],
)
@pytest.mark.yt(static_table_data=['yt_gc_table2_sample.yaml'])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_timezone_3(
        yt_apply, yt_client, cron_context, patch,
):
    assert yt_client.exists('//home/clear_node/table2')
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])
    assert not yt_client.exists('//home/clear_node/table2')


@pytest.mark.now('2021-04-01 00:50:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table2$',
            'action': 'remove',
            'delay': 0,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'regular',
                'campaign_status': 'SCHEDULED',
            },
        },
    ],
)
@pytest.mark.yt(static_table_data=['yt_gc_table2_sample.yaml'])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_timezone_4(
        yt_apply, yt_client, cron_context, patch,
):
    assert yt_client.exists('//home/clear_node/table2')
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])
    assert yt_client.exists('//home/clear_node/table2')


@pytest.mark.now('2030-06-01 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'path': '//home/clear_node',
            'file_mask': r'table(?P<campaign_id>\d+)',
            'action': 'remove',
            'delay': 0,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
    ],
)
@pytest.mark.yt(
    static_table_data=['yt_gc_table1_sample.yaml', 'yt_gc_table3_sample.yaml'],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_disable_rule_1(
        yt_apply, yt_client, cron_context, patch,
):
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])

    for table in ['table1', 'table3']:
        assert yt_client.exists('//home/clear_node/' + table)


@pytest.mark.now('2030-06-01 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': False,
            'path': '//home/clear_node',
            'file_mask': r'table(?P<campaign_id>\d+)',
            'action': 'remove',
            'delay': 0,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
    ],
)
@pytest.mark.yt(
    static_table_data=['yt_gc_table1_sample.yaml', 'yt_gc_table3_sample.yaml'],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_disable_rule_2(
        yt_apply, yt_client, cron_context, patch,
):
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])

    for table in ['table1', 'table3']:
        assert yt_client.exists('//home/clear_node/' + table)


@pytest.mark.now('2030-06-01 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table(?P<campaign_id>\d+)',
            'action': 'remove',
            'delay': 0,
            'max_affected': 1,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
    ],
)
@pytest.mark.yt(
    static_table_data=['yt_gc_table1_sample.yaml', 'yt_gc_table3_sample.yaml'],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_max_affected(
        yt_apply, yt_client, cron_context, patch,
):
    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])

    assert not yt_client.exists(
        '//home/clear_node/table1',
    ) or not yt_client.exists('//home/clear_node/table3')


@pytest.mark.now('2030-06-01 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_CLEAR_NODES=[
        {
            'enable': True,
            'path': '//home/clear_node',
            'file_mask': r'table\d+$',
            'action': 'merge',
            'merge_dst': '//home/clear_node/heap',
            'delay': 24 * 30,
            'fails_until_broken': 2,
            'campaign_filter': {
                'campaign_mask': r'table(?P<campaign_id>\d+)$',
                'campaign_type': 'oneshot',
                'campaign_status': 'CANCELED',
            },
        },
    ],
)
@pytest.mark.yt(static_table_data=['yt_gc_table1_sample.yaml'])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_nodes_skip_broken_tables(
        yt_apply, yt_client, cron_context, patch,
):
    table = '//home/clear_node/table1'

    @patch('crm_admin.utils.yt.yt_garbage_collector._run_add_campaign_id')
    async def _map_op(*args, **kwargs):
        raise yt.YtError()

    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])
    assert yt_client.get(table + '/@clear_nodes_merge_fails') == 1
    assert not yt_client.exists(table + '/@clear_nodes_broken_table')

    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])
    assert yt_client.get(table + '/@clear_nodes_merge_fails') == 2
    assert yt_client.exists(table + '/@clear_nodes_broken_table')

    await run_cron.main(['crm_admin.crontasks.clear_nodes', '-t', '0'])
    assert yt_client.get(table + '/@clear_nodes_merge_fails') == 2
