import datetime

from lxml import etree
import pytest

from taxi import config
from taxi.internal import card_operations
from taxi.internal import dbh
from taxi.internal.order_kit.plg import changes_handler
from taxi.taxi_protocol.protocol_1x import client


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(
    order_proc='for_change_notify_test',
    orders='for_change_notify_test',
    parks='for_change_notify_test',
)
@pytest.inline_callbacks
def test_notify(patch):
    send_calls = []

    @patch('taxi.taxi_protocol.protocol_1x.client.send_updaterequest_change')
    def send_updaterequest_change(proc, body, log_extra=None):
        # successful send_updaterequest_change
        assert_has_comment(body)
        send_calls.append(1)
    order_id = 'some_order_id_comment_no_notify_attempts'
    yield changes_handler._notify_on_change._task_function(
        order_id, 'comment'
    )
    assert len(send_calls) == 1
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    change_obj = proc.changes.objects[-1]
    assert change_obj.send_status.attempts == 1
    assert change_obj.send_status.last_attempt == datetime.datetime.utcnow()
    assert change_obj.send_status.status == 'delivered'


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(
    order_proc='for_change_notify_with_no_status_test',
    orders='for_change_notify_with_no_status_test',
    parks='for_change_notify_with_no_status_test',
)
@pytest.inline_callbacks
def test_notify_no_status(patch):
    send_calls = []

    @patch('taxi.taxi_protocol.protocol_1x.client.send_updaterequest_change')
    def send_updaterequest_change(proc, body, log_extra=None):
        # successful send_updaterequest_change
        assert_has_comment(body)
        send_calls.append(1)
    order_id = 'some_order_id_comment_no_status'
    yield changes_handler._notify_on_change._task_function(
        order_id, 'comment'
    )
    assert len(send_calls) == 1
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    change_obj = proc.changes.objects[-1]
    assert change_obj.send_status.attempts == 1
    assert change_obj.send_status.last_attempt == datetime.datetime.utcnow()
    assert change_obj.send_status.status == 'delivered'


def assert_has_comment(body):
    parsed_xml = etree.fromstring(body)
    assert len(parsed_xml.xpath('/Request/Comments')) == 1


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(
    order_proc='for_change_notify_test',
    orders='for_change_notify_test',
    parks='for_change_notify_test',
)
@pytest.mark.parametrize(
    'order_id,raise_exception,expected_status,num_repeat_calls', [
        # need to resend - which means 'processing' and 1 repeat call
        ('some_order_id_comment_no_notify_attempts',
         client.InvalidResponseServerError(500, 'server error'),
         'processing', 1),

        # don't need to resend - which means 'failed' and 0 repeat calls
        ('some_order_id_comment_no_notify_attempts',
         client.InvalidResponseClientError(410, 'client error'),
         'failed', 0),
        # don't need to resend - park with no host - which means 'failed' and
        # 0 repeat calls
        ('some_order_id_comment_no_notify_attempts',
         client.MissingHost,
         'failed', 0),
])
@pytest.inline_callbacks
def test_notify_attempt_failed(patch, order_id, raise_exception,
                               expected_status, num_repeat_calls):
    send_calls = []

    @patch('taxi.taxi_protocol.protocol_1x.client.send_updaterequest_change')
    def send_updaterequest_change(proc, body, log_extra=None):
        send_calls.append(1)
        raise raise_exception
    repeat_calls = []

    @patch('taxi_stq.stq_task.TaskFactory.call_later')
    def call_later(eta, *args, **kwargs):
        repeat_calls.append(1)
    order_id = 'some_order_id_comment_no_notify_attempts'
    yield changes_handler._notify_on_change._task_function(
        order_id, 'comment'
    )
    assert len(send_calls) == 1
    assert len(repeat_calls) == num_repeat_calls
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    change_obj = proc.changes.objects[-1]
    assert change_obj.send_status.attempts == 1
    assert change_obj.send_status.last_attempt == datetime.datetime.utcnow()
    assert change_obj.send_status.status == expected_status


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(
    order_proc='for_change_notify_test',
    orders='for_change_notify_test',
    parks='for_change_notify_test',
)
@pytest.inline_callbacks
def test_notify_all_failed(patch):
    send_calls = []

    @patch('taxi.taxi_protocol.protocol_1x.client.send_updaterequest_change')
    def send_updaterequest_change(proc, body, log_extra=None):
        send_calls.append(1)
        raise client.InvalidResponseServerError(500, 'server error')

    order_id = 'some_order_id_comment_last_notify_attempt'
    yield changes_handler._notify_on_change._task_function(
        order_id, 'comment'
    )
    assert len(send_calls) == 1
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    change_obj = proc.changes.objects[-1]
    assert change_obj.send_status.attempts == 10
    assert change_obj.send_status.last_attempt == datetime.datetime.utcnow()
    assert change_obj.send_status.status == 'failed'


@pytest.mark.filldb(
    order_proc='for_change_notify_test',
)
@pytest.inline_callbacks
def test_update_ready_for_notifying_change_send_status(patch):
    proc = yield dbh.order_proc.Doc.find_one_by_id('some_order_id')
    proc = yield proc.update_ready_for_notifying_change_send_status(
        'comment', 'delivered', datetime.datetime.utcnow())
    change = proc.get_last_change('comment')
    assert change.send_status.status == 'delivered'
    assert change.send_status.attempts == 1
    assert change.send_status.last_attempt == datetime.datetime.utcnow()


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
@pytest.mark.parametrize('enable_taximeter', [
    True,
    False
])
@pytest.inline_callbacks
def test_send_notification(enable_taximeter, patch):

    @patch('taxi.internal.park_manager.get_doc')
    def get_doc(*args, **kwargs):
        return dbh.parks.Doc({})

    @patch('taxi.internal.park_manager.is_taximeter_sourced')
    def is_taximeter_sourced(park):
        assert isinstance(park, dbh.parks.Doc)
        return enable_taximeter

    results = []

    def handler(proc, log_extra, **kwargs):
        results.append(kwargs)

    result, need_resend = yield changes_handler._send_notification(
        handler,
        dbh.order_proc.Doc(),
        'test'
    )
    assert result is True
    assert need_resend is False
    assert len(results) == 1
    results = sorted(results)
    assert results[0] == {
        'cars_info': True
    }


@pytest.mark.filldb(
    orders='moneyless_newbie',
    order_proc='moneyless_newbie',
    user_phones='moneyless_newbie',
)
@pytest.mark.asyncenv('async')
@pytest.mark.parametrize(
    ['af_eta', 'check_card_disabled', 'check_card', 'status', 'eta', 'values'],
    (
        # no antifraud ETA, need to check_card
        (None, False, True, 'processing', 0, {'wait_sync': True}),
        (None, False, False, 'rejecting', None, None),
        # less than or equal threshold, no need in check_card
        (0, False, True, 'processing', 0, {'wait_sync': True}),
        (0, False, False, 'processing', 0, {'wait_sync': True}),
        # bigger than threshold (default is 10), need to check_card
        (42, False, True, 'processing', 0, {'wait_sync': True}),
        (42, False, False, 'rejecting', None, None),
        # disabled by config: no antifraud ETA, need to check_card
        (None, True, False, 'processing', 0, {'wait_sync': True}),
        # disabled by config: less than or equal threshold, no need in
        #   check_card
        (0, True, False, 'processing', 0, {'wait_sync': True}),
        # disabled by config: bigger than threshold (default is 10), need to
        #   check_card
        (42, True, False, 'processing', 0, {'wait_sync': True}),
    )
)
@pytest.mark.parametrize('order_id, billing_service_type', [
    ('test_order_id', 'card'),
    ('test_order_id_uber', 'uber'),
])
@pytest.mark.parametrize('billing_by_brand_enabled', [False, True])
@pytest.inline_callbacks
def test_switch_to_possible_moneyless_card_for_newbie(
        patch, af_eta, check_card_disabled, check_card, status, eta, values,
        order_id, billing_service_type, billing_by_brand_enabled,
):
    yield config.BILLING_SERVICE_NAME_MAP_BY_BRAND_ENABLED.save(
        billing_by_brand_enabled,
    )
    yield config.USER_ANTIFRAUD_DISABLE_CHECK_CARD_ON_CHANGE_PAYMENT_TYPE.save(
        check_card_disabled,
    )

    @patch('taxi.internal.card_operations.get_card')
    def get_card(*args, **kwargs):
        assert kwargs['service_type'] == billing_service_type

        return card_operations.create_card_object(
            owner='test_yandex_uid',
            card_id='card_x1234',
            system='visa',
            number='1234-5678-0987-6543',
            billing_card_id='test_billing_card_id',
            currency='rub',
            name='',
            blocking_reason='',
            service_labels='',
            persistent_id='test_persistent_id',
            region_id='moscow',
            possible_moneyless=True,
        )

    @patch(
        'taxi.internal.order_kit.plg.changes_handler._check_max_unpaid_orders'
    )
    def _check_max_unpaid_orders(*args, **kwargs):
        return True

    @patch('taxi.internal.card_operations._Card.check_workable')
    def check_workable(*args, **kwargs):
        pass

    @patch('taxi.internal.order_kit.antifraud.check_card')
    def _check_card(*args, **kwargs):
        return check_card

    @patch(
        'taxi.internal.order_kit.invoice_handler.get_antifraud_eta'
    )
    def _get_antifraud_eta(*args, **kwargs):
        return af_eta

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    res_status, res_eta, res_extra_values, res_event_info = (
        yield changes_handler._handle_change_payment(proc)
    )
    expected_event_info = None
    if status == 'rejecting':
        expected_event_info = {
            'event_key': 'change_payment_reject', 'event_arg': {},
        }
    if status == 'processing':
        expected_event_info = {
            'event_key': 'change_payment',
            'event_arg': {
                'billing_card_id': 'test_billing_card_id',
                'change_value': {
                    'ip': '127.0.0.1',
                    'yandex_uid': 'test_yandex_uid',
                    'payment_method_id': 'card_x1234'
                },
                'persistent_id': 'test_persistent_id',
                'card_id': 'card_x1234',
                'payment_type': 'card'
            }
        }
    assert (res_status, res_eta, res_extra_values, res_event_info) == (
        status, eta, values, expected_event_info
    )
