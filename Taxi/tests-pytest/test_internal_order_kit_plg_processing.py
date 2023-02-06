# -*- coding: utf-8 -*-
import datetime
import logging

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.core import log
from taxi.external import experiments3
from taxi.external import taxi_protocol

from taxi.internal import dbh
from taxi.internal.order_kit.plg import corp_expire
from taxi.internal.order_kit.plg import order_control
from taxi.internal.order_kit.plg import ordersync


_RULES_WITH_REASONS = {
    'regular', 'discount', 'ar', 'cr', 'dp', 'acr', 'p_guarantee_id'
}
_DONT_CHECK_DECLINE_REASONS = object()


def _setup_logging():
    logger = logging.getLogger('taxi.internal.order_kit.plg')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        log.SyslogConsoleFormatter(fmt=settings.LOG_CONSOLE_FORMAT)
    )
    stream_handler.setLevel(logging.DEBUG)

    while logger.handlers:
        logger.removeHandler(logger.handlers[0])
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)


@pytest.mark.config(
    CORP_EXPIRED_PROCESSING_ENABLED=True,
    APPLICATION_TO_CORP_SOURCE_MAP={'corpweb': 'corpweb'}
)
@pytest.mark.filldb(
    order_proc='for_corp_order_expired',
    orders='for_corp_order_expired',
    corp_clients='for_corp_order_expired',
)
@pytest.mark.parametrize(
    'order_id,order_status,taxi_status,corp_payment_methods_response,expected_personal_phone_id',
    [
        # success: client can create orders
        (
            'order_1',
            dbh.order_proc.STATUS_PENDING,
            dbh.orders.TAXI_STATUS_NONE,
            {'methods': [{'can_order': True, 'zone_available': True}]},
            'test_personal_phone_id',
        ),
        # skip: not order.corp_client
        (
            'order_2',
            dbh.order_proc.STATUS_PENDING,
            dbh.orders.TAXI_STATUS_NONE,
            {},
            None,
        ),
        # skip: proc.status != dbh.order_proc.STATUS_PENDING
        (
            'order_3',
            dbh.order_proc.STATUS_ASSIGNED,
            dbh.orders.TAXI_STATUS_TRANSPORTING,
            {},
            None,
        ),
        # skip: unknown corp_client_id
        (
            'order_4',
            dbh.order_proc.STATUS_ASSIGNED,
            dbh.orders.TAXI_STATUS_TRANSPORTING,
            {},
            None,
        ),
        # skip: corp_client not found
        (
            'order_5',
            dbh.order_proc.STATUS_PENDING,
            dbh.orders.TAXI_STATUS_NONE,
            {},
            None,
        ),
        # expired: cannot order because of corp-int-api
        (
            'order_6',
            dbh.order_proc.STATUS_FINISHED,
            dbh.orders.TAXI_STATUS_EXPIRED,
            {'methods': [{'can_order': False, 'zone_available': True}]},
            None,
        ),
    ]
)
@pytest.inline_callbacks
def test_mark_corp_expired_on(
        patch,
        order_id,
        order_status,
        taxi_status,
        corp_payment_methods_response,
        corp_clients_get_client_by_client_id_mock,
        expected_personal_phone_id
):
    @patch('taxi.internal.dbh.order_proc.Doc.mark_as_expired')
    @async.inline_callbacks
    def mark_as_expired(user_fraud=False, log_extra=None):
        yield
        order_proc = dbh.order_proc.Doc()  # type: dbh.order_proc.Doc
        order_proc.status = dbh.order_proc.STATUS_FINISHED
        order_proc.order.status = dbh.orders.STATUS_FINISHED
        order_proc.order.taxi_status = dbh.orders.TAXI_STATUS_EXPIRED
        async.return_value(order_proc)

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)

    @patch('taxi.external.corp_integration_api.corp_paymentmethods')
    @async.inline_callbacks
    def corp_payment_methods(*args, **kwargs):
        yield
        request_corp = proc.order.request.corp

        expected_cost_centers_sent = {}
        if request_corp.cost_center:
            expected_cost_centers_sent['old'] = request_corp.cost_center
        new_cost_centers = proc.order.request.corp.cost_centers
        if new_cost_centers or new_cost_centers == []:
            expected_cost_centers_sent['new'] = request_corp.cost_centers

        expected_combo_order = {}
        if request_corp.combo_order:
            expected_combo_order = request_corp.combo_order

        assert kwargs.get('cost_centers', {}) == expected_cost_centers_sent
        assert kwargs.get('combo_order', {}) == expected_combo_order
        assert kwargs.get('personal_phone_id') == expected_personal_phone_id

        async.return_value(corp_payment_methods_response)

    new_proc = yield corp_expire.mark_corp_expired(
        proc, log_extra=None
    )  # type: dbh.order_proc.Doc

    assert new_proc.status == order_status
    assert new_proc.order.status == order_status
    assert new_proc.order.taxi_status == taxi_status


@pytest.inline_callbacks
def test_order_creation(patch):
    order_id_ = 'proc_no_order'
    yield db.order_proc.update({'_id': order_id_}, {'$push': {
        'order_info.statistics.status_updates': {
            'h': True,
            's': 'finished',
            't': 'complete',
            'c': datetime.datetime.fromtimestamp(1555478044)
        }
    }})

    @patch('taxi.internal.order_kit.plg.status_handling.handle_new_status')
    @async.inline_callbacks
    def handle_new_status(
            proc, event_index,
            log_extra=None
    ):
        yield async.return_value([])

    @patch('taxi.internal.order_kit.plg.order_control._get_create_order_settings')
    @async.inline_callbacks
    def mock_fallback_settings(order_id, phone_id, stage, log_extra=None):
        yield async.return_value(order_control._CreateOrderSettings())

    status = {
        'n_order_created': 0
    }

    @patch('taxi.external.taxi_protocol.create_order')
    @async.inline_callbacks
    def mock_create_order(order_id, log_extra=None):
        assert order_id == order_id_
        status['n_order_created'] += 1
        yield db.orders.insert({'_id': order_id})

    proc = yield dbh.order_proc.Doc.find_one_for_processing(order_id_)
    yield ordersync.sync_and_handle_order(proc, log_extra=None)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id_)
    assert proc.order_info.order_object_skipped is False
    assert status['n_order_created'] == 1
    assert proc.order_info.order_object_skipped is False
    for event in proc.order_info.statistics.status_updates:
        assert event.need_handling is False


@pytest.inline_callbacks
def test_late_order_creation_legacy(patch):
    order_id_ = 'proc_no_order'

    status = {
        'n_order_created': 0,
        'n_order_create_attempts': 0,
    }

    @patch('taxi.internal.order_kit.plg.status_handling.handle_new_status')
    @async.inline_callbacks
    def handle_new_status(
            proc, event_index,
            log_extra=None
    ):
        yield async.return_value([])

    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def mock_exp3_get_values(*args, **kwargs):
        yield
        result = [
            experiments3.ExperimentsValue(
                name='processing_create_order_settings',
                value={'__default__': {'try_create': True, 'raise_error': True}}
            )
        ]
        async.return_value(result)

    @patch('taxi.external.taxi_protocol.create_order')
    @async.inline_callbacks
    def mock_create_order(order_id, log_extra=None):
        assert order_id == order_id_
        status['n_order_create_attempts'] += 1
        if status['n_order_create_attempts'] < 2:
            raise taxi_protocol.TaxiProtocolRequestError('request failed')
        status['n_order_created'] += 1
        yield db.orders.insert({'_id': order_id})

    proc = yield dbh.order_proc.Doc.find_one_for_processing(order_id_)

    with pytest.raises(taxi_protocol.TaxiProtocolRequestError):
        yield ordersync.sync_and_handle_order(proc, log_extra=None)

    proc = yield dbh.order_proc.Doc.find_one_for_processing(order_id_)
    yield ordersync.sync_and_handle_order(proc, log_extra=None)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id_)
    assert proc.order_info.order_object_skipped is False
    assert status['n_order_create_attempts'] == 2
    assert status['n_order_created'] == 1


@pytest.inline_callbacks
def test_late_order_creation(patch):
    order_id_ = 'proc_no_order'

    status = {
        'n_order_created': 0,
        'n_order_create_attempts': 0,
        'create': False,
        'statuses': [],
    }

    @patch('taxi.internal.order_kit.plg.status_handling.handle_new_status')
    @async.inline_callbacks
    def handle_new_status(
            proc, event_index,
            log_extra=None
    ):
        yield async.return_value([])

    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def mock_exp3_get_values(*args, **kwargs):
        yield
        result = [
            experiments3.ExperimentsValue(
                name='processing_create_order_settings',
                value={
                    '__default__': {'try_create': True, 'raise_error': True},
                    'create': {'try_create': True, 'raise_error': False},
                    'transporting': {'try_create': False},
                }
            )
        ]
        async.return_value(result)

    @patch('taxi.external.taxi_protocol.create_order')
    @async.inline_callbacks
    def mock_create_order(order_id, log_extra=None):
        assert order_id == order_id_
        status['n_order_create_attempts'] += 1
        proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
        for event in proc.order_info.statistics.status_updates:
            if event.need_handling is True:
                break
        else:
            assert False, 'no unhandled events'
        status['statuses'].append(
            '%s/%s' % (event.status, event.taxi_status or None)
        )
        if not status['create']:
            raise taxi_protocol.TaxiProtocolRequestError('request failed')
        else:
            status['n_order_created'] += 1
            yield db.orders.insert(
                {'_id': order_id, 'version': proc.order.version}
            )

    proc = yield dbh.order_proc.Doc.find_one_for_processing(order_id_)

    # handle order creation, driving, waiting & transporting
    yield ordersync.sync_and_handle_order(proc, log_extra=None)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id_)
    assert status['n_order_create_attempts'] == 1
    assert status['n_order_created'] == 0
    assert status['statuses'] == ['pending/None']
    assert proc.order_info.order_object_skipped
    for event in proc.order_info.statistics.status_updates:
        assert event.need_handling is False

    # add completed
    proc = yield db.order_proc.find_and_modify({'_id': order_id_}, {
        '$push': {
            'order_info.statistics.status_updates': {
                'h': True,
                's': 'finished',
                't': 'complete',
                'c': datetime.datetime.fromtimestamp(1555478044)
            }
        },
    }, new=True)
    proc = dbh.order_proc.Doc(proc)

    # check that completed does not ignore error on order creation
    with pytest.raises(taxi_protocol.TaxiProtocolRequestError):
        yield ordersync.sync_and_handle_order(proc, log_extra=None)
    assert status['n_order_create_attempts'] == 2
    assert status['n_order_created'] == 0
    assert status['statuses'] == ['pending/None', 'finished/complete']
    assert proc.order_info.order_object_skipped

    # check that order created
    status['create'] = True
    yield ordersync.sync_and_handle_order(proc, log_extra=None)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id_)
    assert proc.order_info.order_object_skipped is False
    assert status['n_order_created'] == 1
    assert status['statuses'] == [
        'pending/None', 'finished/complete', 'finished/complete'
    ]
    assert proc.order_info.order_object_skipped is False
    for event in proc.order_info.statistics.status_updates:
        assert event.need_handling is False

    order = yield dbh.orders.Doc.find_one_by_id(order_id_)
    assert order.taxi_status == 'complete'
