import datetime

import pytest

from taxi.core import db
from taxi.internal import fiscal_receipt


@pytest.mark.parametrize(
    ('url', 'result'),
    [
        ('https://taxi.yandex.ru/', 'https://taxi.yandex.ru/'),
        (
            'https://clck.ru/https://trust-test.yandex.ru/',
            'https://clck.ru/https://trust-test.yandex.ru/',
        ),
        (
            'https://trust-test.yandex.ru/param',
            'http://tc-unstable.mobile.yandex.net/tmongo1f/param',
        ),
        (
            'https://trust-test.yandex.ru/https://trust-test.yandex.ru/',
            'http://tc-unstable.mobile.yandex.net/tmongo1f/https://trust-test.yandex.ru/',
        ),
    ],
)
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_patch_fiscal_receipt_url(url, result):
    assert fiscal_receipt._patch_fiscal_receipt_url(url) == result


@pytest.mark.parametrize(
    'order_id,expexted_pushes_sent,' 'expected_payment_events',
    [
        ('order-no-receipt', [], None),
        (
            'order-no-receipt-pending',
            [],
            [
                {
                    'type': 'receipt_sent',
                    'data': {
                        'push_id': '0ddb553e96e7f9002bee101b3f22d11a636bff7a',
                        'url': 'http://trust/fiscal1',
                    },
                },
            ],
        ),
        (
            'order-receipt-refund',
            [
                {
                    'deeplink': (
                        'yandextaxi://receipt?url=http%3A//trust/refund'
                    ),
                    'msg': 'Refund 100rub',
                    'notification_group': 'order-receipt-refund',
                },
            ],
            [
                {
                    'data': {
                        'push_id': '52ab18de1e9e3a6dcf48eb190287be71438986de',
                        'url': 'http://trust/fiscal1',
                    },
                    'type': 'receipt_sent',
                },
                {
                    'c': datetime.datetime(2017, 6, 28, 8, 0),
                    'data': {
                        'push_id': '19a8699994782ba6edba49a50b3942510619d7a7',
                        'trust_payment_id': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
                        'trust_refund_id': 'RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR',
                        'url': 'http://trust/refund',
                    },
                    'status': 'success',
                    'type': 'receipt_sent',
                },
            ],
        ),
        (
            'order-with-reversal',
            [
                {
                    'deeplink': (
                        'yandextaxi://receipt?url=http%3A//trust/reversal/'
                    ),
                    'msg': 'Refund 16rub',
                    'notification_group': 'order-with-reversal',
                },
            ],
            [
                {
                    'c': datetime.datetime(2017, 6, 28, 8, 0),
                    'data': {
                        'push_id': 'c84ae74087036313615df6b3c32d9e5c90baeac4',
                        'trust_payment_id': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
                        'trust_reversal_id': 'rererererererererererere',
                        'url': 'http://trust/reversal/',
                    },
                    'status': 'success',
                    'type': 'receipt_sent',
                },
            ],
        ),
        (
            'order-with-transactions-reversal',
            [
                {
                    'deeplink': (
                        'yandextaxi://receipt?url=http%3A//trust/reversal/'
                    ),
                    'msg': 'Refund 16rub',
                    'notification_group': 'order-with-transactions-reversal',
                },
            ],
            [
                {
                    'c': datetime.datetime(2017, 6, 28, 8, 0),
                    'data': {
                        'push_id': 'bd96917e1134d8238d308c266a770c7a3d533b3b',
                        'trust_payment_id': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
                        'trust_reversal_id': 'rererererererererererere',
                        'url': 'http://trust/reversal/',
                    },
                    'status': 'success',
                    'type': 'receipt_sent',
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    BILLING_FISCAL_RECEIPT_ENABLED=True,
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
    DEEPLINK_PREFIX={'vezet': 'vezet'},
    APPLICATION_MAP_BRAND={'vezet/ios': 'vezet'},
)
@pytest.mark.translations(
    [
        (
            'notify',
            'fiscal_receipt.push.purchase',
            'ru',
            'Purchase %(cost_with_currency)s',
        ),
        (
            'notify',
            'fiscal_receipt.push.refund',
            'ru',
            'Refund %(cost_with_currency)s',
        ),
        (
            'tariff',
            'currency_with_sign.default',
            'ru',
            '$VALUE$$SIGN$$CURRENCY$',
        ),
        ('tariff', 'currency.rub', 'ru', 'rub'),
    ],
)
@pytest.mark.now('2017-06-28 11:00:00+03')
@pytest.mark.filldb(orders='fiscal_receipt')
@pytest.inline_callbacks
def test_notify_send_fiscal_receipt(
        patch, order_id, expected_payment_events, expexted_pushes_sent,
):
    pushes_sent = []

    @patch('taxi.internal.fiscal_receipt_push.send_push_event')
    def send_push_event(data, user_id, push_id, text, log_extra=None):
        pushes_sent.append(data)

    for _ in (1, 2):
        order_doc = yield db.orders.find_one(order_id)
        assert order_doc is not None
        yield fiscal_receipt.notify_send_fiscal_receipt(
            order_doc, log_extra=None,
        )
        assert pushes_sent == expexted_pushes_sent
        order_doc = yield db.orders.find_one(order_id)
        assert order_doc.get('payment_events') == expected_payment_events
