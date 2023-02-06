import copy
import decimal
import json

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.external import billing_orders
from taxi.internal import dbh
from taxi.internal.payment_kit import rebill
from taxi.util import data_structures


@pytest.mark.parametrize(
    'order_id,cost_for_driver,expectation', [
        (
                'full_order_id',
                decimal.Decimal(300),
                'expected_full_data.json'
        ),
        (
                'client_cost_gt_than_driver_cost_order_id',
                decimal.Decimal(300),
                'expected_client_cost_gt_than_driver_cost_data.json'
        ),
        (
                'complete_no_driver_cost_order_id',
                decimal.Decimal(300),
                'expected_complete_no_driver_cost_data.json',
        ),
        (
                'cancelled_no_driver_cost_order_id',
                decimal.Decimal(300),
                'expected_cancelled_no_driver_cost_data.json'
        ),
        (
                'not_finished_order_id',
                decimal.Decimal(300),
                rebill.UnsupportedOrderError,
        ),
        (
                'corp_order_id',
                decimal.Decimal(300),
                rebill.UnsupportedOrderError,
        ),
        (
                'no_performer_order_id',
                decimal.Decimal(300),
                rebill.UnsupportedOrderError,
        ),
])
@pytest.mark.filldb(
    orders='for_test_change_cost_and_rebill',
    order_proc='for_test_change_cost_and_rebill',
)
@pytest.inline_callbacks
def test_change_cost_and_rebill(
        order_id, cost_for_driver, expectation, load, patch):
    _patch_archive(patch)

    @async.inline_callbacks
    def call():
        result = yield rebill.change_cost_and_rebill(
            order_id=order_id,
            cost_for_driver=cost_for_driver,
            ticket_type='chatterbox',
            ticket_id='123',
        )
        async.return_value(result)

    if _is_exception(expectation):
        with pytest.raises(expectation):
            yield call()
    else:
        expected_data = json.loads(load(expectation))
        _patch_billing_orders_get_response(
            patch, expected_data['billing_orders_request']
        )
        doc_id = yield call()
        assert doc_id == 999
        query = {'_id': order_id}
        order = yield db.orders.find_one(query)
        order_proc = yield db.order_proc.find_one(query)
        assert _convert_order(order) == expected_data['order']
        assert _convert_order_proc(order_proc) == expected_data['order_proc']


def _patch_billing_orders_rebill_order(patch, error_code):
    @patch('taxi.external.billing_orders.rebill_order')
    @async.inline_callbacks
    def rebill(proc,
               order,
               reason_kind,
               ticket_type,
               ticket_id,
               tvm_src_service=None,
               log_extra=None):
        yield
        assert isinstance(proc, dbh.order_proc.Doc)
        assert isinstance(order, dbh.orders.Doc)
        assert reason_kind == 'cost_changed'
        assert ticket_type == 'chatterbox'
        assert ticket_id == '123'
        assert tvm_src_service == settings.ADMIN_TVM_SERVICE_NAME
        if error_code is None:
            async.return_value()
        raise billing_orders.BadRequestError(
            code=error_code,
            message='set from test'
        )


class NoExpectation(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.parametrize('billing_orders_error_code,expectation', [
    (None, NoExpectation()),
    ('rebill_order_is_not_allowed', NoExpectation()),
    ('some_code', pytest.raises(billing_orders.BadRequestError)),
])
@pytest.mark.filldb(
    orders='for_test_rebill_on_update_driver_sum_to_pay',
    order_proc='for_test_rebill_on_update_driver_sum_to_pay',
)
@pytest.mark.config(
    REBILL_ORDER_ON_UPDATE_DRIVER_SUM_TO_PAY=True,
)
@pytest.inline_callbacks
def test_rebill_on_update_driver_sum_to_pay(
        patch, billing_orders_error_code, expectation
):
    _patch_archive(patch)
    _patch_billing_orders_rebill_order(patch, billing_orders_error_code)
    order = yield dbh.orders.Doc.find_one_by_id('some_order_id')
    with expectation:
        yield rebill.rebill_on_update_driver_sum_to_pay(
            order=order,
            ticket_type='chatterbox',
            ticket_id='123',
            log_extra=None,
        )


def _is_exception(obj):
    return isinstance(obj, type) and issubclass(obj, Exception)


def _patch_archive(patch):
    @patch('taxi.internal.archive.restore_order')
    def restore_order(order_id, src_tvm_service=None, log_extra=None):
        pass

    @patch('taxi.internal.archive.restore_order_proc')
    def restore_order_proc(order_id, src_tvm_service=None, log_extra=None):
        pass


def _patch_billing_orders_get_response(patch, expected_request):
    @patch('taxi.external.billing_orders._get_response')
    def _get_response(method, location, json=None, **kwargs):
        assert _convert_json(json) == expected_request
        return _Response({'doc': {'id': 999}})


def _convert_order(order):
    return data_structures.partial_dict(order, ['cost', 'driver_cost'])


def _convert_order_proc(order_proc):
    return {
        'order': _convert_order(order_proc['order'])
    }


def _convert_json(json):
    request = copy.deepcopy(json)
    del request['idempotency_token']
    return request


class _Response(object):
    def __init__(self, content):
        self._content = content

    def json(self):
        return self._content

    @property
    def status_code(self):
        return 200

    def raise_for_status(self):
        pass
