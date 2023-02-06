import uuid

import pytest


class Db:
    def __init__(self):
        self.uuids2refs = {}
        self.uuids2revisions = {}
        self.refs2uuids = {}
        self.committed_orders = set()

    def new_order(self, waybill_ref):
        order_id = str(uuid.uuid4())
        self.uuids2refs[order_id] = waybill_ref
        self.uuids2revisions[order_id] = 1
        self.refs2uuids[waybill_ref] = order_id
        return order_id

    def commit(self, order_id):
        self.committed_orders.add(order_id)

    def remove_draft(self, order_id):
        del self.uuids2refs[order_id]
        del self.uuids2revisions[order_id]

    def build_commit_response_body(self, order_id):
        return {
            'order_id': order_id,
            'waybill_ref': self.uuids2refs[order_id],
            'revision': self.uuids2revisions[order_id],
            'provider_order_id': self.taxi_order_id_from_order_id(order_id),
        }

    def waybill_ref_from_taxi_order_id(self, taxi_order_id):
        order_id = taxi_order_id.split('_', 1)[1]
        return self.uuids2refs[order_id]

    def order_id_from_waybill_ref(self, waybill_ref):
        return self.refs2uuids[waybill_ref]

    @staticmethod
    def taxi_order_id_from_order_id(order_id):
        return 'taxi_%s' % order_id


@pytest.fixture(name='cargo_orders_db')
def _cargo_orders_db():
    return Db()


@pytest.fixture(name='cargo_orders_draft_handler')
def _cargo_orders_draft_handler(cargo_orders_db, mockserver):
    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def handler(request):
        order_id = cargo_orders_db.new_order(request.json['waybill_ref'])
        return {'order_id': order_id}

    return handler


@pytest.fixture(name='cargo_orders_commit_handler')
def _cargo_orders_commit_handler(mockserver, cargo_orders_db):
    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def handler(request):
        order_id = request.json['order_id']
        if order_id in cargo_orders_db.uuids2refs:
            cargo_orders_db.commit(order_id)
            return cargo_orders_db.build_commit_response_body(order_id)
        return mockserver.make_response(status=410, json={})

    return handler
