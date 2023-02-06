# pylint: disable=protected-access,unused-variable
import uuid

import dateutil
import pytest

from taxi.pg import exceptions
from taxi.stq import async_worker_ng

from crm_hub.generated.service.swagger import models
from crm_hub.stq import create_yt_absorber_v2


@pytest.mark.parametrize('group_type', ['control', 'verify'])
def test_stq_task_id(monkeypatch, group_type):
    sending_id = uuid.uuid4()
    sending = models.api.BatchSendingFull(
        id=sending_id,
        campaign_id=11,
        group_id=22,
        entity_type='user',
        group_type=group_type,
        channel='push',
        channel_info=models.api.UserPushInfo.deserialize(
            {'channel_name': 'user_push'},
        ),
        start_id=33,
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

    class FakeUuid:
        hex = 'UUID'

    monkeypatch.setattr(uuid, 'uuid4', FakeUuid)

    expected = f'sender_campaign_11_group_22_sending_{sending_id}_start_33'
    if group_type == 'verify':
        expected += '_verify_UUID'
    else:
        expected += '_control'
    expected += '_efficiency_0'

    stq_task_id = create_yt_absorber_v2._bulk_sender_task_id(sending)
    assert stq_task_id == expected


@pytest.mark.pgsql('crm_hub', files=['init.sql'])
async def test_no_available_host(stq3_context, patch):
    @patch('taxi.pg.pool.Pool.acquire')
    def acquire(*args, **kwargs):
        raise exceptions.NoAvailableHost('no suitable host to create pool')

    task_info = async_worker_ng.TaskInfo(
        id='id', exec_tries=1, reschedule_counter=1, queue='',
    )
    with pytest.raises(exceptions.NoAvailableHost):
        await create_yt_absorber_v2.task(
            context=stq3_context,
            task_info=task_info,
            sending_id='00000000000000000000000000000001',
            verify=False,
            control=False,
            com_politic=False,
            report_extra={},
            dependency_id='',
            global_control_enabled=False,
        )
