# pylint: disable=invalid-name,C0302,E0401
import datetime

from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_grocery_invoices import consts
from tests_grocery_invoices import eats_receipts_helpers
from tests_grocery_invoices import helpers
from tests_grocery_invoices import models
from tests_grocery_invoices import pytest_marks
from tests_grocery_invoices.plugins import configs
from tests_grocery_invoices.plugins import mock_eats_core_receipts
from tests_grocery_invoices.plugins import mock_selfemployed


COUNTRY = models.Country.Russia

RECEIPT_PROCDUCT_ITEMS = helpers.make_product_receipt(COUNTRY)
RECEIPT_DELIVERY_ITEMS = helpers.make_delivery_receipt(COUNTRY)
RECEIPT_ITEMS = [*RECEIPT_PROCDUCT_ITEMS, *RECEIPT_DELIVERY_ITEMS]
CART_ITEMS = helpers.make_cart_items(COUNTRY)

RECEIPT_TOTAL = '122.04'

STQ_ERROR_SENSOR = 'grocery_invoices_stq_error_metrics'


@pytest.fixture
def _run_stq(run_grocery_invoices_receipt_polling):
    async def _do(items=None, **kwargs):
        items = items or RECEIPT_PROCDUCT_ITEMS

        await run_grocery_invoices_receipt_polling(
            items=models.items_to_json(items), **kwargs,
        )

    return _do


@pytest.fixture(name='check_eats_receipts_times_called')
def _check_eats_receipts_times_called(eats_receipts, eats_core_receipts):
    def _inner(service, times_called):
        if eats_receipts_helpers.is_eats_core_receipts(service):
            check_called = eats_core_receipts.times_receipts_info_called()
            assert check_called == times_called
        else:
            assert eats_receipts.times_receipt_called() == times_called

    return _inner


@pytest.fixture(name='mock_eats_receipt_info')
def _mock_eats_receipt_info(eats_receipts, eats_core_receipts):
    def _inner(service, **kwargs):
        if eats_receipts_helpers.is_eats_core_receipts(service):
            eats_core_receipts.mock_receipt_info(**kwargs)
        else:
            eats_receipts.mock_receipt_info(**kwargs)

    return _inner


@pytest.fixture(name='check_eats_receipt_info')
def _check_eats_receipt_info(eats_receipts, eats_core_receipts):
    def _inner(service):
        if eats_receipts_helpers.is_eats_core_receipts(service):
            eats_core_receipts.check_receipt_info(
                orderNr=consts.ORDER_ID, documentId=consts.EXTERNAL_PAYMENT_ID,
            )
        else:
            eats_receipts.check_receipt(document_id=consts.EXTERNAL_PAYMENT_ID)

    return _inner


@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'receipt_type', [consts.TYPE_PAYMENT, consts.TYPE_REFUND],
)
async def test_eats_core_receipt(
        grocery_invoices_configs,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        stq,
        check_eats_receipts_times_called,
        check_eats_receipt_info,
        check_billing_tlog_callback_stq_event,
        _run_stq,
        eats_receipts_service,
        receipt_type,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)
    supplier_tin = 'supplier-tin'

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    check_eats_receipt_info(
        service=eats_receipts_helpers.eats_receipts_stq_source(
            eats_receipts_service,
        ),
    )

    await _run_stq(
        receipt_type=receipt_type,
        country=COUNTRY.name,
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
        supplier_tin=supplier_tin,
    )

    check_eats_receipts_times_called(
        service=eats_receipts_service, times_called=1,
    )

    # without reschedule
    assert stq.grocery_invoices_receipt_polling.times_called == 0

    check_billing_tlog_callback_stq_event(
        info=dict(
            order_id=consts.ORDER_ID,
            country=COUNTRY.name,
            receipt_type=receipt_type,
            receipt_data_type='order',
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            operation_id=consts.OPERATION_ID,
            terminal_id=consts.TERMINAL_ID,
            items=models.items_to_json(RECEIPT_PROCDUCT_ITEMS),
            payment_method=consts.DEFAULT_PAYMENT_METHOD,
            payment_finished=consts.PAYMENT_FINISHED,
            supplier_tin=supplier_tin,
        ),
    )

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID, receipt_id=consts.EXTERNAL_PAYMENT_ID,
    )
    assert receipt is not None
    assert receipt.receipt_data_type == consts.ORDER_RECEIPT_DATA_TYPE
    assert receipt.receipt_type == receipt_type
    assert receipt.link == mock_eats_core_receipts.DEFAULT_URL
    assert (
        receipt.receipt_source
        == eats_receipts_helpers.eats_receipts_stq_source(
            eats_receipts_service,
        )
    )
    assert receipt.payload['country'] == COUNTRY.name


@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'receipt_type', [consts.TYPE_PAYMENT, consts.TYPE_REFUND],
)
async def test_eats_core_receipt_expat_flow(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        grocery_invoices_db,
        stq,
        check_eats_receipts_times_called,
        check_eats_receipt_info,
        check_billing_tlog_callback_stq_event,
        _run_stq,
        receipt_type,
):
    receipt_data_type = 'order'
    eats_receipts_service = consts.EATS_RECEIPTS
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    item = {'item_id': 'item_id', 'price': '115.34', 'quantity': '1'}

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    check_eats_receipt_info(
        service=eats_receipts_helpers.eats_receipts_stq_source(
            eats_receipts_service,
        ),
    )

    items = [
        helpers.make_receipt_item(
            item_id=item['item_id'],
            price=item['price'],
            quantity=item['quantity'],
            vat='20',
            title='item_title',
            item_type='expat_coupon',
        ),
    ]

    await _run_stq(
        receipt_type=receipt_type,
        country=COUNTRY.name,
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
        items=items,
        currency=COUNTRY.currency,
    )

    check_eats_receipts_times_called(
        service=eats_receipts_service, times_called=1,
    )

    # without reschedule
    assert stq.grocery_invoices_receipt_polling.times_called == 0

    check_billing_tlog_callback_stq_event(
        info=dict(
            order_id=consts.ORDER_ID,
            country=COUNTRY.name,
            receipt_type=receipt_type,
            receipt_data_type=receipt_data_type,
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            operation_id=consts.OPERATION_ID,
            terminal_id=consts.TERMINAL_ID,
            items=[
                {
                    'item_id': item['item_id'],
                    'price': item['price'],
                    'quantity': item['quantity'],
                    'item_type': 'expat_coupon',
                },
            ],
            payment_method=consts.DEFAULT_PAYMENT_METHOD,
            payment_finished=consts.PAYMENT_FINISHED,
            currency=COUNTRY.currency,
        ),
    )

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID, receipt_id=consts.EXTERNAL_PAYMENT_ID,
    )
    assert receipt is not None
    assert len(receipt.items) == 1

    receipt_item = receipt.items[0]
    assert receipt_item['item_id'] == item['item_id']
    assert receipt_item['item_type'] == 'expat_coupon'
    assert receipt_item['quantity'] == item['quantity']
    assert receipt_item['price'] == item['price']


@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'courier_info', [None, consts.DELIVERY_SERVICE_COURIER],
)
async def test_no_courier_info_tlog(
        grocery_invoices_configs,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        _run_stq,
        courier_info,
):
    eats_receipts_service = consts.EATS_RECEIPTS
    receipt_type = consts.TYPE_PAYMENT
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    grocery_orders.order.update(courier_info=courier_info)

    await _run_stq(
        task_id=consts.TASK_ID,
        receipt_type=receipt_type,
        country=COUNTRY.name,
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
        expect_fail=(courier_info is None),
        items=RECEIPT_ITEMS,
    )

    if courier_info is None:
        pg_task = grocery_invoices_db.load_task(consts.TASK_ID)
        assert pg_task.status == 'failed'
        assert pg_task.params['error_code'] == 'no_courier_info::tlog'


@pytest_marks.MARK_NOW
async def test_fns_receipt_payment(
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        selfemployed,
        stq,
        check_billing_tlog_callback_stq_event,
        _run_stq,
):
    receipt_type = consts.TYPE_PAYMENT
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    selfemployed.check_get_income_result(
        message_id=selfemployed.default_message_id,
    )
    selfemployed.set_get_income_result_response(
        ProcessingStatus='COMPLETED',
        Message={
            'ReceiptId': selfemployed.receipt_id,
            'Link': selfemployed.receipt_url,
        },
    )

    await _run_stq(
        receipt_type=receipt_type,
        country=COUNTRY.name,
        params={'source': consts.FNS_SOURCE},
        send_billing_event=False,
        polling_id=selfemployed.default_message_id,
    )

    assert selfemployed.times_get_income_result_called() == 1

    # without reschedule
    assert stq.grocery_invoices_receipt_polling.times_called == 0

    check_billing_tlog_callback_stq_event(times_called=0)

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID, receipt_id=selfemployed.receipt_id,
    )
    assert receipt is not None
    assert receipt.receipt_data_type == consts.ORDER_RECEIPT_DATA_TYPE
    assert receipt.receipt_type == receipt_type
    assert receipt.link == selfemployed.receipt_url
    assert receipt.receipt_source == consts.FNS_SOURCE
    assert receipt.payload['country'] == COUNTRY.name


@pytest_marks.MARK_NOW
async def test_fns_receipt_refund(
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        selfemployed,
        stq,
        check_billing_tlog_callback_stq_event,
        default_fns_receipt,
        _run_stq,
):
    receipt_type = consts.TYPE_REFUND
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    grocery_orders.order.update(courier_info=consts.SELF_EMPLOYED_COURIER)

    selfemployed.check_get_revert_income_result(
        message_id=selfemployed.default_message_id,
    )
    selfemployed.set_get_revert_result_response(
        ProcessingStatus='COMPLETED', Message={'RequestResult': 'DELETED'},
    )

    await _run_stq(
        receipt_type=receipt_type,
        country=COUNTRY.name,
        params={'source': consts.FNS_SOURCE},
        send_billing_event=False,
        polling_id=selfemployed.default_message_id,
    )

    assert selfemployed.times_get_revert_result_called() == 1

    # without reschedule
    assert stq.grocery_invoices_receipt_polling.times_called == 0

    check_billing_tlog_callback_stq_event(times_called=0)

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID,
        receipt_id=f'{selfemployed.receipt_id}-refund',
    )
    assert receipt is not None
    assert receipt.receipt_data_type == consts.ORDER_RECEIPT_DATA_TYPE
    assert receipt.receipt_type == receipt_type
    assert receipt.link == selfemployed.refund_receipt_url
    assert receipt.receipt_source == consts.FNS_SOURCE
    assert receipt.payload['country'] == COUNTRY.name


@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.MARK_NOW
@configs.GROCERY_RECEIPTS_POLLING_POLICY
async def test_eats_receipt_not_ready(
        grocery_invoices_configs,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        stq,
        mock_eats_receipt_info,
        _run_stq,
        eats_receipts_service,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    mock_eats_receipt_info(
        service=eats_receipts_service, ofd_info={}, ofdReceiptInfo=None,
    )

    await _run_stq(
        country=COUNTRY.name,
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
    )

    # with reschedule
    assert stq.grocery_invoices_receipt_polling.times_called == 1

    # no billing event
    assert stq.grocery_payments_billing_tlog_callback.times_called == 0

    assert not grocery_invoices_db.load_receipts(order_id=consts.ORDER_ID)


@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.MARK_NOW
@configs.GROCERY_RECEIPTS_POLLING_POLICY
async def test_eats_receipt_404(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        stq,
        mock_eats_receipt_info,
        _run_stq,
        eats_receipts_service,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    mock_eats_receipt_info(service=eats_receipts_service, error404=True)

    await _run_stq(
        country=COUNTRY.name,
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
    )

    # with reschedule
    assert stq.grocery_invoices_receipt_polling.times_called == 1

    # no billing event
    assert stq.grocery_payments_billing_tlog_callback.times_called == 0


@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'receipt_type', [consts.TYPE_PAYMENT, consts.TYPE_REFUND],
)
async def test_fns_receipt_not_ready(
        grocery_orders,
        grocery_cart,
        selfemployed,
        stq,
        check_billing_tlog_callback_stq_event,
        _run_stq,
        receipt_type,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    selfemployed.check_get_income_result(message_id=consts.EXTERNAL_PAYMENT_ID)
    selfemployed.set_get_income_result_response(
        status_code=selfemployed.response.processing['status_code'],
        **selfemployed.response.processing['body'],
    )

    await _run_stq(
        receipt_type=receipt_type,
        country=COUNTRY.name,
        params={'source': consts.FNS_SOURCE},
        send_billing_event=False,
    )

    if receipt_type == consts.TYPE_PAYMENT:
        assert selfemployed.times_get_income_result_called() == 1
    else:
        assert selfemployed.times_get_revert_result_called() == 1
    assert grocery_orders.append_receipt_times_called() == 0

    assert stq.grocery_invoices_receipt_polling.times_called == 1

    check_billing_tlog_callback_stq_event(times_called=0)


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'receipt_type', [consts.TYPE_PAYMENT, consts.TYPE_REFUND],
)
@pytest.mark.parametrize(
    'receipt_data_type',
    [consts.DELIVERY_RECEIPT_DATA_TYPE, consts.TIPS_RECEIPT_DATA_TYPE],
)
async def test_fns_receipt_expired(
        grocery_orders,
        grocery_cart,
        selfemployed,
        personal,
        stq,
        check_billing_tlog_callback_stq_event,
        check_receipt_polling_stq_event,
        default_fns_receipt,
        _run_stq,
        taxi_grocery_invoices_monitor,
        receipt_type,
        receipt_data_type,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)
    grocery_orders.order.update(courier_info=consts.SELF_EMPLOYED_COURIER)

    selfemployed.set_get_income_result_response(
        status_code=selfemployed.response.not_found['status_code'],
        **selfemployed.response.not_found['body'],
    )

    new_message_id = 'new-message-id'

    selfemployed.set_register_income_response(message_id=new_message_id)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_invoices_monitor, sensor=STQ_ERROR_SENSOR,
    ) as collector:
        await _run_stq(
            receipt_type=receipt_type,
            receipt_data_type=receipt_data_type,
            country=COUNTRY.name,
            params={'source': consts.FNS_SOURCE},
            send_billing_event=False,
        )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1

    assert metric.labels == {
        'sensor': STQ_ERROR_SENSOR,
        'error_code': 'fns_receipt_expired',
        'country': COUNTRY.name,
    }

    if receipt_type == consts.TYPE_PAYMENT:
        assert selfemployed.times_get_income_result_called() == 1
        assert selfemployed.times_register_income_called() == 1
    else:
        assert selfemployed.times_get_revert_result_called() == 1
        assert selfemployed.times_revert_income_called() == 1

    assert stq.grocery_invoices_receipt_polling.times_called == 1
    event_id = helpers.make_polling_task_id(
        new_message_id, receipt_data_type, consts.FNS_SOURCE,
    )
    check_receipt_polling_stq_event(
        stq_event_id=event_id, polling_id=new_message_id,
    )
    check_billing_tlog_callback_stq_event(times_called=0)


@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'receipt_data_type',
    [consts.DELIVERY_RECEIPT_DATA_TYPE, consts.TIPS_RECEIPT_DATA_TYPE],
)
async def test_fns_receipt_duplicate(
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        selfemployed,
        check_billing_tlog_callback_stq_event,
        _run_stq,
        receipt_data_type,
):
    receipt_type = consts.TYPE_PAYMENT

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    selfemployed.check_get_income_result(message_id=consts.EXTERNAL_PAYMENT_ID)
    selfemployed.set_get_income_result_response(
        status_code=selfemployed.response.duplicate['status_code'],
        **selfemployed.response.duplicate['body'],
    )

    await _run_stq(
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        country=COUNTRY.name,
        params={'source': consts.FNS_SOURCE},
        send_billing_event=False,
    )

    assert selfemployed.times_get_income_result_called() == 1

    check_billing_tlog_callback_stq_event(times_called=0)

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID, receipt_id=selfemployed.receipt_id,
    )
    assert receipt is not None
    assert receipt.receipt_data_type == receipt_data_type
    assert receipt.receipt_type == receipt_type
    assert receipt.link == selfemployed.receipt_url
    assert receipt.receipt_source == consts.FNS_SOURCE


@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'receipt_data_type',
    [consts.DELIVERY_RECEIPT_DATA_TYPE, consts.TIPS_RECEIPT_DATA_TYPE],
)
async def test_fns_receipt_already_deleted(
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        selfemployed,
        check_billing_tlog_callback_stq_event,
        default_fns_receipt,
        _run_stq,
        receipt_data_type,
):
    """
    Test when we create new refund receipt on polling id expiration,
    but the refund receipt was already created for this payment
    """
    receipt_type = consts.TYPE_REFUND

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    selfemployed.check_get_income_result(message_id=consts.EXTERNAL_PAYMENT_ID)
    selfemployed.set_get_income_result_response(
        status_code=selfemployed.response.already_deleted['status_code'],
        **selfemployed.response.already_deleted['body'],
    )

    await _run_stq(
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        country=COUNTRY.name,
        params={'source': consts.FNS_SOURCE},
        send_billing_event=False,
    )

    assert selfemployed.times_get_revert_result_called() == 1

    check_billing_tlog_callback_stq_event(times_called=0)

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID,
        receipt_id=f'{selfemployed.receipt_id}-refund',
    )
    assert receipt is not None
    assert receipt.receipt_data_type == receipt_data_type
    assert receipt.receipt_type == receipt_type
    assert receipt.link == selfemployed.refund_receipt_url
    assert receipt.receipt_source == consts.FNS_SOURCE


@pytest_marks.EATS_RECEIPTS_SERVICES
@configs.GROCERY_RECEIPTS_POLLING_POLICY
@pytest.mark.parametrize('delta, expect_fail', [(-1, False), (1, True)])
async def test_eats_receipts_receipt_not_ready_error_after(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        stq,
        mocked_time,
        mock_eats_receipt_info,
        _run_stq,
        delta,
        expect_fail,
        eats_receipts_service,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    now_delta = datetime.timedelta(
        seconds=configs.POLICY_ERROR_AFTER_SECONDS + delta,
    )
    mocked_time.set(consts.NOW_DT + now_delta)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    mock_eats_receipt_info(
        service=eats_receipts_service, ofd_info={}, ofdReceiptInfo=None,
    )

    await _run_stq(
        country=COUNTRY.name,
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
        expect_fail=expect_fail,
    )

    assert grocery_orders.append_receipt_times_called() == 0

    # no billing event
    assert stq.grocery_payments_billing_tlog_callback.times_called == 0


@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'receipt_type', [consts.TYPE_PAYMENT, consts.TYPE_REFUND],
)
async def test_pg_tasks_success(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        grocery_invoices_db,
        _run_stq,
        eats_receipts_service,
        receipt_type,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    await _run_stq(
        receipt_type=receipt_type,
        country=COUNTRY.name,
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
    )

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task == models.Task(
        task_id=consts.TASK_ID,
        task_type='receipt_polling',
        order_id=consts.ORDER_ID,
        status='success',
        args={
            'items': models.items_to_json(RECEIPT_PROCDUCT_ITEMS),
            'country': COUNTRY.name,
            'order_id': consts.ORDER_ID,
            'terminal_id': consts.TERMINAL_ID,
            'operation_id': consts.OPERATION_ID,
            'receipt_type': receipt_type,
            'payment_method': consts.DEFAULT_PAYMENT_METHOD,
            'payment_finished': consts.PAYMENT_FINISHED,
            'receipt_data_type': 'order',
            'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
        },
        result_payload={'receipt_url': 'https://ofd.ru/url'},
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
            'country_iso3': COUNTRY.country_iso3,
            'polling_id': consts.EXTERNAL_PAYMENT_ID,
            'exec_tries': 1,
        },
    )


@pytest_marks.MARK_NOW
async def test_pg_task_not_ready_in_process(
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        mock_eats_receipt_info,
        _run_stq,
):
    eats_receipts_service = 'eats_receipts'

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    mock_eats_receipt_info(
        service=eats_receipts_service, ofd_info={}, ofdReceiptInfo=None,
    )

    await _run_stq(
        country=COUNTRY.name,
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
    )

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task.status == 'in_process'


@pytest_marks.MARK_NOW
async def test_pg_tasks_failed(
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        selfemployed,
        _run_stq,
):
    receipt_type = consts.TYPE_PAYMENT
    receipt_data_type = consts.DELIVERY_RECEIPT_DATA_TYPE

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    selfemployed.set_get_income_result_response(
        status_code=selfemployed.response.not_found['status_code'],
        **selfemployed.response.not_found['body'],
    )

    await _run_stq(
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        country=COUNTRY.name,
        params={'source': consts.FNS_SOURCE},
        send_billing_event=False,
        expect_fail=True,
    )

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task.status == 'failed'
    assert db_task.params['polling_id'] == consts.EXTERNAL_PAYMENT_ID


async def tests_selfemployed_request_validation_error(
        grocery_orders,
        grocery_cart,
        selfemployed,
        _run_stq,
        grocery_invoices_db,
):
    receipt_data_type = consts.DELIVERY_RECEIPT_DATA_TYPE
    receipt_type = consts.TYPE_PAYMENT

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    selfemployed.set_get_income_result_response(
        status_code=selfemployed.response.request_validation_error[
            'status_code'
        ],
        **selfemployed.response.request_validation_error['body'],
    )

    await _run_stq(
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        country=COUNTRY.name,
        params={'source': consts.FNS_SOURCE},
        send_billing_event=False,
    )

    assert selfemployed.times_get_income_result_called() == 1

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task.status == 'canceled'


@pytest.mark.parametrize(
    'selfemployed_error, receipt_type',
    [
        (mock_selfemployed.SELFEMPLOYED_TAXPAYER_UNBOUND, consts.TYPE_PAYMENT),
        (mock_selfemployed.SELFEMPLOYED_TAXPAYER_UNBOUND, consts.TYPE_REFUND),
        (mock_selfemployed.SELFEMPLOYED_DUPLICATE, consts.TYPE_REFUND),
        (mock_selfemployed.SELFEMPLOYED_ALREADY_DELETED, consts.TYPE_PAYMENT),
        (mock_selfemployed.SELFEMPLOYED_INTERNAL_ERROR, consts.TYPE_PAYMENT),
        (
            mock_selfemployed.SELFEMPLOYED_TAXPAYER_UNREGISTERED,
            consts.TYPE_PAYMENT,
        ),
        (mock_selfemployed.SELFEMPLOYED_PARTNER_DENY, consts.TYPE_PAYMENT),
        (
            mock_selfemployed.SELFEMPLOYED_PERMISSION_NOT_GRANTED,
            consts.TYPE_PAYMENT,
        ),
        (
            mock_selfemployed.SELFEMPLOYED_RECEPT_ID_NOT_FOUND,
            consts.TYPE_PAYMENT,
        ),
    ],
)
@pytest_marks.MARK_NOW
async def tests_fns_resonse_400(
        grocery_orders,
        grocery_cart,
        selfemployed,
        _run_stq,
        grocery_invoices_db,
        grocery_invoices_configs,
        check_receipt_polling_stq_event,
        selfemployed_error,
        receipt_type,
):
    grocery_invoices_configs.set_error_policy(
        delay=datetime.timedelta(days=1),
        error_after=datetime.timedelta(days=1),
    )

    receipt_data_type = consts.DELIVERY_RECEIPT_DATA_TYPE

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    selfemployed.set_get_income_result_response(
        status_code=selfemployed_error['status_code'],
        **selfemployed_error['body'],
    )

    await _run_stq(
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        country=COUNTRY.name,
        params={'source': consts.FNS_SOURCE},
        send_billing_event=False,
    )

    if receipt_type == consts.TYPE_PAYMENT:
        assert selfemployed.times_get_income_result_called() == 1
    else:
        assert selfemployed.times_get_revert_result_called() == 1

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task.status == 'failed'
    assert db_task.params['error_code'] == selfemployed_error['error_code']

    check_receipt_polling_stq_event(times_called=1)


@pytest_marks.MARK_NOW
@configs.GROCERY_RECEIPTS_POLLING_POLICY
async def test_not_ready_policy_expired(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        stq,
        mock_eats_receipt_info,
        _run_stq,
        grocery_invoices_db,
):
    eats_receipts_service = 'eats_receipts'

    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    mock_eats_receipt_info(
        service=eats_receipts_service, ofd_info={}, ofdReceiptInfo=None,
    )

    two_days = datetime.timedelta(days=2)
    two_days_ago = (consts.NOW_DT - two_days).isoformat() + '+00:00'

    await _run_stq(
        country=COUNTRY.name,
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
        task_created=two_days_ago,
        expect_fail=True,
    )

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task.status == 'failed'
    assert db_task.params['error_code'] == 'task_deadline::stq_receipt_polling'
