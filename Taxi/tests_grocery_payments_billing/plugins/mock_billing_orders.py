import copy
import dataclasses
import decimal
import enum
import typing

import pytest

from tests_grocery_payments_billing import consts
from tests_grocery_payments_billing import models


DEFAULT_RESPONSE = {
    'orders': [
        {'topic': 'topic', 'external_ref': 'external_ref', 'doc_id': 1},
    ],
}
COURIER = {'type': consts.TRANSPORT_TYPE, 'id': consts.EATS_COURIER_ID}


def _vat_amount(amount, vat):
    if vat == consts.WITHOUT_VAT:
        return '0'

    amount = decimal.Decimal(amount)
    vat = decimal.Decimal(vat)

    amount_without_vat = (
        amount * decimal.Decimal(100) / (decimal.Decimal(100) + vat)
    )
    amount_without_vat = round(amount_without_vat, 2)

    # normalize for "8.00" => "8"
    return str((amount - amount_without_vat).normalize())


@dataclasses.dataclass
class Payment:
    def __post_init__(self):
        self.vat_amount = _vat_amount(self.amount_with_vat, self.vat_rate)
        self.amount_without_vat = str(
            decimal.Decimal(self.amount_with_vat)
            - decimal.Decimal(self.vat_amount),
        )

    amount_with_vat: str
    detailed_product: str
    payment_kind: str
    product: str
    transaction_type: str
    vat_rate: str
    item_id: str
    quantity: str
    vat_amount: typing.Optional[str] = None
    amount_without_vat: typing.Optional[str] = None
    event_time: typing.Optional[str] = None


class Version(enum.Enum):
    version_1 = 'v1'
    version_2 = 'v2'


@pytest.fixture(name='billing_orders')
def mock_billing_orders(mockserver):
    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _mock_process_async(request):
        data = context.data

        if 'http_error_code' in data and data['http_error_code'] is not None:
            return mockserver.make_response('{}', data['http_error_code'])

        if context.version_to_check is None:
            return DEFAULT_RESPONSE

        if context.version_to_check == Version.version_1:
            _check_v1_request(data, request)
        elif context.version_to_check == Version.version_2:
            _check_v2_request(data, request)

        return DEFAULT_RESPONSE

    class Context:
        def __init__(self):
            self.data = {}
            self.version_to_check = None

        def check_request_v1(
                self, *, order_id, item_id, operation_id, payments,
        ):
            self.version_to_check = Version.version_1

            self.data['order_id'] = order_id
            self.data['item_id'] = item_id
            self.data['operation_id'] = operation_id
            self.data['payments'] = payments

        def check_request_v2(self, **kwargs):
            self.version_to_check = Version.version_2
            self.data.update(**kwargs)

        def set_http_error_code(self, code):
            self.data['http_error_code'] = code

        def process_async_times_called(self):
            return _mock_process_async.times_called

        def flush(self):
            _mock_process_async.flush()

    context = Context()
    return context


def _check_v1_request(data, request):
    order_id = data['order_id']
    item_id = data['item_id']
    operation_id = data['operation_id']
    assert request.json == {
        'orders': [
            {
                'data': {
                    'context': {},
                    'entries': [],
                    'event_version': 1,
                    'payments': data['payments'],
                    'schema_version': 'v1',
                    'topic_begin_at': data.get(
                        'topic_begin_at', consts.FINISH_STARTED,
                    ),
                },
                'event_at': consts.NOW,
                'external_ref': '1',
                'kind': 'arbitrary_payout',
                'topic': (
                    f'taxi/lavka_grocery_sale/{order_id}/{item_id}/'
                    f'{operation_id}'
                ),
            },
        ],
    }


def _check_v2_request(data, request):
    payments_by_item_id: typing.Dict[str, typing.List[Payment]] = data[
        'payments_by_item_id'
    ]
    errors = {}
    used_topic = {}

    order_id = data.get('order_id', consts.ORDER_ID)
    country = data.get('country', models.Country.Russia)
    oebs_depot_id = consts.OEBS_DEPOT_ID

    if 'oebs_depot_id' in data.keys():
        oebs_depot_id = data['oebs_depot_id']

    if data.get('order_cycle') == 'eats':
        topic_prefix = ''
    else:
        topic_prefix = f'{consts.EXTERNAL_PAYMENT_ID}/'

    for item_id, payments in payments_by_item_id.items():
        topic = f'lavka/grocery_sale/{order_id}/{topic_prefix}{item_id}'

        topic_order, all_topic_names = _get_order_by_topic(request, topic)
        if topic_order is None:
            errors[topic] = (
                'not found in request, request topics: '
                + ', '.join(all_topic_names)
            )
            continue

        used_topic[topic] = True

        common_data = {
            'data': {
                'event_version': 1,
                'schema_version': 'v2',
                'template_entries': [],
                'payments': None,
                'topic_begin_at': data.get(
                    'topic_begin_at', consts.FINISH_STARTED,
                ),
            },
            'event_at': consts.NOW,
            'external_ref': '1',
            'kind': 'arbitrary_payout',
            'topic': topic,
        }

        _check_order_common_data(topic_order, common_data)

        topic_payments = copy.deepcopy(topic_order['data']['payments'])

        payment_method_type = {}
        if 'payment_type' in data:
            payment_method_type = {'payment_method_type': data['payment_type']}

        for payment in payments:
            expected_topic_payment = {
                'agglomeration': consts.AGGLOMERATION,
                'client_id': data['balance_client_id'],
                'event_time': data.get('event_time', payment.event_time),
                'original_event_time': data.get(
                    'original_event_time', consts.FINISH_STARTED,
                ),
                'company_type': consts.COMPANY_TYPE,
                'country': country.country_iso3,
                'currency': 'RUB',
                'contract_id': consts.CONTRACT_ID,
                'firm_id': consts.FIRM_ID,
                'ignore_in_balance': consts.IGNORE_IN_BALANCE,
                'payload': {
                    'order_id': order_id,
                    'depot_region_id': consts.DEPOT_REGION_ID,
                    'receipt_id': data.get('receipt_id', consts.RECEIPT_ID),
                    'courier': data.get('courier', COURIER),
                    'item': {
                        'id': payment.item_id,
                        'quantity': payment.quantity,
                    },
                    'order_cycle': data.get('order_cycle', 'grocery'),
                    'depot': {
                        'region_id': consts.DEPOT_REGION_ID,
                        'oebs_depot_id': oebs_depot_id,
                    },
                    **payment_method_type,
                },
                'service_id': consts.SERVICE_ID,
                'amount_with_vat': payment.amount_with_vat,
                'detailed_product': payment.detailed_product,
                'payment_kind': payment.payment_kind,
                'product': payment.product,
                'transaction_type': payment.transaction_type,
                'vat_amount': payment.vat_amount,
                'vat_rate': payment.vat_rate,
                'amount_without_vat': payment.amount_without_vat,
            }

            if not _remove_if_exists_and_equals(
                    expected_topic_payment, topic_payments,
            ):
                if topic not in errors:
                    errors[topic] = {}
                errors[topic][
                    f'detailed_product:{payment.detailed_product}'
                    f'item_id:{payment.item_id} quantity:{payment.quantity}'
                ] = 'not found in request'

        if topic_payments:
            if topic not in errors:
                errors[topic] = {}
            errors[topic][
                'extra-payments'
            ] = f'request topic extra payments: {topic_payments}'

    request_topics_len = len(request.json['orders'])
    input_topics_len = len(payments_by_item_id)
    if input_topics_len != request_topics_len:
        unused_topics = _get_unused_topics(used_topic, request)
        errors['length-error'] = (
            f'request topics count: {request_topics_len}, input topics count: '
            f'{input_topics_len}, did not check topics: '
            + ', '.join(unused_topics)
        )

    if errors:
        print(errors)
        assert errors == {}, errors


def _get_unused_topics(used_topic, request):
    unused_topics = []
    for order in request.json['orders']:
        topic = order['topic']
        if topic in used_topic:
            continue
        unused_topics.append(topic)
    return unused_topics


def _check_order_common_data(order, common_data):
    order_copy = copy.deepcopy(order)
    order_copy['data']['payments'] = None

    for key, value in common_data.items():
        assert order_copy[key] == value, key


def _get_order_by_topic(request, topic):
    topics = []
    for order in request.json['orders']:
        order_topic = order['topic']
        if order_topic == topic:
            return order, None
        topics.append(order_topic)

    return None, topics


def _is_same_payment(payment, order_payment):
    order_payment_item = order_payment['payload']['item']
    payment_item = payment['payload']['item']
    return (
        order_payment['detailed_product'] == payment['detailed_product']
        and order_payment_item['id'] == payment_item['id']
        and order_payment_item['quantity'] == payment_item['quantity']
    )


def _remove_if_exists_and_equals(payment, order_payments):
    order_payments_with_indexes = enumerate(order_payments)
    for index, order_payment in order_payments_with_indexes:
        if _is_same_payment(payment, order_payment):
            item_id = payment['payload']['item']['id']
            quantity = payment['payload']['item']['quantity']
            detailed_product = payment['detailed_product']
            assert order_payment == payment, str(
                f'Payment mismatched, item_id: {item_id} '
                f'quantity: {quantity} '
                f'detailed_product: {detailed_product}',
            )

            order_payments.pop(index)
            return True
    return False
