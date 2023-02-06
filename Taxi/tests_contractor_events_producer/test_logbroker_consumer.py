import pytest

from tests_contractor_events_producer import status_events


@pytest.mark.now('2021-11-14T23:59:59.0+00:00')
# to start with zero metrics
@pytest.mark.uservice_oneshot
async def test_basic_read(
        taxi_contractor_events_producer,
        taxi_contractor_events_producer_monitor,
        testpoint,
):
    expected_metrics = {
        'process_deadline_errors': 0,
        'process_errors': 0,
        'total_events': 0,
        'total_events_affects_online_status': 0,
        'total_messages': 0,
        'total_skipped_parse_errored_events': 0,
    }

    logbroker_testpoint = status_events.make_logbroker_testpoint(testpoint)

    await taxi_contractor_events_producer.tests_control(reset_metrics=True)

    await status_events.post_event(
        taxi_contractor_events_producer,
        [
            status_events.make_raw_event(
                'dbid',
                'uuid',
                status_events.OFFLINE_STATUS,
                '2020-11-14T23:59:59.0+00:00',
            ),
            status_events.make_raw_event(
                'dbid',
                'uuid',
                status_events.ONLINE_STATUS,
                '2020-11-15T23:59:59.0+00:00',
            ),
        ],
    )

    await logbroker_testpoint.wait_call()

    metrics = await taxi_contractor_events_producer_monitor.get_metric(
        'status-events-consumer',
    )

    expected_metrics['total_events'] = 2
    expected_metrics['total_messages'] = 1
    expected_metrics['total_events_affects_online_status'] = 1

    assert metrics == expected_metrics

    await status_events.post_event(
        taxi_contractor_events_producer, ['bad_payload'],
    )

    await logbroker_testpoint.wait_call()

    metrics = await taxi_contractor_events_producer_monitor.get_metric(
        'status-events-consumer',
    )

    expected_metrics['total_messages'] = 2
    expected_metrics['total_skipped_parse_errored_events'] = 1

    assert metrics == expected_metrics
