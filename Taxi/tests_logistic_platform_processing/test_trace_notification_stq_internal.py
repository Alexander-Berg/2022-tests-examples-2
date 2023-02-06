import pytest


@pytest.mark.config(
    LOGISTIC_PLATFORM_PROCESSING_STQ_NOTIFICATION_SOURCES={
        'beru_sources': ['trace_notification_process_beru'],
        'beru_international_sources': [],
        'internal_sources': ['trace_notification_process_internal'],
    },
)
async def test_trace_notification_stq_task(mockserver, stq_runner):
    @mockserver.json_handler(
        '/cargo-misc/internal/pickup-points/v1/change-shipment-status-notify',
    )
    def mock_stq_reschedule(request):
        return {'message': 'OK'}

    await stq_runner.logistic_platform_processing_trace_notification.call(
        task_id='id',
        kwargs={
            'platform_instance': 'platform',
            'claim_request_id': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
            'external_order_id': '00000000',
            'notification_source': 'trace_notification_process_internal',
        },
        expect_fail=False,
    )
    await stq_runner.logistic_platform_processing_trace_notification.call(
        task_id='id',
        kwargs={
            'platform_instance': 'platform',
            'claim_request_id': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
            'external_order_id': '00000000',
            'notification_source': 'something_dumb',
        },
        expect_fail=False,
    )

    assert mock_stq_reschedule.has_calls == 1
