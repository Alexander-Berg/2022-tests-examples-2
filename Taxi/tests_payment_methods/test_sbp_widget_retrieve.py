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


@pytest.mark.config(TAXI_PAYMENTS_SBP_TRASACTION_EXPIRE_TIMEOUT=600)
@pytest.mark.parametrize(
    'request_body, expected_status, expected_response',
    [
        pytest.param(
            {'order_id': 'not_existent_invoice', 'status_updates': []},
            404,
            {'code': '404', 'message': 'Invoice not found'},
            id='Invoice not exists',
        ),
        pytest.param(
            {'order_id': 'payment_by_card', 'status_updates': []},
            404,
            {'code': '404', 'message': 'Incorrect invoice payment method'},
            id='Invoice with NOT sbp payment method',
        ),
        pytest.param(
            {'order_id': 'invoice_in_hidden_status', 'status_updates': []},
            200,
            {},
            id='Invoice in status "hold", not showing widget',
        ),
        pytest.param(
            {'order_id': 'show_widget_success', 'status_updates': []},
            200,
            {
                'widget': {
                    'user_email': 'foo@bar.com',
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
            {'order_id': 'show_notification_success', 'status_updates': []},
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
            {'order_id': 'show_notification_failure', 'status_updates': []},
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
        pytest.param(
            {
                'order_id': 'show_modal_window',
                'status_updates': [
                    {
                        'reason': 'moved_to_cash',
                        'created': '2019-09-10T03:23:37.733+0000',
                    },
                ],
            },
            200,
            {
                'notifications': [
                    {
                        'icon_tag': 'failure_icon_tag',
                        'id': '57113184b5a2d4375745278e',
                        'text': 'Не успех',
                    },
                ],
                'modal_window': {
                    'id': '57113184b5a2d4375745278e',
                    'icon_tag': 'modal_window_icon_tag',
                    'title': 'Оплата не прошла',
                    'text': 'Не достаточно средств',
                    'reason': 'early_hold_cancel',
                    'main_button': {
                        'text': 'Понятно',
                        'color': 'main_button_background_color',
                        'action': {'type': 'do_nothing'},
                    },
                    'extra_button': {
                        'text': 'Не понятно',
                        'color': 'extra_button_background_color',
                        'action': {'type': 'do_nothing'},
                    },
                },
            },
            id='Show modal window',
        ),
        pytest.param(
            {
                'order_id': 'show_widget_success',
                'status_updates': [
                    {
                        'reason': 'requestconfirm_transporting',
                        'created': '2022-03-10T03:23:37.733+0000',
                    },
                ],
                'plan_transporting_time_sec': 650,
            },
            200,
            {
                'widget': {
                    'user_email': 'foo@bar.com',
                    'deadline_timestamp': 1646883217,
                    'icon_tag': 'icon_tag',
                    'last_payment_failed': False,
                    'payment_button': {
                        'background_color': 'HEX',
                        'text': 'Оплатить $TIME$',
                    },
                    'purchase_token': '57113184b5a2d4375745278e',
                    'service_token': 'sbp_service_token',
                    'text': {
                        'loading_title': 'Производится оплата',
                        'title': 'Оплатить за 10 минут',
                    },
                },
            },
            id='Show payment widget with time',
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
        'taxi_payments.sbp.widget.title_long_ride': {
            'ru': 'Оплатить за %(minutes)s минут',
        },
        'taxi_payments.sbp.notification.title.success': {'ru': 'Успех'},
        'taxi_payments.sbp.notification.title.failure': {'ru': 'Не успех'},
        'taxi_payments.sbp.modal_window.title': {'ru': 'Оплата не прошла'},
        'taxi_payments.sbp.modal_window.text': {'ru': 'Не достаточно средств'},
        'taxi_payments.sbp.modal_window.main_button.text': {'ru': 'Понятно'},
        'taxi_payments.sbp.modal_window.extra_button.text': {
            'ru': 'Не понятно',
        },
        'taxi_payments.sbp.widget.button.title_long_ride': {
            'ru': 'Оплатить $TIME$',
        },
    },
)
async def test_spb_widget_retrieve(
        taxi_payment_methods,
        mock_transactions,
        request_body,
        expected_status,
        expected_response,
):
    response = await taxi_payment_methods.post(
        '/v1/sbp/widget/retrieve',
        json=request_body,
        headers={**DEFAULT_HEADERS},
    )
    assert response.status == expected_status
    assert expected_response == response.json()
