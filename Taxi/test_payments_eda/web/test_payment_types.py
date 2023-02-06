import pytest

import api_4_0_middleware.mw as api_40_mw

from payments_eda import consts as service_consts
from payments_eda.utils import payment_types

YANDEX_LOGIN = 'test_login'
PHONE_ID = 'phone_id'
USER_ID = 'user_id'
YANDEX_UID = 'user-uid'
AUTH_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': PHONE_ID,
    'X-Yandex-Login': YANDEX_LOGIN,
    'X-Yandex-UID': YANDEX_UID,
}


@pytest.mark.parametrize(
    'service, location, yandex_uid, phone_id, user_agent, '
    'expected_payment_types_info',
    [
        (
            service_consts.SERVICE_EATS,
            [55, 37],
            'uuid',
            'phone_id',
            'user_agent',
            payment_types.PaymentTypeInfo(
                available_payment_types=[service_consts.PAYMENT_TYPE_CORP],
                merchant_ids=['merchant1'],
            ),
        ),
    ],
)
async def test_get_payment_types_info(
        web_app,
        mock_payment_methods,
        service,
        user_agent,
        location,
        yandex_uid,
        phone_id,
        expected_payment_types_info,
):
    @mock_payment_methods('/v1/superapp-available-payment-types')
    async def _available_payment_types(request):
        return {
            'payment_types': (
                expected_payment_types_info.available_payment_types
            ),
            'merchant_ids': expected_payment_types_info.merchant_ids,
        }

    auth_ctx = api_40_mw.parse_auth_context(AUTH_HEADERS)

    payment_types_info = await payment_types.get_payment_types_info(
        service=service,
        lat=location[1],
        lon=location[0],
        user_agent=user_agent,
        auth_ctx=auth_ctx,
        context=web_app['context'],
    )

    assert payment_types_info == expected_payment_types_info

    assert _available_payment_types.times_called == 1

    request = _available_payment_types.next_call()['request']

    assert request.args['service'] == service
    assert request.headers['User-Agent'] == user_agent
    assert request.headers['X-YaTaxi-UserId'] == USER_ID
    assert request.headers['X-YaTaxi-PhoneId'] == PHONE_ID
    assert request.headers['X-Yandex-Login'] == YANDEX_LOGIN
    assert request.headers['X-Yandex-UID'] == YANDEX_UID
    assert request.json == {'location': location}
