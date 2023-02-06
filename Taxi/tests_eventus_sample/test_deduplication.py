import asyncio
import json
import time
import typing as tp

import pytest

_OEP_PIPELINES = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'atlas-drivers'},
        'root': {'sink_name': 'rms_sink'},
        'name': 'pipeline-name',
    },
]


def _generate_message(
        order_events_gen, make_order_event, index: int,
) -> tp.Dict[str, tp.Any]:
    return {
        'consumer': 'atlas-drivers',
        'data': order_events_gen(
            make_order_event(
                event_key='handle_transporting',
                user_id='user-1',
                db_id='dbid1',
                driver_uuid='driveruuid1',
                status_updated=1571253356.368,
                user_phone_id='custom-user-phone-id',
                destinations_geopoint=[[37.69411325, 55.78685382]],
                topic='smth',
            ),
        ).cast('json'),
        'topic': 'smth',
        'cookie': f'cookie_for_rms_sink_{index}',
        'offset': index // 2,
    }


@pytest.mark.skip('deduplication is disabled for now')
async def test_deduplication(
        taxi_eventus_sample,
        taxi_rider_metrics_storage_mock,
        taxi_rider_metrics_storage_ctx,
        testpoint,
        make_order_event,
        order_events_gen,
        taxi_eventus_orchestrator_mock,
        taxi_config,
        taxi_eventus_sample_monitor,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('eventus-statistics::get_source_stats')
    def get_source_stats(data):
        pass

    await taxi_eventus_sample.tests_control(reset_metrics=True)

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, _OEP_PIPELINES,
    )
    await taxi_eventus_sample.run_task('invalidate-seq_num')

    for i in range(10):
        response = await taxi_eventus_sample.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                _generate_message(order_events_gen, make_order_event, i),
            ),
        )
        assert response.status_code == 200

    message_from_another_partition = _generate_message(
        order_events_gen, make_order_event, 0,
    )
    message_from_another_partition.update(
        partition=1, cookie=f'cookie_for_rms_sink_{10}',
    )
    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(message_from_another_partition),
    )
    assert response.status_code == 200

    # logbroker will get all 11 commits
    for i in range(11):
        assert (await commit.wait_call())[
            'data'
        ] == 'cookie_for_rms_sink_' + str(i)

    # but rider metrics storage will get only messages without duplicates
    deadline = time.time() + 1.0
    while (
            time.time() < deadline
            and taxi_rider_metrics_storage_mock.times_called < 6
    ):
        await asyncio.sleep(0.1)

    assert taxi_rider_metrics_storage_mock.times_called == 6

    _ = await taxi_eventus_sample_monitor.get_metrics()
    source_stats = (await get_source_stats.wait_call())['data']
    assert source_stats['atlas-drivers']['message_duplicates'] == 5
