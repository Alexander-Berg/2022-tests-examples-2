# coding: utf-8

from __future__ import unicode_literals

import datetime
import json

from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import dbh
from taxi.internal import geo_position
from taxi.internal import archive


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_cancel_by_user(patch, mock_send_event):
    _mock_last_position(patch)
    _mock_set_fields(patch)
    _mock_get_fields(patch)
    response = django_test.Client().post(
        '/api/order/foo/cancel/user/',
        content_type='application/json',
        data='{}'
    )
    assert response.status_code == 200, response.content
    proc = yield db.order_proc.find_one({'_id': 'foo'})
    assert proc is not None
    assert proc['order']['status'] == 'cancelled'
    assert proc['order']['taxi_status'] == 'driving'
    assert proc['order']['free_cancel_reason'] == 'Cancel was made by taxi-admin'
    _assert_ready_to_reprocess(proc)
    cancel_event = proc['order_info']['statistics']['status_updates'][-1]
    assert cancel_event['s'] == 'cancelled'
    assert cancel_event['x-idempotency-token'] == 'admin-cancel-as-user'


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_cancel_by_park(patch, mock_send_event):
    _mock_last_position(patch)
    _mock_set_fields(patch)
    _mock_get_fields(patch)

    response = django_test.Client().post(
        '/api/order/foo/cancel/park/',
        content_type='application/json',
        data='{}'
    )
    assert response.status_code == 200, response.content
    proc = yield db.order_proc.find_one({'_id': 'foo'})
    assert proc is not None
    assert proc['order']['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'cancelled'
    assert proc['order']['free_cancel_reason'] == 'Cancel was made by taxi-admin'
    _assert_ready_to_reprocess(proc)
    cancel_event = proc['order_info']['statistics']['status_updates'][-1]
    assert cancel_event['t'] == 'cancelled'
    assert cancel_event['s'] == 'finished'
    assert cancel_event['x-idempotency-token'] == 'admin-cancel-as-park'


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_autoreorder(patch, mock_send_event):
    _mock_last_position(patch)

    response = django_test.Client().post(
        '/api/order/foo/autoreorder/',
        content_type='application/json',
        data='{}'
    )
    assert response.status_code == 200, response.content
    proc = yield db.order_proc.find_one({'_id': 'foo'})
    assert proc is not None
    assert proc['order']['status'] == 'pending'
    assert proc['order'].get('taxi_status') is None
    assert proc['performer'].get('candidate_index') is None
    _assert_ready_to_reprocess(proc)
    autoreorder_event = proc['order_info']['statistics']['status_updates'][-1]
    assert autoreorder_event['t'] is None
    assert autoreorder_event['s'] == 'pending'
    assert autoreorder_event['q'] == 'autoreorder'
    assert autoreorder_event['x-idempotency-token'] == 'reorder-from-1_2'


def _assert_ready_to_reprocess(proc):
    assert proc['order']['version'] == 3
    assert proc['processing']['version'] == 4
    assert proc['processing']['need_start'] is True


def _mock_last_position(patch):
    @patch('taxi.internal.driver_manager.get_last_position')
    @async.inline_callbacks
    def mock_get_last_position(driver_id, park_id, tvm_src_service=None,
                               backdoor=False, log_extra=None):
        yield
        position = geo_position.DriverTrackPoint(
            lon=37, lat=55, geotime=datetime.datetime.now())
        async.return_value(position)


def _mock_get_fields(patch):
    @patch('taxi.external.order_core.get_fields')
    @async.inline_callbacks
    def mock_get_fields(order_id, fields, autorestore=False, log_extra=None):
        order_proc = yield archive.get_order_proc_by_id(
            order_id, log_extra=log_extra
        )
        order_proc = dbh.order_proc.Doc(order_proc)
        processing_version = order_proc.get('processing', {}).get('version', 0)
        order_version = order_proc.get('order', {}).get('version', 0)
        response = {
                    'document': order_proc,
                    'revision': {
                        'processing.version': processing_version,
                        'order.version': order_version,
                    },
                }
        yield response
        async.return_value(response)


def _mock_set_fields(patch):
    @patch('taxi.external.order_core.set_fields')
    @async.inline_callbacks
    def mock_set_fields(order_id, update, revision, log_extra=None):
        try:
            order_proc = yield archive.get_order_proc_by_id(
                order_id, log_extra=log_extra
            )
            order_proc = dbh.order_proc.Doc(order_proc)
            query = {dbh.order_proc.Doc._id: order_id}
            yield dbh.order_proc.Doc._update(query, update)
        except archive.NotFound:
            pass


@pytest.mark.asyncenv('blocking')
@pytest.mark.translations([
    (
        'cargo',
        'errors.use_waybill_autoreorder',
        'ru',
        u'Для заказов доставки используйте админку маршрутных листов'
    ),
])
@pytest.mark.config(
    ADMIN_CARGO_AUTOREORDER_DISABLED=True
)
@pytest.inline_callbacks
def test_autoreorder_disabled_for_cargo(patch):
    _mock_last_position(patch)

    yield db.order_proc.update(
        {'_id': 'foo'},
        {'$set': {dbh.order_proc.Doc.order.request.cargo_ref_id: 'cargo_1'}})

    response = django_test.Client().post(
        '/api/order/foo/autoreorder/',
        content_type='application/json',
        data='{}'
    )
    assert response.status_code == 410, response.content
    response_body = json.loads(response.content)
    assert response_body['message'] == (
        u'Для заказов доставки используйте админку маршрутных листов'
    )

    proc = yield db.order_proc.find_one({'_id': 'foo'})
    assert proc is not None
    assert proc['order']['status'] == 'assigned'
