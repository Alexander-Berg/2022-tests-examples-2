import pytest

DEFAULT_HEADERS = {
    'Accept-Language': 'ru',
    'X-Request-Language': 'ru',
    'X-YaTaxi-UserId': '_id1',
    'X-YaTaxi-PhoneId': '00aaaaaaaaaaaaaaaaaaaa01',
    'X-Yandex-Login': 'test',
    'X-Remote-IP': 'amazing_ip',
    'X-Request-Application': 'app_brand=yataxi',
    'X-Yandex-UID': '123',
}


@pytest.mark.parametrize(
    'order_id, expected_status, expected_response',
    [
        pytest.param(
            'not_existent_invoice',
            404,
            {'code': '404', 'message': 'Invoice not found'},
            id='Invoice not exists',
        ),
        pytest.param(
            'payment_by_card',
            404,
            {'code': '404', 'message': 'Incorrect invoice payment method'},
            id='Invoice with NOT sbp payment method',
        ),
        pytest.param(
            'invoice_in_hidden_status',
            200,
            {},
            id='Invoice in status "hold", not showing widget',
        ),
        pytest.param(
            'show_widget_success',
            200,
            {
                'widget': {
                    'icon_tag': 'icon_tag',
                    'last_payment_failed': False,
                    'payment_button': {
                        'background_color': 'HEX',
                        'text': 'Оплатить',
                    },
                    'purchase_token': '57113184b5a2d4375745278e',
                    'service_token': 'sbp_service_token',
                    'text': {
                        'loading_title': 'Производится оплата',
                        'title': 'Оплата через СБП',
                    },
                },
            },
            id='Show payment widget',
        ),
        pytest.param(
            'show_notification_success',
            200,
            {
                'notifications': [
                    {
                        'icon_tag': 'success_icon_tag',
                        'id': '57113184b5a2d4375745278e',
                        'text': 'Успех',
                    },
                ],
            },
            id='Show only success notification',
        ),
        pytest.param(
            'show_notification_failure',
            200,
            {
                'notifications': [
                    {
                        'icon_tag': 'failure_icon_tag',
                        'id': '57113184b5a2d4375745278e',
                        'text': 'Не успех',
                    },
                ],
            },
            id='Show only failure notification',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxi_payments.sbp.widget.title': {'ru': 'Оплата через СБП'},
        'taxi_payments.sbp.widget.title.loading': {
            'ru': 'Производится оплата',
        },
        'taxi_payments.sbp.widget.button.title': {'ru': 'Оплатить'},
        'taxi_payments.sbp.notification.title.success': {'ru': 'Успех'},
        'taxi_payments.sbp.notification.title.failure': {'ru': 'Не успех'},
    },
)
async def test_spb_widget_retrieve(
        taxi_taxi_payments,
        mock_transactions,
        order_id,
        expected_status,
        expected_response,
):
    response = await taxi_taxi_payments.post(
        '/v1/sbp/widget/retrieve',
        json={'order_id': order_id, 'status_updates': []},
        headers={**DEFAULT_HEADERS},
    )
    assert response.status == expected_status
    assert expected_response == response.json()
