# pylint: disable=too-many-lines

import copy
import json
import typing

from tests_eats_orders_billing import consts


def make_raw_events_stq_args(order_nr, billing_extra_data=None):
    return {'order_nr': order_nr, 'billing_extra_data': billing_extra_data}


def make_billing_events_stq_kwargs(order_nr):
    return {'order_nr': order_nr}


def make_storage_search_request(order_nr):
    return {'external_obj_id': order_nr}


def make_storage_search_response(billing_docs):
    return {'docs': billing_docs}


def make_storage_create_request(billing_docs):
    return billing_docs


def make_storage_finish_request(doc_id, status):
    return {'doc_id': doc_id, 'status': status, 'details': {}}


def make_input_event_stq_args(order_nr, external_event_ref):
    return {
        'kind': 'kind_value',
        'external_obj_id': order_nr,
        'external_event_ref': external_event_ref,
        'event_at': consts.OTHER_DATE,
        'service': 'service_value',
        'service_user_id': 'service_user_id_value',
        'data': {'test': 'test'},
        'status': 'status_value',
    }


def make_events_process_stq_args(order_nr):
    return {'external_obj_id': order_nr}


def make_business_rules_request(
        counteragent_type, counteragent_details, billing_date,
):
    return {
        'counteragent_type': counteragent_type,
        'counteragent_details': counteragent_details,
        'billing_date': billing_date,
    }


def make_business_rules_response(
        client_id, commission, acquiring_commission, fix_commission,
):
    return {
        'client_id': client_id,
        'commissions': {
            'commission': str(commission),
            'acquiring_commission': str(acquiring_commission),
            'fix_commission': str(fix_commission),
        },
    }


def make_billing_doc(
        order_nr,
        kind,
        data,
        doc_id=None,
        event_at=consts.OTHER_DATE,
        external_event_ref='',
        status='new',
        service=consts.SERVICE,
        service_user_id=consts.SERVICE_USER_ID,
):
    doc = {
        'kind': kind,
        'external_obj_id': order_nr,
        'external_event_ref': external_event_ref,
        'event_at': event_at,
        'service_user_id': service_user_id,
        'data': data,
        'tags': [],
        'status': status,
        'service': service,
        'journal_entries': [],
    }
    if doc_id is not None:
        doc['doc_id'] = doc_id
    return doc


def make_order_created_doc(
        doc_id=0,
        order_nr=consts.ORDER_NR,
        order_type='retail',
        created_at=consts.ORDER_CREATED_DATE,
):
    return make_billing_doc(
        doc_id=doc_id,
        order_nr=order_nr,
        kind='OrderCreated',
        data={'orderType': order_type, 'createdAt': created_at},
    )


def make_promo(promo_id=None, promo_discount='0.00'):
    return {'promo_id': promo_id, 'promo_discount': promo_discount}


def make_promocode(
        promocode_id=None,
        promocode_type='marketing_promocode',
        promocode_goods_discount='0.00',
        promocode_delivery_discount='0.00',
        promocode_assembly_discount='0.00',
):
    return {
        'promocode_id': promocode_id,
        'promocode_type': promocode_type,
        'promocode_goods_discount': promocode_goods_discount,
        'promocode_delivery_discount': promocode_delivery_discount,
        'promocode_assembly_discount': promocode_assembly_discount,
    }


# input events
def make_order_created_ie(
        goods_price,
        goods_gmv_amount,
        order_nr=consts.ORDER_NR,
        place_id=consts.PLACE_ID_AS_STRING,
        currency=consts.CURRENCY,
        created_at=consts.OTHER_DATE,
        order_type='native',
        flow_type='native',
        assembly_price='0.00',
        delivery_price='0.00',
        revision_id='1',
        special_commission_type=None,
        promo=None,
        promocode=None,
        place_compensations=None,
        dynamic_price=None,
        processing_type=None,
):
    data = {
        'order_nr': order_nr,
        'place_id': place_id,
        'currency': currency,
        'created_at': created_at,
        'order_type': order_type,
        'flow_type': flow_type,
        'goods_price': goods_price,
        'assembly_price': assembly_price,
        'delivery_price': delivery_price,
        'goods_gmv_amount': goods_gmv_amount,
        'revision_id': revision_id,
    }
    if special_commission_type is not None:
        data['special_commission_type'] = special_commission_type
    if place_compensations is not None:
        data['place_compensations'] = place_compensations
    if promo is None:
        promo = make_promo()
    data['promo'] = promo

    if promocode is None:
        promocode = make_promocode()
    data['promocode'] = promocode
    if dynamic_price is not None:
        data['dynamic_price'] = dynamic_price
    if processing_type is not None:
        data['processing_type'] = processing_type

    return json.dumps(data)


def make_fine_appeal_ie(
        amount,
        fine_id=consts.FINE_ID,
        currency=consts.CURRENCY,
        ticket=consts.FINE_APPEAL_TICKET,
        appealed_at=consts.OTHER_DATE,
        fine_reason='refund',
):
    data = {
        'fine_id': fine_id,
        'amount': amount,
        'currency': currency,
        'ticket': ticket,
        'appealed_at': appealed_at,
        'fine_reason': fine_reason,
    }

    return json.dumps(data)


def make_order_changed_ie(
        goods_price,
        goods_gmv_amount,
        order_nr=consts.ORDER_NR,
        place_id=consts.PLACE_ID_AS_STRING,
        currency=consts.CURRENCY,
        created_at=consts.OTHER_DATE,
        order_type='native',
        flow_type='native',
        assembly_price='0.00',
        delivery_price='0.00',
        revision_id='1',
        special_commission_type=None,
        dynamic_price=None,
        promo=None,
):
    data = {
        'order_nr': order_nr,
        'place_id': place_id,
        'currency': currency,
        'updated_at': created_at,
        'order_type': order_type,
        'flow_type': flow_type,
        'goods_price': goods_price,
        'assembly_price': assembly_price,
        'delivery_price': delivery_price,
        'goods_gmv_amount': goods_gmv_amount,
        'revision_id': revision_id,
        'promocode': {
            'promocode_id': None,
            'promocode_type': 'marketing_promocode',
            'promocode_goods_discount': '0.00',
            'promocode_delivery_discount': '0.00',
            'promocode_assembly_discount': '0.00',
        },
    }
    if promo is None:
        promo = make_promo()
    data['promo'] = promo
    if special_commission_type is not None:
        data['special_commission_type'] = special_commission_type
    if dynamic_price is not None:
        data['dynamic_price'] = dynamic_price
    return json.dumps(data)


def make_confirmed_ie(
        confirmed_at=consts.OTHER_DATE, place_id=consts.PLACE_ID_AS_STRING,
):
    data = {'confirmed_at': confirmed_at, 'place_id': place_id}
    return json.dumps(data)


def make_order_delivered_ie(delivered_at=consts.FINISHED_DATE):
    data = {'delivered_at': delivered_at}
    return json.dumps(data)


def make_order_picked_up_ie(picked_up_at=consts.FINISHED_DATE):
    data = {'picked_up_at': picked_up_at}
    return json.dumps(data)


def make_courier_assigned(courier_id, assigned_at=consts.OTHER_DATE):
    data = {'courier_id': courier_id, 'assigned_at': assigned_at}
    return json.dumps(data)


def make_tlog_accounting_correction(
        amount,
        correction_id,
        correction_type,
        correction_group,
        originator,
        order_nr=consts.ORDER_NR,
        currency=consts.CURRENCY,
        product=None,
        detailed_product=None,
):
    data = {
        'amount': amount,
        'order_nr': order_nr,
        'currency': currency,
        'correction_id': correction_id,
        'correction_type': correction_type,
        'correction_group': correction_group,
        'originator': originator,
    }

    if product is not None:
        data['product'] = product
    if detailed_product is not None:
        data['detailed_product'] = detailed_product
    return json.dumps(data)


def make_accounting_correction_ie(
        amount,
        correction_id,
        account_correction_type,
        ticket=consts.TICKET,
        order_nr=consts.ORDER_NR,
        place_id=consts.PLACE_ID_AS_STRING,
        currency=consts.CURRENCY,
        created_at=consts.OTHER_DATE,
        order_type='native',
        payment_type='account_correction',
):
    data = {
        'amount': amount,
        'ticket': ticket,
        'order_nr': order_nr,
        'place_id': place_id,
        'currency': currency,
        'created_at': created_at,
        'order_type': order_type,
        'payment_type': payment_type,
        'correction_id': correction_id,
        'account_correction_type': account_correction_type,
    }
    return json.dumps(data)


def make_discount(discount_type, amount, discount_provider):
    return {
        'type': discount_type,
        'amount': amount,
        'discount_provider': discount_provider,
    }


def make_product(value_amount, product_type, discounts=None):
    product = {'value_amount': value_amount, 'product_type': product_type}
    if discounts is not None:
        product['discounts'] = discounts
    return product


def make_order_cancelled_ie(
        is_place_fault,
        is_payment_expected,
        is_reimbursement_required,
        products=None,
        cancelled_at=consts.FINISHED_DATE,
        order_cancel_id=consts.ORDER_CANCEL_ID_AS_STRING,
):
    data = {
        'cancelled_at': cancelled_at,
        'is_place_fault': is_place_fault,
        'order_cancel_id': order_cancel_id,
        'is_payment_expected': is_payment_expected,
        'is_reimbursement_required': is_reimbursement_required,
        'products': products,
    }
    return json.dumps(data)


def make_compensation_discount_ie(discount_type, amount, discount_provider):
    return {
        'type': discount_type,
        'amount': amount,
        'discount_provider': discount_provider,
    }


def make_compensation_item_ie(
        item_type, amount, discounts, name=consts.ITEM_NAME, identity=None,
):
    item = {
        'name': name,
        'type': item_type,
        'amount': amount,
        'discounts': discounts,
    }
    if identity is not None:
        item['identity'] = identity
    return item


def make_compensation_ie(
        amount,
        items,
        compensation_id=consts.COMPENSATION_ID_AS_STRING,
        is_place_fault=False,
        compensation_at=consts.OTHER_DATE,
):
    data = {
        'compensation_id': compensation_id,
        'is_place_fault': is_place_fault,
        'compensation_at': compensation_at,
        'amount': amount,
        'items': items,
    }
    return json.dumps(data)


def check_billing_events_stq_call(
        stq,
        expected_times_called,
        expected_task_id=None,
        expected_kwargs=None,
):
    assert (
        stq.eats_orders_billing_process_billing_events.times_called
        == expected_times_called
    )
    if expected_times_called == 0:
        return
    call_info = stq.eats_orders_billing_process_billing_events.next_call()
    assert call_info['id'] == expected_task_id
    assert call_info['queue'] == 'eats_orders_billing_process_billing_events'
    kwargs = call_info['kwargs']
    kwargs.pop('log_extra')
    assert kwargs == expected_kwargs


def check_process_ie_stq_call(
        stq,
        expected_times_called,
        expected_task_id=None,
        expected_kwargs=None,
):
    assert (
        stq.eats_orders_billing_process_input_events.times_called
        == expected_times_called
    )
    if expected_times_called == 0:
        return
    call_info = stq.eats_orders_billing_process_input_events.next_call()
    assert call_info['id'] == expected_task_id
    assert call_info['queue'] == 'eats_orders_billing_process_input_events'
    kwargs = call_info['kwargs']
    kwargs.pop('log_extra')
    assert kwargs == expected_kwargs


def billing_docs_are_equal(doc1, doc2):
    """
    Сравнивает 2 биллинг-дока, игнорируя атрибуты 'event_at'.
    """
    doc1_copy = copy.deepcopy(doc1)
    doc2_copy = copy.deepcopy(doc2)

    doc1_copy.pop('event_at')
    doc2_copy.pop('event_at')

    if ('event_at' in doc1_copy['data']) and ('event_at' in doc2_copy['data']):
        doc1_copy['data'].pop('event_at')
        doc2_copy['data'].pop('event_at')
    elif ('event_at' in doc1_copy['data']) or (
        'event_at' in doc2_copy['data']
    ):
        return False

    def deep_equals(x, y):
        if not isinstance(x, type(y)):
            return False
        if isinstance(x, dict):
            x_keys = sorted(x.keys())
            y_keys = sorted(y.keys())
            if x_keys != y_keys:
                return False
            for key in x_keys:
                if not deep_equals(x[key], y[key]):
                    return False
            return True
        if isinstance(x, list):
            if len(x) != len(y):
                return False
            if not x:
                return True
            for i, y_value in enumerate(y):
                if deep_equals(x[0], y_value):
                    x.pop(0)
                    y.pop(i)
                    return deep_equals(x, y)
            return False
        return x == y

    return deep_equals(doc1_copy, doc2_copy)


def make_customer_service(
        customer_service_id: str,
        name: str,
        cost_for_customer: str,
        currency: str,
        customer_service_type: str,
        trust_product_id: str,
        place_id: str,
        vat: typing.Optional[str] = None,
        personal_tin_id: typing.Optional[str] = None,
        commission_category: typing.Optional[int] = None,
        balance_client_id: typing.Optional[str] = None,
        details: typing.Optional[dict] = None,
        refunded_amount: typing.Optional[str] = None,
) -> dict:
    customer_service: typing.Dict[str, typing.Any] = {
        'id': customer_service_id,
        'name': name,
        'cost_for_customer': cost_for_customer,
        'currency': currency,
        'type': customer_service_type,
        'vat': vat,
        'trust_product_id': trust_product_id,
        'place_id': place_id,
    }

    if personal_tin_id is not None:
        customer_service['personal_tin_id'] = personal_tin_id
    if commission_category is not None:
        customer_service['commission_category'] = commission_category
    if balance_client_id is not None:
        customer_service['balance_client_id'] = balance_client_id
    if details is not None:
        customer_service['details'] = details
    if refunded_amount is not None:
        customer_service['refunded_amount'] = refunded_amount
    return customer_service


def make_customer_service_detailed(customer_service, customer_service_details):
    customer_service_detailed: typing.Dict[str, typing.Any] = {
        **customer_service,
        'details': customer_service_details,
    }
    return customer_service_detailed


def make_customer_service_details(
        composition_products: typing.List[dict],
        refunds: typing.List[dict] = None,
) -> dict:
    if refunds is None:
        refunds = []
    customer_service_details: typing.Dict[str, typing.Any] = {
        'composition_products': composition_products,
        'discriminator_type': 'composition_products_details',
        'refunds': refunds,
    }
    return customer_service_details


def billing_doc_lists_are_equal(doc_list1, doc_list2):
    """
    Сравнивает 2 списка биллинг-доков,
    игнорируя атрибуты 'event_at' в биллинг-доках.
    """
    if not isinstance(doc_list1, list):
        return False
    if not isinstance(doc_list2, list):
        return False
    if len(doc_list1) != len(doc_list2):
        return False

    for doc1 in doc_list1:
        found = False
        for doc2 in doc_list2:
            if billing_docs_are_equal(doc1, doc2):
                found = True
                break
        if not found:
            return False

    for doc2 in doc_list2:
        found = False
        for doc1 in doc_list1:
            if billing_docs_are_equal(doc1, doc2):
                found = True
                break
        if not found:
            return False
    return True


async def raw_processing_test_func(
        stq_runner,
        stq,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_output_stq_args,
        expected_input_stq_fail,
):
    storage_search = mock_storage_search(
        expected_request=expected_search_request, response=search_response,
    )
    storage_store = mock_storage_store(expected_request=expected_store_request)
    storage_finish = mock_storage_finish(
        expected_requests=expected_finish_requests,
    )

    await stq_runner.eats_orders_billing_process_raw_events.call(
        task_id='test_input_task',
        kwargs=input_stq_args,
        expect_fail=expected_input_stq_fail,
    )
    times_called = 1 if expected_search_request else 0
    assert storage_search.times_called == times_called
    times_called = 1 if expected_store_request else 0
    assert storage_store.times_called == times_called
    times_called = (
        len(expected_finish_requests) if expected_finish_requests else 0
    )
    assert storage_finish.times_called == times_called
    times_called = 1 if expected_output_stq_args else 0
    check_billing_events_stq_call(
        stq,
        expected_times_called=times_called,
        expected_task_id='test_input_task',
        expected_kwargs=expected_output_stq_args,
    )


async def billing_processing_test_func(
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
):
    v1_create_error_handler = mock_create_handler()
    storage_search = mock_storage_search(
        expected_request=expected_search_request, response=search_response,
    )
    storage_store = mock_storage_store(expected_request=expected_store_request)
    storage_finish = mock_storage_finish(
        expected_requests=expected_finish_requests,
    )
    business_rules = mock_business_rules(
        expected_requests=expected_business_rules_requests,
        responses=business_rules_responses,
    )
    await stq_runner.eats_orders_billing_process_billing_events.call(
        task_id='test_input_task',
        kwargs=input_stq_args,
        expect_fail=expected_input_stq_fail,
    )
    times_called = 1 if expected_search_request else 0
    assert storage_search.times_called == times_called
    times_called = 1 if expected_store_request else 0
    assert storage_store.times_called == times_called
    times_called = (
        len(expected_finish_requests) if expected_finish_requests else 0
    )
    assert storage_finish.times_called == times_called
    times_called = (
        len(expected_business_rules_requests)
        if expected_business_rules_requests
        else 0
    )
    assert business_rules.times_called == times_called
    assert v1_create_error_handler.times_called == 0


def make_discount_compensation_data(amount, compensation_type):
    return {'amount': amount, 'type': compensation_type}


def make_item_compensation_data(amount, discounts, product_id, product_type):
    return {
        'amount': amount,
        'discounts': discounts,
        'product_id': product_id,
        'type': product_type,
    }


def make_compensation_data(
        items,
        compensation_id=consts.COMPENSATION_ID_AS_STRING,
        courier_id=None,
        currency=consts.CURRENCY,
        flow_type='native',
        order_nr=consts.ORDER_NR,
        picker_id=None,
        place_id=consts.PLACE_ID_AS_STRING,
        transaction_date=consts.OTHER_DATE,
        is_place_fault=False,
        service_fee_amount='0',
        order_finished_at=None,
) -> dict:
    data = {
        'compensation_id': compensation_id,
        'courier_id': courier_id,
        'currency': currency,
        'flow_type': flow_type,
        'order_nr': order_nr,
        'picker_id': picker_id,
        'place_id': place_id,
        'transaction_date': transaction_date,
        'items': items,
        'is_place_fault': is_place_fault,
    }
    if int(service_fee_amount) > 0:
        data['service_fee_amount'] = service_fee_amount
    if order_finished_at is not None:
        data['order_finished_at'] = order_finished_at
    return data


def make_payment_correction(
        amount,
        correction_id,
        originator,
        product_type=None,
        order_nr=consts.ORDER_NR,
        transaction_date=consts.OTHER_DATE,
        place_id=consts.PLACE_ID_AS_STRING,
        currency=consts.CURRENCY,
) -> dict:
    data = {
        'correction_id': correction_id,
        'amount': amount,
        'currency': currency,
        'originator': originator,
        'transaction_date': transaction_date,
        'place_id': place_id,
    }

    if product_type is not None:
        data['product_type'] = product_type
    else:
        data['order_nr'] = order_nr
    return data


def make_commission_correction(
        amount,
        correction_id,
        originator,
        product,
        detailed_product,
        order_nr=consts.ORDER_NR,
        transaction_date=consts.OTHER_DATE,
        place_id=consts.PLACE_ID_AS_STRING,
        currency=consts.CURRENCY,
) -> dict:
    data = {
        'correction_id': correction_id,
        'amount': amount,
        'currency': currency,
        'originator': originator,
        'transaction_date': transaction_date,
        'place_id': place_id,
        'product': product,
        'detailed_product': detailed_product,
    }
    return data


def make_order_gmv_data(
        gmv_amount,
        order_nr=consts.ORDER_NR,
        transaction_date=consts.OTHER_DATE,
        place_id=consts.PLACE_ID_AS_STRING,
        currency=consts.CURRENCY,
        special_commission_type=None,
        dynamic_price=None,
) -> dict:
    data = {
        'order_nr': order_nr,
        'transaction_date': transaction_date,
        'place_id': place_id,
        'currency': currency,
        'gmv_amount': gmv_amount,
    }
    if special_commission_type:
        data['special_commission_type'] = special_commission_type
    if dynamic_price is not None:
        data['dynamic_price'] = dynamic_price
    return data


def make_order_delivered_products(
        product_id,
        product_type,
        payment_type,
        value_amount,
        entity_id=consts.ENTITY_ID,
):
    return {
        'entity_id': entity_id,
        'product_id': product_id,
        'product_type': product_type,
        'type': payment_type,
        'value_amount': value_amount,
    }


def make_order_delivered_data(
        products=None,
        courier_id=None,
        picker_id=None,
        order_nr=consts.ORDER_NR,
        flow_type='native',
        transaction_date=consts.OTHER_DATE,
        delivered_at=consts.FINISHED_DATE,
        place_id=consts.PLACE_ID_AS_STRING,
        currency=consts.CURRENCY,
        service_fee_amount='9',
        courier_token='deal_id_delivery',
) -> dict:
    data = {
        'courier_id': courier_id,
        'courier_token': courier_token,
        'currency': currency,
        'delivered_at': delivered_at,
        'flow_type': flow_type,
        'order_nr': order_nr,
        'picker_id': picker_id,
        'place_id': place_id,
        'products': products,
        'transaction_date': transaction_date,
        'service_fee_amount': service_fee_amount,
    }

    if products is None:
        products = []
    data['products'] = products
    return data


def make_order_created_data(rules='restaurant') -> dict:
    return {'rules': rules}


def make_additional_payment_data(amount) -> dict:
    return {
        'order_nr': consts.ORDER_NR,
        'amount': amount,
        'currency': consts.CURRENCY,
        'transaction_date': consts.OTHER_DATE,
        'place_id': consts.PLACE_ID_AS_STRING,
        'promo_id': 'promo_id',
    }


def make_fine_appeal_data(amount, product_id, fine_reason='refund') -> dict:
    return {
        'fine_id': consts.FINE_ID,
        'order_nr': consts.ORDER_NR,
        'ticket': consts.FINE_APPEAL_TICKET,
        'transaction_date': consts.OTHER_DATE,
        'amount': amount,
        'currency': consts.CURRENCY,
        'product_type': 'product',
        'product_id': product_id,
        'place_id': consts.PLACE_ID_AS_STRING,
        'fine_reason': fine_reason,
    }


def make_request_product(
        product_id,
        product_type,
        value_amount,
        payment_type=consts.PAYMENT_METHOD_PAYMENT_NOT_RECEIVED,
):
    return {
        'product_id': product_id,
        'product_type': product_type,
        'type': payment_type,
        'value_amount': value_amount,
    }


def make_order_cancelled_data(
        is_payment_expected,
        is_reimbursement_required,
        is_place_fault,
        cancelled_at=consts.FINISHED_DATE,
        currency=consts.CURRENCY,
        flow_type='native',
        order_cancel_id=consts.ORDER_CANCEL_ID_AS_STRING,
        order_nr=consts.ORDER_NR,
        order_type='native',
        place_id=consts.PLACE_ID_AS_STRING,
        products=None,
        transaction_date=consts.OTHER_DATE,
        courier_id=None,
        picker_id=None,
        amount_picker_paid=None,
        courier_token='deal_id_delivery',
        gmv_amount=None,
        dynamic_price=None,
) -> dict:
    data = {
        'cancelled_at': cancelled_at,
        'currency': currency,
        'flow_type': flow_type,
        'is_payment_expected': is_payment_expected,
        'is_reimbursement_required': is_reimbursement_required,
        'is_place_fault': is_place_fault,
        'order_cancel_id': order_cancel_id,
        'order_nr': order_nr,
        'order_type': order_type,
        'place_id': place_id,
        'products': products,
        'transaction_date': transaction_date,
        'courier_id': courier_id,
        'courier_token': courier_token,
        'picker_id': picker_id,
    }
    if amount_picker_paid:
        data['amount_picker_paid'] = amount_picker_paid
    if gmv_amount is not None:
        data['gmv_amount'] = gmv_amount
    if dynamic_price is not None:
        data['dynamic_price'] = dynamic_price
    return data


def make_create_request(
        external_id,
        kind,
        data,
        order_nr=consts.ORDER_NR,
        event_at=consts.OTHER_DATE,
        rule_name=consts.RULE_NAME,
        place_compensations=None,
) -> dict:
    result = {
        'order_nr': order_nr,
        'external_id': external_id,
        'event_at': event_at,
        'kind': kind,
        'data': data,
        'rule_name': rule_name,
    }
    if place_compensations is not None:
        data['place_compensations'] = place_compensations
    return result


def make_db_row(
        kind,
        external_event_ref,
        data,
        external_obj_id=consts.ORDER_NR,
        event_at=consts.OTHER_DATE,
        service='test_service',
        service_user_id='service_user_id',
        status='new',
) -> dict:
    return {
        'kind': kind,
        'external_obj_id': external_obj_id,
        'external_event_ref': external_event_ref,
        'event_at': event_at,
        'service': service,
        'service_user_id': service_user_id,
        'data': data,
        'status': status,
    }


async def billing_input_events_test_func(
        stq,
        stq_runner,
        select_billing_input_events,
        input_stq_args,
        expected_input_stq_fail,
):
    await stq_runner.eats_orders_billing_input_events.call(
        task_id='test_input_task',
        kwargs=input_stq_args,
        expect_fail=expected_input_stq_fail,
    )
    events = select_billing_input_events(1)
    assert len(events) == 1
    if not expected_input_stq_fail:
        check_process_ie_stq_call(
            stq,
            expected_times_called=1,
            expected_task_id='test_input_task',
            expected_kwargs={'external_obj_id': consts.ORDER_NR},
        )


async def input_events_process_test_func(
        stq_runner,
        mock_eats_billing_processor_create,
        insert_billing_input_events,
        input_stq_args,
        input_events,
        expected_input_stq_fail,
        times_called=0,
        expected_requests=None,
):
    if input_events:
        insert_billing_input_events(input_events)
    mock_create = mock_eats_billing_processor_create()
    await stq_runner.eats_orders_billing_process_input_events.call(
        task_id='test_input_task',
        kwargs=input_stq_args,
        expect_fail=expected_input_stq_fail,
    )
    print(mock_create.times_called)
    print(times_called)
    assert mock_create.times_called == times_called
    if times_called > 0:
        assert mock_create.times_called == len(expected_requests)
        for expected_request in expected_requests:
            call_info = mock_create.next_call()
            request_copy = call_info['request'].json.copy()
            request_copy.pop('event_at')
            if 'transaction_date' in request_copy['data']:
                request_copy['data'].pop('transaction_date')

            expected_request_copy = expected_request.copy()
            expected_request_copy.pop('event_at')
            if 'transaction_date' in expected_request_copy['data']:
                expected_request_copy['data'].pop('transaction_date')

            if 'courier_id' in expected_request_copy['data']:
                assert (
                    expected_request_copy['data']['courier_id']
                    == request_copy['data']['courier_id']
                )

            print(json.dumps(request_copy))
            print(json.dumps(expected_request_copy))
            assert request_copy == expected_request_copy


def make_use_core_revisions_exp() -> dict:
    return {
        'name': 'eats_opg_use_core_revisions',
        'consumers': ['eats_opg/use_core_revisions'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'default_value': {'use_core': False},
        'clauses': [],
    }
