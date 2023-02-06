# pylint: disable=redefined-outer-name, import-error
import enum

import bson
from pricing_extended import mocking_base
import pytest


class OrderIdRequestType(enum.Enum):
    exact_id = 'exact_id'
    alias_id = 'alias_id'
    client_id = 'client_id'
    any_id = 'any_id'


class OrderCoreContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.expected_projection = None
        self.expected_order_id = None
        self.expected_id_type = None
        self.require_latest = None
        self.expected_update_fields = None
        self.expected_revision = None

    def set_expected_projection(self, expected_proj):
        self.expected_projection = expected_proj

    def set_expected_key(self, order_id, id_type=None, require_latest=None):
        self.expected_order_id = order_id
        self.expected_id_type = id_type.value
        self.require_latest = require_latest

    def set_expected_update_fields(self, data):
        self.expected_update_fields = data

    def set_expected_revision(self, data):
        self.expected_revision = data

    def do_set_fields_request(self, request, mongodb, mockserver):
        assert request.content_type == 'application/bson'
        data = bson.BSON.decode(request.get_data())

        if self.expected_order_id:
            assert request.query['order_id'] == self.expected_order_id
        if self.expected_id_type:
            assert request.query['order_id_type'] == self.expected_id_type
        if self.expected_update_fields is not None:
            assert data['update']['$set'] == self.expected_update_fields
        if self.expected_revision:
            assert data['revision'] == self.expected_revision

        if request.query['order_id_type'] == OrderIdRequestType.exact_id.value:
            query = {'_id': request.query['order_id']}
        else:
            query = {'aliases.id': request.query['order_id']}
        if 'fields' in data:
            proc = mongodb.order_proc.find_one(query, data['fields'])
        else:
            proc = mongodb.order_proc.find_one(query, {'_id': True})
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
        if request.query['order_id_type'] == OrderIdRequestType.exact_id.value:
            query = {'_id': request.query['order_id']}
        else:
            query = {'aliases.id': request.query['order_id']}
        proc = mongodb.order_proc.find_one(query, projection['fields'])
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


@pytest.fixture
def order_core():
    return OrderCoreContext()


@pytest.fixture
def mock_order_core(mockserver, order_core, mongodb):
    class OrderCoreHandlers:
        def __init__(self):
            @mockserver.json_handler(
                '/order-core/internal/processing/v1/order-proc/get-fields',
            )
            def get_fields(request):
                return order_core.order_proc_get_fields(
                    request, mongodb, mockserver,
                )

            @mockserver.handler(
                '/order-core/internal/processing/v1/order-proc/set-fields',
            )
            def set_fields(request):
                return order_core.do_set_fields_request(
                    request, mongodb, mockserver,
                )

            self.get_fields = get_fields
            self.set_fields = set_fields

    return OrderCoreHandlers()
