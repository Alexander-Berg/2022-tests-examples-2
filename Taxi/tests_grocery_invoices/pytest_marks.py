import typing

import pytest

from tests_grocery_invoices import consts
from tests_grocery_invoices import models


def get_payment_title(
        country: models.Country, payment_type: str, receipt_type: str, locale,
):
    return f'{country.lower_name}_{receipt_type}_by_{payment_type}-{locale}'


def _get_payment_title_translations(countries: typing.List[models.Country]):
    result: typing.Dict[str, dict] = {}
    for country in countries:
        for payment_type in models.PaymentType:
            for receipt_type in models.ReceiptType:
                key = (
                    f'{country.lower_name}_payment_title_{payment_type.value}_'
                    f'{receipt_type.value}'
                )

                result[key] = {}
                for locale in ('en', 'fr'):
                    result[key][locale] = get_payment_title(
                        country,
                        payment_type.value,
                        receipt_type.value,
                        locale,
                    )

    return result


TRANSLATIONS_MARK = pytest.mark.translations(
    wms_items={
        'item-id_title': {'he': 'item-id_title'},
        'item-id-0_title': {'he': 'item-id-0_title'},
        'item-id-1_title': {'he': 'item-id-1_title'},
        'item-id-2_title': {'he': 'item-id-2_title'},
        'item-id-3_title': {'he': 'item-id-3_title'},
    },
    grocery_localizations={
        'decimal_separator': {'ru': ',', 'en': '.', 'fr': ',', 'he': '.'},
        'price_with_sign.default': {
            'ru': consts.TEMPLATE_VALUE_FIRST,
            'en': consts.TEMPLATE_VALUE_FIRST,
            'fr': consts.TEMPLATE_VALUE_FIRST,
            'he': consts.TEMPLATE_VALUE_FIRST,
        },
        'price_with_sign.gbp': {
            'ru': consts.TEMPLATE_SIGN_FIRST,
            'en': consts.TEMPLATE_SIGN_FIRST,
            'fr': consts.TEMPLATE_SIGN_FIRST,
            'he': consts.TEMPLATE_SIGN_FIRST,
        },
    },
    grocery_invoices={
        'delivery_receipt_title': {
            'ru': consts.DELIVERY_RECEIPT_RU,
            'en': consts.DELIVERY_RECEIPT_EN,
            'he': consts.DELIVERY_RECEIPT_HE,
            'fr': consts.DELIVERY_RECEIPT_FR,
        },
        'tips_receipt_title': {
            'ru': consts.TIPS_RECEIPT_RU,
            'en': consts.TIPS_RECEIPT_EN,
            'he': consts.TIPS_RECEIPT_HE,
            'fr': consts.TIPS_RECEIPT_FR,
        },
        'service_fee_receipt_title': {
            'ru': consts.SERVICE_FEE_RECEIPT_RU,
            'en': consts.SERVICE_FEE_RECEIPT_EN,
            'he': consts.SERVICE_FEE_RECEIPT_HE,
            'fr': consts.SERVICE_FEE_RECEIPT_FR,
        },
        'russia_expat_payment_item_title': {
            'ru': consts.EXPAT_PAYMENT_COUPON_RU,
        },
        'russia_expat_refund_item_title': {
            'ru': consts.EXPAT_REFUND_COUPON_RU,
        },
        **_get_payment_title_translations(
            [
                models.Country.France,
                models.Country.GreatBritain,
                models.Country.RSA,
            ],
        ),
    },
    currencies={
        'currency_sign.eur': {'ru': '€', 'en': '€', 'fr': '€', 'he': '€'},
        'currency_sign.gbp': {'ru': '£', 'en': '£', 'fr': '£', 'he': '£'},
        'currency_sign.ils': {'ru': '₪', 'en': '₪', 'fr': '₪', 'he': '₪'},
        'currency_sign.rub': {'ru': '₽', 'en': '₽', 'fr': '₽', 'he': '₽'},
        'currency_sign.zar': {'ru': 'R', 'en': 'R', 'fr': 'R', 'he': 'R'},
    },
)

FORMATTER_CONFIGS = pytest.mark.config(
    GROCERY_LOCALIZATION_GROCERY_LOCALIZATIONS_KEYSET='grocery_localizations',
    GROCERY_LOCALIZATION_CURRENCIES_KEYSET='currencies',
    GROCERY_LOCALIZATION_CURRENCY_FORMAT={
        '__default__': {'precision': 2, 'rounding': '0.01'},
        'RUB': {'precision': 2, 'rounding': '0.01'},
        'GBP': {'precision': 2, 'rounding': '0.01'},
        'ILS': {'precision': 2, 'rounding': '0.01'},
    },
)

MARK_NOW = pytest.mark.now(consts.NOW)

RECEIPT_DATA_TYPES = pytest.mark.parametrize(
    'receipt_data_type', ['order', 'tips', 'delivery'],
)

RECEIPT_TYPES = pytest.mark.parametrize(
    'receipt_type',
    [models.ReceiptType.payment.value, models.ReceiptType.refund.value],
)

DEVELOPER_EMAIL_MARK = pytest.mark.config(
    GROCERY_INVOICES_DEVELOPER_EMAIL_EASY_COUNT=consts.DEVELOPER_EMAIL,
)

GROCERY_USER_UUID_MARK = pytest.mark.config(
    GROCERY_INVOICES_GROCERY_UUID_EASY_COUNT=consts.GROCERY_USER_UUID,
)

EATS_RECEIPTS_SERVICES = pytest.mark.parametrize(
    'eats_receipts_service', [consts.EATS_RECEIPTS, consts.EATS_CORE_RECEIPTS],
)

RUSSIA_PAYMENT_TYPES = pytest.mark.parametrize(
    'payment_type',
    [
        models.PaymentType.card.value,
        models.PaymentType.applepay.value,
        models.PaymentType.corp.value,
        models.PaymentType.badge.value,
        models.PaymentType.sbp.value,
    ],
)

ISRAEL_PAYMENT_TYPES = pytest.mark.parametrize(
    'payment_type',
    [
        models.PaymentType.card.value,
        models.PaymentType.applepay.value,
        models.PaymentType.cibus.value,
    ],
)

EUROPE_PAYMENT_TYPES = pytest.mark.parametrize(
    'payment_type',
    [models.PaymentType.card.value, models.PaymentType.applepay.value],
)

CURRENCY_FORMATTING_RULES = pytest.mark.config(
    CURRENCY_FORMATTING_RULES={
        '__default__': {'__default__': 0, 'ip': 2, 'surge': 1},
        'EUR': {'__default__': 1, 'grocery': 2},
        'GBP': {'__default__': 1, 'grocery': 2},
    },
)
