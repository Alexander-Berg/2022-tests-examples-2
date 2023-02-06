# pylint: disable=redefined-outer-name
import datetime
import enum

import bson
import pytest

from . import mocking_base


class OrderIdRequestType(enum.Enum):
    exact_id = 'exact_id'
    alias_id = 'alias_id'
    client_id = 'client_id'
    any_id = 'any_id'


class OrderCoreContext(mocking_base.BasicMock):
    def __init__(self, load_json):
        super().__init__()
        self.expected_projection = None
        self.expected_order_id = None
        self.expected_id_type = None
        self.require_latest = None
        self.times_called = 0
        self.load_json = load_json

    def find_one(self, order_id):
        for order in self.load_json('order_core_response.json'):
            if order_id == order['_id']:
                return order
        return {}

    def set_expected_projection(self, expected_proj):
        self.expected_projection = expected_proj

    def set_expected_key(self, order_id, id_type=None, require_latest=None):
        self.expected_order_id = order_id
        self.expected_id_type = id_type.value
        self.require_latest = require_latest

    def order_proc_get_fields(self, request, mongodb, mockserver):
        projection = bson.BSON.decode(request.get_data())
        if self.expected_projection:
            assert projection == self.expected_projection
        if self.expected_order_id:
            assert request.query['order_id'] == self.expected_order_id
        if self.expected_id_type:
            assert request.query['order_id_type'] == self.expected_id_type
        if self.require_latest is not None:
            assert (
                request.query['require_latest'] == 'true'
                if self.require_latest
                else 'false'
            )

        proc = self.find_one(request.query['order_id'])

        assert request.content_type == 'application/bson'
        if proc:
            return mockserver.make_response(
                status=200,
                content_type='application/bson',
                response=bson.BSON.encode(
                    {
                        'document': proc,
                        'revision': {
                            'processing.version': 1,
                            'order.version': 1,
                        },
                    },
                ),
            )
        return mockserver.make_response(
            status=404, json={'code': 'no_such_order', 'message': ''},
        )

    def order_proc_set_fields(self, request, mongodb, mockserver):
        order_id = request.query['order_id']
        assert order_id

        order = self.find_one(order_id)

        if not order:
            return mockserver.make_response(
                status=404, json={'code': 'no_such_order', 'message': ''},
            )

        data = bson.BSON.decode(request.get_data())

        update = dict(data['update'])
        assert '$set' in update
        for field in ['choices', 'ct', 'msg', 'c', 'iac', 'app_comment']:
            assert 'order.feedback.' + field in update['$set']

        assert dict(data['filter']) == {
            '$or': [
                {'order.feedback.ct': {'$exists': False}},
                {
                    'order.feedback.ct': {
                        '$lte': datetime.datetime(2018, 8, 10, 18, 1, 30),
                    },
                },
            ],
        }

        if order_id == '222ef3c5398b3e07b59f03110563479d':
            return mockserver.make_response(
                status=409,
                json={
                    'code': 'race_condition',
                    'message': 'order_was_changed',
                },
            )

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({'document': {}}),
        )


@pytest.fixture
def order_core(load_json):
    return OrderCoreContext(load_json)


@pytest.fixture(name='order_core_api')
def mock_order_core(mockserver, order_core, mongodb):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _order_proc_get_fields(request):
        return order_core.order_proc_get_fields(request, mongodb, mockserver)

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _order_proc_set_fields(request):
        order_core.times_called += 1
        return order_core.order_proc_set_fields(request, mongodb, mockserver)

    return order_core
