import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'input_stq_args,'
    'expected_search_request,'
    'search_response,'
    'expected_store_request,'
    'expected_finish_requests,'
    'expected_business_rules_requests,'
    'business_rules_responses,'
    'expected_input_stq_fail',
    [
        # На входе:
        # - BillingCancelled.
        # На выходе:
        #  - Ничего
        #
        # Проверяем, что если не было оплаты, на выходе нет поручений
        # BillingCancelled финализируется
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(),
                    helpers.make_billing_doc(
                        doc_id=2147995772,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCancelled',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'cancelled_at': consts.ORDER_CANCELLED_DATE,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'order_cancel_id': (
                                consts.ORDER_CANCEL_ID_AS_STRING
                            ),
                            'is_payment_expected': False,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': consts.PLACE_ID_AS_STRING,
                            'currency': consts.CURRENCY,
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '2000',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                            ],
                            'order_type': 'native',
                            'flow_type': 'retail',
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=2147995772, status='complete',
                ),
            ],
            # expected_business_rules_requests
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='No PayoutOrders if picker didn\'t pay',
        ),
        # На входе:
        # - BillingCancelled.
        # На выходе:
        #  - Ничего
        #
        # Проверяем, что если была оплата на кассе
        # и ожидается списание с пользователя,
        # если нет инсентивов, то на выходе ничего
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(),
                    helpers.make_billing_doc(
                        doc_id=1,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCancelled',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'cancelled_at': consts.ORDER_CANCELLED_DATE,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'order_cancel_id': (
                                consts.ORDER_CANCEL_ID_AS_STRING
                            ),
                            'is_payment_expected': True,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': consts.PLACE_ID_AS_STRING,
                            'currency': consts.CURRENCY,
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '2000',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                            ],
                            'amount_picker_paid': '2000',
                            'order_type': 'native',
                            'flow_type': 'retail',
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            [helpers.make_storage_finish_request(doc_id=1, status='complete')],
            # expected_business_rules_requests
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='No PayoutOrders if payment expected',
        ),
        # На входе:
        # - BillingCancelled.
        # На выходе:
        #  - Поручения на инсентивы
        #
        # Проверяем, что если была оплата на кассе
        # и ожидается списание с пользователя,
        # проводим только инсентивы.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(),
                    helpers.make_billing_doc(
                        doc_id=1,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCancelled',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'cancelled_at': consts.ORDER_CANCELLED_DATE,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'order_cancel_id': (
                                consts.ORDER_CANCEL_ID_AS_STRING
                            ),
                            'is_payment_expected': True,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': consts.PLACE_ID_AS_STRING,
                            'currency': consts.CURRENCY,
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '1500',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '200',
                                    'type': 'marketing',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '300',
                                    'type': 'marketing_promocode',
                                    'product_type': 'retail',
                                },
                            ],
                            'amount_picker_paid': '2000',
                            'order_type': 'native',
                            'flow_type': 'retail',
                        },
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.START_PICKER_ORDER_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCancelled/1/'
                        'retail/retail/native/'
                        'marketing',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'marketing',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '200',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCancelled/1/'
                                'retail/retail/native/'
                                'marketing'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.START_PICKER_ORDER_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCancelled/1/'
                        'retail/retail/native/'
                        'marketing_promocode',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'marketing_promocode',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '300',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCancelled/1/'
                                'retail/retail/native/'
                                'marketing_promocode'
                            ),
                        },
                    ),
                ],
            ),
            # expected_finish_requests
            [helpers.make_storage_finish_request(doc_id=1, status='complete')],
            # expected_business_rules_requests
            [
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.START_PICKER_ORDER_DATE_UTC,
                    counteragent_type='courier',
                    counteragent_details={
                        'courier_id': consts.PICKER_ID,
                        'product_type': 'delivery',
                        'agreement_type': 'picker',
                    },
                ),
            ],
            # business_rules_response
            [
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='PayoutOrders for marketing and promocodes',
        ),
        # На входе:
        # - BillingCancelled.
        # На выходе:
        #  - Поручения на инсентивы и компенсация за продукты
        #
        # Проверяем, что если была оплата на кассе
        # и не ожидается списание с пользователя,
        # проводим плату за все продукты.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(),
                    helpers.make_billing_doc(
                        doc_id=1,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCancelled',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'cancelled_at': consts.ORDER_CANCELLED_DATE,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'order_cancel_id': (
                                consts.ORDER_CANCEL_ID_AS_STRING
                            ),
                            'is_payment_expected': False,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': consts.PLACE_ID_AS_STRING,
                            'currency': consts.CURRENCY,
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '1500',
                                    'type': 'our_refund',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '200',
                                    'type': 'marketing',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '300',
                                    'type': 'marketing_promocode',
                                    'product_type': 'retail',
                                },
                            ],
                            'amount_picker_paid': '2000',
                            'order_type': 'native',
                            'flow_type': 'retail',
                        },
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.START_PICKER_ORDER_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCancelled/1/'
                        'retail/retail/native/'
                        'our_refund',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'our_refund',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '1500',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCancelled/1/'
                                'retail/retail/native/'
                                'our_refund'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.START_PICKER_ORDER_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCancelled/1/'
                        'retail/retail/native/'
                        'marketing',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'marketing',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '200',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCancelled/1/'
                                'retail/retail/native/'
                                'marketing'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.START_PICKER_ORDER_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCancelled/1/'
                        'retail/retail/native/'
                        'marketing_promocode',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'marketing_promocode',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '300',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCancelled/1/'
                                'retail/retail/native/'
                                'marketing_promocode'
                            ),
                        },
                    ),
                ],
            ),
            # expected_finish_requests
            [helpers.make_storage_finish_request(doc_id=1, status='complete')],
            # expected_business_rules_requests
            [
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.START_PICKER_ORDER_DATE_UTC,
                    counteragent_type='courier',
                    counteragent_details={
                        'courier_id': consts.PICKER_ID,
                        'product_type': 'delivery',
                        'agreement_type': 'picker',
                    },
                ),
            ],
            # business_rules_response
            [
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='PayoutOrders for marketing, promocodes and our_refund',
        ),
        # На входе:
        # - BillingCancelled.
        # На выходе:
        #  - Ничего, падаем с ошибкой
        #
        # Проверяем, что если не пришел courier_id и transaction_date,
        # мы упадем
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(),
                    helpers.make_billing_doc(
                        doc_id=1,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCancelled',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'cancelled_at': consts.ORDER_CANCELLED_DATE,
                            'transaction_date': None,
                            'order_cancel_id': (
                                consts.ORDER_CANCEL_ID_AS_STRING
                            ),
                            'is_payment_expected': False,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': None,
                            'place_id': consts.PLACE_ID_AS_STRING,
                            'currency': consts.CURRENCY,
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '1500',
                                    'type': 'our_refund',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '200',
                                    'type': 'marketing',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '300',
                                    'type': 'marketing_promocode',
                                    'product_type': 'retail',
                                },
                            ],
                            'amount_picker_paid': '2000',
                            'order_type': 'native',
                            'flow_type': 'retail',
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            None,
            # expected_business_rules_requests
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            True,
            id='Failure when no courier id and transaction date',
        ),
        # На входе:
        # - BillingCancelled с двумя типами продукта
        # На выходе:
        #  - Выплаты инсентивов
        #
        # Проверяем, что првильно ходим в бизнес-рулс
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(),
                    helpers.make_billing_doc(
                        doc_id=1,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCancelled',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'cancelled_at': consts.ORDER_CANCELLED_DATE,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'order_cancel_id': (
                                consts.ORDER_CANCEL_ID_AS_STRING
                            ),
                            'is_payment_expected': False,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': consts.PLACE_ID_AS_STRING,
                            'currency': consts.CURRENCY,
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '300',
                                    'type': 'marketing_promocode',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'assembly/retail/native',
                                    'value_amount': '10',
                                    'type': 'marketing_promocode',
                                    'product_type': 'assembly',
                                },
                            ],
                            'amount_picker_paid': '2000',
                            'order_type': 'native',
                            'flow_type': 'retail',
                        },
                    ),
                ],
            ),
            # expected_store_request
            [
                helpers.make_billing_doc(
                    order_nr=consts.ORDER_NR,
                    kind='PayoutOrder',
                    event_at=consts.START_PICKER_ORDER_DATE,
                    external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                    'BillingCancelled/1/'
                    'retail/retail/native/'
                    'marketing_promocode',
                    data={
                        'service_order_id': consts.ORDER_NR,
                        # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                        'service_id': 111,
                        'dt': consts.START_PICKER_ORDER_DATE,
                        'client_id': consts.CLIENT_ID,
                        'paysys_partner_id': 'yaeda',
                        'transaction_type': 'payment',
                        'payload': {},
                        'payment_type': 'marketing_promocode',
                        'payment_terminal_id': None,
                        # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                        'product': 'goods',
                        'value_amount': '300',
                        'currency': 'RUB',
                        'commission': '0',
                        'identity': (
                            f'PayoutOrder/{consts.ORDER_NR}/'
                            'BillingCancelled/1/'
                            'retail/retail/native/'
                            'marketing_promocode'
                        ),
                    },
                ),
                helpers.make_billing_doc(
                    order_nr=consts.ORDER_NR,
                    kind='PayoutOrder',
                    event_at=consts.START_PICKER_ORDER_DATE,
                    external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                    'BillingCancelled/1/'
                    'assembly/retail/native/'
                    'marketing_promocode',
                    data={
                        'service_order_id': consts.ORDER_NR,
                        # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                        'service_id': 111,
                        'dt': consts.START_PICKER_ORDER_DATE,
                        'client_id': consts.CLIENT_ID,
                        'paysys_partner_id': 'yaeda',
                        'transaction_type': 'payment',
                        'payload': {},
                        'payment_type': 'picker_marketing_promocode',
                        'payment_terminal_id': None,
                        # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                        'product': 'goods',
                        'value_amount': '10',
                        'currency': 'RUB',
                        'commission': '12',
                        'identity': (
                            f'PayoutOrder/{consts.ORDER_NR}/'
                            'BillingCancelled/1/'
                            'assembly/retail/native/'
                            'marketing_promocode'
                        ),
                    },
                ),
            ],
            # expected_finish_requests
            [helpers.make_storage_finish_request(doc_id=1, status='complete')],
            # expected_business_rules_requests
            [
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.START_PICKER_ORDER_DATE_UTC,
                    counteragent_type='courier',
                    counteragent_details={
                        'courier_id': consts.PICKER_ID,
                        'product_type': 'delivery',
                        'agreement_type': 'picker',
                    },
                ),
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.START_PICKER_ORDER_DATE_UTC,
                    counteragent_type='courier',
                    counteragent_details={
                        'courier_id': consts.PICKER_ID,
                        'product_type': 'delivery',
                        'agreement_type': 'picker',
                    },
                ),
            ],
            # business_rules_response
            [
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Multiple products in event',
        ),
    ],
)
async def test_billing_cancelled(
        stq_runner,
        experiments3,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        mock_business_rules,
        mock_create_handler,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_business_rules_requests,
        business_rules_responses,
        expected_input_stq_fail,
        mock_order_revision_list,
):
    mock_order_revision_list(revisions=[{'revision_id': '123-321'}])

    experiments3.add_experiment(**helpers.make_use_core_revisions_exp())

    await helpers.billing_processing_test_func(
        stq_runner,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        mock_business_rules,
        mock_create_handler,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_business_rules_requests,
        business_rules_responses,
        expected_input_stq_fail,
    )
