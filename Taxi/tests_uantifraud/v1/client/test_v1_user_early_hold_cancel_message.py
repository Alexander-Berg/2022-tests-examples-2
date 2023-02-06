import pytest


@pytest.mark.config(
    UAFS_EARLY_HOLD_CANCEL_WINDOW_FIELDS={
        'window_fields': {
            'change_params_button_text': {
                'key': 'change_params_button_text',
                'keyset': 'taxia_strings',
            },
            'retry_button_text': {
                'key': 'retry_button_text',
                'keyset': 'taxia_strings',
            },
            'text': {'key': 'text', 'keyset': 'taxia_strings'},
            'title': {'key': 'title', 'keyset': 'taxia_strings'},
        },
        '__default_change_params_button_text__': {
            'key': 'change_params_button_text',
            'keyset': 'taxia_strings',
        },
    },
)
@pytest.mark.translations(
    taxia_strings={
        'change_params_button_text': {'ru': 'Изменить'},
        'retry_button_text': {'ru': 'Повторить'},
        'text': {'ru': 'Деньги списать не удалось, поэтому заказ отменили'},
        'title': {'ru': 'Заказ отменён'},
    },
)
async def test_ok(taxi_uantifraud):
    order_id = 'some_order_id'
    response = await taxi_uantifraud.get(
        f'/v1/client/user/early_hold_cancel/message?order_id={order_id}',
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'order_status_alert': {
            'change_params_button_text': 'Изменить',
            'retry_button_text': 'Повторить',
            'text': 'Деньги списать не удалось, поэтому заказ отменили',
            'title': 'Заказ отменён',
        },
    }
