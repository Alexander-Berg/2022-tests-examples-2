import decimal
from typing import Optional

import pytest

from test_iiko_integration import stubs


@pytest.mark.translations(**stubs.ORDERHISTORY_TRANSLATIONS)
@pytest.mark.config(
    **stubs.RESTAURANT_INFO_CONFIGS,
    CURRENCY_FORMATTING_RULES=stubs.CURRENCY_FORMATTING_RULES,
)
@pytest.mark.parametrize(
    ('discount', 'complement_amount', 'not_receipts'),
    (
        pytest.param(decimal.Decimal(0), None, False, id='Perfect request'),
        pytest.param(
            decimal.Decimal('10.53'),
            None,
            False,
            id='Perfect request with discount',
        ),
        pytest.param(
            decimal.Decimal(0),
            decimal.Decimal('99'),
            False,
            id='Perfect request with complement payment method',
        ),
        pytest.param(
            decimal.Decimal(0),
            None,
            True,
            id='Perfect request, not receipts for order',
        ),
    ),
)
@pytest.mark.parametrize('language', ('ru', 'en'))
async def test_normal_work(
        mockserver,
        web_app_client,
        mock_cardstorage,
        load_json,
        pgsql,
        not_receipts: bool,
        discount: decimal.Decimal,
        complement_amount: Optional[decimal.Decimal],
        language: str,
):
    @mock_cardstorage('/v1/card')
    def _cardstorage(request):
        return load_json('cardstorage_response.json')

    if not_receipts:
        with pgsql['iiko_integration'].cursor() as cursor:
            cursor.execute('DELETE FROM iiko_integration.receipts')

    _update_db(discount, complement_amount, pgsql)

    headers = {'X-Yandex-UID': 'user1', 'X-Request-Language': language}
    response = await web_app_client.get(
        f'iiko-integration/v1/orderhistory/order?order_id=01', headers=headers,
    )
    assert response.status == 200
    content = await response.json()
    order = content['order']
    _check_order_info(
        order, language, discount, complement_amount, not_receipts,
    )
    _check_translations(order, language)
    _check_address(order, language)
    _check_phone(order)


def _update_db(
        discount: decimal.Decimal,
        complement_amount: Optional[decimal.Decimal],
        pgsql,
):
    with pgsql['iiko_integration'].cursor() as cursor:
        cursor.execute(
            f'UPDATE iiko_integration.orders SET discount = {discount};',
        )
        if complement_amount:
            cursor.execute(
                f'UPDATE iiko_integration.orders SET'
                f' complement_amount = {complement_amount}, '
                f'complement_payment_method_id = \'123456789abcdef\', '
                f'complement_payment_method_type = \'personal_wallet\';',
            )


def _check_order_info(
        order: dict,
        language: str,
        discount: decimal.Decimal,
        complement_amount: Optional[decimal.Decimal],
        not_receipts: bool,
):
    calculation = order['calculation']
    addends_cost_0 = _format_sum(decimal.Decimal(50), language)
    addends_cost_1 = _format_sum(decimal.Decimal(200), language)
    assert calculation['addends'] == [
        {'cost_per_unit': addends_cost_0, 'count': '2', 'name': 'product01'},
        {'cost_per_unit': addends_cost_1, 'count': '0.5', 'name': 'product02'},
    ]
    order_cost = decimal.Decimal(100)
    formated_order_cost = _format_sum(order_cost, language)
    if discount > 0:
        total_price = order_cost + discount
        formatted_total_price = _format_sum(total_price, language)
        assert calculation['total_price_with_discount'] == formated_order_cost
        assert calculation['total_price'] == formatted_total_price
    else:
        assert 'total_price_with_discount' not in calculation
        assert calculation['total_price'] == formated_order_cost

    payment = order['payment']
    assert payment['currency_code'] == 'RUB'
    if complement_amount:
        paid_with_money = order_cost - complement_amount
        formatted_paid_with_money = _format_sum(paid_with_money, language)
        assert payment['final_cost'] == formatted_paid_with_money
        assert payment['paid_by_points'] == str(complement_amount)
    else:
        assert payment['final_cost'] == formated_order_cost
        assert 'paid_by_points' not in payment
    if complement_amount:
        assert 'cashback' not in payment
    else:
        assert payment['cashback'] == '5'
    assert payment['payment_method'] == {
        'title': 'VISA ****8643',
        'type': 'card',
        'system': 'VISA',
    }

    assert order['created_at'] == '2020-06-11T12:05:00+03:00'
    assert order['order_id'] == '01'
    assert order['status'] == 'paid'
    assert order['service'] == 'qr_pay'

    if not_receipts:
        assert order['receipts'] == []
        return

    if language == 'ru':
        payment_title = 'Чек за оплату'
        refund_title = 'Чек за возврат'
    else:
        payment_title = 'Payment receipt'
        refund_title = 'Refund receipt'
    payment_cost = _format_sum(decimal.Decimal(150.5), language)
    refund_cost = _format_sum(decimal.Decimal(25.25), language)
    assert order['receipts'] == [
        {
            'receipt_url': 'https://taxi-iiko-integration.s3.yandex.net/d00',
            'type': 'payment',
            'title': payment_title,
            'sum': payment_cost,
        },
        {
            'receipt_url': 'https://taxi-iiko-integration.s3.yandex.net/d01',
            'type': 'refund',
            'title': refund_title,
            'sum': refund_cost,
        },
        {
            'receipt_url': 'https://taxi-iiko-integration.s3.yandex.net/d02',
            'type': 'refund',
            'title': refund_title,
            'sum': refund_cost,
        },
    ]


def _format_sum(sum_: decimal.Decimal, language: str):
    quantiz_sum = sum_.quantize(decimal.Decimal('0.01'))
    formatted_sum = f'{quantiz_sum} $SIGN$$CURRENCY$'
    if language == 'ru':
        return formatted_sum.replace('.', ',')
    return formatted_sum


def _check_translations(order, language):
    legal_entities = order['legal_entities']
    additional_properties = legal_entities['additional_properties']
    if language == 'ru':
        assert legal_entities['title'] == 'О ресторане'
        assert additional_properties[0]['title'] == 'Телефон'
        assert additional_properties[1]['title'] == 'Адрес'
        assert order['title'] == 'Ресторан 01'
    else:
        assert legal_entities['title'] == 'About'
        assert additional_properties[0]['title'] == 'Phone number'
        assert additional_properties[1]['title'] == 'Address'
        assert order['title'] == 'Restaurant 01'


def _check_address(order, language):
    address = order['address']
    adderss_le = order['legal_entities']['additional_properties'][1]['value']
    if language == 'ru':
        assert adderss_le == address == 'address_ru'
    else:
        assert adderss_le == address == 'address_en'


def _check_phone(order):
    phone_number = order['legal_entities']['additional_properties'][0]['value']
    assert phone_number == '+70000047448'


@pytest.mark.translations(**stubs.ORDERHISTORY_TRANSLATIONS)
@pytest.mark.config(
    **stubs.RESTAURANT_INFO_CONFIGS,
    CURRENCY_FORMATTING_RULES=stubs.CURRENCY_FORMATTING_RULES,
    IIKO_INTEGRATION_PAYMENT_METHODS_TANKER_KEYS={
        'personal_wallet': 'restaurant.payment_method.personal_wallet',
    },
)
@pytest.mark.parametrize(
    ('method_type', 'method_id', 'is_cardstorage_problem', 'language'),
    (
        pytest.param(None, None, False, 'en', id='No payment method'),
        pytest.param('googlepay', None, False, 'en', id='No tanker_key'),
        pytest.param(
            'personal_wallet',
            None,
            False,
            'ru',
            id='Successful non-card payment ru',
        ),
        pytest.param(
            'personal_wallet',
            None,
            False,
            'en',
            id='Successful non-card payment en',
        ),
        pytest.param('card', None, False, 'en', id='No card_id'),
        pytest.param(
            'card', 'some_card_id', True, 'en', id='Cardstorage problem',
        ),
        pytest.param(
            'card', 'some_card_id', False, 'en', id='Successful card payment',
        ),
    ),
)
async def test_payment_methods(
        web_app_client,
        mock_cardstorage,
        load_json,
        pgsql,
        method_type,
        method_id,
        is_cardstorage_problem,
        language,
):
    @mock_cardstorage('/v1/card')
    def _cardstorage(request):
        if is_cardstorage_problem:
            return {}
        return load_json('cardstorage_response.json')

    _set_payment_method_in_db(method_type, method_id, pgsql)

    headers = {'X-Yandex-UID': 'user1', 'X-Request-Language': language}
    response = await web_app_client.get(
        f'iiko-integration/v1/orderhistory/order?order_id=01', headers=headers,
    )
    assert response.status == 200
    content = await response.json()
    order = content['order']
    payment_method = order['payment'].get('payment_method')
    if any(
            (
                not method_type,
                method_type == 'googlepay',
                not method_id,
                is_cardstorage_problem,
            ),
    ):
        assert not payment_method
        return
    if method_type:
        assert payment_method['type'] == method_type
    else:
        assert payment_method['type'] is None
    if method_type == 'personal_wallet':
        title = 'Яндекс.Плюс' if language == 'ru' else 'Yandex.Plus'
        assert payment_method['title'] == title
    if method_type == 'card':
        assert payment_method['title'] == 'VISA ****8643'
        assert payment_method['system'] == 'VISA'


def _set_payment_method_in_db(method_type, method_id, pgsql):
    method_type = f'\'{method_type}\'' if method_type else 'NULL'
    method_id = f'\'{method_id}\'' if method_id else 'NULL'
    with pgsql['iiko_integration'].cursor() as cursor:
        cursor.execute(
            f'UPDATE iiko_integration.orders '
            f'SET payment_method_type = {method_type}, '
            f'payment_method_id = {method_id};',
        )


@pytest.mark.parametrize(
    ('yandex_uid', 'order_id'),
    (
        ('user1', 'wrong_order'),
        ('wrong_user', '01'),
        ('user1', 'not_confirmed'),
    ),
)
async def test_order_not_found(web_app_client, yandex_uid, order_id):
    headers = {'X-Yandex-UID': yandex_uid, 'X-Request-Language': 'ru'}
    response = await web_app_client.get(
        f'iiko-integration/v1/orderhistory/order?&order_id={order_id}',
        headers=headers,
    )
    assert response.status == 404
    content = await response.json()
    assert content['code'] == 'order_not_found'
    assert content['message'] == 'Order not found'
