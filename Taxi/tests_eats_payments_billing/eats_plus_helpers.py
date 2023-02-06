import typing

from tests_eats_payments_billing import eats_plus_consts


def make_stq_kwargs(
        rewards: typing.List[dict],
        amount: str,
        comission_cashback: str,
        base_amount: str = eats_plus_consts.BASE_AMOUNT,
        order_id: str = eats_plus_consts.ORDER_ID,
        has_payload: bool = True,
) -> dict:
    payload = {}

    if has_payload:
        payload = {
            'cashback_service': eats_plus_consts.CASHBACK_SERVICE,
            'cashback_type': eats_plus_consts.CASHBACK_TYPE,
            'amount': amount,
            'commission_cashback': comission_cashback,
            'currency': eats_plus_consts.CURRENCY,
            'service_id': eats_plus_consts.SERVICE_ID,
            'has_plus': eats_plus_consts.TRUE,
            'order_id': order_id,
            'base_amount': base_amount,
            'client_id': eats_plus_consts.CLIENT_ID,
            'city': eats_plus_consts.CITY,
        }

    return {
        'order_id': order_id,
        'last_operation': {
            'operation_id': eats_plus_consts.OPERATION_ID,
            'yandex_uid': eats_plus_consts.YANDEX_UID,
            'user_ip': eats_plus_consts.USER_IP,
            'wallet_id': eats_plus_consts.WALLET_ID,
            'reward': rewards,
            'billing_service': eats_plus_consts.BILLING_SERVICE,
            'extra_payload': payload,
        },
    }


def make_billing_events_stq_kwargs(order_nr):
    return {'order_nr': order_nr}


def make_stq_reward(amount: str, source: str) -> dict:
    return {'amount': amount, 'source': source}


def make_request_arg_payment(
        amount: str,
        amount_per_place: str,
        amount_per_eda: str,
        commission_cashback: str,
        order_id: str = eats_plus_consts.ORDER_ID,
        base_amount: str = eats_plus_consts.BASE_AMOUNT,
):
    request_arg = []

    request_arg.append(
        {
            'external_obj_id': order_id,
            'event_at': eats_plus_consts.EVENT_AT,
            'service': eats_plus_consts.SERVICE,
            'status': eats_plus_consts.STATUS,
            'service_user_id': eats_plus_consts.SERVICE_USER_ID,
            'kind': eats_plus_consts.BILLING_PLUS_CASHBACK_EMISSION,
            'external_event_ref': (
                eats_plus_consts.BILLING_PLUS_CASHBACK_EMISSION
                + '/'
                + eats_plus_consts.OPERATION_ID
                + '/'
                + order_id
            ),
            'journal_entries': [],
            'tags': [],
            'data': {
                'order_nr': order_id,
                'event_at': eats_plus_consts.EVENT_AT,
                'amount': amount,
                'amount_details': {
                    'plus_cashback_amount_per_place': amount_per_place,
                    'plus_cashback_amount_per_eda': amount_per_eda,
                },
                'currency': eats_plus_consts.CURRENCY,
                'client_id': eats_plus_consts.CLIENT_ID,
                'payload': {
                    'cashback_service': eats_plus_consts.CASHBACK_SERVICE,
                    'cashback_type': eats_plus_consts.CASHBACK_TYPE,
                    'amount': amount,
                    'commission_cashback': commission_cashback,
                    'currency': eats_plus_consts.CURRENCY,
                    'service_id': eats_plus_consts.SERVICE_ID,
                    'has_plus': eats_plus_consts.TRUE,
                    'order_id': order_id,
                    'base_amount': base_amount,
                    'client_id': eats_plus_consts.CLIENT_ID,
                    'city': eats_plus_consts.CITY,
                },
                'flow_type': 'native',
            },
        },
    )

    return request_arg


def make_b_processor_cashback_emis(
        amount: str,
        amount_per_place: str,
        amount_per_eda: str,
        commission_cashback: str,
        order_id: str = eats_plus_consts.ORDER_ID,
        base_amount: str = eats_plus_consts.BASE_AMOUNT,
):
    request = {
        'order_nr': order_id,
        'external_id': 'BillingPlusCashbackEmission/operation_id/' + order_id,
        'event_at': '2021-09-01T16:30:55.628907+00:00',
        'kind': 'plus_cashback_emission',
        'data': {
            'order_nr': order_id,
            'event_at': '2021-09-01T16:30:55Z',
            'amount': amount,
            'amount_details': {
                'plus_cashback_amount_per_place': amount_per_place,
                'plus_cashback_amount_per_eda': amount_per_eda,
            },
            'currency': 'RUB',
            'client_id': '1235',
            'payload': {
                'cashback_service': 'eda',
                'cashback_type': 'transaction',
                'amount': '50',
                'commission_cashback': commission_cashback,
                'currency': 'RUB',
                'service_id': '645',
                'has_plus': 'true',
                'order_id': order_id,
                'base_amount': base_amount,
                'client_id': '1235',
                'city': 'Moscow',
            },
            'flow_type': 'native',
        },
        'rule_name': 'default',
    }

    return [request]


def make_b_processor_cashback_total(
        amount: str,
        processing_type: typing.Optional[str] = None,
        order_id: str = eats_plus_consts.ORDER_ID,
        flow_type: str = 'native',
        order_type: str = 'native',
):
    request = {
        'order_nr': order_id,
        'external_id': (
            'BillingPaymentUpdatePlusCashback/sample_task/'
            + order_id
            + '/product/'
            + flow_type
            + '/'
            + order_type
        ),
        'event_at': '2020-09-23T00:00:00+00:00',
        'kind': 'payment_update_plus_cashback',
        'data': {
            'order_nr': order_id,
            'transaction_date': '2020-09-28T18:42:59Z',
            'amount': amount,
            'currency': '',
            'client_id': '9876',
            'event_at': '2020-09-23T00:00:00Z',
            'payment_method': 'cashback',
            'counteragent_id': '3456',
            'product_type': 'product',
            'product_id': 'product/' + flow_type + '/' + order_type,
            'transaction_type': 'plus_update',
            'flow_type': flow_type,
            'order_type': order_type,
            'processing_type': processing_type,
        },
        'rule_name': 'default',
    }

    return [request]
