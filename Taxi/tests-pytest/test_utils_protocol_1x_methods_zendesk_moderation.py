import json
import mocks
import pytest

from taxi.core import async, db
from taxi.external import taxi_protocol
from taxi.internal import archive
from taxi.internal import dbh
from utils.protocol_1x.methods import zendesk_moderation

from cardstorage_mock import mock_cardstorage


@async.inline_callbacks
def _get_response(request):
    method = zendesk_moderation.Method()
    response = yield method.POST(request)
    async.return_value(response)


class FakePaymentTech(object):
    def __init__(self, type):
        self.type = type


class FakeOrder(object):
    def __init__(self, payment_tech, pk):
        self.payment_tech = payment_tech
        self.pk = pk


@pytest.mark.parametrize('content,expected_response,expected_response_code', [
    (
            {},
            {'error': "Missing 'order_id' field"},
            400
    ),
    (
            {
                'order_id': 1,
                'reason': 'reason',
                'reason_code': 'reason_code',
                'login': 'login',
                'comment': 'comment',
            },
            {'error': "Field 'order_id' is of incorrect type"},
            400
    ),
])
@pytest.inline_callbacks
def test_incorrect_content(content, expected_response, expected_response_code):
    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert response == expected_response
    assert request.response_code == expected_response_code


@pytest.inline_callbacks
def test_taxi_protocol_not_found(patch):
    @patch('taxi.external.taxi_protocol.get_order_info')
    @async.inline_callbacks
    def get_order_info(*args, **kwargs):
        yield
        raise taxi_protocol.NotFoundError

    @patch('taxi.internal.archive.get_order_by_exact_alias')
    @async.inline_callbacks
    def get_order_by_exact_alias(*args, **kwargs):
        yield

    content = {
        'order_id': 'order_id',
        'reason': 'reason',
        'reason_code': 'reason_code',
        'login': 'login',
        'comment': 'comment',
    }
    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert response == {'error': 'get_order_info not found'}
    assert request.response_code == 404


@pytest.inline_callbacks
def test_archive_not_found(patch):
    @patch('taxi.external.taxi_protocol.get_order_info')
    @async.inline_callbacks
    def get_order_info(*args, **kwargs):
        yield
        async.return_value({'park_id': 'park_id'})

    @patch('taxi.internal.archive.get_order_by_exact_alias')
    @async.inline_callbacks
    def get_order_by_exact_alias(*args, **kwargs):
        yield
        raise archive.NotFound

    content = {
        'order_id': 'order_id',
        'reason': 'reason',
        'reason_code': 'reason_code',
        'login': 'login',
        'comment': 'comment',
    }
    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert response == {'error': 'order not found'}
    assert request.response_code == 404


@pytest.inline_callbacks
def test_park_not_found(patch):
    @patch('taxi.external.taxi_protocol.get_order_info')
    @async.inline_callbacks
    def get_order_info(*args, **kwargs):
        yield
        async.return_value({'park_id': 'park_id'})

    @patch('taxi.internal.archive.get_order_by_exact_alias')
    @async.inline_callbacks
    def get_order_by_exact_alias(*args, **kwargs):
        yield

    @patch('taxi.internal.dbh.orders.Doc')
    class FakeDoc(object):
        updated = 'update'
        payment_tech = 'payment_tech'

        def __call__(*args, **kwargs):
            return FakeOrder(FakePaymentTech('payment_tech'),
                             '540_1')

        def update_update_sum_to_pay(*args, **kwargs):
            return

    content = {
        'order_id': 'order_id',
        'reason': 'reason',
        'reason_code': 'reason_code',
        'login': 'login',
        'comment': 'comment',
    }
    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert response == {'error': 'park not found'}
    assert request.response_code == 404


@pytest.mark.parametrize(
    'order_id,reason_code,payment_tech,expected_response,'
    'expected_response_code',
    [
        (
            "540_1",
            "reason_code",
            "payment_tech",
            {},
            None,
        ),
        (
            "540_1",
            zendesk_moderation.PAID_BY_CASH_REASON,
            dbh.orders.PAYMENT_TYPE_CARD,
            {},
            None,
        ),
        (
            "540_1",
            zendesk_moderation.PAID_BY_CASH_REASON,
            dbh.orders.PAYMENT_TYPE_CARD,
            {},
            None,
        ),
        (
            "540_2",
            zendesk_moderation.PAID_BY_CASH_REASON,
            dbh.orders.PAYMENT_TYPE_CARD,
            {'error': 'order not found'},
            404,
        ),
    ],
)
@pytest.mark.filldb()
@pytest.inline_callbacks
def test_refund(order_id, reason_code, payment_tech, expected_response,
                expected_response_code, patch):

    @patch('taxi.external.taxi_protocol.get_order_info')
    @async.inline_callbacks
    def get_order_info(*args, **kwargs):
        yield
        async.return_value({'park_id': 'park_id'})

    @patch('taxi.internal.archive.get_order_by_exact_alias')
    @async.inline_callbacks
    def get_order_by_exact_alias(*args, **kwargs):
        query = {dbh.orders.Doc.performer.taxi_alias.id: order_id}
        doc = yield db.secondary.orders.find_one(query)
        if doc is None:
            raise archive.NotFound
        async.return_value(doc)

    @patch('taxi.internal.dbh.orders.Doc.update_update_sum_to_pay')
    def update_update_sum_to_pay(*args, **kwargs):
        return

    @patch('taxi.internal.dbh._helpers.Doc.find_one_by_id')
    def find_one_by_id(*args, **kwargs):
        yield

    @patch('taxi.internal.dbh.order_proc.Doc.enqueue_on_moved_to_cash')
    def enqueue_on_moved_to_cash(*args, **kwargs):
        yield

    mock_cardstorage(patch)

    content = {
        'order_id': order_id,
        'reason': 'reason',
        'reason_code': reason_code,
        'login': 'login',
        'comment': 'comment',
    }
    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert response == expected_response
    assert request.response_code == expected_response_code
