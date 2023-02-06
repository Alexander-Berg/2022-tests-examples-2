import dateutil.parser
import pytest

from taxi_tests import utils


message = {
    'dbid': '1488',
    'uuid': 'driver',
    'action': 'MessageNew',
    'code': 100,
    'data': {'id': '1234567890', 'name': 'Anon', 'message': 'New message'},
    'collapse_key': 'Alert: 1234567890',
}


@pytest.mark.now('2100-01-02T00:00:00Z')
@pytest.mark.config(
    XIVA_RETRIES=1,
    DEVICE_NOTIFY_RETRIES=1,
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'device-notify'],
    COMMUNICATIONS_NOTIFICATION_FALLBACK={
        'enabled': True,
        'min_requests_count': 10,
        'max_error_percent': 40,
        'recheck_period_secs': 0,  # Force check client stats on every request
        'statistics_period_secs': 30,
        'disable_period_secs': 60,
    },
)
@pytest.mark.experiments3(
    name='push_to_device_notify',
    consumers=['communications'],
    match={
        'consumers': ['communications'],
        'predicate': {'type': 'true'},
        'enabled': True,
        'driver_id': '1488',
        'park_db_id': 'driver',
        'applications': [{'name': 'taximeter', 'version_range': {}}],
    },
    clauses=[],
    default_value={},
)
def test_autofallback_on_send(taxi_communications, db, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva_send(request):
        return mockserver.make_response('', 502)

    @mockserver.handler('/device-notify/v1/send')
    def mock_device_notify(request):
        return mockserver.make_response('', 200)

    # Test starts here
    for i in range(20):
        response = taxi_communications.post(
            'driver/notification/push', json=message,
        )
        assert response.status_code == 200

    # Xiva must be called 10 times of 20:
    #  * It will fail all 10 requests so error rate will be >40%
    #    (max_error_percent)
    #  * At 10'th call autofallback will be enabled (min_requests_count)
    assert mock_xiva_send.times_called == 10
    assert mock_device_notify.times_called == 20

    # Advance time to +120 sec. Xiva client must be unblocked (due to
    # disable_period_secs) and previous errors must be vanished (due to
    # statistics_period_secs)
    mock_now = utils.to_utc(dateutil.parser.parse('2100-01-02T00:02:00Z'))
    taxi_communications.tests_control(now=mock_now, invalidate_caches=False)

    for i in range(20):
        response = taxi_communications.post(
            'driver/notification/push', json=message,
        )
        assert response.status_code == 200
    assert mock_xiva_send.times_called == 20
    assert mock_device_notify.times_called == 40
