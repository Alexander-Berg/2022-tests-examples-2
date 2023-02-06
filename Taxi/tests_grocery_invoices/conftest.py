import decimal
import typing

# pylint: disable=import-error
from grocery_mocks.utils import helpers as mock_helpers
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_invoices_plugins import *  # noqa: F403 F401


from tests_grocery_invoices import consts
from tests_grocery_invoices import models


@pytest.fixture(name='easy_count')
def mock_easy_count(mockserver):
    class Context:
        def __init__(self):
            self.customer_name = None
            self.developer_email = None
            self.items: typing.List[models.Item] = []
            self.payment = None
            self.price_total = None
            self.idempotency_token = None
            self.invoice_type = None
            self.is_payment = None
            self.document_vat = None
            self.user_uuid = None
            self.parent = None

            self.check_request_flag = False

        def check_request(
                self,
                *,
                customer_name: str,
                developer_email: str,
                items: typing.List[models.Item],
                payment: models.EasyCountPayment,
                price_total: str,
                invoice_type: int,
                is_payment: bool,
                idempotency_token: str = None,
                document_vat: typing.Optional[str] = None,
                user_uuid: typing.Optional[str] = None,
                parent: typing.Optional[str] = None,
        ):
            self.customer_name = customer_name
            self.developer_email = developer_email
            self.items = items
            self.payment = payment
            self.price_total = price_total
            self.idempotency_token = idempotency_token
            self.invoice_type = invoice_type
            self.is_payment = is_payment
            self.document_vat = document_vat
            self.user_uuid = user_uuid
            self.parent = parent

            self.check_request_flag = True

        def times_called(self):
            return _mock_create.times_called

        def flush(self):
            _mock_create.flush()

        def _to_easy_payment_type(self, payment_type: str):
            if payment_type == models.PaymentType.card.value:
                return 3
            if payment_type in (
                    models.PaymentType.applepay.value,
                    models.PaymentType.cibus.value,
            ):
                return 9

            assert False
            return None

        def get_easy_count_payment(
                self,
                total_price: str,
                payment_type: str = models.PaymentType.card.value,
                cc_type: typing.Optional[int] = None,  # visa
                cc_number: typing.Optional[str] = None,
                cc_deal_type: typing.Optional[int] = None,
                other_payment_type_name: typing.Optional[str] = None,
        ) -> models.EasyCountPayment:
            if payment_type == models.PaymentType.card.value:
                if cc_type is None:
                    cc_type = 2  # visa
                if cc_number is None:
                    cc_number = consts.DEFAULT_LAST_4_DIGITS
                if cc_deal_type is None:
                    cc_deal_type = 1  # just 1 for card
            if payment_type == models.PaymentType.applepay.value:
                if other_payment_type_name is None:
                    other_payment_type_name = 'Apple Pay'
            if payment_type == models.PaymentType.cibus.value:
                if other_payment_type_name is None:
                    other_payment_type_name = 'Cibus'

            return models.EasyCountPayment(
                cc_deal_type=cc_deal_type,
                cc_number=cc_number,
                cc_type=cc_type,
                other_payment_type_name=other_payment_type_name,
                payment_sum=total_price,
                payment_type=self._to_easy_payment_type(payment_type),
            )

    @mockserver.json_handler('/easy-count/api/createDoc')
    def _mock_create(request):
        assert request.headers['User-Agent'] == consts.EASY_COUNT_USER_AGENT

        if context.check_request_flag:
            items = []
            for item in context.items:

                if item.vat == consts.ZERO_VAT:
                    vat_type = 'NON'
                else:
                    vat_type = 'INC'

                items.append(
                    {
                        'details': item.title,
                        'amount': item.quantity,
                        'price': item.price,
                        'vat_type': vat_type,
                    },
                )

                if item.full_price is None:
                    continue

                price = item.price
                full_price = item.full_price
                discount = decimal.Decimal(full_price) - decimal.Decimal(price)
                items[-1]['discount_price'] = str(
                    discount * decimal.Decimal(item.quantity),
                )
                items[-1]['discount_type'] = 'NUMBER'
                items[-1]['price'] = full_price

            vat = consts.DEFAULT_VAT
            if context.document_vat is not None:
                vat = context.document_vat

            expected = {
                'api_key': consts.EASY_COUNT_TOKEN,
                'customer_name': context.customer_name,
                'developer_email': context.developer_email,
                'dont_send_email': True,
                'item': items,
                'type': context.invoice_type,
                'vat': vat,
                'show_items_including_vat': True,
            }

            if context.idempotency_token is not None:
                expected['transaction_id'] = context.idempotency_token

            if context.is_payment:
                expected['payment'] = [context.payment.to_json()]
                expected['price_total'] = context.price_total

            if context.user_uuid is not None:
                expected['ua_uuid'] = context.user_uuid

            if context.parent is not None:
                expected['parent'] = context.parent

            mock_helpers.assert_dict_contains(request.json, expected)

        return {
            'pdf_link': consts.EASY_COUNT_LINK,
            'pdf_link_copy': 'https://url_copy.pdf',
            'doc_number': consts.EASY_COUNT_DOC_NUMBER,
            'doc_uuid': consts.EASY_COUNT_DOC_UUID,
            'sent_mails': [],
            'success': True,
        }

    context = Context()
    return context


@pytest.fixture(name='cardstorage')
def mock_cardstorage(mockserver):
    class Context:
        def __init__(self):
            self.payment_method_id = None
            self.yandex_uid = None

            self.check_request_flag = False

            self.pan = None
            self.system = None

        def set_pan(self, pan):
            self.pan = pan

        def set_system(self, system):
            self.system = system

        def check_request(self, *, payment_method_id: str, yandex_uid: str):
            self.payment_method_id = payment_method_id
            self.yandex_uid = yandex_uid

            self.check_request_flag = True

        def times_card_called(self):
            return _mock_card_info.times_called

        def flush(self):
            _mock_card_info.flush()

    @mockserver.json_handler('/cardstorage/v1/card')
    def _mock_card_info(request):
        if context.check_request_flag:
            assert request.json == {
                'card_id': context.payment_method_id,
                'yandex_uid': context.yandex_uid,
                'service_type': 'card',
            }

        pan = f'400000****{consts.DEFAULT_LAST_4_DIGITS}'
        if context.pan is not None:
            pan = context.pan

        system = 'VISA'
        if context.system is not None:
            system = context.system

        return {
            'card_id': consts.DEFAULT_PAYMENT_METHOD_ID,
            'billing_card_id': 'xc0f55c4b0a350c74502f4e92',
            'permanent_card_id': 'card-xc0f55c4b0a350c74502f4e92',
            'persistent_id': 'd327c7b6c019401f9b7eeda9171757a6',
            'currency': 'RUB',
            'expiration_month': 5,
            'expiration_year': 2022,
            'number': pan,
            'bin': '400000',
            'owner': '4052275114',
            'possible_moneyless': False,
            'region_id': '225',
            'regions_checked': ['225'],
            'service_labels': [
                'taxi:persistent_id:d327c7b6c019401f9b7eeda9171757a6',
            ],
            'aliases': ['card-xc0f55c4b0a350c74502f4e92'],
            'system': system,
            'valid': True,
            'bound': True,
            'unverified': False,
            'busy': False,
            'busy_with': [],
            'from_db': True,
            'ebin_tags': [],
        }

    context = Context()
    return context


@pytest.fixture(name='grocery_orders')
def mock_grocery_orders(grocery_orders_lib):
    grocery_orders_lib.add_order(
        order_id=consts.ORDER_ID, courier_info=consts.DELIVERY_SERVICE_COURIER,
    )
    return grocery_orders_lib
