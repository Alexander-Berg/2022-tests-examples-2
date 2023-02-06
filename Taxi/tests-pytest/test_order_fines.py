import datetime as dt
import json

import pytest

from taxi.conf import settings
from taxi.core import arequests
from taxi.core import async
from taxi.internal import dbh
from taxi.internal import order_events

TVM_TICKET = 'test_tvm_ticket'
TVM_RULES = [
    {'src': 'stq', 'dst': 'order-fines'},
]


@pytest.mark.config(
    TVM_RULES=TVM_RULES,
    ORDER_FINES_COMPLETED_AMENDED_ENABLED=False,
)
@pytest.inline_callbacks
def test_no_calls_if_disabled(order_proc, fines_handler):
    result = yield order_events._get_fine_decision(order_proc)
    assert result == order_events.FineDecision(
        has_fine=False, fine_code=None, last_modified_at=dt.datetime.min,
    )
    assert fines_handler.times_called == 0


@pytest.mark.config(
    TVM_RULES=TVM_RULES,
    ORDER_FINES_COMPLETED_AMENDED_ENABLED=True,
    ORDER_FINES_ONLY_FOR_CARGO=True,
)
@pytest.inline_callbacks
def test_no_calls_if_non_cargo(fines_handler):
    order_proc = dbh.order_proc.Doc({'_id': 'some_order_id'})
    result = yield order_events._get_fine_decision(order_proc)
    assert result == order_events.FineDecision(
        has_fine=False, fine_code=None, last_modified_at=dt.datetime.min,
    )
    assert fines_handler.times_called == 0


@pytest.mark.parametrize('returned_decision, expected_result', [
    (
        {'decision': {'has_fine': False}},
        order_events.FineDecision(
            has_fine=False,
            fine_code=None,
            last_modified_at=dt.datetime.min,
        ),
    ),
    (
        {
            'decision': {
                'has_fine': True,
                'fine_code': 'some_fine_code',
                'last_modified_at': '2021-04-07T20:22:23.000000+00:00',
            },
        },
        order_events.FineDecision(
            has_fine=True,
            fine_code='some_fine_code',
            last_modified_at=dt.datetime(2021, 4, 7, 20, 22, 23),
        ),
    ),
])
@pytest.mark.config(
    TVM_RULES=TVM_RULES,
    ORDER_FINES_COMPLETED_AMENDED_ENABLED=True,
)
@pytest.inline_callbacks
def test_return_expected(
        order_proc,
        fines_handler,
        decision,
        returned_decision,
        expected_result,
):
    decision.set(returned_decision)
    result = yield order_events._get_fine_decision(order_proc)
    assert fines_handler.times_called == 1
    assert result == expected_result


@pytest.mark.config(
    TVM_RULES=TVM_RULES,
    ORDER_FINES_COMPLETED_AMENDED_ENABLED=True,
)
@pytest.inline_callbacks
def test_request_params(order_proc, fines_handler):
    yield order_events._get_fine_decision(order_proc)
    assert fines_handler.times_called == 1
    request = fines_handler.next_call()
    assert request['method'] == arequests.METHOD_GET
    url = '%s/%s' % (settings.ORDER_FINES_SERVICE_HOST, 'internal/order/fine')
    assert request['url'] == url


@pytest.fixture(autouse=True)
def fines_handler(areq_request, handler_class, decision):
    handler = handler_class()

    @areq_request
    def response(method, url, **kwargs):
        handler.add_request(method=method, url=url, **kwargs)
        code = 200
        body = json.dumps(decision.get())
        headers = None
        return (code, body, headers)

    return handler


@pytest.fixture(autouse=True)
def tvm_get_ticket(patch, handler_class):
    handler = handler_class()

    @patch('taxi.external.tvm.get_ticket')
    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        yield
        handler.add_request(
            src_service_name=src_service_name,
            dst_service_name=dst_service_name,
            log_extra=log_extra,
        )
        async.return_value(TVM_TICKET)

    return handler


@pytest.fixture
def decision():
    class Decision:
        def __init__(self):
            self._value = {'decision': {'has_fine': False}}

        def get(self):
            return self._value

        def set(self, value):
            self._value = value

    return Decision()


@pytest.fixture
def order_proc():
    doc = {
        '_id': 'some_order_id',
        'order': {
            'request': {
                'cargo_ref_id': 'some_cargo_ref_id',
            },
        },
    }
    return dbh.order_proc.Doc(doc)


@pytest.fixture
def handler_class():
    class Handler:
        def __init__(self):
            self._requests = []

        def add_request(self, **kwargs):
            self._requests.append(kwargs)

        def next_call(self):
            return self._requests.pop(0)

        @property
        def times_called(self):
            return len(self._requests)

    return Handler
