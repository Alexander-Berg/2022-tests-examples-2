import pytest

from payments_eda import consts as service_consts
from payments_eda.utils import experiments
from payments_eda.utils import payment_types
from test_payments_eda import consts

# pylint: disable=C0103
pytestmark = [
    pytest.mark.translations(
        client_messages={
            'payments_eda.orders.error.user_order_mismatch.message': {
                'ru': 'user order mismatch message',
            },
            'payments_eda.orders.error.user_order_mismatch.title': {
                'ru': 'user order mismatch title',
            },
            'payments_eda.orders.error.not_found.message': {
                'ru': 'not found message',
            },
            'payments_eda.orders.error.not_found.title': {
                'ru': 'not found title',
            },
            'payments_eda.orders.error.invalid_payment_method.message': {
                'ru': 'invalid payment method',
            },
            'payments_eda.orders.error.invalid_payment_method.title': {
                'ru': 'invalid payment method title',
            },
            'payments_eda.orders.error.restaurants.transaction_conflict'
            '.message': {'ru': 'transaction conflict'},
            'payments_eda.orders.error.restaurants.transaction_conflict'
            '.title': {'ru': 'transaction conflict title'},
            'payments_eda.orders.error.restaurants.missing_hmac.message': {
                'ru': 'missing hmac message',
            },
            'payments_eda.orders.error.restaurants.missing_hmac.title': {
                'ru': 'missing hmac title',
            },
            'payments_eda.orders.error.restaurants.order_canceled.message': {
                'ru': 'order canceled message',
            },
            'payments_eda.orders.error.restaurants.order_canceled.title': {
                'ru': 'order canceled title',
            },
            'payments_eda.orders.error.restaurants.order_closed.message': {
                'ru': 'order closed message',
            },
            'payments_eda.orders.error.restaurants.order_closed.title': {
                'ru': 'order closed title',
            },
            'payments_eda.orders.error.restaurants.order_expired.title': {
                'ru': 'order expired title',
            },
            'payments_eda.orders.error.restaurants.order_expired.message': {
                'ru': 'order expired message',
            },
            'payments_eda.orders.error.restaurants.user_mismatch.message': {
                'ru': 'user mismatch message',
            },
            'payments_eda.orders.error.restaurants.user_mismatch.title': {
                'ru': 'user mismatch title',
            },
            'payments_eda.orders.error.restaurants.bad_request.message': {
                'ru': 'bad request message',
            },
            'payments_eda.orders.error.restaurants.bad_request.title': {
                'ru': 'bad request title',
            },
            'payments_eda.orders.error.restaurants.hmac_validation_failed'
            '.message': {'ru': 'hmac validation failed message'},
            'payments_eda.orders.error.restaurants.hmac_validation_failed'
            '.title': {'ru': 'hmac validation_failed title'},
            'payments_eda.orders.error.restaurants.order_not_found.message': {
                'ru': 'order not found message',
            },
            'payments_eda.orders.error.restaurants.order_not_found.title': {
                'ru': 'order not found title',
            },
            'payments_eda.orders.error.restaurants.status_mismatch.message': {
                'ru': 'status mismatch message',
            },
            'payments_eda.orders.error.restaurants.status_mismatch.title': {
                'ru': 'status mismatch title',
            },
            'payments_eda.orders.error.restaurants.eda_validation_failed'
            '.message': {'ru': 'eda validation failed message'},
            'payments_eda.orders.error.restaurants.eda_validation_failed'
            '.title': {'ru': 'eda validation failed title'},
            'payments_eda.orders.error.restaurants.service_unavailable'
            '.message': {'ru': 'sservice unavailable message'},
            'payments_eda.orders.error.restaurants.service_unavailable'
            '.title': {'ru': 'service unavailable title'},
            'payments_eda.orders.error.restaurants.invalid_email.message': {
                'ru': 'invalid email message',
            },
        },
    ),
]


def _iiko_order(
        restaurant_status='PENDING',
        invoice_status='INIT',
        yandex_uid=None,
        user_id=None,
        invoice_id=None,
):
    return {
        'order_id': 'order_id',
        'restaurant_order_id': 'restaurant_order_id',
        'amount': '49',
        'currency': 'RUB',
        'cashback': {'rate': '2', 'value': '1'},
        'discount': '1.00',
        'amount_without_discount': '50',
        'restaurant_info': {
            'name': 'name',
            'region_id': 1,
            'country_code': 'country_code',
            'geopoint': {'lat': 11, 'lon': 12},
            'eda_client_id': 42,
        },
        'items': [
            {
                'item_id': 1,
                'product_id': 'product_id_1',
                'parent_product_id': 'parent1_product_id_1',
                'name': 'name_1',
                'quantity': '2',
                'price_per_unit': '10',
                'price_for_customer': '19',
                'discount_amount': '1',
                'discount_percent': '5',
                'price_without_discount': '20',
                'vat_percent': '10',
                'vat_amount': '1.9',
            },
            {
                'item_id': 2,
                'product_id': 'product_id_2',
                'parent_product_id': 'parent_product_id_2',
                'name': 'name_2',
                'quantity': '1',
                'price_per_unit': '30',
                'price_for_customer': '30',
                'discount_amount': '0',
                'discount_percent': '0',
                'price_without_discount': '30',
                'vat_percent': '20',
                'vat_amount': '6',
            },
            {
                'item_id': 3,
                'product_id': 'parent_product_id_2',
                'name': 'parent_name_2',
                'quantity': '1',
                'price_per_unit': '0',
                'price_for_customer': '0',
                'discount_amount': '0',
                'discount_percent': '0',
                'price_without_discount': '0',
                'vat_percent': '20',
                'vat_amount': '0',
            },
        ],
        'status': {
            'restaurant_status': restaurant_status,
            'invoice_status': invoice_status,
            'updated_at': 'status_updated_at',
        },
        'yandex_uid': yandex_uid,
        'user_id': user_id,
        'invoice_id': invoice_id,
    }


EXPECTED_INVOICE_UPDATE_REQUEST = {
    'id': '7efc8e217e5f99c21d8a69b2719d27e6',
    'originator': 'processing',
    'operation_id': 'create_order_1',
    'items_by_payment_type': [
        {
            'items': [
                {
                    'amount': '19',
                    'item_id': '1',
                    'product_id': 'eda_107819207_ride',
                    'fiscal_receipt_info': {
                        'vat': 'nds_10',
                        'title': 'name_1 x2',
                    },
                },
                {
                    'amount': '30',
                    'item_id': '2',
                    'product_id': 'eda_107819207_ride',
                    'fiscal_receipt_info': {
                        'vat': 'nds_20',
                        'title': 'name_2 x1',
                    },
                },
                {
                    'amount': '0',
                    'item_id': '3',
                    'product_id': 'eda_107819207_ride',
                    'fiscal_receipt_info': {
                        'vat': 'nds_20',
                        'title': 'parent_name_2 x1',
                    },
                },
            ],
            'payment_type': 'card',
        },
    ],
    'payments': [
        {
            'billing_id': '',
            'method': 'card-x5a4adedaf78dba6f9c56fee4',
            'type': 'card',
        },
    ],
    'version': 1,
}


async def _request(
        web_app_client,
        patch,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        build_pa_headers,
        with_complements=False,
        url='/4.0/payments/v1/orders'
        '?external_ref=order1&service=restaurants&hmac=hmac',
        email_for_receipts=None,
):
    @patch('payments_eda.utils.payment_types.get_payment_types_info')
    async def _mock_get_values(*args, **kwargs):
        return payment_types.PaymentTypeInfo(
            available_payment_types=['card', 'personal_wallet'],
            merchant_ids=[],
        )

    @mock_cardstorage('/v1/payment_methods')
    async def _mock_payment_method(*args, **kwargs):
        return load_json('cardstorage_payment_methods.json')

    eda_doc_mockserver(
        {
            'items': [
                {'amount': '123.43', 'currency': 'RUB', 'item_id': '123'},
            ],
            'country_code': 'RU',
            'region_id': '1',
            'service_product_id': 'food_product_id',
            'uuid': 'default_yandex_uid',
            'location': [30.313119, 59.931513],
            'business': 'restaurants',
        },
    )
    request_body = {
        'payment_method': 'card',
        'payment_method_id': 'card-x5a4adedaf78dba6f9c56fee4',
        'email_for_receipts': email_for_receipts,
    }
    if with_complements:
        request_body['complements'] = [
            {
                'payment_method_id': 'wallet_id/1234567890',
                'payment_method': 'personal_wallet',
            },
        ]
    return await web_app_client.post(
        url, json=request_body, headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )


@pytest.mark.parametrize(
    ('hmac', 'expected_code'),
    (
        pytest.param(None, 200, id='hmac_missing'),
        pytest.param('hmac', 200, id='hmac_ok'),
    ),
)
async def test_hmac_validation(
        web_app,
        web_app_client,
        mockserver,
        mock_cardstorage,
        eda_doc_mockserver,
        patch,
        load_json,
        build_pa_headers,
        hmac,
        expected_code,
        empty_transactions_update_mock,
        empty_transactions_create_mock,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(request):
        assert request.query == {
            'id': 'order1',
            'locale': 'ru',
            'for_user': 'false',
        }
        return _iiko_order()

    @mockserver.json_handler('/iiko-integration/v1/order/authorized-update')
    def _iiko_update_mock(request):
        return {}

    url = f'/4.0/payments/v1/orders?external_ref=order1&service=restaurants'
    if hmac:
        url = url + f'&hmac={hmac}'

    resp = await _request(
        web_app_client,
        patch,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        build_pa_headers,
        url=url,
    )
    assert resp.status == expected_code


@pytest.mark.config(
    PERSONAL_WALLET_FIRM_BY_SERVICE={'restaurants': {'RUB': '32'}},
)
@pytest.mark.client_experiments3(
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
@pytest.mark.parametrize(
    (
        'restaurant_status',
        'invoice_status',
        'is_update_called',
        'is_invoice_created',
        'expected_code',
    ),
    (
        pytest.param(
            'PENDING', 'INIT', True, True, 200, id='all_calls_for_pending',
        ),
        pytest.param(
            'CANCELED', 'INIT', False, False, 404, id='error_for_cancelled',
        ),
        pytest.param(
            'CANCELED',
            'HOLDING',
            False,
            False,
            404,
            id='error_for_cancelled2',
        ),
        pytest.param(
            'CLOSED', 'INIT', False, False, 404, id='error_for_closed',
        ),
        pytest.param(
            'CLOSED', 'HOLD_FAILED', False, False, 404, id='error_for_closed2',
        ),
        pytest.param(
            'PENDING', 'HOLDING', True, True, 200, id='ok_with_holding',
        ),
        pytest.param(
            'WAITING_FOR_CONFIRMATION',
            'HELD',
            False,
            False,
            200,
            id='held_and_waiting_already_processing',
        ),
        pytest.param(
            'PAYMENT_CONFIRMED',
            'HELD',
            False,
            False,
            200,
            id='held_and_confirmed_already_processing',
        ),
        pytest.param(
            'PENDING',
            'HOLD_FAILED',
            True,
            True,
            200,
            id='update_and_create_invoice_for_hold_failed',
        ),
        pytest.param(
            'PAYMENT_CONFIRMED',
            'HOLD_FAILED',
            False,
            False,
            200,
            id='hold_failed_and_confirmed_already_processing',
        ),
        pytest.param(
            'PAYMENT_CONFIRMED',
            'CLEARING',
            False,
            False,
            200,
            id='clearing_already_processing',
        ),
        pytest.param(
            'PAYMENT_CONFIRMED',
            'CLEARED',
            False,
            False,
            200,
            id='cleared_already_processing',
        ),
    ),
)
@pytest.mark.parametrize(
    'with_complements',
    (
        pytest.param(False, id='without complements'),
        pytest.param(True, id='with complements'),
    ),
)
async def test_order_by_status(
        web_app,
        web_app_client,
        mockserver,
        mock_cardstorage,
        eda_doc_mockserver,
        patch,
        load_json,
        build_pa_headers,
        restaurant_status,
        invoice_status,
        is_update_called,
        is_invoice_created,
        stq,
        expected_code,
        empty_transactions_create_mock,
        with_complements,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(request):
        return _iiko_order(
            restaurant_status=restaurant_status,
            invoice_status=invoice_status,
            yandex_uid='default_yandex_uid',
            user_id='default_user_id',
            invoice_id='7efc8e217e5f99c21d8a69b2719d27e6',
        )

    @mockserver.json_handler('/personal_wallet/v1/available-accounts')
    def _personal_wallet_mock(request):
        return load_json('available_accounts_with_complements.json')

    @mockserver.json_handler('/iiko-integration/v1/order/authorized-update')
    def _iiko_update_mock(request):
        expected_request = {
            'invoice_id': 'db5b2ee14276e83c9723a9e5ca54d79a',
            'invoice_status': 'HOLDING',
            'user_id': 'default_user_id',
            'payment_method': {
                'id': 'card-x5a4adedaf78dba6f9c56fee4',
                'type': 'card',
            },
            'yandex_uid': 'default_yandex_uid',
            'locale': 'ru',
        }
        if with_complements:
            expected_request['invoice_id'] = '817856348ccbaca78fb26518564b05ef'
            expected_request['complement_payment_method'] = {
                'id': 'wallet_id/1234567890',
                'type': 'personal_wallet',
                'balance': '500',
            }
        assert request.json == expected_request
        return {}

    resp = await _request(
        web_app_client,
        patch,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        build_pa_headers,
        with_complements=with_complements,
    )
    assert resp.status == expected_code

    assert _iiko_update_mock.times_called == (1 if is_update_called else 0)

    invoice_calls = 1 if is_invoice_created else 0
    assert (
        stq.restaurant_order_update_transactions.times_called == invoice_calls
    )
    assert empty_transactions_create_mock.times_called == invoice_calls


@pytest.mark.parametrize(
    (
        'restaurant_status',
        'iiko_order_code',
        'iiko_update_code',
        'expected_code',
        'expected_message',
    ),
    (
        ('PENDING', 200, 200, 200, None),
        ('PENDING', 400, 200, 400, 'bad request message'),
        ('PENDING', 404, 200, 404, 'not found message'),
        ('PENDING', 200, 400, 400, 'bad request message'),
        ('PENDING', 200, 404, 404, 'not found message'),
        ('PENDING', 200, 409, 409, 'status mismatch message'),
        ('CANCELED', 200, 200, 404, 'order canceled message'),
        ('CLOSED', 200, 200, 404, 'order closed message'),
        ('EXPIRED', 200, 200, 404, 'order expired message'),
    ),
)
async def test_error_handling(
        web_app,
        web_app_client,
        mockserver,
        eda_doc_mockserver,
        mock_cardstorage,
        patch,
        load_json,
        build_pa_headers,
        restaurant_status,
        iiko_order_code,
        iiko_update_code,
        expected_code,
        expected_message,
        empty_transactions_update_mock,
        empty_transactions_create_mock,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(req):
        if iiko_order_code != 200:
            return mockserver.make_response(
                status=iiko_order_code, json={'code': '', 'message': ''},
            )
        return _iiko_order(restaurant_status=restaurant_status)

    @mockserver.json_handler('/iiko-integration/v1/order/authorized-update')
    def _iiko_update_mock(request):
        if iiko_update_code != 200:
            return mockserver.make_response(
                status=iiko_update_code, json={'code': '', 'message': ''},
            )
        return {}

    resp = await _request(
        web_app_client,
        patch,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        build_pa_headers,
    )
    assert resp.status == expected_code
    if expected_code != 200:
        data = await resp.json()
        assert data['message'] == expected_message


@pytest.mark.parametrize(
    ('iiko_code', 'expected_code'),
    (
        pytest.param(
            'service_unavailable',
            'service_unavailable',
            id='restaurants_unavailable',
        ),
        pytest.param(
            'anything', 'bad_request', id='bad_request_for_other_codes',
        ),
    ),
)
async def test_restaurants_unavailable(
        web_app,
        web_app_client,
        mockserver,
        mock_cardstorage,
        eda_doc_mockserver,
        patch,
        load_json,
        build_pa_headers,
        iiko_code,
        expected_code,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(request):
        return mockserver.make_response(
            status=400, json={'code': iiko_code, 'message': ''},
        )

    resp = await _request(
        web_app_client,
        patch,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        build_pa_headers,
    )
    assert resp.status == 400

    data = await resp.json()
    assert data['code'] == expected_code


SUM_TO_PAY_OK = [
    {
        'items': [
            {'amount': '19', 'item_id': '1'},
            {'amount': '30', 'item_id': '2'},
            {'amount': '0', 'item_id': '3'},
        ],
        'payment_type': 'card',
    },
]

SUM_TO_PAY_2TYPES = [
    {
        'items': [
            {'amount': '30', 'item_id': '2'},
            {'amount': '0', 'item_id': '3'},
        ],
        'payment_type': 'card',
    },
    {'items': [{'amount': '19', 'item_id': '1'}], 'payment_type': 'cash'},
]

SUM_TO_PAY_WRONG_AMOUNT = [
    {
        'items': [
            {'amount': '19', 'item_id': '1'},
            {'amount': '42', 'item_id': '2'},
            {'amount': '0', 'item_id': '3'},
        ],
        'payment_type': 'card',
    },
]

SUM_TO_PAY_WRONG_ITEM_ID = [
    {
        'items': [
            {'amount': '19', 'item_id': '1'},
            {'amount': '30', 'item_id': '2'},
        ],
        'payment_type': 'card',
    },
]

SUM_TO_PAY_4ITEMS = [
    {
        'items': [
            {'amount': '19', 'item_id': '1'},
            {'amount': '30', 'item_id': '2'},
            {'amount': '0', 'item_id': '3'},
            {'amount': '0', 'item_id': '4'},
        ],
        'payment_type': 'card',
    },
]


def _invoice_retrieve_response(status, version=2, currency='RUB'):
    return {
        'cleared': [],
        'currency': currency,
        'debt': [],
        'held': [],
        'id': 'rest_order_id_default_user_id',
        'invoice_due': '2018-07-20T14:00:00.0000+0000',
        'created': '2018-07-20T14:00:00.0000+0000',
        'operation_info': {
            'originator': 'processing',
            'priority': 1,
            'version': version,
        },
        'operations': [],
        'payment_types': ['card'],
        'status': status,
        'sum_to_pay': [],
        'transactions': [],
        'yandex_uid': 'default_yandex_uid',
    }


@pytest.mark.parametrize(
    ('invoice', 'can_be_resolved', 'expected_code'),
    (
        pytest.param(None, False, 500, id='invoice_not_found'),
        pytest.param(
            _invoice_retrieve_response(status='init', version=1),
            True,
            200,
            id='invoice_created_but_not_updated',
        ),
        pytest.param(
            _invoice_retrieve_response(status='hold-failed', version=3),
            True,
            200,
            id='hold_failed',
        ),
        pytest.param(
            _invoice_retrieve_response(status='holding', version=3),
            True,
            200,
            id='holding',
        ),
        pytest.param(
            _invoice_retrieve_response(status='cleared', version=3),
            False,
            409,
            id='cleared',
        ),
    ),
)
async def test_transactions_conflict(
        web_app,
        web_app_client,
        mockserver,
        mock_cardstorage,
        eda_doc_mockserver,
        patch,
        load_json,
        build_pa_headers,
        stq,
        invoice,
        expected_code,
        can_be_resolved,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(req):
        return _iiko_order()

    @mockserver.json_handler('/iiko-integration/v1/order/authorized-update')
    def _iiko_update_mock(request):
        return {}

    @mockserver.json_handler('/transactions-eda/v2/invoice/create')
    def transactions_create_mock(request):
        return mockserver.make_response(
            status=409, json={'code': '', 'message': ''},
        )

    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def transactions_retrieve_mock(request):
        if invoice:
            return invoice
        return mockserver.make_response(
            status=404, json={'code': '', 'message': ''},
        )

    resp = await _request(
        web_app_client,
        patch,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        build_pa_headers,
    )

    assert resp.status == expected_code
    if resp.status == 409:
        data = await resp.json()
        assert data['code'] == 'transaction_conflict'

    assert transactions_create_mock.times_called == 1
    assert transactions_retrieve_mock.times_called == 1

    if can_be_resolved:
        assert stq.restaurant_order_update_transactions.times_called == 1
    else:
        assert stq.restaurant_order_update_transactions.times_called == 0


EMAIL_EXPERIMENT = dict(
    consumer=service_consts.EXP3_CONSUMER_WEB,
    experiment_name=experiments.EMAIL_REQUEST_FOR_QR,
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
    ['email', 'expected_status', 'is_personal_error', 'is_email_exp'],
    [
        pytest.param(
            'p_er-fe123.ct@em.ail.ru', 200, False, False, id='off experiment',
        ),
        pytest.param(
            '   p_ER-fe123.ct@em.ail.ru ',
            200,
            False,
            True,
            id='successfull',
            marks=pytest.mark.client_experiments3(**EMAIL_EXPERIMENT),
        ),
        pytest.param(
            '',
            409,
            False,
            True,
            id='empty email',
            marks=pytest.mark.client_experiments3(**EMAIL_EXPERIMENT),
        ),
        pytest.param(
            'qwert@123@yu',
            409,
            False,
            True,
            id='invalid email 1',
            marks=pytest.mark.client_experiments3(**EMAIL_EXPERIMENT),
        ),
        pytest.param(
            'qwert@@yu.ru',
            409,
            False,
            True,
            id='invalid email 2',
            marks=pytest.mark.client_experiments3(**EMAIL_EXPERIMENT),
        ),
        pytest.param(
            'qwertyu',
            409,
            False,
            True,
            id='invalid email 3',
            marks=pytest.mark.client_experiments3(**EMAIL_EXPERIMENT),
        ),
        pytest.param(
            'asd*@ko.te',
            409,
            False,
            True,
            id='invalid email 4',
            marks=pytest.mark.client_experiments3(**EMAIL_EXPERIMENT),
        ),
        pytest.param(
            'p_er-fe123.ct@em.ail.ru3',
            409,
            False,
            True,
            id='invalid email 5',
            marks=pytest.mark.client_experiments3(**EMAIL_EXPERIMENT),
        ),
        pytest.param(
            'p_er-fe123.ct@em.ail.ru',
            500,
            True,
            True,
            id='personal problem',
            marks=pytest.mark.client_experiments3(**EMAIL_EXPERIMENT),
        ),
    ],
)
async def test_email_for_receipts(
        web_app,
        web_app_client,
        mockserver,
        mock_cardstorage,
        eda_doc_mockserver,
        patch,
        load_json,
        build_pa_headers,
        empty_transactions_update_mock,
        empty_transactions_create_mock,
        email: str,
        expected_status: int,
        is_personal_error: bool,
        is_email_exp: bool,
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(request):
        return _iiko_order()

    @mockserver.json_handler('/personal/v1/emails/store')
    def _personal_store_email(request):
        if is_personal_error:
            return mockserver.make_response(
                status=500, json={'code': '', 'message': ''},
            )
        assert request.json == {
            'validate': True,
            'value': 'p_ER-fe123.ct@em.ail.ru',
        }
        return {'id': 'personal_email_id', 'value': 'p_er-fe123.ct@em.ail.ru'}

    @mockserver.json_handler('/iiko-integration/v1/order/authorized-update')
    def _iiko_update_mock(request):
        request_body = request.json
        if is_email_exp:
            assert request_body['personal_email_id'] == 'personal_email_id'
        return {}

    resp = await _request(
        web_app_client,
        patch,
        mock_cardstorage,
        eda_doc_mockserver,
        load_json,
        build_pa_headers,
        email_for_receipts=email,
    )
    assert resp.status == expected_status
    if expected_status == 409:
        data = await resp.json()
        assert data['code'] == 'invalid_email'
        assert data['message'] == 'invalid email message'
