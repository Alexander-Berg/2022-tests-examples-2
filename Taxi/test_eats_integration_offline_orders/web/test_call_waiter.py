from urllib import parse

import jinja2
import pytest

GROUP_CHAT_ID = 1000000
TABLE_UUID = 'uuid__1'
TABLE_POS_ID = 'table_id__1'
COMMENT = 'Привет, можно мне счёт?'


def telegram_render(context, call_waiter_type: str, **kwargs) -> str:
    templates = (
        context.config.EATS_INTEGRATION_OFFLINE_ORDERS_TELEGRAM_TEMPLATES
    )
    template = templates['call_waiter'][call_waiter_type]
    environment = jinja2.Environment()
    return environment.from_string(template).render(**kwargs)


@pytest.mark.parametrize(
    ('params', 'result_kwargs'),
    (
        ({'uuid': TABLE_UUID}, {'table': TABLE_POS_ID}),
        (
            {'uuid': TABLE_UUID, 'call_waiter_type': 'call'},
            {'table': TABLE_POS_ID},
        ),
        (
            {'uuid': TABLE_UUID, 'call_waiter_type': 'cash_payment'},
            {'table': TABLE_POS_ID},
        ),
        (
            {'uuid': TABLE_UUID, 'comment': COMMENT},
            {'table': TABLE_POS_ID, 'comment': COMMENT},
        ),
        (
            {
                'uuid': TABLE_UUID,
                'comment': COMMENT,
                'call_waiter_type': 'call',
            },
            {'table': TABLE_POS_ID, 'comment': COMMENT},
        ),
        (
            {
                'uuid': TABLE_UUID,
                'comment': COMMENT,
                'call_waiter_type': 'cash_payment',
            },
            {'table': TABLE_POS_ID, 'comment': COMMENT},
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['db.sql', 'restaurant_options_all_enabled.sql'],
)
@pytest.mark.config(
    EI_OFFLINE_ORDERS_PAY_METHOD_SETTINGS={'include_cash': False},
)
async def test_call_waiter_telegram(
        web_context,
        web_app_client,
        mockserver,
        patch,
        params: dict,
        result_kwargs: dict,
):
    @patch('aiogram.bot.api.Methods.api_url')
    def _api_url(token, method):
        return '$mockserver/telegram/bot{token}/{method}'.format(
            token=token, method=method,
        )

    @mockserver.json_handler(
        '/telegram/bot123456:ABC-DEF1234aaaaa-zyx11A1a1a111aa11/sendMessage',
    )
    def telegram_send_message(request):
        kwargs = parse.parse_qs(request.get_data().decode())
        assert str(GROUP_CHAT_ID) == kwargs['chat_id'][0]
        text = telegram_render(
            web_context,
            params.get('call_waiter_type', 'call'),
            **result_kwargs,
        )
        assert text == kwargs['text'][0]
        return {'ok': True, 'result': {}}

    response = await web_app_client.post(f'/v1/call-waiter', params=params)
    assert response.status == 200
    assert telegram_send_message.times_called == 1


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['db.sql', 'restaurant_options_no_payment_offline.sql'],
)
@pytest.mark.config(
    EI_OFFLINE_ORDERS_PAY_METHOD_SETTINGS={'include_cash': True},
)
async def test_call_waiter_offline_payment(
        taxi_eats_integration_offline_orders_web, pgsql,
):
    params = {
        'uuid': TABLE_UUID,
        'comment': COMMENT,
        'call_waiter_type': 'cash_payment',
    }

    response = await taxi_eats_integration_offline_orders_web.post(
        f'/v1/call-waiter', params=params,
    )
    assert response.status == 400


DEFAULT_PLACE_ID = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
DEFAULT_WAITER_ID = '1965cdbe-cac1-44ba-9355-d5da6fd87009'


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_IIKO_WAITER={'host': '$mockserver'},
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['db.sql', 'db_iiko_waiter.sql'],
)
async def test_call_iiko_waiter(web_app_client, mockserver):
    @mockserver.handler('/api/v1/notifications/mobile/waiter-call')
    def _get_test_call_waiter(request):
        assert request.json['userId'] == DEFAULT_WAITER_ID
        return mockserver.make_response('', status=202)

    response = await web_app_client.post(
        f'/v1/call-waiter?uuid={DEFAULT_PLACE_ID}'
        f'&waiter_id={DEFAULT_WAITER_ID}',
    )
    assert response.status == 200
