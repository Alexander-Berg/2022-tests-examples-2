import datetime
import socket

import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.external import billing


@pytest.mark.parametrize(
    'input,output',
    [
        ('EUR', 'EUR'),
        ('USD', 'USD'),
        ('RUR', 'RUB'),
        ('RUB', 'RUB'),
    ]
)
@pytest.mark.filldb(_fill=False)
def test_normalize_currency(input, output):
    result = billing.normalize_currency(input)
    assert result == output


@pytest.mark.now('2017-09-12 10:00:00.00+03')
@pytest.mark.parametrize('events_to_statistics_enabled', [False, True])
@pytest.inline_callbacks
def test_store_billing_stats(patch, events_to_statistics_enabled):
    yield config.BACKEND_PY2_BILLING_EVENTS_TO_STATISTICS_ENABLED.save(
        events_to_statistics_enabled,
    )

    store_metrics_calls = []

    @patch('taxi.external.statistics_agent.store_metrics')
    @async.inline_callbacks
    def store_metrics(request, log_extra=None):
        store_metrics_calls.append(request)
        yield
        async.return_value({})

    yield billing._store_billing_stats('card', 'UpdateBasket', 'success')

    docs = yield db.event_stats.find().run()
    assert len(docs) == 1

    doc = docs[0]
    del doc['_id']
    assert doc == {
        'created': datetime.datetime(2017, 9, 12, 7, 0),
        'detailed': {
            'card': {
                'UpdateBasket': {
                    'success': 1
                }
            }
        },
        'name': 'billing_call_simple',
        'success': 1
    }

    if events_to_statistics_enabled:
        assert len(store_metrics_calls) == 1
        assert store_metrics_calls[0] == {
            'metrics': [
                {
                    'name': (
                        'billing_call_simple.detailed.'
                        'card.UpdateBasket.success'
                    ),
                    'value': 1,
                },
                {
                    'name': 'billing_call_simple.total.success',
                    'value': 1,
                },
            ],
        }


@pytest.mark.parametrize(
    'response,expected_value',
    [
        ({'verification_id': 'foobar'}, ('in_progress', 'foobar')),
        ({'status': 'error'}, ('error', None)),
    ],
)
@pytest.inline_callbacks
def test_start_check_card(patch, response, expected_value):

    @patch('taxi.external.billing._call_simple')
    def _call_simple(*args, **kwargs):
        assert not args
        assert kwargs['method'] == 'CheckCard'
        assert kwargs['timeout'] == 120
        params = kwargs['params']
        assert params == {
            'async_verification': '1',
            'card_id': 'x-1234',
            'currency': 'RUB',
            'region_id': 225,
            'uid': '12345',
            'user_ip': '127.0.0.1',
        }
        return response

    actual_value = yield billing.start_check_card(
        yandex_uid='12345',
        billing_card_id='x-1234',
        user_ip='127.0.0.1',
        region_id=225,
        currency='RUB',
        timeout=120,
        service='card',
        uber_uid=None,
        log_extra=None,
    )
    assert actual_value == expected_value


@pytest.mark.parametrize(
    'response,expected_value',
    [
        ({'status': 'success'}, (True, True)),
        ({'status': 'error'}, (True, False)),
        ({'status': 'in_progress'}, (False, False)),
    ],
)
@pytest.inline_callbacks
def test_fetch_check_card_status(patch, response, expected_value):

    @patch('taxi.external.billing._call_simple')
    def _call_simple(*args, **kwargs):
        assert not args
        assert kwargs['method'] == 'CheckCardVerificationStatus'
        assert kwargs['timeout'] == 120
        params = kwargs['params']
        assert params == {'verification_id': 'verification-id'}
        return response

    actual_value = yield billing.fetch_check_card_status(
        verification_id='verification-id',
        timeout=120,
        service='card',
        log_extra=None,
    )
    assert actual_value == expected_value


@pytest.yield_fixture
def listener():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    sock.listen(1)
    yield sock.getsockname()
    sock.close()


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.mocklevel(None)
def test_call_xmlrpc_blocking_timeout(listener):
    uri = 'http://{}:{}'.format(*listener)

    with pytest.raises(billing.TimeoutError):
        billing._call_xmlrpc_blocking(uri, 'dummy', 0.001)


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.mocklevel(None)
def test_call_xmlrpc_blocking_etimedout(patch):

    @patch('taxi.external.billing.TimeoutServerProxy')
    def timeout_server_proxy(*args, **kwargs):
        class TimeoutServerProxy:
            def __init__(self, uri, **kwargs):
                pass

            @staticmethod
            def dummy(*args):
                raise socket.error(socket.errno.ETIMEDOUT)
        return TimeoutServerProxy

    with pytest.raises(billing.TimeoutError):
        billing._call_xmlrpc_blocking('localhost', 'dummy', 1)


@pytest.mark.filldb(_fill=False)
@pytest.mark.mocklevel(None)
@pytest.mark.asyncenv('async')
@pytest.mark.config(ADMIN_BILLING_TIMEOUTS={
    "is_enabled": False,
    "billing": 20,
    "balance": 30
})
@pytest.inline_callbacks
def test_get_timeout_config_disabled():
    timeout1 = yield billing._get_timeout('billing')
    assert timeout1 == 15

    timeout2 = yield billing._get_timeout('balance')
    assert timeout2 == 15


@pytest.mark.filldb(_fill=False)
@pytest.mark.mocklevel(None)
@pytest.mark.asyncenv('async')
@pytest.mark.config(ADMIN_BILLING_TIMEOUTS={
    "is_enabled": True,
    "billing": 20,
    "balance": 30
})
@pytest.inline_callbacks
def test_get_timeout_config_enabled():
    timeout1 = yield billing._get_timeout('billing')
    assert timeout1 == 20

    timeout2 = yield billing._get_timeout('balance')
    assert timeout2 == 30
