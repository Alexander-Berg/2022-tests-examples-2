from aiohttp import web
import pytest


@pytest.mark.now('2019-06-04T03:11:22')
@pytest.mark.parametrize(
    'change_source, idempotency_token, operation_id',
    (
        (None, None, 'change:foobar'),
        (None, 'some_token', 'change:some_token'),
        ('tips', None, 'change:foobar:tips'),
        ('tips', 'some_token', 'change:some_token:tips'),
        ('admin', 'some_token', 'change:some_token:admin'),
    ),
)
@pytest.mark.parametrize('version', (None, 123))
async def test_basic(
        web_app_client,
        mockserver,
        load_json,
        mock_uuid,
        change_source,
        idempotency_token,
        operation_id,
        version,
):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def retrieve_handler(request):  # pylint: disable=unused-variable
        return load_json('transactions_eda_invoice_retrieve.json')

    def validate_update_request(request, v2_update):
        body = request.json

        expected = {
            'id': 'my-order',
            'originator': 'processing',
            'operation_id': operation_id,
        }
        items = [{'amount': '10.53', 'item_id': 'food'}]
        if version is not None:
            expected['version'] = version
        if v2_update:
            expected['items_by_payment_type'] = [
                {'items': items, 'payment_type': 'card'},
            ]
        else:
            expected['items'] = items

        assert body == expected

    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def v2_update_handler(request):
        validate_update_request(request, v2_update=True)
        return {}

    data = {'amount': '10.53', 'currency': 'RUB'}
    if change_source is not None:
        data['change_source'] = change_source
    if version is not None:
        data['version'] = version
    if idempotency_token is not None:
        data['idempotency_token'] = idempotency_token

    mock_uuid('foobar')

    response = await web_app_client.put(
        '/v1/orders/items',
        params={'order_id': 'my-order', 'item_id': 'xxx'},
        json=data,
    )

    assert response.status == 200
    assert v2_update_handler.times_called == 1


@pytest.mark.now('2019-06-04T03:11:22')
async def test_basic_error(web_app_client, mockserver, load_json, mock_uuid):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def retrieve_handler(request):  # pylint: disable=unused-variable
        return load_json('transactions_eda_invoice_retrieve.json')

    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def v2_update_handler(request):
        return {}

    data = {'amount': '10.53', 'currency': 'RUB', 'change_source': 'foo:bar'}

    mock_uuid('foobar')

    response = await web_app_client.put(
        '/v1/orders/items',
        params={'order_id': 'my-order', 'item_id': 'xxx'},
        json=data,
    )

    assert response.status == 400
    assert v2_update_handler.times_called == 0


@pytest.mark.parametrize('http_code', [404, 409])
async def test_http_errors(web_app_client, mockserver, http_code, load_json):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def retrieve_handler(request):  # pylint: disable=unused-variable
        return load_json('transactions_eda_invoice_retrieve.json')

    bad_response = web.Response(
        status=http_code,
        body='{"code": "error", "message": "yet another error"}',
    )

    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def v2_update_handler(request):
        return bad_response

    response = await web_app_client.put(
        '/v1/orders/items',
        params={'order_id': 'my-order', 'item_id': 'xxx'},
        json={'amount': '10.53', 'currency': 'RUB'},
    )
    assert response.status == http_code
    assert v2_update_handler.times_called == 1


def get_sum(**kwargs):
    return [
        {'payment_type': payment_type, 'amount': str(amount)}
        for payment_type, amount in kwargs.items()
    ]


def get_split(**kwargs):
    return [
        {
            'payment_type': payment_type,
            'items': [{'amount': str(amount), 'item_id': 'food'}],
        }
        for payment_type, amount in kwargs.items()
    ]


@pytest.mark.parametrize(
    'amount,sum_by_payment_type,expected_split',
    [
        ('50', get_sum(card=50), get_split(card=50)),
        ('100', get_sum(card=100), get_split(card=100)),
        (
            '50',
            get_sum(card=25, personal_wallet=25),
            get_split(card=25, personal_wallet=25),
        ),
    ],
)
async def test_split_v2(
        web_app_client,
        mockserver,
        sum_by_payment_type,
        amount,
        expected_split,
):
    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def v2_update_handler(request):
        assert request.json['items_by_payment_type'] == expected_split
        return {}

    data = {
        'amount': amount,
        'currency': 'RUB',
        'sum_by_payment_type': sum_by_payment_type,
    }

    response = await web_app_client.put(
        '/v1/orders/items',
        params={'order_id': 'my-order', 'item_id': 'xxx'},
        json=data,
    )

    assert response.status == 200
    assert v2_update_handler.times_called == 1
