# pylint: disable=redefined-builtin, invalid-name
import typing

import pytest

YANDEX_UID_1 = 'yandex_uid__1'

ORDER_1 = 'order_uuid__1'
PRODUCT_1 = 'product_id__1'


def _make_item(id, quantity):
    return {'id': id, 'quantity': quantity}


def _make_request_data(order_uuid, *order_items):
    return {'order_uuid': order_uuid, 'order_items': list(order_items)}


def _make_request_headers(
        yandex_uid: typing.Optional[str] = YANDEX_UID_1, phone_id='PHONE_ID_1',
):
    result = {'x-eats-user': f'personal_phone_id={phone_id}'}
    if yandex_uid:
        result['x-yandex-uid'] = yandex_uid
    return result


PAY_METHOD_CASH = {'pay_type': 'cash'}
PAY_METHOD_PAYTURE = {'pay_type': 'payture'}
PAY_METHOD_CARD = {
    'id': 'card-x66b88c90fc8d571e6d5e9715',
    'name': 'unknown',
    'pay_type': 'trust_card',
    'short_title': '****0000',
    'system': 'unknown',
    'card_linking_needed': False,
}
PAY_METHOD_SBP = {'pay_type': 'sbp'}
PAY_METHOD_BADGE = {
    'card_linking_needed': False,
    'id': 'badge:yandex_badge:RUB',
    'name': 'Yandex Badge',
    'pay_type': 'badge',
}
PAY_METHOD_CORP = {
    'card_linking_needed': False,
    'id': 'corp:61a7f66f3bc44cf2a8e2a32c8326abf0:RUB',
    'name': 'ООО СОЦ-Информ',
    'pay_type': 'corp',
}
PAY_METHOD_B2B_CORP = {
    'card_linking_needed': False,
    'id': 'test',
    'name': 'Test',
    'pay_type': 'b2b_corp',
    'linked_card': {'id': 'test', 'number': '1234', 'system': 'visa'},
}


def _make_expected_response(*pay_methods):
    return {'pay_methods': list(pay_methods)}


def _make_corp_orders_response(
        is_payment_possible=True, payment_impossible_reason=None,
):
    result = {
        'is_payment_possible': is_payment_possible,
        'card': {
            'id': 'test',
            'type': 'card',
            'number': '1234',
            'system': 'visa',
        },
        'corp': {'id': 'test', 'type': 'corp', 'name': 'Test'},
    }
    if payment_impossible_reason is not None:
        result['payment_impossible_reason'] = payment_impossible_reason
    return result


def _make_pytest_param(
        id,
        request_data,
        request_headers,
        expected_response,
        payment_offline=True,
        expected_status=200,
        expected_item_set_len=2,
        corp_orders_response=None,
):
    return pytest.param(
        request_headers,
        request_data,
        corp_orders_response or _make_corp_orders_response(),
        expected_item_set_len,
        payment_offline,
        expected_status,
        expected_response,
        id=id,
    )


def _sorted_pay_methods(data):
    if 'pay_methods' in data:
        data['pay_methods'] = sorted(
            data['pay_methods'],
            key=lambda value: (value['pay_type'], value.get('id', '')),
        )
    return data


@pytest.mark.parametrize(
    'request_headers,'
    'request_data,'
    'corp_orders_response,'
    'expected_item_set_len,'
    'payment_offline,'
    'expected_status,'
    'expected_response,',
    [
        _make_pytest_param(
            id='success',
            request_headers=_make_request_headers(),
            request_data=_make_request_data(ORDER_1),
            expected_response=_make_expected_response(
                PAY_METHOD_CASH,
                PAY_METHOD_CARD,
                PAY_METHOD_BADGE,
                PAY_METHOD_CORP,
                PAY_METHOD_SBP,
                PAY_METHOD_B2B_CORP,
            ),
        ),
        _make_pytest_param(
            id='success no cash',
            request_headers=_make_request_headers(),
            request_data=_make_request_data(ORDER_1),
            expected_response=_make_expected_response(
                PAY_METHOD_CARD,
                PAY_METHOD_BADGE,
                PAY_METHOD_CORP,
                PAY_METHOD_SBP,
                PAY_METHOD_B2B_CORP,
            ),
            payment_offline=False,
        ),
        _make_pytest_param(
            id='not authorized',
            request_headers=_make_request_headers(yandex_uid=None),
            request_data=_make_request_data(ORDER_1),
            expected_response=_make_expected_response(
                PAY_METHOD_CASH, PAY_METHOD_PAYTURE, PAY_METHOD_SBP,
            ),
        ),
        _make_pytest_param(
            id='not authorized no cash',
            request_headers=_make_request_headers(yandex_uid=None),
            request_data=_make_request_data(ORDER_1),
            expected_response=_make_expected_response(
                PAY_METHOD_PAYTURE, PAY_METHOD_SBP,
            ),
            payment_offline=False,
        ),
        _make_pytest_param(
            id='partial order',
            request_headers=_make_request_headers(),
            request_data=_make_request_data(ORDER_1, _make_item(PRODUCT_1, 1)),
            expected_response=_make_expected_response(
                PAY_METHOD_CASH,
                PAY_METHOD_CARD,
                PAY_METHOD_BADGE,
                PAY_METHOD_CORP,
                PAY_METHOD_SBP,
                PAY_METHOD_B2B_CORP,
            ),
            expected_item_set_len=1,
        ),
        _make_pytest_param(
            id='order is not found',
            request_headers=_make_request_headers(),
            request_data=_make_request_data(
                'fake_uuid', _make_item(PRODUCT_1, 1),
            ),
            expected_status=404,
            expected_response={
                'code': 'ORDER_IS_NOT_FOUND',
                'message': 'Order is not found',
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'restaurants_options.sql',
        'tables.sql',
        'orders.sql',
    ],
)
@pytest.mark.client_experiments3(
    consumer='eats-integration-offline-orders/enabled-payments-methods',
    config_name='eats_integration_offline_orders-enabled_payments_methods',
    args=[
        {'name': 'place_id', 'type': 'string', 'value': 'place_id__1'},
        {'name': 'yandex_uid', 'type': 'string', 'value': YANDEX_UID_1},
    ],
    value={'enabled_methods': ['trust_card', 'corp', 'badge', 'b2b_corp']},
)
@pytest.mark.config(
    EI_OFFLINE_ORDERS_USE_EATS_CORP_ORDERS_BY_PLACE={'__default__': True},
    EI_OFFLINE_ORDERS_PAY_METHOD_SETTINGS={'include_cash': True},
)
async def test_pay_available_methods_post(
        web_app_client,
        web_context,
        pgsql,
        mock_eats_payment_methods_availability,
        mock_eats_corp_orders,
        epma_v1_payment_methods_availability_response,
        # params:
        request_headers,
        request_data,
        corp_orders_response,
        expected_item_set_len,
        payment_offline,
        expected_status,
        expected_response,
):
    @mock_eats_payment_methods_availability('/v1/payment-methods/availability')
    async def _mock_v1_payment_methods_availability(request):
        assert request.json['destination_point'] == [39.022872, 45.056503]
        assert request.json['region_id'] == 13
        assert (
            len(request.json['order_info']['item_sets'])
            == expected_item_set_len
        )
        return epma_v1_payment_methods_availability_response

    @mock_eats_corp_orders('/v1/payment-method/get-verified')
    async def _mock_get_verified(request):
        return corp_orders_response

    cursor = pgsql['eats_integration_offline_orders'].cursor()
    cursor.execute(
        f"""
UPDATE restaurants_options
SET payment_offline={payment_offline}
WHERE place_id='place_id__1'
        """,
    )

    response = await web_app_client.post(
        '/v1/pay/available-methods',
        headers=request_headers,
        json=request_data,
    )
    assert response.status == expected_status
    response_data = await response.json()
    assert _sorted_pay_methods(response_data) == _sorted_pay_methods(
        expected_response,
    )
