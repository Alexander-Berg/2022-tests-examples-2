# pylint: disable=import-only-modules
import pytest

from taxi.stq import async_worker_ng

from crm_hub.repositories.efficiency_sending import EfficiencySendingStorage
from crm_hub.stq import create_efficiency_yt_absorber as absorber


@pytest.mark.config(
    CRM_HUB_EFFICIENCY_SETTINGS={
        'campaign_row': 'campaign_id',
        'group_row': 'group_id',
        'timezone_name_row': 'timezone_name',
        'content_row': 'recipient_context',
        'chunk_size': 10,
    },
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'global_policy_allowed': False,
        'policy_chunk_size': 100,
        'policy_max_connections': 4,
        'policy_use_results': False,
    },
    CRM_HUB_TIMEZONE_PROCESSING_POLICY={
        'timezone_processed_for_efficiency_flow': 'ENABLED',
        'timezone_processed_for_admin_flow': 'ENABLED',
    },
)
@pytest.mark.parametrize(
    'file_name, row_count, efficiency_len, batch_len, multi_len, '
    'calls, state, filter_group_name, campaign_id, group_id',
    [
        ('admin_table.json', 25, 1, 4, 4, 4, 'new', '2', 1, 2),
        (
            'admin_empty_table.json',
            0,
            1,
            0,
            0,
            0,
            'finished',
            None,
            None,
            None,
        ),
        ('admin_chunks_table.json', 12, 1, 4, 4, 4, 'new', 'Default', 2, 3),
    ],
)
async def test_efficiency_yt_absorber_for_admin(
        patch,
        stq3_context,
        mockserver,
        load_json,
        file_name,
        campaign_id,
        group_id,
        filter_group_name,
        row_count,
        efficiency_len,
        batch_len,
        multi_len,
        calls,
        state,
):
    params = load_json(file_name)
    yt_table_path = '//yt_table'

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(table):
        # pylint: disable=protected-access
        result = params['yt_table']
        attributes = table._path_object.attributes

        if 'ranges' not in attributes:
            return result

        range_attribute = attributes['ranges'][0]
        if (
                'lower_limit' in range_attribute
                and 'upper_limit' in range_attribute
        ):
            start_index = range_attribute['lower_limit']['row_index']
            stop_index = range_attribute['upper_limit']['row_index']
            result = result[start_index:stop_index]

        return result

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.row_count')
    async def _(*args, **kwargs):
        return row_count

    @patch('crm_hub.logic.efficiency_yt_absorber.SendingJob.start_bulk_sender')
    async def patched_start_bulk_sender(*args, **kwargs):
        return

    @patch('crm_hub.repositories.process_results.DataLoader.load_to_logbroker')
    async def load_to_logbroker(data, *args, **kwargs):
        pass

    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    def _batch_sending_item(request):
        campaign_id = request.args['campaign_id']
        group_id = request.args['group_id']
        sending_key = f'{campaign_id}_{group_id}'
        batch_sendings = load_json('campaigns.json')
        return batch_sendings[sending_key]

    sending_id = '00000000000000000000000000000001'

    storage = EfficiencySendingStorage(context=stq3_context)
    await storage.create(sending_id=sending_id, table_path='table_path')

    await absorber.task(
        context=stq3_context,
        sending_id=sending_id,
        table_path=yt_table_path,
        denied_path=None,
        test_table_path=None,
        task_info=async_worker_ng.TaskInfo('task_id', 0, 0, 'queue'),
        absorber_type='crm-admin',
        filter_group_name=filter_group_name,
        verify=False,
        campaign_id=campaign_id,
        group_id=group_id,
    )

    async with stq3_context.pg.master_pool.acquire() as conn:
        batch_sending_records = await conn.fetch(
            'SELECT * FROM crm_hub.batch_sending;',
        )
        assert len(batch_sending_records) == batch_len
        for record in batch_sending_records:
            pg_table = record['pg_table']
            job_records = await conn.fetch(
                f'SELECT user_id FROM crm_hub.{pg_table};',
            )

            computed = [record['user_id'] for record in job_records]
            expected = params['result'][pg_table]
            assert record['yt_table'] == yt_table_path
            assert computed == expected

        multi_sending_records = await conn.fetch(
            'SELECT * FROM crm_hub.multi_sending_parts;',
        )
        assert len(multi_sending_records) == multi_len

        efficiency_sending_records = await conn.fetch(
            'SELECT * FROM crm_hub.efficiency_sending;',
        )
        efficiency_sending = efficiency_sending_records[0]

        assert len(efficiency_sending_records) == efficiency_len

        if row_count:
            assert load_to_logbroker.calls[0]['data'] is not None
        else:
            assert not load_to_logbroker.calls

        assert efficiency_sending['state'] == state
        assert len(patched_start_bulk_sender.calls) == calls


# TODO: this is useful for converting tests from efficiency to admin;
#  to be removed before merging into trunk;

# @pytest.mark.config(
#     CRM_HUB_EFFICIENCY_SETTINGS={
#         'campaign_row': 'campaign_id',
#         'group_row': 'group_id',
#         'timezone_name_row': 'timezone_name',
#         'content_row': 'recipient_context',
#         'chunk_size': 10,
#     },
#     CRM_HUB_BATCH_SENDING_SETTINGS={
#         'global_policy_allowed': False,
#         'policy_chunk_size': 100,
#         'policy_max_connections': 4,
#         'policy_use_results': False,
#     },
# )
# @pytest.mark.parametrize(
#     'file_name',
#     [
#         ('efficiency_table.json'),
#         ('efficiency_empty_table.json'),
#         ('efficiency_chunks_table.json'),
#         ('efficiency_table_with_tz.json'),
#         ('efficiency_db_creation.json'),
#     ],
# )
# async def test_convert(
#         patch,
#         stq3_context,
#         mockserver,
#         load_json,
#         file_name,
# ):
#     import json
#     params = load_json(file_name)
#     with open(file_name.replace('efficiency', 'admin'), 'w') as outfile:
#         params.pop('yt_denied_table', None)
#         for param in params['yt_table']:
#             recipient_context = param.pop('recipient_context')
#             param.pop('campaign_id')
#             param.update(recipient_context)
#         json.dump(params, outfile, indent=2)
