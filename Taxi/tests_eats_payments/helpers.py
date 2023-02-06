# pylint: disable=too-many-lines
import copy
import datetime as dt
import typing

from . import consts
from . import models

DEFAULT_EXTERNAL_PAYMENT_ID = 'c964a582b3b4b3dcd514ab1914a7d2a8'

DEFAULT_TRANSACTION = {
    'created': '2020-08-14T17:39:50.265000+03:00',
    'external_payment_id': DEFAULT_EXTERNAL_PAYMENT_ID,
    'cleared': '2020-08-14T17:39:50.265000+03:00',
    'fiscal_receipt_url': (
        'https://trust.yandex.ru/checks/abc/receipts/def?mode=mobile'
    ),
    'held': '2020-08-14T17:40:01.053000+03:00',
    'initial_sum': [{'amount': '5.00', 'item_id': 'big_mac'}],
    'operation_id': 'foo:12345',
    'payment_method_id': '123',
    'payment_type': 'card',
    'refunds': [],
    'status': 'hold_success',
    'sum': [{'amount': '5.00', 'item_id': 'big_mac'}],
    'technical_error': False,
    'terminal_id': '57000176',
    'updated': '2020-08-14T17:40:01.053000+03:00',
}

DEFAULT_OPERATION = {
    'created': '2020-08-14T17:39:49.663000+03:00',
    'id': 'create:12345',
    'status': 'done',
    'sum_to_pay': [
        {
            'items': [{'amount': '5.00', 'item_id': 'big_mac'}],
            'payment_type': 'card',
        },
    ],
}

EATS_PAYMENT_SERVICE = '645'
GROCERY_PAYMENT_SERVICE = '662'
TEST_CURRENCY = 'RUB'


def sort_items(items_by_payment_type):
    return [
        {
            'payment_type': payment_items['payment_type'],
            'items': sorted(
                payment_items['items'], key=lambda item: item['item_id'],
            ),
        }
        for payment_items in items_by_payment_type
    ]


def make_item(
        item_id: str,
        commission_category: typing.Optional[int] = None,
        amount: typing.Optional[str] = None,
        quantity: typing.Optional[str] = None,
        price: typing.Optional[str] = None,
        fiscal_receipt_info: typing.Optional[dict] = None,
        billing_info: typing.Optional[dict] = None,
        item_type: models.ItemType = models.ItemType.product,
        product_id: typing.Optional[str] = None,
) -> dict:
    item: typing.Dict[str, typing.Any] = {
        'item_id': item_id,
        'product_id': 'burger',
    }
    if product_id is not None:
        item['product_id'] = product_id
    if fiscal_receipt_info is not None:
        item['fiscal_receipt_info'] = fiscal_receipt_info
    if billing_info is not None:
        item['billing_info'] = billing_info
    if commission_category is not None:
        item['commission_category'] = commission_category
    if amount is not None:
        item['amount'] = amount
    if quantity is not None:
        item['quantity'] = quantity
    if price is not None:
        item['price'] = price
    item['item_type'] = item_type.value
    return item


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


def make_composition_product(
        composition_product_id: str,
        name: str,
        cost_for_customer: str,
        composition_product_type: str,
        vat: typing.Optional[str] = None,
):
    composition_product: typing.Dict[str, typing.Any] = {
        'id': composition_product_id,
        'name': name,
        'cost_for_customer': cost_for_customer,
        'type': composition_product_type,
        'vat': vat,
    }
    return composition_product


def make_composition_product_refund(
        refund_revision_id: str, refund_products: typing.List[dict],
):
    composition_product: typing.Dict[str, typing.Any] = {
        'refund_revision_id': refund_revision_id,
        'refund_products': refund_products,
    }

    return composition_product


def make_transactions_item(
        item_id: str,
        commission_category: typing.Optional[int] = None,
        amount: typing.Optional[str] = None,
        quantity: typing.Optional[str] = None,
        price: typing.Optional[str] = None,
        calc_amount: bool = False,
        fiscal_receipt_info: typing.Optional[dict] = None,
        product_id: typing.Optional[str] = None,
) -> dict:
    item: typing.Dict[str, typing.Any] = {
        'item_id': item_id,
        'product_id': 'burger' if product_id is None else product_id,
    }
    if commission_category is not None:
        item['commission_category'] = commission_category
    if fiscal_receipt_info is not None:
        item['fiscal_receipt_info'] = fiscal_receipt_info
    if amount is not None:
        item['amount'] = amount
    else:
        assert (
            quantity and price
        ), 'Either amount or both quantity and price should be present'
        item['quantity'] = quantity
        item['price'] = price
        # transactions returns amount in retrieve response
        if calc_amount:
            item['amount'] = f'{float(quantity) * float(price):.2f}'
    return item


def make_cargo_payment_item(
        article: str,
        count: int,
        nds: str,
        price: str,
        supplier_inn: str,
        title: str,
        returned: int = None,
        currency: str = TEST_CURRENCY,
        agent_type: str = None,
) -> dict:
    result = {
        'article': article,
        'count': count,
        'currency': currency,
        'nds': nds,
        'price': price,
        'supplier_inn': supplier_inn,
        'title': title,
    }
    if returned is not None:
        result['returned'] = returned
    if agent_type is not None:
        result['agent_type'] = agent_type
    if supplier_inn is None:
        del result['supplier_inn']

    return result


def make_cargo_payment_item_from(item):
    payment_item = {'article': item['item_id'], 'currency': TEST_CURRENCY}
    if 'fiscal_receipt_info' in item:
        payment_item['nds'] = item['fiscal_receipt_info']['vat']
        payment_item['supplier_inn'] = '1234567890'
        payment_item['title'] = item['fiscal_receipt_info']['title']
    else:
        payment_item['nds'] = 'nds_none'
        payment_item['supplier_inn'] = '7810351835'
        if item['item_type'] == 'delivery':
            payment_item['title'] = 'Доставка'
        elif item['item_type'] == 'assembly':
            payment_item['title'] = 'Услуга по сборке'
        elif item['item_type'] == 'retail':
            payment_item['title'] = 'Расходы на исполнение поручений по заказу'
        elif item['item_type'] == 'service_fee':
            payment_item['title'] = 'Сервисный сбор'
        else:
            payment_item['title'] = ''
    if 'amount' in item:
        payment_item['count'] = 1
        payment_item['price'] = item['amount']
    else:
        # count is always 1 for weight products
        payment_item['count'] = 1
        payment_item['price'] = item['price']

    if 'item_type' in item:
        if models.ItemType(item['item_type']) is models.ItemType.service_fee:
            payment_item['agent_type'] = 'none'
        else:
            payment_item['agent_type'] = 'another_agent'

    if payment_item['agent_type'] == 'none':
        del payment_item['supplier_inn']

    return payment_item


def make_db_row(
        item_id: str,
        order_id: str = 'test_order',
        place_id: str = '100500',
        balance_client_id='123456',
        item_type: str = 'product',
) -> dict:
    return {
        'order_id': order_id,
        'item_id': item_id,
        'place_id': place_id,
        'balance_client_id': balance_client_id,
        'type': item_type,
    }


def make_billing_item(
        item_id: str,
        amount: str,
        place_id: str = '100500',
        balance_client_id: str = '123456',
        item_type: str = 'product',
) -> dict:
    return {
        'item_id': item_id,
        'amount': amount,
        'place_id': place_id,
        'balance_client_id': balance_client_id,
        'item_type': item_type,
    }


def make_transactions_payment_items(
        payment_type: str, items: typing.List[dict],
) -> dict:
    return {'payment_type': payment_type, 'items': items}


def make_transaction(**extra) -> dict:
    return {**DEFAULT_TRANSACTION, **extra}


def make_operation(**extra) -> dict:
    return {**DEFAULT_OPERATION, **extra}


def make_callback_transaction(status: str, **extra) -> dict:
    return {
        'external_payment_id': DEFAULT_EXTERNAL_PAYMENT_ID,
        'payment_type': 'card',
        'status': status,
        **extra,
    }


def make_wallet_payload(
        cashback_service: str,
        order_id: str,
        wallet_id: str,
        service_id=consts.EATS_CASHBACK_SERVICE_ID,
) -> dict:

    result = {
        'service_id': service_id,
        'cashback_service': cashback_service,
        'order_id': order_id,
        'has_plus': 'true',
        'wallet_id': wallet_id,
    }

    if (
            cashback_service == 'lavka'
            and service_id == consts.GROCERY_CASHBACK_SERVICE_ID
    ):
        result['ticket'] = 'NEWSERVICE-1322'

    return result


def map_service_to_wallet_service(service: str) -> str:
    if service == 'eats':
        return 'eda'

    if service == 'grocery':
        return 'lavka'

    raise RuntimeError('unknown service')


def make_refund(refund_sum: typing.List[dict], operation_id: str, **kwargs):
    return {
        'created': '2020-08-14T17:39:50.265000+03:00',
        'updated': '2020-08-14T17:39:50.265000+03:00',
        'sum': refund_sum,
        'status': 'refund_success',
        'operation_id': operation_id,
        **kwargs,
    }


def _get_item_id(idx):
    return f'item_id_{idx}'


def _make_items(
        request_items: typing.List[models.TestItem],
        create_item_func,
        is_request=False,
) -> typing.List[dict]:
    result = []

    for idx, item in enumerate(request_items):
        item_id = (
            item.item_id if item.item_id is not None else _get_item_id(idx)
        )

        if item.amount is not None:
            amount = item.amount
            if not is_request:
                amount = item.price_without_complement()
            result.append(
                create_item_func(
                    item_id=item_id, amount=amount, product_id=item.product_id,
                ),
            )
        else:
            price = item.price
            if not is_request:
                price = item.price_without_complement()
            result.append(
                create_item_func(
                    item_id=item_id,
                    price=price,
                    quantity=item.quantity,
                    product_id=item.product_id,
                ),
            )
    return result


def make_transactions_items(request_items: typing.List[models.TestItem]):
    return _make_items(
        request_items=request_items,
        create_item_func=make_transactions_item,
        is_request=False,
    )


# pylint: disable=invalid-name
def make_transactions_items_complement(
        request_items: typing.List[models.TestItem],
):
    items = []
    for idx, item in enumerate(request_items):
        if item.by_complement is None:
            continue

        item_id = (
            item.item_id if item.item_id is not None else _get_item_id(idx)
        )

        if item.amount is not None:
            items.append(
                make_transactions_item(
                    item_id=item_id,
                    amount=item.by_complement,
                    product_id=item.product_id,
                ),
            )
        else:
            items.append(
                make_transactions_item(
                    item_id=item_id,
                    price=item.by_complement,
                    quantity=item.quantity,
                    product_id=item.product_id,
                ),
            )
    return items


def to_complement_payload(complement):
    complement_payload = {}
    if complement is not None:
        complement_payload = {
            'complements': [
                {
                    'payment_method': {
                        'id': complement.payment_id,
                        'type': complement.payment_type,
                    },
                    'amount': complement.amount,
                },
            ],
        }
        amount = getattr(complement, 'item_types_amount', None)
        if amount is not None:
            complement_payload['complements'][0]['item_types_amount'] = amount
    return complement_payload


def make_request_items(request_items: typing.List[models.TestItem]):
    result = []

    for idx, item in enumerate(request_items):
        if item.amount is not None:
            amount = item.amount
            result.append(
                make_item(
                    item_id=_get_item_id(idx),
                    amount=amount,
                    item_type=item.item_type,
                    billing_info=item.billing_info_as_json_object(),
                ),
            )
        else:
            price = item.price
            result.append(
                make_item(
                    item_id=_get_item_id(idx),
                    price=price,
                    quantity=item.quantity,
                    item_type=item.item_type,
                    billing_info=item.billing_info_as_json_object(),
                ),
            )
    return result


def make_billing_experiment(send_enabled) -> dict:
    return {
        'name': 'eats_payments_billing_notifications',
        'consumers': ['eats-payments/billing-notifications'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'send_billing_notifications_enabled': send_enabled},
            },
        ],
    }


def check_callback_mock(
        callback_mock,
        task_id: str,
        queue: str,
        times_called: int = 1,
        eta: dt.datetime = None,
        **expected_kwargs: dict,
):
    assert callback_mock.times_called == times_called
    if times_called == 0:
        return
    callback_call = callback_mock.next_call()

    print(callback_call['id'])
    print(task_id)
    assert callback_call['id'] == task_id
    assert callback_call['queue'] == queue
    if eta is not None:
        assert callback_call['eta'] == eta

    if not expected_kwargs:
        return

    callback_kwargs = callback_call['kwargs']
    callback_kwargs.pop('log_extra')

    print(callback_kwargs)
    print(expected_kwargs)
    assert callback_kwargs == expected_kwargs


def make_debts_experiment(
        debt_enabled,
        eats_debt_user_scoring_enabled,
        auto_debt_enabled=False,
        check_invoice_status_delay=1000,
        check_invoice_status_task_ttl=5000,
        request_to_user_scoring_verdict_enabled=False,
        allow_credit_if_scoring_is_unavailable=False,
) -> dict:
    return {
        'name': 'eats_payments_debts',
        'consumers': ['eats-payments/debts'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {
                    'debt_enabled': debt_enabled,
                    'request_to_eats_debt_user_scoring_enabled': (
                        eats_debt_user_scoring_enabled
                    ),
                    'request_to_user_scoring_verdict_enabled': (
                        request_to_user_scoring_verdict_enabled
                    ),
                    'auto_debt_enabled': auto_debt_enabled,
                    'check_invoice_status_delay': check_invoice_status_delay,
                    'check_invoice_status_task_ttl': (
                        check_invoice_status_task_ttl
                    ),
                    'allow_credit_if_scoring_is_unavailable': (
                        allow_credit_if_scoring_is_unavailable
                    ),
                },
            },
        ],
    }


def make_business_experiment(business=None) -> dict:
    if business is None:
        business = consts.DEFAULT_BUSINESS_CONFIG
    return {
        'name': 'eats_payments_business_tokens',
        'consumers': ['eats-payments/business-tokens'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': business,
            },
        ],
    }


def get_complement_model(payment_type, amount, service=consts.DEFAULT_SERVICE):
    if payment_type == 'corp':
        return models.ComplementCorp(amount=amount)
    return models.Complement(amount=amount, service=service)


def make_terminal_pass_params_experiment(enabled) -> dict:
    return {
        'name': 'terminal_pass_params',
        'consumers': ['eats-payments/terminal-pass-params'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'terminal_pass_params_enabled': enabled},
            },
        ],
    }


def make_new_service_revision(enabled) -> dict:
    return {
        'name': 'eats_payments_new_service_revision',
        'consumers': ['eats-payments/new_service_revision'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'is_new_service_available': enabled},
            },
        ],
    }


def make_terminal_pass_params_experiment2(enabled) -> dict:
    return {
        'name': 'terminal_pass_params',
        'consumers': ['eats-payments/terminal-pass-params'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'value': {'terminal_pass_params_enabled': enabled},
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'yandex_uid',
                                    'arg_type': 'string',
                                    'value': '100500',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'merchant',
                                    'arg_type': 'string',
                                    'value': 'eda',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'business',
                                    'arg_type': 'string',
                                    'value': 'restaurant',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'currency',
                                    'arg_type': 'string',
                                    'value': 'RUB',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'payment_type',
                                    'arg_type': 'string',
                                    'value': 'card',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
        ],
    }


def make_hold_unhold_experiment() -> dict:
    return {
        'name': 'eats_payments_hold_unhold',
        'consumers': ['eats-payments/orders-close'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'value': {
                    'hold_unhold_enabled': True,
                    'hold_delay_seconds': 1,
                    'maximum_delta': 0.50,
                },
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'bin',
                                    'set': ['427929', '424242'],
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'arg_name': 'payment_method',
                                    'arg_type': 'string',
                                    'value': 'card',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'currency',
                                    'arg_type': 'string',
                                    'value': 'RUB',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
        ],
    }


def make_debt_technical_error_experiment() -> dict:
    return {
        'name': 'eats_payments_debt_technical_error',
        'consumers': ['eats-payments/debt_technical_error'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'value': {'is_debt_allowed': True},
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'error_reason_code',
                                    'set': [
                                        'trust2host.couldnt_connect_timeout',
                                    ],
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'arg_name': 'payment_method',
                                    'arg_type': 'string',
                                    'value': 'card',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
            {
                'value': {'is_debt_allowed': True},
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': 'true',
                                    'arg_name': 'is_technical_error',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'predicate': {
                                        'init': {
                                            'set': ['sbp'],
                                            'arg_name': 'payment_method',
                                            'set_elem_type': 'string',
                                        },
                                        'type': 'in_set',
                                    },
                                },
                                'type': 'not',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
        ],
    }


def make_debt_collector_experiment(debt_collector_enabled) -> dict:
    return {
        'name': 'eats_payments_debt_collector',
        'consumers': ['eats-payments/debt-collector'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'debt_collector_enabled': debt_collector_enabled},
            },
        ],
    }


def make_debt(
        order_id='test_order',
        reason_code='technical_debt',
        debt=None,
        total=None,
) -> dict:
    if debt is None:
        debt = []
    if total is None:
        total = []
    return {
        'id': order_id,
        'reason': {'code': reason_code, 'metadata': {}},
        'metadata': {},
        'service': 'eats',
        'debtors': ['eats/yandex_uid/12345'],
        'version': 1,
        'invoice': {
            'id': order_id,
            'transactions_installation': 'eda',
            'originator': 'eats_payments',
        },
        'collection': {
            'strategy': {'kind': 'null', 'metadata': {}},
            'installed_at': '2021-09-01T00:00:00+03:00',
        },
        'transactions_params': {},
        'currency': 'RUB',
        'items_by_payment_type': {'debt': debt, 'total': total},
        'created_at': '2021-09-01T00:00:00+03:00',
        'updated_at': '2021-09-01T00:00:00+03:00',
    }


def make_pass_afs_params_experiment(  # pylint: disable=invalid-name
        pass_afs_params, clause_predicate=None,
) -> dict:
    return {
        'name': 'eats_payments_pass_afs_params',
        'consumers': ['eats-payments/pass_afs_params'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': clause_predicate or {'type': 'true'},
                'value': {'pass_afs_params': pass_afs_params},
            },
        ],
        'default_value': {'pass_afs_params': False},
    }


def make_eats_payments_receipts_operations_switch_experiment(  # noqa: E501 pylint: disable=invalid-name,line-too-long
        enabled,
) -> dict:
    return {
        'name': 'eats_payments_receipts_operations_switch',
        'consumers': ['eats-payments/receipts_operations_switch'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
    }


def make_pass_3ds_params_experiment(  # pylint: disable=invalid-name
        pass_3ds_availability_true, clause_predicate=None,
) -> dict:
    return {
        'name': 'eats_payments_pass_3ds_params',
        'consumers': ['eats-payments/pass_3ds_params'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': clause_predicate or {'type': 'true'},
                'value': {
                    'pass_3ds_availability_true': pass_3ds_availability_true,
                    'pass_3ds_availability_true_for_not_available_card_only': (
                        False
                    ),
                    'show_not_available_cards_if_available_cards_exists': True,
                    'pass_developer_payload': pass_3ds_availability_true,
                },
            },
        ],
        'default_value': {'pass_3ds_availability_true': False},
    }


def make_operations_config() -> dict:
    return {
        'name': 'eats_payments_operations',
        'consumers': ['eats-payments/operations'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [],
        'default_value': {'is_enabled': True, 'max_attempts': 2},
    }


def make_without_trust_orders_config() -> dict:
    return {
        'name': 'eats_payments_without_trust_orders',
        'consumers': ['eats-payments/eats_payments_without_trust_orders'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [],
        'default_value': {'enabled': True},
    }


def make_payment_fallback() -> dict:
    fallback = {
        'fallback': {
            'name': 'test_fallback',
            'terminal_id': '95426005',
            'processing_cc': 'test_dummy_name',
        },
    }

    clause = {
        'title': 'test',
        'value': {
            'fallback': {
                'name': 'test_fallback',
                'terminal_id': '95426005',
                'processing_cc': 'test_dummy_name',
            },
        },
        'enabled': True,
        'is_signal': False,
        'predicate': {
            'type': 'all_of',
            'init': {
                'predicates': [
                    {
                        'init': {
                            'value': '95426005',
                            'arg_name': 'terminal_id',
                            'arg_type': 'string',
                        },
                        'type': 'eq',
                    },
                    {
                        'init': {
                            'predicate': {
                                'init': {
                                    'value': 'not_enough_funds',
                                    'arg_name': 'error_reason_code',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                        },
                        'type': 'not',
                    },
                    {
                        'init': {
                            'value': 'card',
                            'arg_name': 'payment_type',
                            'arg_type': 'string',
                        },
                        'type': 'eq',
                    },
                ],
            },
        },
        'is_tech_group': False,
        'extension_method': 'replace',
        'is_paired_signal': False,
    }

    return {
        'name': 'eats_payments_payment_fallback',
        'consumers': ['eats-payments/payment_fallback'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [clause],
        'default_value': fallback,
    }
