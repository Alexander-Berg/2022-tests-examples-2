# pylint: disable=protected-access

import uuid

import dateutil
import psycopg2
import pytest

from generated.models import crm_admin
from taxi.util import dates

from crm_hub.generated.service.swagger import models
from crm_hub.logic import supercontrol
from crm_hub.logic import yt_absorber_v2 as yt
from crm_hub.repositories import batch_sending


def mock_admin(mockserver):
    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        return {
            'name': 'my_name',
            'entity_type': 'Driver',
            'group_type': 'testing',
            'channel': 'SMS',
            'yt_table': 'my_yt_table',
            'yt_test_table': 'my_yt_table_verification',
            'local_control': False,
            'global_control': False,
            'channel_info': {
                'channel_name': 'driver_sms',
                'intent': 'none',
                'sender': 'sender',
                'text': 'text',
                'action': 'MessageNew',
                'content': 'my_content',
                'deeplink': 'my_deeplink',
                'code': 100,
                'ttl': 30,
                'collapse_key': 'MessageNew:test',
                'feed_id': 'id',
                'send_at': '2020-09-11T10:00:00+03:00',
                'type': 'type',
                'url': 'url',
                'title': 'title',
                'teaser': 'teaser',
            },
            'extra_data': {},
            'report_info': {
                'creation_day': 'friday_the_13th',
                'channel': 'driver_sms',
                'experiment_name': 'experiment_name',
                'experiment_type': 'experiment_type',
                'experiment_id': 'experiment_id',
            },
        }


def mock_admin_v2(mockserver):
    @mockserver.json_handler('crm-admin/v2/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        return {
            'name': 'my_name',
            'entity_type': 'Driver',
            'group_type': 'testing',
            'yt_table': 'my_yt_table',
            'yt_test_table': 'my_yt_table_verification',
            'local_control': False,
            'global_control': False,
            'actions': [
                {'action_name': 'policy', 'channel': 'SMS'},
                {
                    'action_name': 'channel',
                    'channel_info': {
                        'channel_name': 'driver_sms',
                        'intent': 'none',
                        'sender': 'sender',
                        'text': 'text',
                        'action': 'MessageNew',
                        'content': 'my_content',
                        'deeplink': 'my_deeplink',
                        'code': 100,
                        'ttl': 30,
                        'collapse_key': 'MessageNew:test',
                        'feed_id': 'id',
                        'send_at': '2020-09-11T10:00:00+03:00',
                        'type': 'type',
                        'url': 'url',
                        'title': 'title',
                        'teaser': 'teaser',
                    },
                },
            ],
            'extra_data': {},
            'report_info': {
                'creation_day': 'friday_the_13th',
                'channel': 'driver_sms',
                'experiment_name': 'experiment_name',
                'experiment_type': 'experiment_type',
                'experiment_id': 'experiment_id',
            },
        }


async def verify_results(
        context,
        pgsql,
        pg_table,
        expected_results,
        sending_id,
        patch,
        mockserver,
        global_control_enabled=True,
):
    @patch('crm_hub.repositories.process_results.DataLoader.load_to_logbroker')
    async def load_to_logbroker(data, *args, **kwargs):
        pass

    mock_admin(mockserver)
    mock_admin_v2(mockserver)

    storage = batch_sending.BatchSendingStorage(context)
    sending = await storage.fetch(sending_id)
    master_pool = context.pg.master_pool
    async with master_pool.acquire() as conn:
        args = (context, conn, sending, True, global_control_enabled)
        yt_absorber = await yt.YtAbsorber.create(*args)
        await yt_absorber.process()
    cursor = pgsql['crm_hub'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(f'SELECT * FROM crm_hub.{pg_table};')
    actual_results = cursor.fetchall()

    logbroker_logs = [
        logbroker_log
        for logbroker_chunk in load_to_logbroker.calls
        for logbroker_log in logbroker_chunk['data']
    ]

    assert len(logbroker_logs) == len(actual_results)
    assert len(actual_results) == len(expected_results[sending_id])
    for index, row in enumerate(actual_results):
        result = expected_results[sending_id][index]
        for key in result:
            assert row[key] == result[key]


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'global_policy_allowed': False,
        'policy_chunk_size': 100,
        'policy_max_connections': 4,
        'policy_use_results': False,
    },
)
@pytest.mark.parametrize(
    'campaign_id, group_id, verify, expected_group_types, efficiency',
    [
        (1, 1, False, ['testing', 'control'], '0'),
        (1, 1, True, ['verify'], '0'),
        (1, 2, False, ['testing', 'control'], '0'),
        (1, 2, True, ['verify'], '0'),
    ],
)
async def test_job_creation(
        web_context,
        patch,
        mockserver,
        load_json,
        campaign_id,
        group_id,
        verify,
        expected_group_types,
        efficiency,
):
    sending_key = f'batch_{campaign_id}_{group_id}'

    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    async def _batch_sending_item(*_a, **_kw):
        batch_sendings = load_json('crm_admin_batch_sending.json')
        return batch_sendings[sending_key]

    @patch('crm_hub.logic.yt_absorber_v2._call_yt_absorber_task')
    async def _call_yt_absorber_task(
            context, sending_full_info, *args, **kwargs,
    ):
        pass

    send_at = dates.utcnow()
    subfilter = models.api.FilterObject(column='efficiency', value=efficiency)
    await yt.create_absorber_task(
        web_context, campaign_id, group_id, verify, send_at, [subfilter], 0,
    )

    actual_group_types = [
        call['sending_full_info'].group_type
        for call in _call_yt_absorber_task.calls
    ]
    assert expected_group_types == actual_group_types


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'global_policy_allowed': False,
        'policy_chunk_size': 100,
        'policy_max_connections': 4,
        'policy_use_results': False,
    },
    CRM_HUB_ENABLE_BATCH_SENDING_V2={
        'fully_enabled': False,
        'enabled_campaigns': [1],
    },
)
@pytest.mark.parametrize(
    'campaign_id, group_id, verify, expected_group_types, efficiency',
    [
        (1, 1, False, ['testing', 'control'], '0'),
        (1, 1, True, ['verify'], '0'),
        (1, 2, False, ['testing', 'control'], '0'),
        (1, 2, True, ['verify'], '0'),
        (1, 3, False, ['testing', 'control'], '0'),
        (1, 3, True, ['verify'], '0'),
        (1, 4, False, ['testing', 'control'], '0'),
        (1, 4, True, ['verify'], '0'),
    ],
)
async def test_job_creation_v2_batch_sending(
        web_context,
        patch,
        mockserver,
        load_json,
        campaign_id,
        group_id,
        verify,
        expected_group_types,
        efficiency,
):
    sending_key = f'batch_{campaign_id}_{group_id}'

    @mockserver.json_handler('crm-admin/v2/batch-sending/item')
    async def _batch_sending_item(*_a, **_kw):
        batch_sendings = load_json('crm_admin_batch_sending_v2.json')
        return batch_sendings[sending_key]

    @patch('crm_hub.logic.yt_absorber_v2._call_yt_absorber_task')
    async def _call_yt_absorber_task(
            context, sending_full_info, *args, **kwargs,
    ):
        pass

    send_at = dates.utcnow()
    subfilter = models.api.FilterObject(column='efficiency', value=efficiency)
    await yt.create_absorber_task(
        web_context, campaign_id, group_id, verify, send_at, [subfilter], 0,
    )

    actual_group_types = [
        call['sending_full_info'].group_type
        for call in _call_yt_absorber_task.calls
    ]

    assert actual_group_types == expected_group_types


@pytest.mark.parametrize(
    'entity, sending_id, pg_table',
    [
        ('driver', '00000000000000000000000000000001', 'batch_1_1'),
        ('driver', '00000000000000000000000000000002', 'batch_1_2'),
        ('driver', '00000000000000000000000000000003', 'batch_1_3'),
        ('driver', '00000000000000000000000000000004', 'batch_1_4'),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_sending.sql'])
async def test_absorber(
        patch,
        stq3_context,
        load_json,
        pgsql,
        entity,
        sending_id,
        pg_table,
        mockserver,
):
    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.get')
    async def _get(*args, **kwargs):
        return segments[entity]['schema']

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(*args, **kwargs):
        return segments[entity]['segment']

    segments = load_json('crm_admin_segments.json')
    expected_results = load_json('yt_absorber_result.json')
    await verify_results(
        stq3_context,
        pgsql,
        pg_table,
        expected_results,
        sending_id,
        patch,
        mockserver,
    )


@pytest.mark.parametrize(
    'entity, sending_id, pg_table',
    [
        ('driver', '00000000000000000000000000000001', 'batch_1_1'),
        ('driver', '00000000000000000000000000000002', 'batch_1_2'),
        ('driver', '00000000000000000000000000000003', 'batch_1_3'),
        ('driver', '00000000000000000000000000000004', 'batch_1_4'),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_sending_v2.sql'])
async def test_absorber_v2(
        patch,
        web_context,
        load_json,
        pgsql,
        entity,
        sending_id,
        pg_table,
        mockserver,
):
    @patch('crm_hub.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def _get(*args, **kwargs):
        return segments[entity]['schema']

    @patch('crm_hub.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(*args, **kwargs):
        return segments[entity]['segment']

    segments = load_json('crm_admin_segments.json')
    expected_results = load_json('yt_absorber_result_v2.json')
    await verify_results(
        web_context,
        pgsql,
        pg_table,
        expected_results,
        sending_id,
        patch,
        mockserver,
    )


@pytest.mark.parametrize(
    'sending_id,pg_table,global_control_enabled',
    [
        ('00000000000000000000000000000005', 'batch_2_1_testing', False),
        ('00000000000000000000000000000006', 'batch_2_1_testing', True),
        ('00000000000000000000000000000007', 'batch_2_1_control', False),
        ('00000000000000000000000000000008', 'batch_2_1_control', True),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_sending.sql'])
async def test_absorber_w_control(
        patch,
        stq3_context,
        load_json,
        pgsql,
        sending_id,
        pg_table,
        global_control_enabled,
        mockserver,
):
    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.get')
    async def _get(*args, **kwargs):
        return segments['schema']

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(*args, **kwargs):
        return segments['segment']

    segments = load_json('crm_admin_segments_w_control.json')
    results = load_json('yt_absorber_w_control_result.json')
    await verify_results(
        stq3_context,
        pgsql,
        pg_table,
        results,
        sending_id,
        patch,
        mockserver,
        global_control_enabled,
    )


@pytest.mark.config(CRM_HUB_SUPERCONTROL_SETTINGS={'enabled_for_all': True})
@pytest.mark.pgsql('crm_hub', files=['batch_sending.sql'])
@pytest.mark.parametrize(
    'sending_id, pg_table, campaign_got_targets',
    [
        ('00000000000000000000000000000005', 'batch_2_1_testing', False),
        ('00000000000000000000000000000006', 'batch_2_1_testing', True),
        ('00000000000000000000000000000007', 'batch_2_1_control', False),
        ('00000000000000000000000000000008', 'batch_2_1_control', True),
    ],
)
async def test_absorber_w_supercontrol(
        patch,
        stq3_context,
        load_json,
        pgsql,
        sending_id,
        pg_table,
        campaign_got_targets,
        mockserver,
):
    @patch('crm_hub.logic.supercontrol.TargetsConfig.from_admin')
    async def _wat(*args, **kwargs):
        if campaign_got_targets:
            return supercontrol.TargetsConfig.from_admin_response(
                crm_admin.TargetConfig(
                    targets_labels=[],
                    control_targets=[
                        crm_admin.TargetControlConfig(
                            const_salt='salt',
                            is_active=True,
                            label='global_control',
                            id=123,
                            current_period=crm_admin.PeriodControlConfig(
                                inverted_period_selection=False,
                                previous_control_saved_percentage=50,
                                current_control=crm_admin.SupercontrolConfig(
                                    control_percentage=5,
                                    mechanism='exp3',
                                    salt='RandomHash20210623',
                                    key='unique_driver_id',
                                ),
                                previous_control=crm_admin.SupercontrolConfig(
                                    control_percentage=5,
                                    mechanism='exp3',
                                    salt='RandomHash20210623',
                                    key='unique_driver_id',
                                ),
                            ),
                            previous_period=crm_admin.PeriodControlConfig(
                                inverted_period_selection=False,
                                previous_control_saved_percentage=50,
                                current_control=crm_admin.SupercontrolConfig(
                                    control_percentage=5,
                                    mechanism='exp3',
                                    salt='RandomHash20210623',
                                    key='unique_driver_id',
                                ),
                                previous_control=crm_admin.SupercontrolConfig(
                                    control_percentage=5,
                                    mechanism='exp3',
                                    salt='RandomHash20210623',
                                    key='unique_driver_id',
                                ),
                            ),
                        ),
                    ],
                ),
            )
        return supercontrol.TargetsConfig.from_admin_response(
            crm_admin.TargetConfig(targets_labels=[], control_targets=[]),
        )

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.get')
    async def _get(*args, **kwargs):
        return segments['schema']

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(*args, **kwargs):
        return segments['segment']

    segments = load_json('crm_admin_segments_w_supercontrol.json')
    expected_results = load_json('yt_absorber_w_supercontrol_result.json')
    await verify_results(
        stq3_context,
        pgsql,
        pg_table,
        expected_results,
        sending_id,
        patch,
        mockserver,
    )


@pytest.mark.parametrize(
    'entity, sending_id, pg_table',
    [
        ('user', '00000000000000000000000000000014', 'batch_4_1'),
        ('user', '00000000000000000000000000000015', 'batch_4_1'),
        ('user', '00000000000000000000000000000016', 'batch_4_1'),
        ('driver', '00000000000000000000000000000017', 'batch_5_1'),
        ('driver', '00000000000000000000000000000018', 'batch_5_1'),
        ('driver', '00000000000000000000000000000019', 'batch_5_1'),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_sending.sql'])
async def test_absorber_w_efficiency(
        patch,
        stq3_context,
        load_json,
        pgsql,
        entity,
        sending_id,
        pg_table,
        mockserver,
):
    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.get')
    async def _get(*args, **kwargs):
        return segments[entity]['schema']

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(*args, **kwargs):
        return segments[entity]['segment']

    segments = load_json('crm_admin_segments_w_efficiency.json')
    expected_results = load_json('yt_absorber_w_efficiency_result.json')
    await verify_results(
        stq3_context,
        pgsql,
        pg_table,
        expected_results,
        sending_id,
        patch,
        mockserver,
    )


@pytest.mark.parametrize(
    'entity, sending_id, pg_table',
    [
        ('user', '00000000000000000000000000000014', 'batch_4_1'),
        ('user', '00000000000000000000000000000015', 'batch_4_1'),
        ('user', '00000000000000000000000000000016', 'batch_4_1'),
        ('driver', '00000000000000000000000000000017', 'batch_5_1'),
        ('driver', '00000000000000000000000000000018', 'batch_5_1'),
        ('driver', '00000000000000000000000000000019', 'batch_5_1'),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_sending_v2.sql'])
async def test_absorber_w_efficiency_v2(
        patch,
        web_context,
        load_json,
        pgsql,
        entity,
        sending_id,
        pg_table,
        mockserver,
):
    @patch('crm_hub.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def _get(*args, **kwargs):
        return segments[entity]['schema']

    @patch('crm_hub.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table')
    async def _read_table(*args, **kwargs):
        return segments[entity]['segment']

    segments = load_json('crm_admin_segments_w_efficiency.json')
    expected_results = load_json('yt_absorber_w_efficiency_result_v2.json')
    await verify_results(
        web_context,
        pgsql,
        pg_table,
        expected_results,
        sending_id,
        patch,
        mockserver,
    )


@pytest.mark.parametrize(
    'campaign_id, group_id, group_type, subfilters, start_id, expected_result',
    [
        (1, 1, 'verify', [], 0, True),
        (1, 1, 'control', [], 0, True),
        (2, 1, 'verify', [], 0, True),
        (2, 1, 'control', [], 0, True),
        (2, 1, 'testing', [], 0, False),
        (2, 1, 'testing', [], 1, True),
        (
            2,
            1,
            'testing',
            [models.api.FilterObject(column='efficiency', value='1')],
            0,
            True,
        ),
        (3, 1, 'verify', [], 0, True),
        (3, 1, 'control', [], 0, True),
        (3, 1, 'testing', [], 0, True),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['deny_retry.sql'])
async def test_allow_only_verify_retry(
        web_context,
        campaign_id,
        group_id,
        group_type,
        subfilters,
        start_id,
        expected_result,
):
    storage = batch_sending.BatchSendingStorage(web_context)

    # pylint: disable=W0212
    allow = await yt._allow_only_verify_retry(
        storage, campaign_id, group_id, group_type, subfilters, start_id,
    )

    assert allow == expected_result


def test_stq_task_id():
    sending_id = uuid.uuid4()
    sending = models.api.BatchSendingFull(
        id=sending_id,
        campaign_id=11,
        group_id=22,
        entity_type='user',
        group_type='control',
        channel='push',
        channel_info=models.api.UserPushInfo.deserialize(
            {'channel_name': 'user_push'},
        ),
        state='NEW',
        use_policy=True,
        filter='filter',
        subfilters=[
            models.api.FilterObject.deserialize(
                {'column': 'efficiency', 'value': '0'},
            ),
        ],
        yt_table='yt_table',
        yt_test_table='yt_test_table',
        pg_table='pg_table',
        processing_chunk_size=10,
        created_at=dateutil.parser.parse('2021-07-08 12:05:00'),
        updated_at=None,
    )

    expected = (
        f'campaign_11_group_22_'
        f'sending_{sending_id}_start_control_efficiency_0'
    )
    stq_task_id = yt._yt_absorber_task_id(sending)
    assert stq_task_id == expected
