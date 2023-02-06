import dateutil.parser
import pytest

from taxi_tests import utils


xiva_return_code = 200


# Xiva must be called twice: first time immediatelly from /push (return 500),
# second time from notifications worker on send retry (return 200)
@pytest.fixture
def mock_xiva(mockserver, scope='session'):
    class BadXiva:
        @mockserver.handler('/xiva/send')
        def send(request):
            return mockserver.make_response(status=xiva_return_code)

    return BadXiva()


message = {
    'data': {'id': '1234567890', 'name': 'Anon', 'message': 'New message'},
    'collapse_key': 'Alert: 1234567890',
}


@pytest.mark.now('2100-01-01T00:00:00Z')
@pytest.mark.config(
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'queue'], XIVA_RETRIES=1,
)
def test_fallback_communications(
        taxi_communications, db, mock_xiva, testpoint,
):
    @testpoint('notification_worker_finished')
    def notification_worker_finished(stats):
        pass

    n_messages = 100

    global xiva_return_code
    xiva_return_code = 500
    for i in range(n_messages):
        response = taxi_communications.post(
            'driver/notification/push?dbid=1488&uuid=driver&ttl=60'
            '&action=MessageNew&code=100',
            json=message,
        )
        assert response.status_code == 200

    # Xiva will be called by handler n_messages times and return 500 on each
    # call. So all messages will be queued.
    assert mock_xiva.send.times_called == n_messages
    assert db.notifications_fallback_queue.count() == n_messages

    # Advance now() to +15s to allow worker run one more time.
    # Timeout must be greater than distlock timeout (2s) and
    # less than message ttl (60s), otherwise message will expire.
    xiva_return_code = 200
    mock_now = utils.to_utc(dateutil.parser.parse('2100-01-01T00:00:15Z'))
    taxi_communications.invalidate_caches(mock_now)

    taxi_communications.run_workers(['notifications-fallback'])
    call = notification_worker_finished.wait_call()
    assert call['stats'] == {
        'fetched': n_messages,
        'sent': n_messages,
        'expired': 0,
        'skipped': 0,
        'errors': 0,
    }

    # Xiva will be called by worker for each message and this time it
    # will return 200
    assert mock_xiva.send.times_called == n_messages * 2
    assert db.notifications_fallback_queue.count() == 0
