import pytest

# pylint: disable=invalid-name
pytestmark = [pytest.mark.experiments3(filename='experiments3_defaults.json')]

HEADERS = {
    'X-SDK-Client-ID': 'taxi.test',
    'X-SDK-Version': '10.10.10',
    'X-Yandex-UID': 'user_plus_context',
    'X-YaTaxi-Pass-Flags': 'portal,cashback-plus',
    'X-Request-Language': 'ru',
    'X-Remote-IP': '185.15.98.233',
}


@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['ya_plus_rus_v2']},
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={
        'ya_plus_rus_v2': (
            'ru.yandex.plus.30min.autorenewable.native.web.notrial.debug'
        ),
    },
    PLUS_SWEET_HOME_REGISTERED_CLIENTS={
        'taxi': [{'client_id': 'taxi.test', 'platform': 'ios'}],
    },
)
@pytest.mark.parametrize(
    'plus_context, status_code, stq_id, cnt_stq_call, stq_args',
    [
        (
            '%3Fevent%3Dcatching_up_cashback%26order_id%3Ddefault_order',
            200,
            'default_order',
            1,
            {
                'order_id': 'default_order',
                'subscription_purchase_id': '1000',
                'yandex_uid': 'user_plus_context',
                'event': 'catching_up_cashback',
            },
        ),
        (
            '?event=catching_up_cashback&order_id=default_order',
            200,
            'default_order',
            1,
            {
                'order_id': 'default_order',
                'subscription_purchase_id': '1000',
                'yandex_uid': 'user_plus_context',
                'event': 'catching_up_cashback',
            },
        ),
        ('?event=catching_up_cashback', 400, None, 0, None),
        ('?event=unknown_event&order_id=default_order_id', 200, None, 0, None),
        ('oeorngoels', 400, None, 0, None),
        ('$$PUSRCHASE_PARAMETRS$$', 400, None, 0, None),
        ('$$PUSRCHASE_PARAMETRS$$=', 200, None, 0, None),
        ('$$PUSRCHASE_PARAMETRS$$&=', 400, None, 0, None),
        ('$$PUSRCHASE_PARAMETRS$$=&fsdmflsdf=fkrme', 200, None, 0, None),
    ],
)
async def test_purchase_with_plus_context(
        taxi_plus_sweet_home,
        mockserver,
        stq,
        plus_context,
        status_code,
        stq_id,
        cnt_stq_call,
        stq_args,
):
    @mockserver.json_handler(
        '/mediabilling/internal-api/account/submit-native-order',
    )
    def _mock_submit_native_order(request):
        return {'result': {'status': 'success', 'orderId': 1000}}

    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v1/subscriptions/purchase',
        json={
            'subscription_id': 'ya_plus_rus_v2',
            'payment_method_id': 'method_id',
            'plus_context': plus_context,
        },
        headers=HEADERS,
    )

    assert response.status_code == status_code

    if status_code != 200:
        return

    content = response.json()
    assert content['purchase_id'] == '1000'

    assert (
        stq.plus_sweet_home_purchase_subscription_status.times_called
        == cnt_stq_call
    )
    if cnt_stq_call:
        stq_call = stq.plus_sweet_home_purchase_subscription_status.next_call()

        assert stq_call['id'] == stq_id

        stq_call_args = stq_call['kwargs']
        if 'log_extra' in stq_call_args:
            del stq_call_args['log_extra']
        assert stq_call['kwargs'] == stq_args
