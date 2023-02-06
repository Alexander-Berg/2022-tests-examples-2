import datetime

from crm_hub.generated.service.swagger import models
from crm_hub.logic import cleanup
from crm_hub.logic import state
from crm_hub.repositories import batch_sending


EXTRA_DATA = models.api.ExtraData(
    column='cities',
    values=[
        models.api.ExtraDataList(
            key='moscow',
            values=[
                models.api.ExtraDataField(key='ext1', value='moscow_value1'),
                models.api.ExtraDataField(key='ext2', value='moscow_value2'),
            ],
        ),
        models.api.ExtraDataList(
            key='minsk',
            values=[
                models.api.ExtraDataField(key='ext1', value='minsk_value1'),
                models.api.ExtraDataField(key='ext2', value='minsk_value1'),
            ],
        ),
        models.api.ExtraDataList(
            key='kiev',
            values=[
                models.api.ExtraDataField(key='ext1', value='kiev_value1'),
                models.api.ExtraDataField(key='ext2', value='kiev_value2'),
            ],
        ),
    ],
)


async def test_repo(web_context):

    finished_at = datetime.datetime(2021, 2, 3, 9, 0, 0, 0)

    channel_info = models.api.DriverSmsInfo(
        channel_name='driver_sms',
        content='content',
        intent='intent',
        sender='sender',
    )

    sending_stats = models.api.SendingResult(
        planned=1000,
        sent=700,
        failed=200,
        skipped=100,
        finished_at=finished_at,
    )

    sending = models.api.BatchSending(
        campaign_id=1,
        group_id=2,
        filter='filter',
        yt_table='yt_table',
        yt_test_table='yt_table_verification',
        pg_table='pg_table',
        entity_type='driver',
        group_type='testing',
        channel='sms',
        channel_info=channel_info,
        processing_chunk_size=100,
        use_policy=True,
        state=state.NEW,
        extra_data=EXTRA_DATA,
        extra_data_path='//home/taxi-crm/cmp_extra_data',
        sending_stats=sending_stats,
        start_id=0,
        replication_state='NEW',
        cleanup_state=cleanup.CleanupState.NEW.as_sql(),
    )

    storage = batch_sending.BatchSendingStorage(web_context)
    sending_full = await storage.create(sending)

    finished_at += datetime.timedelta(days=2)

    sending_full.yt_table = 'new_yt_table'
    sending_full.pg_table = 'new_pg_table'
    sending_full.start_id = 5
    sending_full.sending_stats.finished_at = finished_at
    sending_full.replication_state = 'PROCESSING'

    await storage.update(sending_full)

    fetched_sending = await storage.fetch(sending_full.id)

    assert fetched_sending.yt_table == 'new_yt_table'
    assert fetched_sending.pg_table == 'new_pg_table'
    assert fetched_sending.start_id == 5
    assert fetched_sending.sending_stats.finished_at == finished_at
    assert fetched_sending.replication_state == 'PROCESSING'
