# -*- coding: utf-8 -*-

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.external import experiments3
from taxi.internal import dbh
from taxi.internal.order_kit import const
from taxi.internal.order_kit import invoice_handler
from taxi.internal.order_kit.plg import processing
from taxi.internal.order_kit.plg import changes_handler


def _working(proc):
    working_statuses = [
        dbh.order_proc.CHANGE_STATUS_APPLYING,
        dbh.order_proc.CHANGE_STATUS_PENDING
    ]
    for obj in proc.changes.objects:
        if obj.status in working_statuses:
            return True
    return False


@pytest.fixture(autouse=True)
def mock_exp3_get_values(patch):
    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def mock_exp3_get_values(*args, **kwargs):
        yield
        result = [
            experiments3.ExperimentsValue(
                name='order_client_notification',
                value={'enabled': False}
            )
        ]

        async.return_value(result)


@pytest.mark.translations([
    ('tariff', 'econom', 'ru', u'Эконом'),
    ('notify', 'time', 'ru', u'%I:%M %p'),
    ('notify', 'sms.on_assigned', 'ru', u'kek'),
])
@pytest.mark.filldb(
    orders='for_card_to_card',
    order_proc='for_card_to_card',
    user_phones='for_card_to_card',
    parks='for_card_to_card',
    cards='for_card_to_card',
    cities='for_card_to_card',
    tariffs='for_card_to_card',
    tariff_settings='for_card_to_card',
    users='for_card_to_card',
    dbdrivers='for_card_to_card',
    dbparks='for_card_to_card',
    cardlocks='for_card_to_card',
)
@pytest.mark.load_data(
    countries='for_card_to_card',
)
@pytest.mark.parametrize(
    ('order_id,uber,roaming,start_card,result_card,expected_payment_type,expected_service_type,init_busy'), [
        (
            'd70db3edc88f07d1a797ce4e4c88403f', False, None,
            'card-x1234', 'card-x5678', 'card', 'card', False
        ),
        (
            'd70db3edc88f07d1a797ce4e4c68403f', False, None,
            'card-x1234', 'yabank_wallet-wallet-rub-4048420433-01', 'yandex_card', 'card', False
        ),
        (
            'e707fb7b9d9dbe27b95e63cacce91566', False, None,
            'card-x1234', 'card-x1234', 'card', 'not_called', True
        ),
        (
            'd70db3edc88f07d1a797ce4e4c88403f', True, False,
            'card-x1234', 'card-x5678', 'card', 'uber', False
        ),
    ]
)
@pytest.mark.config(
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
)
@pytest.inline_callbacks
def test_card_result_card(
        patch, order_id, uber, roaming, start_card, result_card, expected_payment_type,
        expected_service_type, init_busy, userapi_get_user_phone_mock,
        personal_retrieve_mock, mock_processing_antifraud, mock_send_event,
):
    if uber:
        update = {
            '$set': {
                'source': const.YAUBER_SOURCE
            }
        }
        if roaming:
            update['$set']['request.is_roaming_user'] = True
        update_result = yield db.orders.update({'_id': order_id}, update)
        assert update_result['nModified'] == 1

    @patch('taxi.external.taxi_protocol.create_order')
    @async.inline_callbacks
    def mock_create_order(order_id, log_extra=None):
        yield

    @patch('taxi_stq._client.put')
    def put(queue=None, eta=None, task_id=None, args=None, kwargs=None):
        pass

    cards = [{
        'owner': '1111111111',
        'card_id': 'card-x1234',
        'system': 'Mastercard',
        'number': '5555-5555-5555-4444',
        'billing_card_id': 'x1234',
        'currency': 'RUB',
        'service_labels': [
            'taxi:persistent_id:e2d7ad7c476d43899ec17fe9259ed514'
        ],
        'persistent_id': 'e2d7ad7c476d43899ec17fe9259ed514',
        'busy_with': [
            {"order_id": "e707fb7b9d9dbe27b95e63cacce91566"},
            {"order_id": "d70db3edc88f07d1a797ce4e4c88403f"},
            {"order_id": "945f561aefac08a21a0a9182084d2916"}
        ] if init_busy else [],
        'from_db': False,
    },
    {
        'owner': '1111111111',
        'card_id': 'card-x5678',
        'system': 'Mastercard',
        'number': '4111-1111-1111-1111',
        'billing_card_id': 'x5678',
        'currency': 'RUB',
        'service_labels': [
            'taxi:persistent_id:f2e84afe99fc69af9f7417617eb36275'
        ],
        'persistent_id': 'f2e84afe99fc69af9f7417617eb36275',
        'busy_with': [],
        'from_db': False,
    },
    {
        'owner': '1111111111',
        'card_id': 'card-x1029',
        'system': 'Mastercard',
        'number': '4111-8888-3333-2222',
        'billing_card_id': 'x1029',
        'currency': 'RUB',
        'service_labels': [
            'taxi:persistent_id:b2e760f93eae561bb8f4bf267dddfe84'
        ],
        'persistent_id': 'b2e760f93eae561bb8f4bf267dddfe84',
        'busy_with': [],
        'from_db': False,
    }]

    yandex_cards = [
        {
            'id': 'yabank_wallet-wallet-rub-4048420433-01',
            'currency': 'RUB',
        }
    ]

    def find_card(id_name, value):
        for card in cards:
            if card[id_name] == value:
                return card

    @patch('taxi.external.cardstorage.get_payment_methods')
    def get_cards(request, log_extra=None):
        if expected_service_type:
            assert request.service_type == expected_service_type
        else:
            assert not hasattr(request, 'service_type')
        assert request.yandex_uid == '1111111111'
        return cards

    @patch('taxi.external.cardstorage.get_yandex_payment_methods')
    def get_cards_(request, log_extra=None):
        if expected_service_type:
            assert request.service_type == expected_service_type
        else:
            assert not hasattr(request, 'service_type')
        assert request.yandex_uid == '1111111111'
        return yandex_cards

    @patch('taxi.internal.payment_kit.invoices.transactions_enabled')
    def is_transactions_enabled(request, log_extra=None):
        return False

    @patch('taxi.external.cardstorage.get_card')
    def get_card(request, log_extra=None):
        return find_card('card_id', request.card_id)

    @patch('taxi.external.cardstorage.update_card')
    def update_card(request, log_extra=None):
        card = find_card('card_id', request.card_id)
        if hasattr(request, 'mark_busy'):
            card['busy_with'].append({'order_id': request.mark_busy})
        if hasattr(request, 'unmark_busy'):
            if request.card_id in card['busy_with']:
                card['busy_with'].remove({'order_id': request.unmark_busy})

    @patch('taxi.external.billing.create_order')
    @async.inline_callbacks
    def create_order(
            billing_service, uid, user_ip, product_id, order_id, region_id,
            due_date, due_tz, log_extra=None):
        yield
        pass

    @patch('taxi.external.billing.create_basket')
    @async.inline_callbacks
    def create_basket(*args, **kwargs):
        yield
        pass

    @patch('taxi.external.billing.pay_basket')
    @async.inline_callbacks
    def pay_basket(*args, **kwargs):
        yield
        pass

    @patch('taxi.external.billing.check_basket')
    @async.inline_callbacks
    def check_basket(*args, **kwargs):
        yield
        async.return_value({'status': 'success'})

    @patch('taxi.internal.order_kit.antifraud._get_zone_config')
    @async.inline_callbacks
    def _get_zone_config(zone_id, *args, **kwargs):
        yield
        async.return_value({'enabled': True, 'personal': []})

    @patch('taxi.internal.order_kit.antifraud._get_personal_config')
    @async.inline_callbacks
    def _get_personal_config(
            zone_config, user_group, tariff_class, log_extra=None):
        yield
        async.return_value({
            'pause_before_hold': 60,
            'pause_before_hold_fix_price': 100,
            'pause_before_hold_airport': 150,
            'payment_deltas': ['min', 250, 500, 750, 1000],
            'last_payment_delta': 1000
        })

    settings.PERSONAL_APIKEY = 'qwerty'
    proc = (yield dbh.order_proc.Doc.find_one_by_id(order_id))
    while _working(proc):
        yield processing.do_processing_iteration_throw(order_id)
        yield changes_handler._process_change._task_function(
            order_id, 'payment'
        )
        yield processing.do_processing_iteration_throw(order_id)
        yield invoice_handler.update_transactions_iteration(order_id)
        proc = (yield dbh.order_proc.Doc.find_one_by_id(order_id))

    order = (yield dbh.orders.Doc.find_one_by_id(order_id))
    assert order.payment_tech.main_card_payment_id == result_card
    if expected_payment_type == 'yandex_card':
        return

    ncard = find_card('card_id', result_card)
    ocard = find_card('card_id', start_card)
    nlock = (yield db.cardlocks.find_one({u'i': ncard['persistent_id']}))

    assert order.payment_tech.main_card_payment_id == result_card

    assert {u'order_id': order_id} in ncard[u'busy_with']

    if start_card != result_card:
        assert {u'order_id': order_id} not in ocard[u'busy_with']

    assert nlock and order_id in nlock[u'o']


@async.inline_callbacks
def test_invalid_payment_method():
    order_id = 'd0be4a4b4b2116ccc78c2cbdc295408f'
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    order['status'] = 'pending'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    change = proc.get_last_active_change(dbh.order_proc.ORDER_CHANGE_PAYMENT)
    res = yield changes_handler._init_change_payment_type(proc, order, change)
    assert res == ('rejecting', None, None, None)


@async.inline_callbacks
def test_change_payment_when_order_is_finished():
    order_id = 'd0be4a4b4b2116ccc78c2cbdc295408f'
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    change = proc.get_last_active_change(dbh.order_proc.ORDER_CHANGE_PAYMENT)
    res = yield changes_handler._init_change_payment_type(proc, order, change)
    assert res == ('rejecting', None, None, None)


@pytest.inline_callbacks
def test_yandex_card_compatibility_error(patch):
    @patch('taxi.external.cardstorage.get_yandex_payment_methods')
    def get_cards(request, log_extra=None):
        return [{"id": "card-x0000"}]
    order_id = 'd0be4a4b4b2116ccc78c2cbdc295408f'
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    order['status'] = 'pending'
    order['billing_tech']['transactions'] = []
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    del proc.order["user_login_id"]
    change = proc.get_last_active_change(dbh.order_proc.ORDER_CHANGE_PAYMENT)
    change["vl"]["payment_method_type"] = 'yandex_card'
    change["vl"]["payment_method_id"] = 'card-x0000'
    res = yield changes_handler._init_change_payment_type(proc, order, change)
    assert res == ('rejecting', None, None, None)


@pytest.mark.config(ALLOW_CHANGE_TO_CASH_IF_UNSUCCESSFUL_PAYMENT=True)
@pytest.mark.translations([
    ('tariff', 'econom', 'ru', u'Эконом'),
    ('notify', 'time', 'ru', u'%I:%M %p'),
    ('notify', 'sms.on_assigned', 'ru', u'kek'),
])
@pytest.mark.filldb(
    order_proc='for_card_to_card',
    user_phones='for_card_to_card',
    parks='for_card_to_card',
    cards='for_card_to_card',
    cities='for_card_to_card',
    tariffs='for_card_to_card',
    tariff_settings='for_card_to_card',
    users='for_card_to_card',
    dbdrivers='for_card_to_card',
    dbparks='for_card_to_card',
    cardlocks='for_card_to_card',
)
@pytest.mark.load_data(
    countries='for_card_to_card',
)
@pytest.mark.parametrize(
    'order_id', [
        'card_to_cash_order'
    ]
)
@pytest.mark.filldb(orders='for_card_to_card')
@pytest.mark.config(
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
)
@pytest.inline_callbacks
def test_change_to_cash(
        patch, order_id, userapi_get_user_phone_mock, personal_retrieve_mock,
        mock_processing_antifraud, mock_send_event,
):
    @patch('taxi.external.taxi_protocol.create_order')
    @async.inline_callbacks
    def mock_create_order(order_id, log_extra=None):
        yield

    @patch('taxi.external.billing.create_order')
    @async.inline_callbacks
    def create_order(
            billing_service, uid, user_ip, product_id, order_id, region_id,
            due_date, due_tz, log_extra=None):
        yield
        pass

    settings.PERSONAL_APIKEY = 'qwerty'
    proc = (yield dbh.order_proc.Doc.find_one_by_id(order_id))
    while _working(proc):
        yield processing.do_processing_iteration_throw(order_id)
        yield changes_handler._process_change._task_function(
            order_id, 'payment'
        )
        yield processing.do_processing_iteration_throw(order_id)
        yield invoice_handler.update_transactions_iteration(order_id)
        proc = (yield dbh.order_proc.Doc.find_one_by_id(order_id))

    order = (yield dbh.orders.Doc.find_one_by_id(order_id))
    assert order.payment_tech.type == 'cash'


@pytest.mark.translations([
    ('tariff', 'econom', 'ru', u'Эконом'),
    ('notify', 'time', 'ru', u'%I:%M %p'),
    ('notify', 'sms.on_assigned', 'ru', u'kek'),
])
@pytest.mark.filldb(
    order_proc='complements',
    orders='complements',
    user_phones='for_card_to_card',
    parks='for_card_to_card',
    cards='for_card_to_card',
    cities='for_card_to_card',
    tariffs='for_card_to_card',
    tariff_settings='for_card_to_card',
    users='for_card_to_card',
    dbdrivers='for_card_to_card',
    dbparks='for_card_to_card',
    cardlocks='for_card_to_card',
)
@pytest.mark.load_data(
    countries='for_card_to_card',
)
@pytest.mark.parametrize(
    'order_id', [
        'd0be4a4b4b2116ccc78c2cbdc295408f'
    ]
)
@pytest.mark.filldb(orders='for_card_to_card')
@pytest.inline_callbacks
def test_composite_reset(patch, order_id):
    @patch('taxi.external.taxi_protocol.create_order')
    @async.inline_callbacks
    def mock_create_order(order_id, log_extra=None):
        yield

    @patch('taxi.external.billing.create_order')
    @async.inline_callbacks
    def create_order(
            billing_service, uid, user_ip, product_id, order_id, region_id,
            due_date, due_tz, log_extra=None):
        yield
        pass

    @patch('taxi.internal.notifications.order._send_notification')
    def patch_send_notification(*args, **kwargs):
        return

    order = (yield dbh.orders.Doc.find_one_by_id(order_id))
    assert order.payment_tech.complements == [
        {'type': 'personal_wallet', 'payment_method_id': 'wallet_id/1123456'}
    ]

    order_proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    assert order_proc.payment_tech.complements == [
        {'type': 'personal_wallet', 'payment_method_id': 'wallet_id/1123456'}
    ]

    yield processing.do_processing_iteration_throw(order_id)

    order = (yield dbh.orders.Doc.find_one_by_id(order_id))
    assert order.payment_tech.complements == []

    order_proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    assert order_proc.payment_tech.complements == []


@pytest.mark.translations([
    ('tariff', 'econom', 'ru', u'Эконом'),
    ('notify', 'time', 'ru', u'%I:%M %p'),
    ('notify', 'sms.on_assigned', 'ru', u'kek'),
])
@pytest.mark.filldb(
    order_proc='for_card_to_card',
    user_phones='for_card_to_card',
    parks='for_card_to_card',
    cards='for_card_to_card',
    cities='for_card_to_card',
    tariffs='for_card_to_card',
    tariff_settings='for_card_to_card',
    users='for_card_to_card',
    dbdrivers='for_card_to_card',
    dbparks='for_card_to_card',
    cardlocks='for_card_to_card',
)
@pytest.mark.load_data(
    countries='for_card_to_card',
)
@pytest.mark.parametrize(
    'order_id', [
        'cash_to_agent_order'
    ]
)
@pytest.mark.filldb(orders='for_card_to_card')
@pytest.mark.config(
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
    BILLING_AGENT_IDS=['agent_007'],
)
@pytest.inline_callbacks
def test_change_from_cash_to_agent(
        patch, order_id, userapi_get_user_phone_mock, personal_retrieve_mock,
        mock_processing_antifraud, mock_send_event,
):
    @patch('taxi.external.taxi_protocol.create_order')
    @async.inline_callbacks
    def mock_create_order(order_id, log_extra=None):
        yield

    @patch('taxi.external.billing.create_order')
    @async.inline_callbacks
    def create_order(
            billing_service, uid, user_ip, product_id, order_id, region_id,
            due_date, due_tz, log_extra=None):
        yield
        pass

    @patch('taxi.external.transactions.v2_invoice_retrieve')
    @async.inline_callbacks
    def v2_invoice_retrieve(
            id_, prefer_transactions_data, tvm_src_service, log_extra=None,
    ):
        async.return_value({
            'cleared': [],
            'commit_version': 1,
            'held': [],
            'is_refundable': True,
            'operation_info': {
                'version': 1
            },
            'transactions': [],
            'transactions_ready': True
        })
        yield

    settings.PERSONAL_APIKEY = 'qwerty'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    while _working(proc):
        yield processing.do_processing_iteration_throw(order_id)
        yield changes_handler._process_change._task_function(
            order_id, 'payment'
        )
        yield processing.do_processing_iteration_throw(order_id)
        yield invoice_handler.update_transactions_iteration(order_id)
        proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert order.payment_tech.type == 'agent'
    assert order.payment_tech.main_card_payment_id == 'agent_007'


@pytest.mark.filldb(
    orders='transaction',
    order_proc='transaction',
)
@pytest.mark.parametrize(
    'orders_query,proc_query,expected_id_by_type,expected_id_by_updated',
    (
        (
            # No transactions in billing_tech
            {'$set': {'billing_tech.transactions': []}},
            {'$pop': {'changes.objects': 1}},
            None,
            None,
        ),
        (
            # Only one fail transaction in billing_tech
            # Change have same type as transaction
            # change.created > transaction.created
            {'$pop': {'billing_tech.transactions': -1}},
            {'$pop': {'changes.objects': 1}},
            'fail_transaction_id',
            'fail_transaction_id',
        ),
        (
            # Transaction and change have different card id
            {'$pop': {'billing_tech.transactions': 1}},
            {'$pop': {'changes.objects': 1}},
            None,
            'success_transaction_id',
        ),
        (
            # In billing_tech there are two transactions
            # with different statuses and different card ids
            None,
            {'$pop': {'changes.objects': 1}},
            'fail_transaction_id',
            'success_transaction_id',
        ),
        (
            # Transaction with same card id as change was
            # created earlier than change
            {'$set': {'payment_tech.main_card_billing_id': 'x1234'}},
            {'$pop': {'changes.objects': -1}},
            None,
            'success_transaction_id',
        ),
    ),
)
@pytest.mark.parametrize('is_exp_enabled', (True, False))
@pytest.inline_callbacks
def test_find_transaction_by_payment_type(
        mock_fix_change_payment_in_py2_config,
        orders_query,
        proc_query,
        expected_id_by_type,
        expected_id_by_updated,
        is_exp_enabled,
):
    mock_fix_change_payment_in_py2_config(is_exp_enabled)

    if orders_query:
        yield db.orders.update({'_id': 'order_id'}, orders_query)
    if proc_query:
        yield db.order_proc.update({'_id': 'order_id'}, proc_query)

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    res_status, res_eta, res_extra_values, res_event_info = (
        yield changes_handler._handle_change_payment(proc)
    )

    change_transaction_id = (
        expected_id_by_type if is_exp_enabled else expected_id_by_updated
    )
    if change_transaction_id == 'success_transaction_id':
        expected_change_status = 'applying'
    elif change_transaction_id == 'fail_transaction_id':
        expected_change_status = 'rejecting'
    else:
        expected_change_status = 'processing'
    assert res_status == expected_change_status
