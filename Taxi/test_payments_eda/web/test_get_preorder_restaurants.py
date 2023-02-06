from typing import Optional

import aiohttp
import pytest

from payments_eda import consts as service_consts
from payments_eda.utils import experiments
from payments_eda.utils import payment_types
from test_payments_eda import consts


def create_exp3_preorder_response(yandex_uid: str):
    return pytest.mark.client_experiments3(
        consumer=service_consts.EXP3_CONSUMER_WEB,
        experiment_name=experiments.QR_PAYMENT_PREORDER,
        args=[
            {'name': 'yandex_uid', 'type': 'string', 'value': yandex_uid},
            {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
            {'name': 'service', 'type': 'string', 'value': 'restaurants'},
        ],
        value={'enabled': True},
    )


# pylint: disable=C0103
pytestmark = [
    pytest.mark.translations(
        tariff={
            'currency_with_sign.default': {
                'ru': '$VALUE$ $SIGN$$CURRENCY$',
                'en': '$VALUE$ $SIGN$$CURRENCY$',
            },
            'currency.rub': {'ru': 'rub.', 'en': 'eub.'},
            'currency.usd': {'en': 'usd'},
            'currency_sign.rub': {'ru': '$R', 'en': '$R'},
            'currency_sign.usd': {'ru': '$R', 'en': '$R'},
        },
        client_messages={
            'payments_eda.preorder.user_order_mismatch.message': {
                'ru': 'User order mismatch ru message',
            },
            'payments_eda.preorder.restaurants.bad_request.message': {
                'ru': 'Restaurants bad request ru message',
            },
            'payments_eda.preorder.restaurants.bad_request.title': {
                'ru': 'Restaurants bad request ru title',
            },
            'payments_eda.preorder.restaurants.hmac_validation_failed'
            '.message': {
                'ru': 'Restaurants hmac validation failed ru message',
            },
            'payments_eda.preorder.restaurants.hmac_validation_failed.title': {
                'ru': 'Restaurants hmac validation failed ru title',
            },
            'payments_eda.preorder.restaurants.order_not_found.message': {
                'ru': 'Restaurants order not found ru message',
            },
            'payments_eda.preorder.restaurants.order_not_found.title': {
                'ru': 'Restaurants order not found ru title',
            },
            'payments_eda.preorder.restaurants.hmac_missing.message': {
                'ru': 'Restaurants hmac missing message',
            },
            'payments_eda.preorder.restaurants.hmac_missing.title': {
                'ru': 'Restaurants hmac missing title',
            },
            'payments_eda.preorder.restaurants.order_closed.message': {
                'ru': 'Order closed message',
            },
            'payments_eda.preorder.restaurants.order_closed.title': {
                'ru': 'Order closed title',
            },
            'payments_eda.preorder.restaurants.order_expired.message': {
                'ru': 'Order expired message',
            },
            'payments_eda.preorder.restaurants.order_expired.title': {
                'ru': 'Order expired title',
            },
            'payments_eda.preorder.restaurants.order_closed_by_restaurant'
            '.message': {'ru': 'Order closed by restaurant message'},
            'payments_eda.preorder.restaurants.order_closed_by_restaurant'
            '.title': {'ru': 'Order closed by restaurant title'},
            'payments_eda.preorder.restaurants.order_canceled_by_restaurant'
            '.message': {'ru': 'Order canceled by restaurant message'},
            'payments_eda.preorder.restaurants.order_canceled_by_restaurant'
            '.title': {'ru': 'Order canceled by restaurant title'},
            'payments_eda.preorder.restaurants.service_unavailable.message': {
                'ru': 'Service unavailable ru message',
            },
            'payments_eda.preorder.restaurants.service_unavailable.title': {
                'ru': 'Service unavailable ru title',
            },
            'payments_eda.preorder.restaurants.user_mismatch.message': {
                'ru': 'User mismatch ru message',
            },
            'payments_eda.preorder.restaurants.user_mismatch.title': {
                'ru': 'User mismatch ru title',
            },
        },
    ),
    create_exp3_preorder_response(consts.DEFAULT_YANDEX_UID),
    create_exp3_preorder_response('any_uid'),
    create_exp3_preorder_response('bad_uid'),
    create_exp3_preorder_response('good_uid'),
]


def strip_zeros(value: str) -> str:
    return value.strip('0').strip('.')


@pytest.mark.parametrize(
    ('discount', 'address', 'item'),
    [
        pytest.param(
            '0.00',
            None,
            {
                'item_id': 1,
                'product_id': 'product_id',
                'name': 'name',
                'quantity': '1',
                'price_per_unit': '1',
                'price_for_customer': '0',
                'discount_amount': '1',
                'discount_percent': 'discount_percent',
                'price_without_discount': '1',
                'vat_percent': '10',
                'vat_amount': '1',
            },
            id='empty_optional_fields',
        ),
        pytest.param(
            '15.00',
            'address',
            {
                'item_id': 1,
                'product_id': 'product_id',
                'parent_product_id': 'parent_product_id',
                'name': 'name',
                'quantity': '2',
                'price_per_unit': '1',
                'price_for_customer': '0',
                'discount_amount': '1',
                'discount_percent': 'discount_percent',
                'price_without_discount': '1',
                'vat_percent': '10',
                'vat_amount': '1',
            },
            id='filled_optional_fields',
        ),
    ],
)
async def test_restaurants(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        patch,
        build_pa_headers,
        mockserver,
        discount,
        address,
        item,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(req):
        assert req.query == {'id': '1', 'locale': 'ru', 'for_user': 'true'}
        return _iiko_order(discount=discount, address=address, item=item)

    @patch('payments_eda.utils.payment_types.get_payment_types_info')
    async def _mock_get_values(
            service: str, lat: float, lon: float, *args, **kwargs,
    ):
        assert service == 'restaurants'
        assert lat == 11
        assert lon == 12
        return payment_types.PaymentTypeInfo(
            available_payment_types=[], merchant_ids=[],
        )

    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=restaurants&external_ref=1&hmac=2',
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == 200
    body = await response.json()

    # check required fields
    assert body['amount'] == '0'
    assert body['amount_template'] == '0 $SIGN$$CURRENCY$'
    assert body['country_code'] == 'country_code'
    assert body['currency'] == 'RUB'
    assert body['currency_rules'] == {
        'code': 'RUB',
        'sign': '$R',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'rub.',
    }
    assert body['merchant_id_list'] == []
    assert body['payment_methods'] == []
    assert body['region_id'] == 1
    assert body['cashback'] == {'amount_template': '1'}
    assert 'cashback_points' not in body

    # check optional fields
    if discount == '0.00':
        assert 'discount_template' not in body
        assert 'original_amount_template' not in body
    else:
        assert (
            body['discount_template']
            == strip_zeros(discount) + ' $SIGN$$CURRENCY$'
        )
        assert body['original_amount_template'] == '1 $SIGN$$CURRENCY$'

    # check service info
    assert body['service_info']['name'] == 'name'
    if address:
        assert body['service_info']['address'] == address
    else:
        assert 'address' not in body['service_info']

    # check order item
    response_item = body['items'][0]
    assert response_item['amount_template'] == '0 $SIGN$$CURRENCY$'
    assert response_item['currency'] == 'RUB'
    assert response_item['id'] == 'product_id'
    assert response_item['name'] == 'name'
    if item['quantity'] != '1':
        assert response_item['price_per_unit_template'] == '1 $SIGN$$CURRENCY$'
        assert response_item['quantity'] == str(item['quantity'])
    else:
        assert 'price_per_unit' not in response_item
        assert 'quantity' not in response_item
    assert response_item['vat_percent'] == '10'
    assert (
        response_item['vat_value_template']
        == strip_zeros(item['vat_amount']) + ' $SIGN$$CURRENCY$'
    )
    if 'parent_product_id' in item:
        assert response_item['parent_id'] == item['parent_product_id']
    else:
        assert 'parent_id' not in response_item


@pytest.mark.parametrize(
    ('iiko_status', 'iiko_code', 'expected_body'),
    [
        pytest.param(
            400,
            '',
            {
                'code': 'bad_request',
                'message': 'Restaurants bad request ru message',
                'details': {'title': 'Restaurants bad request ru title'},
            },
            id='bad-request',
        ),
        pytest.param(
            404,
            '',
            {
                'code': 'order_not_found',
                'message': 'Restaurants order not found ru message',
                'details': {'title': 'Restaurants order not found ru title'},
            },
            id='order-not-found',
        ),
        pytest.param(
            400,
            'service_unavailable',
            {
                'code': 'service_unavailable',
                'message': 'Service unavailable ru message',
                'details': {'title': 'Service unavailable ru title'},
            },
            id='service-unavailable',
        ),
    ],
)
async def test_restaurants_iiko_errors(
        web_app_client,
        build_pa_headers,
        mockserver,
        iiko_status,
        iiko_code,
        expected_body,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order(req):
        return aiohttp.web.json_response(
            status=iiko_status, data={'code': iiko_code, 'message': ''},
        )

    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=restaurants&external_ref=1&hmac=2',
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == iiko_status
    body = await response.json()
    assert body == expected_body


async def test_no_preorder_experiment(web_app_client, build_pa_headers):
    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=restaurants&external_ref=1&hmac=2',
        headers=build_pa_headers(
            '1.1.1.1', 'ru-RU', yandex_uid='random_uid_outside_exp',
        ),
    )
    assert response.status == 400

    body = await response.json()
    assert body == {
        'code': 'service_unavailable',
        'message': 'Service unavailable ru message',
        'details': {'title': 'Service unavailable ru title'},
    }


@pytest.mark.parametrize(
    ('hmac', 'expected_status', 'expected_body'),
    [
        pytest.param(None, 200, None, id='hmac-missing'),
        pytest.param('some-hmac', 200, None, id='hmac-provided'),
    ],
)
async def test_restaurants_hmac_validation_failure(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        patch,
        build_pa_headers,
        mockserver,
        hmac,
        expected_status,
        expected_body,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(req):
        return _iiko_order()

    @patch('payments_eda.utils.payment_types.get_payment_types_info')
    async def _mock_get_values(*args, **kwargs):
        return payment_types.PaymentTypeInfo(
            available_payment_types=[], merchant_ids=[],
        )

    hmac_part = '&hmac=' + hmac if hmac else ''
    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=restaurants&external_ref=1'
        + hmac_part,
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == expected_status
    if expected_body is not None:
        body = await response.json()
        assert body == expected_body


DEFAULT_IIKO_ORDER_ITEM = {
    'item_id': 1,
    'product_id': 'product_id',
    'name': 'name',
    'quantity': '1',
    'price_per_unit': '1',
    'price_for_customer': '20',
    'discount_amount': '1',
    'discount_percent': 'discount_percent',
    'price_without_discount': '1',
    'vat_percent': '10',
    'vat_amount': '1',
}


def _iiko_order(
        discount='0.00',
        amount_without_discount='1',
        address=None,
        item=None,
        restaurant_status='PENDING',
        invoice_status='INIT',
        user_id=None,
        yandex_uid=None,
        price_for_customer='20',
):
    default_item = {
        **DEFAULT_IIKO_ORDER_ITEM,
        'price_for_customer': price_for_customer,
    }
    return {
        'order_id': 'order_id',
        'restaurant_order_id': 'restaurant_order_id',
        'amount': '1',
        'currency': 'RUB',
        'cashback': {'rate': '2', 'value': '1'},
        'discount': discount,
        'amount_without_discount': amount_without_discount,
        'restaurant_info': {
            'address': address,
            'name': 'name',
            'region_id': 1,
            'country_code': 'country_code',
            'geopoint': {'lat': 11, 'lon': 12},
            'eda_client_id': 42,
        },
        'items': [item if item else default_item],
        'status': {
            'restaurant_status': restaurant_status,
            'invoice_status': invoice_status,
            'updated_at': 'status_updated_at',
        },
        'user_id': user_id,
        'yandex_uid': yandex_uid,
    }


CLOSED_ERROR = {
    'code': 'order_closed',
    'message': 'Order closed message',
    'details': {'title': 'Order closed title'},
}


@pytest.mark.parametrize(
    (
        'restaurant_status',
        'invoice_status',
        'expected_status',
        'expected_body',
    ),
    [
        pytest.param('PENDING', 'INIT', 200, None, id='ok-pending'),
        pytest.param('PENDING', 'HOLDING', 200, None, id='ok-holding'),
        pytest.param(
            'WAITING_FOR_CONFIRMATION',
            'HELD',
            404,
            CLOSED_ERROR,
            id='error-held-and-waiting-for-confirmation',
        ),
        pytest.param(
            'PAYMENT_CONFIRMED',
            'HELD',
            404,
            CLOSED_ERROR,
            id='error-held-and-confirmed',
        ),
        pytest.param('PENDING', 'HOLD_FAILED', 200, None, id='ok-hold-failed'),
        pytest.param(
            'CANCELED',
            'INIT',
            404,
            {
                'code': 'order_canceled_by_restaurant',
                'message': 'Order canceled by restaurant message',
                'details': {'title': 'Order canceled by restaurant title'},
            },
            id='error-canceled',
        ),
        pytest.param(
            'CLOSED',
            'INIT',
            404,
            {
                'code': 'order_closed_by_restaurant',
                'message': 'Order closed by restaurant message',
                'details': {'title': 'Order closed by restaurant title'},
            },
            id='error-closed',
        ),
        pytest.param(
            'PAYMENT_CONFIRMED',
            'CLEARING',
            404,
            CLOSED_ERROR,
            id='error-clearing',
        ),
        pytest.param(
            'PAYMENT_CONFIRMED',
            'CLEARED',
            404,
            CLOSED_ERROR,
            id='error-cleared',
        ),
        pytest.param(
            'EXPIRED',
            'CLEARED',
            404,
            {
                'code': 'order_expired',
                'message': 'Order expired message',
                'details': {'title': 'Order expired title'},
            },
            id='error-expired',
        ),
    ],
)
async def test_restaurants_status_check(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        patch,
        build_pa_headers,
        mockserver,
        restaurant_status,
        invoice_status,
        expected_status,
        expected_body,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(req):
        return _iiko_order(
            restaurant_status=restaurant_status,
            invoice_status=invoice_status,
            yandex_uid='default_yandex_uid',
            user_id='default_user_id',
        )

    @patch('payments_eda.utils.payment_types.get_payment_types_info')
    async def _mock_get_values(*args, **kwargs):
        return payment_types.PaymentTypeInfo(
            available_payment_types=[], merchant_ids=[],
        )

    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=restaurants&external_ref=1&hmac=2',
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == expected_status
    if expected_body is not None:
        body = await response.json()
        assert body == expected_body


@pytest.mark.parametrize(
    ('request_user_uid', 'request_user_id', 'expected_status'),
    (
        pytest.param('good_uid', 'good_id', 200, id='ok_for_uid_match'),
        pytest.param('bad_uid', 'good_id', 409, id='err_for_uid_mismatch'),
        pytest.param('good_uid', 'bad_id', 409, id='err_for_user_id_mismatch'),
    ),
)
async def test_auth_check(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        patch,
        build_pa_headers,
        mockserver,
        request_user_uid,
        request_user_id,
        expected_status,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(req):
        return _iiko_order(
            yandex_uid='good_uid', user_id='good_id', invoice_status='HOLDING',
        )

    @patch('payments_eda.utils.payment_types.get_payment_types_info')
    async def _mock_get_values(*args, **kwargs):
        return payment_types.PaymentTypeInfo(
            available_payment_types=[], merchant_ids=[],
        )

    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=restaurants&external_ref=1&hmac=2',
        headers=build_pa_headers(
            '1.1.1.1',
            'ru-RU',
            yandex_uid=request_user_uid,
            ya_taxi_user_id=request_user_id,
        ),
    )
    assert response.status == expected_status


MARK_PERSONAL_WALLET_EXP = dict(
    consumer=service_consts.EXP3_CONSUMER_WEB,
    experiment_name=experiments.PERSONAL_WALLET_ENABLED_EXP,
    args=[
        {
            'name': 'yandex_uid',
            'type': 'string',
            'value': consts.DEFAULT_YANDEX_UID,
        },
        {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
        {'name': 'service', 'type': 'string', 'value': 'restaurants'},
    ],
    value={'enabled': True},
)


@pytest.mark.config(
    PERSONAL_WALLET_FIRM_BY_SERVICE={'restaurants': {'RUB': '32'}},
)
@pytest.mark.client_experiments3(**MARK_PERSONAL_WALLET_EXP)
@pytest.mark.client_experiments3(
    consumer=service_consts.EXP3_CONSUMER_WEB,
    experiment_name=experiments.SUPERAPP_COMPLEMENT_PAYMENT,
    args=[
        {
            'name': 'yandex_uid',
            'type': 'string',
            'value': consts.DEFAULT_YANDEX_UID,
        },
        {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
        {'name': 'service', 'type': 'string', 'value': 'restaurants'},
    ],
    value={'enabled': True},
)
@pytest.mark.client_experiments3(
    consumer=service_consts.EXP3_CONSUMER_WEB,
    experiment_name=experiments.CASHBACK_POINTS_EXPERIMENT,
    args=[
        {
            'name': 'yandex_uid',
            'type': 'string',
            'value': consts.DEFAULT_YANDEX_UID,
        },
        {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
        {'name': 'service', 'type': 'string', 'value': 'restaurants'},
    ],
    value={'enabled': True},
)
@pytest.mark.parametrize(
    (
        'item_price',
        'complements',
        'cashback_exist',
        'original_amount',
        'amount',
        'discount',
    ),
    [
        pytest.param(
            '2000', [], True, None, '2000', False, id='without complements',
        ),
        pytest.param(
            '2000',
            consts.DEFAULT_COMPLEMENTS,
            False,
            '2000',
            '1500',
            False,
            id='with complements 0',
        ),
        pytest.param(
            '100',
            consts.DEFAULT_COMPLEMENTS,
            False,
            '100',
            '1',
            False,
            id='with complements 1',
        ),
        pytest.param(
            '2000',
            [],
            True,
            '2200',
            '2000',
            True,
            id='without complements, with discount',
        ),
        pytest.param(
            '2000',
            consts.DEFAULT_COMPLEMENTS,
            False,
            '2000',
            '1500',
            True,
            id='with complements, with discount',
        ),
    ],
)
async def test_restaurants_complement(
        web_app_client,
        mock_cardstorage,
        load_json,
        patch,
        build_pa_headers,
        mockserver,
        item_price,
        complements,
        cashback_exist,
        original_amount,
        amount,
        discount,
):
    @mockserver.json_handler('/personal_wallet/v1/available-accounts')
    def _available_accounts_mock(request):
        return load_json('available_accounts_with_complements.json')

    @mock_cardstorage('/v1/payment_methods')
    async def _mock_payment_method(*args, **kwargs):
        return load_json('cardstorage_payment_methods.json')

    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(request):
        if discount:
            return _iiko_order(
                price_for_customer=item_price,
                amount_without_discount=str(int(item_price) * 1.1),
                discount='10',
            )
        return _iiko_order(price_for_customer=item_price)

    @patch('payments_eda.utils.payment_types.get_payment_types_info')
    async def _mock_get_values(*args, **kwargs):
        return payment_types.PaymentTypeInfo(
            available_payment_types=['card', 'personal_wallet'],
            merchant_ids=[],
        )

    request_json = {
        'payment_method': 'card',
        'payment_method_id': 'card-x5a4adedaf78dba6f9c56fee4',
        'complements': complements,
    }
    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=restaurants&external_ref=1&hmac=2',
        json=request_json,
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == 200
    body = await response.json()

    assert body['amount'] == amount
    assert ('cashback' in body) == cashback_exist
    assert body['selected_payment_method'] == request_json
    if original_amount:
        original_amount = f'{original_amount} $SIGN$$CURRENCY$'
    assert body.get('original_amount_template') == original_amount
    assert body['cashback_points'] == {
        'get_amount': '1',
        'spend_amount': _get_spend_amount(item_price),  # one item in order
    }


def _get_spend_amount(price_with_discount: str):
    # for wallet_id/1234567890 in available_accounts_with_complements.json
    personal_wallet_balance = 500

    max_spend_amount = int(price_with_discount) - 1
    spend_amount = min(max_spend_amount, personal_wallet_balance)
    return str(spend_amount)


@pytest.mark.config(
    PERSONAL_WALLET_FIRM_BY_SERVICE={'restaurants': {'RUB': '32'}},
    PAYMENTS_EDA_CORP_ENABLED=True,
)
@pytest.mark.client_experiments3(**MARK_PERSONAL_WALLET_EXP)
@pytest.mark.parametrize('payment_type', ['corp', 'card', None, {}])
async def test_selected_payment_method(
        web_app_client,
        mock_cardstorage,
        mock_taxi_corp_integration,
        load_json,
        patch,
        build_pa_headers,
        mockserver,
        payment_type: Optional[str],
):
    @mockserver.json_handler('/personal_wallet/v1/available-accounts')
    def _available_accounts_mock(request):
        return load_json('available_accounts_with_complements.json')

    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(request):
        return _iiko_order()

    @patch('payments_eda.utils.payment_types.get_payment_types_info')
    async def _mock_get_values(*args, **kwargs):
        return payment_types.PaymentTypeInfo(
            available_payment_types=['card', 'personal_wallet', 'corp'],
            merchant_ids=[],
        )

    if payment_type == 'card':

        @mock_cardstorage('/v1/payment_methods')
        async def _mock_payment_method(*args, **kwargs):
            return load_json('cardstorage_payment_methods.json')

    elif payment_type == 'corp':

        @mock_taxi_corp_integration('/v1/payment-methods/eats')
        async def _mock_corp_int_api(*args, **kwargs):
            body = load_json('corp_int_api_list_payment_methods.json')
            return mockserver.make_response(
                status=200, json=body, headers={'X-YaRequestId': '123'},
            )

    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=restaurants&external_ref=1&hmac=2',
        json={},
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == 200
    body = await response.json()

    if payment_type:
        selected_method = body['selected_payment_method']
        assert selected_method['payment_method'] == payment_type
    else:
        assert 'selected_payment_method' not in body
