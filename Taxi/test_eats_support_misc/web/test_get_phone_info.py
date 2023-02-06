import pytest


PHONE_ID = 'some_phone_id'
PHONE_NUMBER = '+70000000000'
ORDER_NR = '220428-000001'

ORDER_META = {
    'eater_id': 'some_id',
    'eater_name': 'Alice',
    'eater_decency': 'good',
    'is_first_order': True,
    'is_blocked_user': False,
    'order_status': 'order_taken',
    'order_type': 'native',
    'delivery_type': 'our_delivery',
    'delivery_class': 'regular',
    'is_fast_food': False,
    'app_type': 'eats',
    'country_code': 'RU',
    'country_label': 'Russia',
    'city_label': 'Moscow',
    'order_created_at': '2021-01-01T01:00:00+03:00',
    'order_promised_at': '2021-01-01T01:00:00+03:00',
    'is_surge': False,
    'is_option_leave_under_door_selected': False,
    'is_promocode_used': False,
    'persons_count': 1,
    'payment_method': 'card',
    'order_total_amount': 150.15,
    'place_id': '10',
    'place_name': 'some_place_name',
    'is_sent_to_restapp': False,
    'is_sent_to_integration': True,
    'integration_type': 'native',
    'courier_id': '1',
}

COURIER_IVR_INFO_WITH_ACTIVE_ORDER = {
    'type': 'courier',
    'has_more_than_one_active_order': False,
    'active_order_nr': ORDER_NR,
    'customer_phone_number': '+79999999999',
    'restaurant': {
        'id': 1,
        'is_fastfood': False,
        'delivery_type': 'native',
        'phone_number': '+79123456789',
        'integration_type': 'vendor',
        'is_brand_escaping': True,
        'brand_id': None,
    },
    'region': {'id': 1, 'name': 'region'},
    'has_ultima_order': False,
}


@pytest.mark.parametrize(
    ('response_status', 'error_code', 'error_message', 'expected_response'),
    [
        (
            404,
            '404',
            'No document with such id',
            {'code': '404', 'message': 'No document with such id'},
        ),
    ],
)
async def test_fail_to_retrieve_phone_number_by_phone_id(
        # ---- fixtures ----
        mock_fail_to_get_personal_data_value_by_id,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        response_status,
        error_code,
        error_message,
        expected_response,
):
    mock_fail_to_get_personal_data_value_by_id(
        'phones', response_status, error_code, error_message,
    )
    response = await taxi_eats_support_misc_web.get(
        '/v1/phone-info', params={'personal_phone_id': PHONE_ID},
    )

    assert response.status == 404
    data = await response.json()
    assert data == expected_response


@pytest.mark.parametrize(
    ('order_nr', 'courier_info', 'order_meta', 'expected_response'),
    [
        (
            ORDER_NR,
            COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
            ORDER_META,
            {
                'active_order': {
                    'brand_id': 'undefined',
                    'business_type': 'undefined',
                    'caller_role': 'courier',
                    'client_application': 'eats',
                    'client_id': 'some_id',
                    'courier_id': '1',
                    'delivery_eta': '2021-01-01T01:00:00+03:00',
                    'delivery_type': 'native',
                    'delivery_class': 'regular',
                    'is_delaying': True,
                    'order_city': 'Moscow',
                    'order_id': '220428-000001',
                    'order_status': 'order_taken',
                    'partner_id': '10',
                    'partner_name': 'some_place_name',
                },
                'courier_id': '1',
                'has_more_than_one_active_order': False,
                'has_ultima_order': False,
            },
        ),
    ],
)
async def test_green_flow_courier(
        # ---- fixtures ----
        mock_get_personal_data_value_by_id,
        mock_get_ivr_info,
        mock_get_order_meta,
        web_app_client,
        # ---- parameters ----
        order_nr,
        order_meta,
        courier_info,
        expected_response,
):
    mock_get_personal_data_value_by_id(PHONE_ID, 'phones', PHONE_NUMBER)
    mock_get_ivr_info('courier', PHONE_NUMBER, courier_info)
    mock_get_order_meta(order_nr, order_meta)

    response = await web_app_client.get(
        '/v1/phone-info', params={'personal_phone_id': PHONE_ID},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response
