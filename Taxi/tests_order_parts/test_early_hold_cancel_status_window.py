import pytest

DEFAULT_HEADERS = {'X-Yandex-UID': '999'}
ORDER_PRICE = 123
CONFIG_WINDOW_CONTENT = {
    'window_fields': {
        'text_personal': {'key': 'text_personal', 'keyset': 'client_messages'},
        'text_family': {'key': 'text_family', 'keyset': 'client_messages'},
        'text_business': {'key': 'text_business', 'keyset': 'client_messages'},
        'text_yandex_card': {
            'key': 'text_yandex_card',
            'keyset': 'client_messages',
        },
        'title': {'key': 'title', 'keyset': 'client_messages'},
        'main_button_text': {
            'key': 'main_button_text',
            'keyset': 'client_messages',
        },
        'main_button_color': 'yellow',
        'main_button_action_screen': 'payment_methods',
        'extra_button_text': {
            'key': 'extra_button_text',
            'keyset': 'client_messages',
        },
        'extra_button_color': 'white',
        'extra_button_action_screen': 'summary',
        'extra_button_text_color': 'textMain',
    },
}
CLIENT_MESSAGES = {
    'text_personal': {
        'ru': (
            'Мы не смогли заморозить %(amount)s на вашей карте. '
            'Проверьте, что с ней всё в порядке, или измените '
            'способ оплаты на наличные.'
        ),
    },
    'text_family': {
        'ru': (
            'Мы не смогли заморозить %(amount)s на семейной карте. '
            'Попробуйте другой способ оплаты.'
        ),
    },
    'text_business': {
        'ru': (
            'Мы не смогли заморозить %(amount)s на карте '
            'бизнес-аккаунта. Попробуйте другой способ оплаты.'
        ),
    },
    'text_yandex_card': {
        'ru': (
            'Мы не смогли заморозить %(amount)s на вашем Счёте '
            'в Яндексе. Проверьте баланс счёта.'
        ),
    },
    'title': {'ru': 'Заказ отменён'},
    'main_button_text': {'ru': 'Изменить способ оплаты'},
    'extra_button_text': {'ru': 'Понятно'},
}


@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='order_parts_early_hold_cancel_status_window_handler_enabled',
    consumers=['order_parts/early_hold_cancel_status_window'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.config(
    ORDER_PARTS_EARLY_HOLD_ORDER_CANCEL_WINDOW_CONTENT=CONFIG_WINDOW_CONTENT,
)
@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'payment_tech_type,payment_method_id,status_code,order_status_window_text',
    [
        pytest.param(
            'card',
            'card-12345678910',
            200,
            (
                'Мы не смогли заморозить {} $SIGN$$CURRENCY$ на вашей карте. '
                'Проверьте, что с ней всё в порядке, или измените '
                'способ оплаты на наличные.'.format(ORDER_PRICE)
            ),
            id='personal_account-payment_type_is_card',
        ),
        pytest.param(
            'applepay',
            'card-12345678910',
            200,
            (
                'Мы не смогли заморозить {} $SIGN$$CURRENCY$ на вашей карте. '
                'Проверьте, что с ней всё в порядке, или измените '
                'способ оплаты на наличные.'.format(ORDER_PRICE)
            ),
            id='personal_account-payment_type_is_applepay',
        ),
        pytest.param(
            'googlepay',
            'card-12345678910',
            200,
            (
                'Мы не смогли заморозить {} $SIGN$$CURRENCY$ на вашей карте. '
                'Проверьте, что с ней всё в порядке, или измените '
                'способ оплаты на наличные.'.format(ORDER_PRICE)
            ),
            id='personal_account-payment_type_is_googlepay',
        ),
        pytest.param(
            'coop_account',
            'family-12345678910',
            200,
            (
                'Мы не смогли заморозить {} $SIGN$$CURRENCY$ на семейной '
                'карте. Попробуйте другой способ оплаты.'.format(ORDER_PRICE)
            ),
            id='family_account-payment_type_is_coop_account',
        ),
        pytest.param(
            'coop_account',
            'business-12345678910',
            200,
            (
                'Мы не смогли заморозить {} $SIGN$$CURRENCY$ на карте '
                'бизнес-аккаунта. Попробуйте другой способ оплаты.'.format(
                    ORDER_PRICE,
                )
            ),
            id='business_account-payment_type_is_coop_account',
        ),
        pytest.param(
            'corp',
            'corp-12345678910',
            500,
            None,
            id='personal_account-payment_type_is_corp',
        ),
        pytest.param(
            'yandex_card',
            'card-x290be35f4dccc542e7f895f5',
            200,
            (
                'Мы не смогли заморозить {} $SIGN$$CURRENCY$ на вашем Счёте '
                'в Яндексе. Проверьте баланс счёта.'.format(ORDER_PRICE)
            ),
            id='personal_account-payment_type_is_yandex_card',
        ),
    ],
)
async def test_early_hold_cancel_status_window(
        taxi_order_parts,
        payment_tech_type,
        payment_method_id,
        status_code,
        order_status_window_text,
):
    response = await taxi_order_parts.post(
        '/v1/early_hold_cancel/status_window/message',
        json={
            'order_id': 'order_id',
            'order_price': ORDER_PRICE,
            'currency_name': 'RUB',
            'payment_tech_type': payment_tech_type,
            'payment_method_id': payment_method_id,
        },
        headers={**DEFAULT_HEADERS, 'X-Request-Language': 'ru'},
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == {
            'order_status_window': {
                'id': 'early_hold_cancel',
                'text': order_status_window_text,
                'title': 'Заказ отменён',
                'reason': 'early_hold_cancel',
                'main_button': {
                    'text': 'Изменить способ оплаты',
                    'color': 'yellow',
                    'action': {
                        'screen': 'payment_methods',
                        'type': 'go_to_screen',
                    },
                },
                'extra_button': {
                    'text': 'Понятно',
                    'color': 'white',
                    'text_color': 'textMain',
                    'action': {'screen': 'summary', 'type': 'go_to_screen'},
                },
            },
        }


@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='order_parts_early_hold_cancel_status_window_handler_enabled',
    consumers=['order_parts/early_hold_cancel_status_window'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.config(
    ORDER_PARTS_EARLY_HOLD_ORDER_CANCEL_WINDOW_CONTENT=CONFIG_WINDOW_CONTENT,
)
@pytest.mark.translations(non_existing_keyset=CLIENT_MESSAGES)
async def test_early_hold_cancel_status_window_non_existing_keyset(
        taxi_order_parts,
):
    response = await taxi_order_parts.post(
        '/v1/early_hold_cancel/status_window/message',
        json={
            'order_id': 'order_id',
            'order_price': ORDER_PRICE,
            'currency_name': 'RUB',
            'payment_tech_type': 'card',
            'payment_method_id': 'card-12345678910',
        },
        headers={**DEFAULT_HEADERS, 'X-Request-Language': 'ru'},
    )
    assert response.status_code == 500
