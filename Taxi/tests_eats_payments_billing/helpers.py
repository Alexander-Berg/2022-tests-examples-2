import copy
import typing

from tests_eats_payments_billing import consts


def make_stq_kwargs(
        items: typing.List[dict],
        order_id: str = consts.ORDER_ID,
        transaction_type: str = consts.TRANSACTION_TYPE,
        currency: str = consts.CURRENCY,
        payment_type: str = consts.PAYMENT_TYPE,
        payment_service: typing.Optional[str] = None,
        billing_extra_data=None,
        deal_id=None,
) -> dict:
    doc = {
        'order_id': order_id,
        'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
        'transaction_type': transaction_type,
        'event_at': consts.EVENT_AT,
        'payment_type': payment_type,
        'currency': currency,
        'terminal_id': consts.TERMINAL_ID,
        'items': items,
        'billing_extra_data': billing_extra_data,
    }

    if payment_service is not None:
        doc['payment_service'] = payment_service

    if deal_id is not None:
        doc['deal_id'] = deal_id

    return doc


def make_logistic_stq_kwargs(
        amount: str,
        item_type: str,
        status: str,
        payment_type: str,
        currency: str = consts.CURRENCY,
        order_id: str = consts.ORDER_ID,
        event_dt: str = consts.EVENT_AT_TIMEZONE,
) -> dict:
    return {
        'order_id': order_id,
        'amount': amount,
        'currency': currency,
        'item_type': item_type,
        'status': status,
        'payment_type': payment_type,
        'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
        'event_dt': event_dt,
    }


def make_stq_kwargs_no_optional(
        items: typing.List[dict],
        transaction_type: str = consts.TRANSACTION_TYPE,
        currency: str = consts.CURRENCY,
        payment_type: str = consts.PAYMENT_TYPE,
) -> dict:
    return {
        'order_id': consts.ORDER_ID,
        'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
        'transaction_type': transaction_type,
        'event_at': consts.EVENT_AT,
        'payment_type': payment_type,
        'currency': currency,
        'items': items,
    }


def make_stq_kwargs_no_payment(
        items: typing.List[dict],
        transaction_type: str = consts.TRANSACTION_TYPE,
        currency: str = consts.CURRENCY,
        payment_type: str = consts.PAYMENT_TYPE,
        external_payment_id: typing.Optional[str] = consts.EXTERNAL_PAYMENT_ID,
) -> dict:
    kwargs = {
        'order_id': consts.ORDER_ID,
        'transaction_type': transaction_type,
        'event_at': consts.EVENT_AT,
        'payment_type': payment_type,
        'currency': currency,
        'items': items,
    }
    if external_payment_id is not None:
        kwargs['external_payment_id'] = external_payment_id
    return kwargs


def make_stq_item(
        item_id: str,
        amount: str,
        item_type: str = 'product',
        place_id: str = consts.PLACE_ID,
        deal_id: str = None,
        balance_client_id=consts.BALANCE_CLIENT_ID,
) -> dict:
    stq_item = {
        'item_id': item_id,
        'item_type': item_type,
        'balance_client_id': balance_client_id,
        'place_id': place_id,
        'amount': amount,
    }
    if deal_id is not None:
        stq_item['deal_id'] = deal_id

    return stq_item


def make_request_arg_payment(
        old_kind: str,
        old_items: list,
        amount: str,
        goods_amount: str,
        delivery_amount: str,
        new_kind: str,
        new_items: list,
        flow_type: str = consts.FLOW_TYPE,
        order_type: str = consts.ORDER_TYPE,
        currency: str = consts.CURRENCY,
        old_payment_type: str = consts.PAYMENT_TYPE,
        payment_type: str = consts.PAYMENT_TYPE,
        external_payment_id: str = consts.EXTERNAL_PAYMENT_ID,
        payment_service: typing.Optional[str] = None,
        order_id=consts.ORDER_ID,
        transaction_date: str = consts.TRANSACTION_DATE,
):
    request_arg = []

    if float(amount) > 0:
        # old event
        request_arg.append(
            {
                'external_obj_id': order_id,
                'event_at': consts.EVENT_AT,
                'service': consts.SERVICE,
                'status': consts.STATUS,
                'service_user_id': consts.SERVICE_USER_ID,
                'kind': old_kind,
                'external_event_ref': (
                    old_kind + '/' + consts.TASK_ID + '/' + order_id
                ),
                'journal_entries': [],
                'tags': [],
                'data': {
                    'amount': amount,
                    'goodsAmount': goods_amount,
                    'deliveryAmount': delivery_amount,
                    'currency': currency,
                    'eventAt': consts.EVENT_AT,
                    'externalPaymentId': consts.EXTERNAL_PAYMENT_ID,
                    'orderNr': order_id,
                    'paymentReceivedAt': consts.EVENT_AT,
                    'paymentType': old_payment_type,
                    'terminalId': consts.TERMINAL_ID,
                    'items': old_items,
                    'transactionDate': transaction_date,
                },
            },
        )

    # new events
    new_events = make_request_arg_new_events(
        new_kind,
        new_items,
        'payment',
        flow_type,
        order_type,
        currency=currency,
        payment_type=payment_type,
        external_payment_id=external_payment_id,
        payment_service=payment_service,
        order_id=order_id,
        transaction_date=transaction_date,
    )
    request_arg.extend(new_events)

    return request_arg


def make_request_arg_payment_no_opt(
        old_kind: str,
        old_items: list,
        amount: str,
        goods_amount: str,
        delivery_amount: str,
        new_kind: str,
        new_items: list,
        flow_type: str = consts.FLOW_TYPE,
        order_type: str = consts.ORDER_TYPE,
        currency: str = consts.CURRENCY,
        payment_type: str = consts.PAYMENT_TYPE,
        external_payment_id: str = consts.EXTERNAL_PAYMENT_ID,
):
    request_arg = []

    # old event
    request_arg.append(
        {
            'external_obj_id': consts.ORDER_ID,
            'event_at': consts.EVENT_AT,
            'service': consts.SERVICE,
            'status': consts.STATUS,
            'service_user_id': consts.SERVICE_USER_ID,
            'kind': old_kind,
            'external_event_ref': (
                old_kind + '/' + consts.TASK_ID + '/' + consts.ORDER_ID
            ),
            'journal_entries': [],
            'tags': [],
            'data': {
                'amount': amount,
                'goodsAmount': goods_amount,
                'deliveryAmount': delivery_amount,
                'currency': currency,
                'eventAt': consts.EVENT_AT,
                'externalPaymentId': consts.EXTERNAL_PAYMENT_ID,
                'orderNr': consts.ORDER_ID,
                'paymentReceivedAt': consts.EVENT_AT,
                'paymentType': payment_type,
                'items': old_items,
                'transactionDate': consts.TRANSACTION_DATE,
            },
        },
    )

    # new events
    new_events = _make_request_arg_new_events_without_optional(
        new_kind,
        new_items,
        'payment',
        flow_type,
        order_type,
        currency=currency,
        payment_type=payment_type,
        external_payment_id=external_payment_id,
    )
    request_arg.extend(new_events)

    return request_arg


def make_request_arg_refund(
        old_kind: typing.Optional[str],
        old_items: list,
        new_kind: str,
        new_items: list,
        flow_type: str,
        order_type: str,
        currency: str = consts.CURRENCY,
        payment_type: str = consts.PAYMENT_TYPE,
        external_payment_id: str = consts.EXTERNAL_PAYMENT_ID,
        payment_service: typing.Optional[str] = None,
):
    request_arg = []

    # old event
    if old_kind is not None:
        request_arg.append(
            {
                'external_obj_id': consts.ORDER_ID,
                'event_at': consts.EVENT_AT,
                'service': consts.SERVICE,
                'status': consts.STATUS,
                'service_user_id': consts.SERVICE_USER_ID,
                'kind': old_kind,
                'external_event_ref': (
                    old_kind + '/' + consts.TASK_ID + '/' + consts.ORDER_ID
                ),
                'journal_entries': [],
                'tags': [],
                'data': {
                    'currency': currency,
                    'eventAt': consts.EVENT_AT,
                    'externalPaymentId': consts.EXTERNAL_PAYMENT_ID,
                    'orderNr': consts.ORDER_ID,
                    'paymentType': payment_type,
                    'terminalId': consts.TERMINAL_ID,
                    'items': old_items,
                },
            },
        )

    # new events
    new_events = make_request_arg_new_events(
        new_kind,
        new_items,
        'refund',
        flow_type,
        order_type,
        currency=currency,
        payment_type=payment_type,
        external_payment_id=external_payment_id,
        payment_service=payment_service,
    )
    request_arg.extend(new_events)

    return request_arg


def make_request_arg_refund_no_opt(
        old_kind: typing.Optional[str],
        old_items: list,
        new_kind: str,
        new_items: list,
        flow_type: str,
        order_type: str,
        currency: str = consts.CURRENCY,
        payment_type: str = consts.PAYMENT_TYPE,
        external_payment_id: str = consts.EXTERNAL_PAYMENT_ID,
):
    request_arg = []

    # old event
    if old_kind is not None:
        request_arg.append(
            {
                'external_obj_id': consts.ORDER_ID,
                'event_at': consts.EVENT_AT,
                'service': consts.SERVICE,
                'status': consts.STATUS,
                'service_user_id': consts.SERVICE_USER_ID,
                'kind': old_kind,
                'external_event_ref': (
                    old_kind + '/' + consts.TASK_ID + '/' + consts.ORDER_ID
                ),
                'journal_entries': [],
                'tags': [],
                'data': {
                    'currency': currency,
                    'eventAt': consts.EVENT_AT,
                    'externalPaymentId': consts.EXTERNAL_PAYMENT_ID,
                    'orderNr': consts.ORDER_ID,
                    'paymentType': payment_type,
                    'items': old_items,
                },
            },
        )

    # new events
    new_events = _make_request_arg_new_events_without_optional(
        new_kind,
        new_items,
        'refund',
        flow_type,
        order_type,
        currency=currency,
        payment_type=payment_type,
        external_payment_id=external_payment_id,
    )
    request_arg.extend(new_events)

    return request_arg


def make_request_arg_no_payment(
        old_kind: str,
        new_kind: typing.Optional[str],
        new_items: list,
        flow_type: str,
        order_type: str,
        currency: str = consts.CURRENCY,
        external_payment_id: typing.Optional[str] = consts.EXTERNAL_PAYMENT_ID,
):
    request_arg = []

    request_arg.append(
        {
            'external_obj_id': consts.ORDER_ID,
            'event_at': consts.EVENT_AT,
            'service': consts.SERVICE,
            'status': consts.STATUS,
            'service_user_id': consts.SERVICE_USER_ID,
            'kind': old_kind,
            'external_event_ref': (
                old_kind + '/' + consts.TASK_ID + '/' + consts.ORDER_ID
            ),
            'journal_entries': [],
            'tags': [],
            'data': {'paymentNotReceivedAt': consts.EVENT_AT},
        },
    )

    products = []

    for new_item in new_items:
        product = {
            'product_id': new_item['productId'],
            'value_amount': new_item['amount'],
            'product_type': new_item['productType'],
        }
        products.append(product)

    data = {
        'order_nr': consts.ORDER_ID,
        'transaction_date': consts.TRANSACTION_DATE,
        'payment_not_received_at': consts.EVENT_AT,
        'courier_id': consts.COURIER_ID,
        'picker_id': consts.PICKER_ID,
        'place_id': consts.PLACE_ID,
        'payment_type': 'card',
        'payment_terminal_id': None,
        'currency': currency,
        'order_type': order_type,
        'flow_type': flow_type,
        'products': products,
    }
    if external_payment_id is not None:
        data['external_payment_id'] = external_payment_id

    if new_kind is not None:
        request_arg.append(
            {
                'external_obj_id': consts.ORDER_ID,
                'event_at': consts.EVENT_AT,
                'service': consts.SERVICE,
                'status': consts.STATUS,
                'service_user_id': consts.SERVICE_USER_ID,
                'kind': new_kind,
                'external_event_ref': (
                    new_kind + '/' + consts.TASK_ID + '/' + consts.ORDER_ID
                ),
                'journal_entries': [],
                'tags': [],
                'data': data,
            },
        )

    return request_arg


def make_request_arg_old_item(item_id: str, item_type: str, amount: str):
    return {
        'itemId': item_id,
        'itemType': item_type,
        'balanceClientId': consts.BALANCE_CLIENT_ID,
        'amount': amount,
    }


def make_request_arg_new_item(
        product_type: str,
        amount: str,
        counteragent_id: str,
        product_id: str,
        deal_id: str = None,
):
    return_value = {
        'productType': product_type,
        'amount': amount,
        'counteragentId': counteragent_id,
        'productId': product_id,
    }

    if deal_id is not None:
        return_value['dealId'] = deal_id
    return return_value


def make_request_arg_new_events(
        kind: str,
        items: list,
        transaction_type: str,
        flow_type: str,
        order_type: str,
        currency: str,
        payment_type: str,
        external_payment_id: typing.Optional[str] = None,
        payment_service: typing.Optional[str] = None,
        order_id=consts.ORDER_ID,
        transaction_date=consts.TRANSACTION_DATE,
):
    new_events = []

    for item in items:
        billing_doc_data = {
            'order_nr': order_id,
            'transaction_date': transaction_date,
            'amount': item['amount'],
            'currency': currency,
            'client_id': consts.BALANCE_CLIENT_ID,
            'event_at': consts.EVENT_AT,
            'payment_method': payment_type,
            'payment_terminal_id': consts.TERMINAL_ID,
            'counteragent_id': item['counteragentId'],
            'product_type': item['productType'],
            'product_id': item['productId'],
            'transaction_type': transaction_type,
            'flow_type': flow_type,
            'order_type': order_type,
        }
        if external_payment_id is not None:
            billing_doc_data['external_payment_id'] = external_payment_id
        if payment_service is not None:
            billing_doc_data['payment_service'] = payment_service

        billing_doc = {
            'external_obj_id': order_id,
            'event_at': consts.EVENT_AT,
            'service': consts.SERVICE,
            'status': consts.STATUS,
            'service_user_id': consts.SERVICE_USER_ID,
            'kind': kind,
            'external_event_ref': (
                kind
                + '/'
                + consts.TASK_ID
                + '/'
                + order_id
                + '/'
                + item['productId']
            ),
            'journal_entries': [],
            'tags': [],
            'data': billing_doc_data,
        }
        new_events.append(billing_doc)

    return new_events


def make_request_total_event(
        kind: str,
        items: list,
        transaction_type: str,
        flow_type: str,
        order_type: str,
        currency: str,
        payment_type: str,
        order_id: str = consts.ORDER_ID,
        transaction_date: str = consts.TRANSACTION_DATE,
        external_payment_id: typing.Optional[str] = None,
        processing_type: typing.Optional[str] = None,
):
    new_events = []

    for item in items:
        billing_doc_data = {
            'order_nr': order_id,
            'transaction_date': transaction_date,
            'amount': item['amount'],
            'currency': currency,
            'client_id': consts.BALANCE_CLIENT_ID,
            'event_at': consts.EVENT_AT,
            'payment_method': payment_type,
            'payment_terminal_id': consts.TERMINAL_ID,
            'counteragent_id': item['counteragentId'],
            'product_type': item['productType'],
            'product_id': item['productId'],
            'transaction_type': transaction_type,
            'flow_type': flow_type,
            'order_type': order_type,
            'processing_type': processing_type,
        }
        if 'dealId' in item:
            billing_doc_data['deal_id'] = item['dealId']

        if external_payment_id is not None:
            billing_doc_data['external_payment_id'] = external_payment_id

        billing_doc = {
            'external_obj_id': order_id,
            'event_at': consts.EVENT_AT,
            'service': consts.SERVICE,
            'status': consts.STATUS,
            'service_user_id': consts.SERVICE_USER_ID,
            'kind': kind,
            'external_event_ref': (
                kind
                + '/'
                + consts.TASK_ID
                + '/'
                + order_id
                + '/'
                + item['productId']
            ),
            'journal_entries': [],
            'tags': [],
            'data': billing_doc_data,
        }
        new_events.append(billing_doc)

    return new_events


def _make_request_arg_new_events_without_optional(
        kind: str,
        items: list,
        transaction_type: str,
        flow_type: str,
        order_type: str,
        currency: str,
        payment_type: str,
        external_payment_id: typing.Optional[str] = None,
):
    new_events = []

    for item in items:
        billing_doc_data = {
            'order_nr': consts.ORDER_ID,
            'transaction_date': consts.TRANSACTION_DATE,
            'amount': item['amount'],
            'currency': currency,
            'client_id': consts.BALANCE_CLIENT_ID,
            'event_at': consts.EVENT_AT,
            'payment_method': payment_type,
            'counteragent_id': item['counteragentId'],
            'product_type': item['productType'],
            'product_id': item['productId'],
            'transaction_type': transaction_type,
            'flow_type': flow_type,
            'order_type': order_type,
        }
        if external_payment_id is not None:
            billing_doc_data['external_payment_id'] = external_payment_id

        billing_doc = {
            'external_obj_id': consts.ORDER_ID,
            'event_at': consts.EVENT_AT,
            'service': consts.SERVICE,
            'status': consts.STATUS,
            'service_user_id': consts.SERVICE_USER_ID,
            'kind': kind,
            'external_event_ref': (
                kind
                + '/'
                + consts.TASK_ID
                + '/'
                + consts.ORDER_ID
                + '/'
                + item['productId']
            ),
            'journal_entries': [],
            'tags': [],
            'data': billing_doc_data,
        }
        new_events.append(billing_doc)

    return new_events


def make_billing_events_stq_kwargs(order_nr, billing_extra_data=None):
    result = {'order_nr': order_nr}
    if billing_extra_data is not None:
        result['billing_extra_data'] = billing_extra_data
    return result


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


def make_billing_processor_request(
        kind: str,
        items: list,
        transaction_type: str,
        flow_type: str,
        order_type: str,
        rule_name=consts.RULE_NAME,
        payment_terminal_id=consts.TERMINAL_ID,
        external_payment_id: str = consts.EXTERNAL_PAYMENT_ID,
        order_nr=consts.ORDER_ID,
        event_at=consts.EVENT_AT,
        transaction_date=consts.TRANSACTION_DATE,
        currency: str = consts.CURRENCY,
        payment_type: str = consts.PAYMENT_TYPE,
        payment_service: typing.Optional[str] = None,
):
    requests = []

    for item in items:
        data = {
            'order_nr': order_nr,
            'transaction_date': transaction_date,
            'amount': item['amount'],
            'currency': currency,
            'client_id': consts.BALANCE_CLIENT_ID,
            'event_at': event_at,
            'payment_method': payment_type,
            'counteragent_id': item['counteragentId'],
            'product_type': item['productType'],
            'product_id': item['productId'],
            'transaction_type': transaction_type,
            'flow_type': flow_type,
            'order_type': order_type,
            'payment_terminal_id': payment_terminal_id,
        }

        if 'dealId' in item:
            data['deal_id'] = item['dealId']

        if external_payment_id is not None:
            data['external_payment_id'] = external_payment_id
        if payment_service is not None:
            data['payment_service'] = payment_service

        request = {
            'order_nr': order_nr,
            'external_id': (
                kind
                + '/'
                + consts.TASK_ID
                + '/'
                + order_nr
                + '/'
                + item['productId']
            ),
            'event_at': event_at,
            'kind': kind,
            'data': data,
            'rule_name': rule_name,
        }
        requests.append(request)

    return requests


def make_eats_billing_nopay_request(
        kind: str,
        items: list,
        flow_type: str,
        order_type: str,
        order_nr=consts.ORDER_ID,
        currency: str = consts.CURRENCY,
        rule_name=consts.RULE_NAME,
        external_payment_id: typing.Optional[str] = consts.EXTERNAL_PAYMENT_ID,
):
    products = []

    for item in items:
        product = {
            'product_id': item['productId'],
            'value_amount': item['amount'],
            'product_type': item['productType'],
        }
        products.append(product)

    data = {
        'order_nr': consts.ORDER_ID,
        'transaction_date': consts.TRANSACTION_DATE,
        'payment_not_received_at': consts.EVENT_AT,
        'courier_id': consts.COURIER_ID,
        'picker_id': consts.PICKER_ID,
        'place_id': consts.PLACE_ID,
        'payment_type': 'card',
        'payment_terminal_id': None,
        'currency': currency,
        'order_type': order_type,
        'flow_type': flow_type,
        'products': products,
    }
    if external_payment_id is not None:
        data['external_payment_id'] = external_payment_id

    return {
        'order_nr': order_nr,
        'external_id': (kind + '/' + consts.TASK_ID + '/' + order_nr),
        'event_at': consts.EVENT_AT,
        'kind': kind,
        'data': data,
        'rule_name': rule_name,
    }


def make_billing_events_experiment() -> dict:
    return {
        'name': 'eats_payments_billing_billing_events',
        'consumers': ['eats-payments-billing/billing-events'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'default_value': {'is_send_to_billing_processor_allowed': True},
        'clauses': [
            {
                'title': 'service_fee',
                'value': {'is_send_to_billing_processor_allowed': False},
                'enabled': True,
                'is_signal': False,
                'predicate': {
                    'init': {
                        'value': 'service_fee',
                        'arg_name': 'item_type',
                        'arg_type': 'string',
                    },
                    'type': 'eq',
                },
                'is_tech_group': False,
                'extension_method': 'replace',
                'is_paired_signal': False,
            },
        ],
    }
