# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_grocery_invoices import consts
from tests_grocery_invoices import eats_receipts_helpers
from tests_grocery_invoices import helpers
from tests_grocery_invoices import models
from tests_grocery_invoices import pytest_marks
from tests_grocery_invoices.stq.configs import france as france_configs
from tests_grocery_invoices.stq.configs import (
    great_britain as great_britain_configs,
)


OPERATION_ID = 'operation_id'
TERMINAL_ID = 'terminal_id'

STQ_TASK_ID = 'stq_task_id'

POLLING_SENSOR = 'grocery_invoices_receipt_polling_state_metrics'
CALLBACK_SENSOR = 'grocery_invoices_receipt_callback_metrics'
STQ_ERROR_SENSOR = 'grocery_invoices_stq_error_metrics'

CART_ITEMS_ISR = helpers.make_cart_items(models.Country.Israel)
CART_ITEMS_RUS = helpers.make_cart_items(models.Country.Russia)
CART_ITEMS_FRA = helpers.make_cart_items(models.Country.France)

TRIES = pytest.mark.parametrize('tries', [1, 2])


@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest_marks.RUSSIA_PAYMENT_TYPES
@pytest_marks.RECEIPT_DATA_TYPES
@TRIES
async def test_receipt_metrics_polling_done_ru(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        taxi_grocery_invoices_monitor,
        testpoint,
        run_grocery_invoices_receipt_polling,
        receipt_type,
        payment_type,
        receipt_data_type,
        eats_receipts_service,
        tries,
):
    country = models.Country.Russia

    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    @testpoint('metrics_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    payment_method = {'type': payment_type, 'id': 'payment-id'}
    params = {
        'source': eats_receipts_helpers.eats_receipts_stq_source(
            eats_receipts_service,
        ),
    }

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_invoices_monitor, sensor=POLLING_SENSOR,
    ) as collector:
        for exec_tries in range(tries):
            await run_grocery_invoices_receipt_polling(
                receipt_type=receipt_type,
                country=country.name,
                receipt_data_type=receipt_data_type,
                payment_method=payment_method,
                params=params,
                exec_tries=exec_tries,
            )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1

    assert metric.labels == {
        'sensor': POLLING_SENSOR,
        'receipt_polling_state': 'done',
        'country': country.name,
        'receipt_source': eats_receipts_helpers.eats_receipts_stq_source(
            eats_receipts_service,
        ),
        'receipt_type': receipt_type,
    }

    assert repeated_task_execution_tp.times_called == tries - 1


@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest_marks.RUSSIA_PAYMENT_TYPES
@TRIES
async def test_receipt_metrics_polling_pending_ru(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        taxi_grocery_invoices_monitor,
        testpoint,
        run_grocery_invoices_callback,
        receipt_type,
        payment_type,
        tries,
        eats_receipts_service,
):
    country = models.Country.Russia

    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    @testpoint('metrics_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    receipt_data_type = 'order'
    payment_method = {'type': payment_type, 'id': 'payment-id'}

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_invoices_monitor, sensor=POLLING_SENSOR,
    ) as collector:
        for exec_tries in range(tries):
            await run_grocery_invoices_callback(
                receipt_type=receipt_type,
                country=country.name,
                receipt_data_type=receipt_data_type,
                payment_method=payment_method,
                exec_tries=exec_tries,
            )

    metric = collector.get_single_collected_metric()

    if payment_type in ('badge', 'corp'):
        assert not metric

        assert repeated_task_execution_tp.times_called == 0
    else:
        assert metric.value == 1

        assert metric.labels == {
            'sensor': POLLING_SENSOR,
            'receipt_polling_state': 'pending',
            'country': country.name,
            'receipt_source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
            'receipt_type': receipt_type,
        }

        assert repeated_task_execution_tp.times_called == tries - 1


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest_marks.RECEIPT_DATA_TYPES
@pytest_marks.ISRAEL_PAYMENT_TYPES
@TRIES
async def test_receipt_metrics_callback_il(
        grocery_orders,
        grocery_cart,
        easy_count,
        personal,
        cardstorage,
        taxi_grocery_invoices_monitor,
        testpoint,
        run_grocery_invoices_callback,
        default_isr_receipt,
        receipt_type,
        receipt_data_type,
        payment_type,
        tries,
):
    country = models.Country.Israel

    @testpoint('metrics_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    payment_method = {'type': payment_type, 'id': 'payment-id'}

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_invoices_monitor, sensor=CALLBACK_SENSOR,
    ) as collector:
        for exec_tries in range(tries):
            await run_grocery_invoices_callback(
                receipt_type=receipt_type,
                country=country.name,
                receipt_data_type=receipt_data_type,
                payment_method=payment_method,
                exec_tries=exec_tries,
            )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1

    assert metric.labels == {
        'sensor': CALLBACK_SENSOR,
        'country': country.name,
        'receipt_source': consts.EASY_COUNT_SOURCE,
        'receipt_type': receipt_type,
    }

    assert repeated_task_execution_tp.times_called == tries - 1


@france_configs.RECEIPT_PARAMS
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest_marks.EUROPE_PAYMENT_TYPES
@pytest_marks.RECEIPT_DATA_TYPES
@TRIES
async def test_receipt_metrics_callback_fr(
        grocery_orders,
        grocery_cart,
        document_templator,
        personal,
        cardstorage,
        taxi_grocery_invoices_monitor,
        testpoint,
        run_grocery_invoices_callback,
        receipt_type,
        payment_type,
        receipt_data_type,
        tries,
):
    country = models.Country.France

    @testpoint('metrics_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_FRA)

    payment_method = {'type': payment_type, 'id': 'payment-id'}

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_invoices_monitor, sensor=CALLBACK_SENSOR,
    ) as collector:
        for exec_tries in range(tries):
            await run_grocery_invoices_callback(
                receipt_type=receipt_type,
                country=country.name,
                receipt_data_type=receipt_data_type,
                payment_method=payment_method,
                exec_tries=exec_tries,
            )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1

    assert metric.labels == {
        'sensor': CALLBACK_SENSOR,
        'country': country.name,
        'receipt_source': consts.FRANCE_DOCUMENT_TEMPLATOR_SOURCE,
        'receipt_type': receipt_type,
    }

    assert repeated_task_execution_tp.times_called == tries - 1


@great_britain_configs.RECEIPT_PARAMS
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest_marks.EUROPE_PAYMENT_TYPES
@pytest_marks.RECEIPT_DATA_TYPES
@TRIES
async def test_receipt_metrics_callback_gbr(
        grocery_orders,
        grocery_cart,
        document_templator,
        personal,
        cardstorage,
        stq_runner,
        taxi_grocery_invoices_monitor,
        testpoint,
        run_grocery_invoices_callback,
        receipt_type,
        payment_type,
        receipt_data_type,
        tries,
):
    country = models.Country.GreatBritain

    @testpoint('metrics_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_FRA)

    payment_method = {'type': payment_type, 'id': 'payment-id'}

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_invoices_monitor, sensor=CALLBACK_SENSOR,
    ) as collector:
        for exec_tries in range(tries):
            await run_grocery_invoices_callback(
                receipt_type=receipt_type,
                country=country.name,
                receipt_data_type=receipt_data_type,
                payment_method=payment_method,
                exec_tries=exec_tries,
            )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1

    assert metric.labels == {
        'sensor': CALLBACK_SENSOR,
        'country': country.name,
        'receipt_source': consts.GREAT_BRITAIN_DOCUMENT_TEMPLATOR_SOURCE,
        'receipt_type': receipt_type,
    }

    assert repeated_task_execution_tp.times_called == tries - 1


async def test_receipt_polling_stq_error(
        grocery_orders,
        grocery_cart,
        taxi_grocery_invoices_monitor,
        run_grocery_invoices_receipt_polling,
):
    country = models.Country.France

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_invoices_monitor, sensor=STQ_ERROR_SENSOR,
    ) as collector:
        await run_grocery_invoices_receipt_polling(
            country=country.name, expect_fail=True,
        )

    metric = collector.get_single_collected_metric()

    assert metric.labels == {
        'sensor': STQ_ERROR_SENSOR,
        'error_code': 'unsupported_country::stq_receipt_polling',
        'country': country.name,
    }


async def test_callback_stq_error(
        grocery_orders,
        grocery_cart,
        taxi_grocery_invoices_monitor,
        run_grocery_invoices_callback,
):
    country = models.Country.Belarus

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_invoices_monitor, sensor=STQ_ERROR_SENSOR,
    ) as collector:
        await run_grocery_invoices_callback(
            country=country.name, expect_fail=True,
        )

    metric = collector.get_single_collected_metric()

    assert metric.labels == {
        'sensor': STQ_ERROR_SENSOR,
        'error_code': 'unsupported_country::stq_callback',
        'country': country.name,
    }
