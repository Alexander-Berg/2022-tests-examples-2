import pytest

from taxi.stq import async_worker_ng

from crm_hub.repositories import efficiency_sending as ef_storage
from crm_hub.stq import create_efficiency_yt_absorber as absorber


async def verify_batch_sending_records(conn, yt_table_path, params, batch_len):
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


async def verify_multi_sending_records(conn, multi_len):
    multi_sending_records = await conn.fetch(
        'SELECT * FROM crm_hub.multi_sending_parts;',
    )
    assert len(multi_sending_records) == multi_len


async def verify_eff_sending_records(conn, efficiency_len, state):
    efficiency_sending_records = await conn.fetch(
        'SELECT * FROM crm_hub.efficiency_sending;',
    )
    efficiency_sending = efficiency_sending_records[0]

    assert len(efficiency_sending_records) == efficiency_len
    assert efficiency_sending['state'] == state


async def get_batch_sendings(context):
    query = 'SELECT * FROM crm_hub.batch_sending;'
    async with context.pg.master_pool.acquire() as conn:
        return await conn.fetch(query)


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
)
@pytest.mark.parametrize(
    'file_name, row_count, efficiency_len, batch_len, multi_len, calls, state',
    [
        ('efficiency_table.json', 25, 1, 10, 10, 10, 'new'),
        ('efficiency_empty_table.json', 0, 1, 0, 0, 0, 'finished'),
        ('efficiency_chunks_table.json', 12, 1, 4, 4, 4, 'new'),
    ],
)
async def test_efficiency_yt_absorber(
        patch,
        stq3_context,
        mockserver,
        load_json,
        file_name,
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

    storage = ef_storage.EfficiencySendingStorage(context=stq3_context)
    await storage.create(sending_id=sending_id, table_path='table_path')

    await absorber.task(
        context=stq3_context,
        sending_id=sending_id,
        table_path=yt_table_path,
        denied_path=None,
        test_table_path=None,
        task_info=async_worker_ng.TaskInfo('task_id', 0, 0, 'queue'),
        absorber_type='crm-efficiency',
        filter_group_name=None,
        verify=False,
        campaign_id=None,
        group_id=None,
    )

    async with stq3_context.pg.master_pool.acquire() as conn:
        await verify_batch_sending_records(
            conn, yt_table_path, params, batch_len,
        )
        await verify_multi_sending_records(conn, multi_len)
        await verify_eff_sending_records(conn, efficiency_len, state)

        assert len(patched_start_bulk_sender.calls) == calls

        if row_count:
            assert load_to_logbroker.calls[0]['data'] is not None
        else:
            assert not load_to_logbroker.calls


@pytest.mark.config(
    CRM_HUB_EFFICIENCY_SETTINGS={
        'campaign_row': 'campaign_id',
        'group_row': 'group_id',
        'timezone_name_row': 'timezone_name',
        'content_row': 'recipient_context',
        'chunk_size': 5,
    },
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'global_policy_allowed': False,
        'policy_chunk_size': 100,
        'policy_max_connections': 4,
        'policy_use_results': False,
    },
)
@pytest.mark.parametrize('filename', ['efficiency_db_creation.json'])
async def test_efficiency_yt_absorber_db_creation(
        stq3_context, load_json, patch, mockserver, filename,
):
    params = load_json(filename)
    batch_sendings = load_json('campaigns.json')

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.row_count')
    async def _(*args, **kwargs):
        return len(params['yt_table'])

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(*args, **kwargs):
        return params['yt_table']

    @patch('crm_hub.logic.efficiency_yt_absorber.SendingJob.start_bulk_sender')
    async def _patched_start_bulk_sender(*args, **kwargs):
        pass

    @mockserver.json_handler('/crm-scheduler/v1/register_communiction_to_send')
    def _register_communication(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    def _batch_sending_item(request):
        campaign_id = request.args['campaign_id']
        group_id = request.args['group_id']
        sending_key = f'{campaign_id}_{group_id}'
        return batch_sendings[sending_key]

    sending_id = '00000000000000000000000000000001'
    yt_table_path = '//yt_table'

    storage = ef_storage.EfficiencySendingStorage(context=stq3_context)
    await storage.create(sending_id=sending_id, table_path=yt_table_path)

    await absorber.task(
        context=stq3_context,
        sending_id=sending_id,
        table_path=yt_table_path,
        test_table_path=None,
        denied_path='',
        task_info=async_worker_ng.TaskInfo('task_id', 0, 0, 'queue'),
        absorber_type='crm-efficiency',
        filter_group_name=None,
        verify=False,
    )

    batch_sending_records = await get_batch_sendings(stq3_context)
    assert len(batch_sending_records) == params['jobs_number']

    yt_records = params['yt_table']
    for record in batch_sending_records:
        index = int(record['pg_table'].split('_')[2].replace('part', '')) - 1

        assert record['campaign_id'] == yt_records[index]['campaign_id']
        assert record['group_id'] == yt_records[index]['group_id']
        assert record['group_name'] == yt_records[index]['group_name']
        assert record['yt_table'] == yt_table_path


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
    CRM_HUB_ENABLE_BATCH_SENDING_V2={
        'fully_enabled': True,
        'enabled_campaigns': [],
    },
)
@pytest.mark.parametrize(
    'file_name, row_count, efficiency_len, batch_len, multi_len, calls, state',
    [
        ('efficiency_table.json', 25, 1, 10, 10, 10, 'new'),
        ('efficiency_empty_table.json', 0, 1, 0, 0, 0, 'finished'),
        ('efficiency_chunks_table.json', 12, 1, 4, 4, 4, 'new'),
    ],
)
async def test_efficiency_yt_absorber_v2_batch_sending(
        patch,
        stq3_context,
        mockserver,
        load_json,
        file_name,
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

    @mockserver.json_handler('crm-admin/v2/batch-sending/item')
    def _batch_sending_item(request):
        campaign_id = request.args['campaign_id']
        group_id = request.args['group_id']
        sending_key = f'{campaign_id}_{group_id}'
        batch_sendings = load_json('campaigns_new_handler.json')
        return batch_sendings[sending_key]

    sending_id = '00000000000000000000000000000001'

    storage = ef_storage.EfficiencySendingStorage(context=stq3_context)
    await storage.create(sending_id=sending_id, table_path='table_path')

    await absorber.task(
        context=stq3_context,
        sending_id=sending_id,
        table_path=yt_table_path,
        test_table_path=None,
        denied_path=None,
        task_info=async_worker_ng.TaskInfo('task_id', 0, 0, 'queue'),
        absorber_type='crm-efficiency',
        filter_group_name=None,
        verify=False,
    )

    async with stq3_context.pg.master_pool.acquire() as conn:
        await verify_batch_sending_records(
            conn, yt_table_path, params, batch_len,
        )
        await verify_multi_sending_records(conn, multi_len)
        await verify_eff_sending_records(conn, efficiency_len, state)

        assert len(patched_start_bulk_sender.calls) == calls


@pytest.mark.config(
    CRM_HUB_EFFICIENCY_SETTINGS={
        'campaign_row': 'campaign_id',
        'group_row': 'group_id',
        'timezone_name_row': 'timezone_name',
        'content_row': 'recipient_context',
        'chunk_size': 5,
    },
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'global_policy_allowed': False,
        'policy_chunk_size': 100,
        'policy_max_connections': 4,
        'policy_use_results': False,
    },
    CRM_HUB_ENABLE_BATCH_SENDING_V2={
        'fully_enabled': True,
        'enabled_campaigns': [],
    },
)
@pytest.mark.parametrize('filename', ['efficiency_db_creation.json'])
async def test_efficiency_yt_absorber_db_creation_v2_batch_sending(
        stq3_context, load_json, patch, mockserver, filename,
):
    params = load_json(filename)
    batch_sendings = load_json('campaigns_new_handler.json')

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.row_count')
    async def _(*args, **kwargs):
        return len(params['yt_table'])

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(*args, **kwargs):
        return params['yt_table']

    @patch('crm_hub.logic.efficiency_yt_absorber.SendingJob.start_bulk_sender')
    async def _patched_start_bulk_sender(*args, **kwargs):
        pass

    @mockserver.json_handler('/crm-scheduler/v1/register_communiction_to_send')
    def _register_communication(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('crm-admin/v2/batch-sending/item')
    def _batch_sending_item(request):
        campaign_id = request.args['campaign_id']
        group_id = request.args['group_id']
        sending_key = f'{campaign_id}_{group_id}'
        return batch_sendings[sending_key]

    sending_id = '00000000000000000000000000000001'
    yt_table_path = '//yt_table'

    storage = ef_storage.EfficiencySendingStorage(context=stq3_context)
    await storage.create(sending_id=sending_id, table_path=yt_table_path)

    await absorber.task(
        context=stq3_context,
        sending_id=sending_id,
        table_path=yt_table_path,
        test_table_path=None,
        denied_path='',
        task_info=async_worker_ng.TaskInfo('task_id', 0, 0, 'queue'),
        absorber_type='crm-efficiency',
        filter_group_name=None,
        verify=False,
    )

    batch_sending_records = await get_batch_sendings(stq3_context)
    assert len(batch_sending_records) == params['jobs_number']

    yt_records = params['yt_table']
    for record in batch_sending_records:
        index = int(record['pg_table'].split('_')[2].replace('part', '')) - 1

        assert record['campaign_id'] == yt_records[index]['campaign_id']
        assert record['group_id'] == yt_records[index]['group_id']
        assert record['group_name'] == yt_records[index]['group_name']
        assert record['yt_table'] == yt_table_path


# -------------------- CRM-SCHEDULER SENDING FLOW --------------------
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
)
@pytest.mark.parametrize(
    'file_name, row_count, efficiency_len, batch_len, multi_len, calls, state'
    ', denied',
    [
        ('efficiency_table.json', 25, 1, 10, 10, 10, 'new', False),
        ('efficiency_empty_table.json', 0, 1, 0, 0, 0, 'finished', False),
        ('efficiency_chunks_table.json', 12, 1, 4, 4, 4, 'new', False),
        ('efficiency_table.json', 25, 1, 12, 12, 12, 'new', True),
        ('efficiency_empty_table.json', 0, 1, 0, 0, 0, 'finished', True),
        ('efficiency_chunks_table.json', 12, 1, 4, 4, 4, 'new', True),
    ],
)
async def test_efficiency_yt_absorber_scheduler(
        patch,
        stq3_context,
        mockserver,
        load_json,
        file_name,
        row_count,
        efficiency_len,
        batch_len,
        multi_len,
        calls,
        state,
        denied,
):
    params = load_json(file_name)
    yt_table_path = '//yt_table'
    yt_denied_path = '//yt_denied_table' if denied else None

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(table):
        # pylint: disable=protected-access
        if table == yt_table_path:
            result = params['yt_table']
        else:
            result = params['yt_denied_table']
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

    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    def _batch_sending_item(request):
        campaign_id = request.args['campaign_id']
        group_id = request.args['group_id']
        sending_key = f'{campaign_id}_{group_id}'
        batch_sendings = load_json('campaigns.json')
        return batch_sendings[sending_key]

    @mockserver.json_handler('/crm-scheduler/v1/register_communiction_to_send')
    def _register_communication(request):
        return mockserver.make_response(status=200, json={})

    sending_id = '00000000000000000000000000000001'

    storage = ef_storage.EfficiencySendingStorage(context=stq3_context)
    await storage.create(sending_id=sending_id, table_path='table_path')

    await absorber.task(
        context=stq3_context,
        sending_id=sending_id,
        table_path=yt_table_path,
        denied_path=yt_denied_path,
        test_table_path=None,
        task_info=async_worker_ng.TaskInfo('task_id', 0, 0, 'queue'),
        absorber_type='crm-efficiency',
        filter_group_name=None,
        verify=False,
    )

    async with stq3_context.pg.master_pool.acquire() as conn:
        batch_sending_records = await conn.fetch(
            'SELECT * FROM crm_hub.batch_sending;',
        )
        assert len(batch_sending_records) == batch_len
        for record in batch_sending_records:
            pg_table = record['pg_table']
            job_records = await conn.fetch(
                f'SELECT user_id, status FROM crm_hub.{pg_table};',
            )

            computed = [record['user_id'] for record in job_records]
            expected = params['result_scheduler'][pg_table]
            assert set(computed) == set(expected)

            if pg_table.endswith('denied'):
                assert record['yt_table'] == yt_denied_path
                assert set(record['status'] for record in job_records) == {
                    'DENIED',
                }
            else:
                assert record['yt_table'] == yt_table_path

        await verify_multi_sending_records(conn, multi_len)
        await verify_eff_sending_records(conn, efficiency_len, state)
        assert len(patched_start_bulk_sender.calls) == calls


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
    CRM_HUB_ENABLE_BATCH_SENDING_V2={
        'fully_enabled': True,
        'enabled_campaigns': [],
    },
    CRM_HUB_TIMEZONE_PROCESSING_POLICY={
        'timezone_processed_for_efficiency_flow': 'ENABLED',
        'timezone_processed_for_admin_flow': 'ENABLED',
    },
)
@pytest.mark.parametrize(
    'file_name, row_count, efficiency_len, batch_len, multi_len, calls, state'
    ', denied',
    [
        ('efficiency_table.json', 25, 1, 10, 10, 10, 'new', False),
        ('efficiency_empty_table.json', 0, 1, 0, 0, 0, 'finished', False),
        ('efficiency_chunks_table.json', 12, 1, 4, 4, 4, 'new', False),
        ('efficiency_table.json', 25, 1, 12, 12, 12, 'new', True),
        ('efficiency_table_with_tz.json', 25, 1, 14, 14, 14, 'new', True),
        ('efficiency_empty_table.json', 0, 1, 0, 0, 0, 'finished', True),
        ('efficiency_chunks_table.json', 12, 1, 4, 4, 4, 'new', True),
    ],
)
async def test_efficiency_yt_absorber_scheduler_v2_batch_sending(
        patch,
        stq3_context,
        mockserver,
        load_json,
        file_name,
        row_count,
        efficiency_len,
        batch_len,
        multi_len,
        calls,
        state,
        denied,
):
    # TODO: do we have batch_len == multi_len == calls?
    params = load_json(file_name)
    yt_table_path = '//yt_table'
    yt_denied_path = '//yt_denied_table' if denied else None

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(table):
        # pylint: disable=protected-access
        if table == yt_table_path:
            result = params['yt_table']
        else:
            result = params['yt_denied_table']
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

    @mockserver.json_handler('crm-admin/v2/batch-sending/item')
    def _batch_sending_item(request):
        campaign_id = request.args['campaign_id']
        group_id = request.args['group_id']
        sending_key = f'{campaign_id}_{group_id}'
        batch_sendings = load_json('campaigns_new_handler.json')
        return batch_sendings[sending_key]

    @mockserver.json_handler('/crm-scheduler/v1/register_communiction_to_send')
    def _register_communication(request):
        return mockserver.make_response(status=200, json={})

    sending_id = '00000000000000000000000000000001'

    storage = ef_storage.EfficiencySendingStorage(context=stq3_context)
    await storage.create(sending_id=sending_id, table_path='table_path')

    await absorber.task(
        context=stq3_context,
        sending_id=sending_id,
        table_path=yt_table_path,
        denied_path=yt_denied_path,
        test_table_path=None,
        task_info=async_worker_ng.TaskInfo('task_id', 0, 0, 'queue'),
        absorber_type='crm-efficiency',
        filter_group_name=None,
        verify=False,
    )

    async with stq3_context.pg.master_pool.acquire() as conn:
        batch_sending_records = await conn.fetch(
            'SELECT * FROM crm_hub.batch_sending;',
        )
        assert len(batch_sending_records) == batch_len
        for record in batch_sending_records:
            pg_table = record['pg_table']
            job_records = await conn.fetch(
                f'SELECT user_id, status FROM crm_hub.{pg_table};',
            )

            computed = [record['user_id'] for record in job_records]
            expected = params['result_scheduler'][pg_table]
            assert set(computed) == set(expected)

            if pg_table.endswith('denied'):
                assert record['yt_table'] == yt_denied_path
                assert set(record['status'] for record in job_records) == {
                    'DENIED',
                }
            else:
                assert record['yt_table'] == yt_table_path

        await verify_multi_sending_records(conn, multi_len)
        await verify_eff_sending_records(conn, efficiency_len, state)

        assert len(patched_start_bulk_sender.calls) == calls
