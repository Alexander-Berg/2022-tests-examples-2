import pytest

from taxi.core import async
from taxi.external import tvm
from taxi.internal.notifications import executor
from taxi.internal.notifications import _wns_client
from taxi.internal import dbh


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'group_key,exception,expected_status,expected_exception',
    [
        (
            'mykey',
            _wns_client.WNSRequestError({'error': 1, 'http_status_code': 402}),
            dbh.notifications_queue.STATUS_CANCELED,
            None
        ),
        (
            'mykey',
            _wns_client.WNSRequestError({'error': 1, 'http_status_code': 429}),
            dbh.notifications_queue.STATUS_NEW,
            _wns_client.WNSRequestError
        ),
        (
            'mykey',
            Exception,
            dbh.notifications_queue.STATUS_NEW,
            Exception
        ),
        (
            'mykey',
            None,
            dbh.notifications_queue.STATUS_SENT,
            None
        ),
        (
            'not_new',
            Exception,
            dbh.notifications_queue.STATUS_SENT,
            None
        )
    ]
)
@pytest.inline_callbacks
def test_run_task(patch, group_key, exception, expected_status, expected_exception):
    @patch('taxi.internal.notifications._wns_client.WNSClient.process')
    def process(self, url, wns_type='toast', **wns_params):
        if exception:
            raise exception

    tasks = yield dbh.notifications_queue.Doc.retrieve(group_key, 5)
    if group_key == 'mykey':
        assert len(tasks) == 2
        for task in tasks:
            assert task.status == dbh.notifications_queue.STATUS_NEW
    else:
        assert len(tasks) == 0

    if expected_exception:
        with pytest.raises(expected_exception):
            yield executor.run_task(group_key, None)
    else:
        yield executor.run_task(group_key, None)

    tasks = yield dbh.notifications_queue.Doc.retrieve(
        group_key, 5, status=expected_status
    )
    assert len(tasks) > 0
    for task in tasks:
        assert task.status == expected_status


@pytest.mark.filldb()
@pytest.mark.parametrize('bass_return_code,expected_status', [
    (200, dbh.notifications_queue.STATUS_SENT),
    (400, dbh.notifications_queue.STATUS_CANCELED),
    (429, dbh.notifications_queue.STATUS_CANCELED),
    (504, dbh.notifications_queue.STATUS_CANCELED)
])
@pytest.mark.config(ALICE_NOTIFICATIONS_REQUEST_TIMEOUT=500000)  # notreal only for test
@pytest.inline_callbacks
def test_alice_simple(patch, areq_request,
                       bass_return_code, expected_status):

    group_key = '12e05188-354c-4772-a351-e6475f2443a7'
    tvm_ticket = 'tvm ticket'

    @patch('taxi.external.tvm.get_auth_headers')
    @async.inline_callbacks
    def get_auth_headers(src_service, dst_service, log_extra):
        assert src_service == 'stq'
        assert dst_service == 'alice'

        yield
        async.return_value({tvm.TVM_TICKET_HEADER: tvm_ticket})

    @areq_request
    def mock_request(method, url, *args, **kwargs):

        assert method == 'POST'
        assert url == (
            'http://bass-prod.yandex.ru/push'
        )
        assert kwargs['headers'] == {'X-Ya-Service-Ticket': tvm_ticket}
        assert kwargs['timeout'] == 500000
        assert kwargs['exponential_backoff'] is True
        assert kwargs['retry_on_fails'] is False
        assert kwargs['json'] == {
            'service_data': {
                'order_id': group_key,
                'tz': 'Europe/Moscow',
                'due': 'time'
            },
            'callback_data': 'alice callback',
            'event': 'on_search_failed',
            'service': 'taxi'
        }

        return areq_request.response(bass_return_code)

    tasks = yield dbh.notifications_queue.Doc.retrieve(group_key, 5)
    assert len(tasks) == 1
    for task in tasks:
        assert task == dbh.notifications_queue.Doc({
            '_id': 'alice_push',
            'status': dbh.notifications_queue.STATUS_NEW,
            'index': -1,
            'user_id': 'user_id',
            'payload': {
                'service_data': {
                    'order_id': '12e05188-354c-4772-a351-e6475f2443a7',
                    'tz': 'Europe/Moscow', 'due': 'time'
                },
                'callback_data': 'alice callback',
                'id': '123',
                'event': 'on_search_failed'
            },
            'application': 'alice',
            'key': '12e05188-354c-4772-a351-e6475f2443a7:-1:alice.on_search_failed',
            'destination_type': 'alice',
            'group_key': '12e05188-354c-4772-a351-e6475f2443a7',
            'event': 'alice.on_search_failed'
        })

    yield executor.run_task(group_key, None)
    len(get_auth_headers.calls) == 1
    len(mock_request.calls) == 1
    tasks = yield dbh.notifications_queue.Doc.retrieve(
        group_key, 5, status=expected_status
    )
    assert len(tasks) > 0
    for task in tasks:
        assert task.status == expected_status


@pytest.mark.filldb()
@pytest.mark.parametrize('use_idempotency_token', [False, True])
@pytest.inline_callbacks
def test_send_push_via_ucommunications(patch, areq_request,
                                       use_idempotency_token):
    group_key = 'push_send_test'
    tvm_ticket = 'tvm ticket'

    @patch('taxi.config.COMMUNICATIONS_PY2_PUSH_IDEMPOTENCY_SEND.get')
    @async.inline_callbacks
    def _get_py2_push_idempotency_send():
        yield
        async.return_value(use_idempotency_token)

    @patch('taxi.external.tvm.get_auth_headers')
    @async.inline_callbacks
    def get_auth_headers(src_service, dst_service, log_extra):
        assert src_service == 'stq'
        assert dst_service == 'ucommunications'
        yield
        async.return_value({tvm.TVM_TICKET_HEADER: tvm_ticket})

    @areq_request
    def mock_request(method, url, *args, **kwargs):
        assert method == 'POST'
        assert url == (
            'http://ucommunications.taxi.dev.yandex.net/user/notification/push'
        )
        expected_headers = {'X-Ya-Service-Ticket': tvm_ticket}
        if use_idempotency_token:
            expected_headers['X-Idempotency-Token'] = 'some_unique_key'
        assert kwargs['headers'] == expected_headers
        assert kwargs['json'] == {
            'user': u'user_id',
            'data': {
                'payload': {
                    'extra': {
                        'order_id': 'order_id',
                    },
                    'id': '2830227ea6944f95b894d27df5f9ace4',
                    'title': 'Some push text for user',
                    'notification_title': 'Some push text for user',
                },
                'repack': {
                    'apns': {
                        'collapse-id': 'order_id',
                        'aps': {
                            'interruption-level': 'time-sensitive',
                            'alert': u'Some push text for user',
                            'content-available': 1,
                            'sound': u'default',
                            'thread-id': 'taxi_order',
                        },
                        'repack_payload': [u'id', u'extra'],
                    },
                    'fcm': {
                        'repack_payload': [u'id', u'extra', 'title'],
                    },
                    'hms': {
                        'repack_payload': [
                            u'id',
                            u'extra',
                            'notification_title',
                        ],
                    },
                }
            },
            'intent': 'taxi_apns_on_transporting',
        }

        return areq_request.response(200, body='{}')

    yield executor.run_task(group_key, None)
    len(get_auth_headers.calls) == 1
    len(mock_request.calls) == 1
    tasks = yield dbh.notifications_queue.Doc.retrieve(
        group_key, 5, status=dbh.notifications_queue.STATUS_SENT
    )
    assert len(tasks) == 1
    for task in tasks:
        assert task.status == dbh.notifications_queue.STATUS_SENT
