import enum
import json

import pytest

WALLET_ID = 'w/28c44321-16a3-5221-a0b1-3f823998bdff'


class DiscountType(enum.Enum):
    ITEM_DISCOUNT = 'item_discount'
    PAYMENT_METHOD_DISCOUNT = 'payment_method_discount'
    BUNDLE_DISCOUNT_V2 = 'bundle_discount_v2'


class DiscountValueType(enum.Enum):
    ABSOLUTE = 1
    RELATIVE = 2


class PaymentType(enum.Enum):
    MONEY_DISCOUNT = 1
    CASHBACK_DISCOUNT = 2


@pytest.fixture(name='grocery_p13n', autouse=True)
def mock_grocery_p13n(mockserver):
    modifiers = []
    cashback_info = {}

    @mockserver.json_handler('/grocery-p13n/internal/v1/p13n/v1/cashback-info')
    def mock_cashback_info(request):
        if context.on_cashback_request:
            assert context.on_cashback_request(request.headers, request.json)

        if context.is_cashback_disabled or not cashback_info:
            return mockserver.make_response(
                json.dumps({'code': 'DISABLED_BY_EXPERIMENT', 'message': ''}),
                404,
            )
        return {
            'wallet_id': WALLET_ID,
            'complement_payment_types': ['card', 'applepay'],
            **cashback_info,
        }

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def discount_modifiers(request):
        if context.on_modifiers_request:
            print(request.json)
            assert context.on_modifiers_request(request.headers, request.json)

        return {'modifiers': modifiers}

    @mockserver.json_handler('grocery-p13n/internal/v1/p13n/v1/discounts-info')
    def discounts_info(request):
        if context.on_discounts_info_request:
            assert context.on_discounts_info_request(
                request.headers, request.json,
            )

        return {}

    class Context:
        def __init__(self):
            self.is_cashback_disabled = False
            self.on_modifiers_request = None
            self.on_cashback_request = None
            self.on_discounts_info_request = None

        def set_modifiers_request_check(self, *, on_modifiers_request):
            self.on_modifiers_request = on_modifiers_request

        def set_cashback_request_check(self, *, on_cashback_request):
            self.on_cashback_request = on_cashback_request

        def set_discounts_request_check(self, *, on_discounts_info_request):
            self.on_discounts_info_request = on_discounts_info_request

        def set_cashback_info_response(
                self, payment_available, balance, availability_type='buy_plus',
        ):
            cashback_info['balance'] = str(balance)
            if not payment_available:
                cashback_info['unavailability'] = {
                    'charge_disabled_code': availability_type,
                }

        def remove_cashback_info(self):
            context.is_cashback_disabled = True

        def add_modifier(
                self,
                *,
                product_id,
                value,
                payment_type: PaymentType = PaymentType.MONEY_DISCOUNT,
                value_type: DiscountValueType = DiscountValueType.ABSOLUTE,
                discount_type: DiscountType = DiscountType.ITEM_DISCOUNT,
                meta=None,
        ):
            value = str(value)
            if meta is None:
                meta = {}
            modifiers.append(
                {
                    'product_id': product_id,
                    'rule': _get_payment_rule(value, value_type, payment_type),
                    'type': str(discount_type.value),
                    'meta': meta,
                },
            )

        def add_bundle_v2_modifier(
                self,
                *,
                value,
                bundle_id='bundle-id',
                payment_type: PaymentType = PaymentType.MONEY_DISCOUNT,
                value_type: DiscountValueType = DiscountValueType.RELATIVE,
                meta=None,
        ):
            value = str(value)
            if meta is None:
                meta = {}
            modifiers.append(
                {
                    'bundle_id': bundle_id,
                    'rule': _get_payment_rule(value, value_type, payment_type),
                    'type': str(DiscountType.BUNDLE_DISCOUNT_V2.value),
                    'meta': meta,
                },
            )

        def add_modifier_product_payment(
                self, *, product_id, payment_per_product, quantity, meta=None,
        ):
            if meta is None:
                meta = {}
            modifiers.append(
                {
                    'product_id': product_id,
                    'rule': {
                        'quantity': quantity,
                        'payment_per_product': {
                            'discount_percent': payment_per_product,
                        },
                    },
                    'type': 'item_discount',
                    'meta': meta,
                },
            )

        def add_cart_modifier(
                self, *, steps, meta=None, payment_rule='discount_value',
        ):
            if meta is None:
                meta = {}
            modifiers.append(
                {
                    'steps': [
                        {'threshold': threshold, 'rule': {payment_rule: value}}
                        for threshold, value in steps
                    ],
                    'min_cart_price': '0',
                    'type': 'cart_discount',
                    'meta': meta,
                },
            )

        def add_cart_modifier_with_rules(self, *, steps, meta=None):
            if meta is None:
                meta = {}
            modifiers.append(
                {
                    'steps': [
                        {'threshold': threshold, 'rule': {payment_rule: value}}
                        for threshold, value, payment_rule in steps
                    ],
                    'min_cart_price': '0',
                    'type': 'cart_discount',
                    'meta': meta,
                },
            )

        def add_modifier_percent_discount(
                self, *, product_id, discount_percentage, meta=None,
        ):
            if meta is None:
                meta = {}
            self.add_modifier(
                product_id=product_id,
                value=str(discount_percentage),
                value_type=DiscountValueType.RELATIVE,
                meta=meta,
            )

        def add_modifier_absolute_discount(
                self, *, product_id, discount_value, meta=None,
        ):
            if meta is None:
                meta = {}
            self.add_modifier(
                product_id=product_id,
                value=str(discount_value),
                value_type=DiscountValueType.ABSOLUTE,
                meta=meta,
            )

        def clear_modifiers(self):
            modifiers.clear()

        @property
        def discount_modifiers_times_called(self):
            return discount_modifiers.times_called

        @property
        def cashback_info_times_called(self):
            return mock_cashback_info.times_called

        @property
        def discounts_info_times_called(self):
            return discounts_info.times_called

    context = Context()
    return context


def _get_payment_rule(
        value,
        discount_value_type: DiscountValueType,
        payment_type: PaymentType,
):
    if (
            discount_value_type == DiscountValueType.ABSOLUTE
            and payment_type == PaymentType.MONEY_DISCOUNT
    ):
        return {'discount_value': value}
    if (
            discount_value_type == DiscountValueType.RELATIVE
            and payment_type == PaymentType.MONEY_DISCOUNT
    ):
        return {'discount_percent': value}
    if (
            discount_value_type == DiscountValueType.ABSOLUTE
            and payment_type == PaymentType.CASHBACK_DISCOUNT
    ):
        return {'gain_value': value}
    if (
            discount_value_type == DiscountValueType.RELATIVE
            and payment_type == PaymentType.CASHBACK_DISCOUNT
    ):
        return {'gain_percent': value}
    return None
