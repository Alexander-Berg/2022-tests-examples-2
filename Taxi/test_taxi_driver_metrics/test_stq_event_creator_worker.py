import datetime

from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.stq.workers import EventCreatorWorker

UDID_1 = '5b05621ee6c22ea2654849c9'
TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)
TST_REASON = 'tst_reason'


async def test_whole_routine(
        stq3_context, dms_mockserver, stq, event_provider,
):
    with stq.flushing():
        worker = EventCreatorWorker(
            context=stq3_context, queue=stq3_context.stq.driver_metrics_client,
        )
        await worker.add_driver_created_event(
            stq3_context,
            UDID_1,
            TIMESTAMP,
            reason=TST_REASON,
            extra_data={'some_data': 'some_value'},
            dbid_uuid='some_dbid_uuid',
        )

        call = stq.driver_metrics_client.next_call()
        assert call
        await worker.do_work(call['args'][0], task_id=call['id'])
        res = await event_provider.fetch_unprocessed_events(
            params={'limit': 1, 'worker_id': 0, 'workers_count': 1},
        )
        assert res
        assert res[0].entity_id == UDID_1
        assert res[0].events
        event = res[0].events[0]
        assert event.timestamp == TIMESTAMP
        assert getattr(event, 'dbid_uuid') == 'some_dbid_uuid'
        assert event.event_type == Events.EventType.DRIVER_METRICS_EVENT
        assert event.extra_data == {'some_data': 'some_value'}
