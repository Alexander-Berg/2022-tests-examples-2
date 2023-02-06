import pytest

from test_iiko_integration import get_order_stubs
from test_iiko_integration import transactions_stubs

RES_GROUP_INFO = get_order_stubs.CONFIG_RESTAURANT_GROUP_INFO
RES_INFO = get_order_stubs.CONFIG_RESTAURANT_INFO


@pytest.mark.config(
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=RES_GROUP_INFO,
    IIKO_INTEGRATION_RESTAURANT_INFO=RES_INFO,
    IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
    QR_PAY_REFUND_AVAILABLE_REASONS={
        'reason_code_1': 'reason_description_1',
        'reason_code_2': 'reason_description_2',
    },
    TVM_RULES=[{'src': 'iiko-integration', 'dst': 'personal'}],
)
@pytest.mark.translations(
    qr_payment={'restaurants.restaurant_01_key': {'ru': 'Ресторан 01'}},
)
@pytest.mark.parametrize(
    (
        'order_id',
        'invoice_id',
        'expected_status',
        'expected_response',
        'expected_status_with_invoice_id',
        'expected_response_with_invoice_id',
        'with_complement',
    ),
    (
        pytest.param(
            '01',
            'invoice_01',
            200,
            get_order_stubs.ORDER_ADMIN_OK_RESPONSE,
            200,
            get_order_stubs.ORDER_ADMIN_OK_RESPONSE,
            False,
            id='ok',
        ),
        pytest.param(
            '01',
            'invoice_01',
            200,
            get_order_stubs.admin_order_with_complement(),
            200,
            get_order_stubs.admin_order_with_complement(),
            True,
            id='ok',
        ),
        pytest.param(
            '02',
            'invoice_02',
            200,
            get_order_stubs.ORDER_2_ADMIN_OK_RESPONSE,
            404,
            get_order_stubs.ORDER_BY_INVOICE_ID_NOT_FOUND_RESPONSE,
            False,
            id='ok with NULL history',
        ),
        pytest.param(
            '03',
            'invoice_03',
            200,
            get_order_stubs.ORDER_3_ADMIN_OK_RESPONSE,
            404,
            get_order_stubs.ORDER_BY_INVOICE_ID_NOT_FOUND_RESPONSE,
            False,
            id='ok with card_number',
        ),
        pytest.param(
            'invalid_order_id',
            'invoice_invalid_id',
            404,
            get_order_stubs.ORDER_NOT_FOUND_RESPONSE,
            404,
            get_order_stubs.ORDER_BY_INVOICE_ID_NOT_FOUND_RESPONSE,
            False,
            id='order not found',
        ),
    ),
)
@pytest.mark.parametrize('use_invoice_api', [False, True])
@pytest.mark.pgsql('iiko_integration', directories=['test_get_order'])
async def test_get_order_admin(
        mock_invoice_retrieve,
        mock_cardstorage,
        load_json,
        pgsql,
        web_app_client,
        order_id: str,
        invoice_id: str,
        expected_response: dict,
        expected_status: int,
        expected_response_with_invoice_id: dict,
        expected_status_with_invoice_id: int,
        with_complement: bool,
        use_invoice_api: bool,
        mockserver,
):
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _get_email_mock(request):
        if request.json == dict(id='a1s2d3f4_email'):
            return {'id': 'a1s2d3f4_email', 'value': 'user@yandex.ru'}
        return mockserver.make_response(
            status=404, json={'code': 'c', 'message': 'm'},
        )

    if with_complement:
        get_order_stubs.add_complement_to_db(pgsql)

    @mock_cardstorage('/v1/card')
    def _cardstorage(request):
        return load_json('cardstorage_response.json')

    mock_invoice_retrieve(
        invoice_id=f'invoice_{order_id}',
        response_data=transactions_stubs.DEFAULT_INVOICE_RETRIEVE_RESPONSE,
    )

    url = f'/admin/qr-pay/v1/order?id={order_id}'
    if use_invoice_api:
        url = f'/admin/qr-pay/v1/order_by_invoice_id?invoice_id={invoice_id}'
        expected_status = expected_status_with_invoice_id
        expected_response = expected_response_with_invoice_id

    response = await web_app_client.get(url)

    assert response.status == expected_status
    response_json = await response.json()
    assert response_json == expected_response
