import http
import typing

import pytest

from test_eats_support_misc import utils

COURIER_PERSONAL_PHONE_ID = 'courier_personal_phone_id'
COURIER_PHONE_NUMBER = '+72222222222'
COURIER_ID = '12345678'
COURIER_CITY = 'Moscow'
ACTIVE_ORDER_NR = '1111-2222'
RESTAURANT_ID = 123
RESTAURANT_NAME = 'some_restaurant_name'
RESTAURANT_PHONE_NUMBER = '+79999999999'
RESTAURANT_PERSONAL_PHONE_ID = 'restaurant_personal_phone_id'
BRAND_ID = 999

DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER: typing.Dict[str, typing.Any] = {
    'type': 'courier',
    'has_more_than_one_active_order': False,
    'active_order_nr': ACTIVE_ORDER_NR,
    'customer_phone_number': '+71111111111',
    'restaurant': {
        'id': RESTAURANT_ID,
        'is_fastfood': False,
        'delivery_type': 'native',
        'phone_number': RESTAURANT_PHONE_NUMBER,
        'integration_type': 'vendor',
        'is_brand_escaping': False,
        'brand_id': str(BRAND_ID),
    },
    'region': {'id': 7, 'name': 'Moscow'},
}

DEFAULT_COURIER_IVR_INFO_WITHOUT_ACTIVE_ORDER = {
    'type': 'courier',
    'has_more_than_one_active_order': False,
    'active_order_nr': None,
    'customer_phone_number': None,
    'restaurant': None,
    'region': {'id': 7, 'name': COURIER_CITY},
}

DEFAULT_ACTIVE_ORDER_META = {
    'eater_id': 'some_eater_id',
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
    'order_created_at': '2021-01-01T00:10:00+03:00',
    'order_promised_at': '2021-01-01T01:00:00+03:00',
    'is_surge': False,
    'is_option_leave_under_door_selected': False,
    'is_promocode_used': False,
    'persons_count': 1,
    'payment_method': 'card',
    'order_total_amount': 150.15,
    'place_id': str(RESTAURANT_ID),
    'place_name': RESTAURANT_NAME,
    'is_sent_to_restapp': False,
    'is_sent_to_integration': True,
    'integration_type': 'native',
    'courier_id': COURIER_ID,
    'brand_id': str(BRAND_ID),
}

DEFAULT_FIND_BRAND_RESPONSE = {
    'brand': {
        'id': BRAND_ID,
        'name': 'some_brand_name',
        'business_type': 'shop',
    },
}

DEFAULT_COURIER_INFO = {
    'courier': {
        'id': int(COURIER_ID),
        'first_name': 'some_courier_first_name',
        'last_name': 'some_courier_last_name',
        'phone_number': COURIER_PHONE_NUMBER,
        'billing_type': 'card',
        'courier_type': 'bicycle',
        'registration_country': {'name': 'Russian', 'code': 'ru'},
        'work_region': {'id': 7, 'name': 'Moscow'},
        'work_status': 'active',
        'work_status_updated_at': '2020-01-01T00:10:00+03:00',
    },
}

DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER = {
    'courier_id': COURIER_ID,
    'courier_city': COURIER_CITY,
    'has_more_than_one_active_order': False,
    'active_order': {
        'order_id': ACTIVE_ORDER_NR,
        'caller_role': 'courier',
        'order_city': 'Moscow',
        'order_status': 'order_taken',
        'delivery_type': 'native',
        'delivery_class': 'regular',
        'client_id': 'some_eater_id',
        'client_application': 'eats',
        'courier_id': COURIER_ID,
        'courier_type': 'bicycle',
        'courier_personal_phone_id': COURIER_PERSONAL_PHONE_ID,
        'partner_id': str(RESTAURANT_ID),
        'partner_name': RESTAURANT_NAME,
        'partner_personal_phone_id': RESTAURANT_PERSONAL_PHONE_ID,
        'brand_id': str(BRAND_ID),
        'business_type': 'shop',
        'delivery_eta': '2021-01-01T01:00:00+03:00',
        'is_pickup': False,
        'is_delaying': False,
    },
}

DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER = {
    'courier_id': COURIER_ID,
    'courier_city': COURIER_CITY,
    'has_more_than_one_active_order': False,
}

DEFAULT_FIND_COURIER_BY_PHONE = {'couriers': [DEFAULT_COURIER_INFO['courier']]}

DEFAULT_RESPONSE_WITH_ERROR_ORDER_META = {
    'courier_id': COURIER_ID,
    'courier_city': COURIER_CITY,
    'has_more_than_one_active_order': False,
    'active_order': {
        'order_id': ACTIVE_ORDER_NR,
        'caller_role': 'courier',
        'delivery_type': 'native',
        'partner_id': str(RESTAURANT_ID),
        'partner_name': 'undefined',
        'brand_id': str(BRAND_ID),
        'partner_personal_phone_id': RESTAURANT_PERSONAL_PHONE_ID,
        'order_city': 'undefined',
        'client_id': 'undefined',
        'business_type': 'shop',
        'is_pickup': False,
        'is_delaying': False,
    },
}


@pytest.fixture
def _default_mock_requests(
        mock_get_personal_data_value_by_id,
        mock_get_ivr_info,
        mock_couriers_core_find_by_phone,
        mock_get_personal_id_by_value,
        mock_get_order_meta,
        mock_brands_find_by_id,
        mock_couriers_core_find_by_id,
):
    mock_get_personal_data_value_by_id(
        personal_data_id=COURIER_PERSONAL_PHONE_ID,
        data_type='phones',
        personal_data_value=COURIER_PHONE_NUMBER,
    )

    mock_get_ivr_info(
        channel='courier',
        phone_number=COURIER_PHONE_NUMBER,
        ivr_info=DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
    )

    mock_couriers_core_find_by_phone(
        courier_phone=COURIER_PHONE_NUMBER,
        courier_info=DEFAULT_FIND_COURIER_BY_PHONE,
    )

    mock_get_personal_id_by_value(
        data_type='phones',
        relation_dict={RESTAURANT_PHONE_NUMBER: RESTAURANT_PERSONAL_PHONE_ID},
    )

    mock_get_order_meta(
        order_nr=ACTIVE_ORDER_NR, order_meta=DEFAULT_ACTIVE_ORDER_META,
    )

    mock_brands_find_by_id(
        brand_id=BRAND_ID, brand_info=DEFAULT_FIND_BRAND_RESPONSE,
    )

    mock_couriers_core_find_by_id(
        courier_id=COURIER_ID, courier_info=DEFAULT_COURIER_INFO,
    )


@pytest.mark.now('2021-01-01T00:30:00+03:00')
@pytest.mark.parametrize(
    (
        'ivr_info',
        'order_meta',
        'brand_info',
        'courier_info_by_id',
        'courier_info_by_phone',
        'expected_result',
    ),
    [
        pytest.param(
            DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
            id='full_active_order',
        ),
        pytest.param(
            DEFAULT_COURIER_IVR_INFO_WITHOUT_ACTIVE_ORDER,
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER,
            id='courier_without_active_order',
        ),
        pytest.param(
            dict(DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER, restaurant=None),
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['active_order.partner_personal_phone_id'],
            ),
            id='active_order_ivr_info_restaurant_none',
        ),
        pytest.param(
            dict(DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER, restaurant=None),
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['active_order.partner_personal_phone_id'],
            ),
            id='active_order_ivr_info_restaurant_none',
        ),
        pytest.param(
            dict(
                DEFAULT_COURIER_IVR_INFO_WITHOUT_ACTIVE_ORDER,
                has_more_than_one_active_order=True,
            ),
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            dict(
                DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER,
                has_more_than_one_active_order=True,
            ),
            id='has_more_than_one_active_order=True',
        ),
        pytest.param(
            utils.get_dict_copy_with_edit_items(
                DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
                update_items={'restaurant.brand_id': None},
            ),
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
            id='active_order_ivr_info_none_brand_id',
        ),
        pytest.param(
            utils.get_dict_copy_with_edit_items(
                DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
                update_items={'restaurant.brand_id': None},
            ),
            utils.get_dict_copy_with_edit_items(
                DEFAULT_ACTIVE_ORDER_META, deleted_keys=['brand_id'],
            ),
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                update_items={
                    'active_order.brand_id': 'undefined',
                    'active_order.business_type': 'undefined',
                },
            ),
            id='active_order_empty_brand_info',
        ),
        pytest.param(
            utils.get_dict_copy_with_edit_items(
                DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
                update_items={'restaurant.delivery_type': 'both'},
            ),
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
            id='active_order_ivr_info_bad_delivery_type',
        ),
        pytest.param(
            DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_ACTIVE_ORDER_META,
                update_items={'delivery_type': 'marketplace'},
            ),
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                update_items={'active_order.delivery_type': 'marketplace'},
            ),
            id='active_order_marketplace_delivery_type',
        ),
        pytest.param(
            DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_ACTIVE_ORDER_META,
                update_items={'delivery_type': 'pickup'},
            ),
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                update_items={'active_order.is_pickup': True},
            ),
            id='active_order_is_pickup_delivery_type',
        ),
        pytest.param(
            DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_ACTIVE_ORDER_META,
                update_items={
                    'order_promised_at': '2021-01-01T00:29:00+03:00',
                },
            ),
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_COURIER_BY_PHONE,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                update_items={
                    'active_order.is_delaying': True,
                    'active_order.delivery_eta': '2021-01-01T00:29:00+03:00',
                },
            ),
            id='active_order_is_delaying_True',
        ),
    ],
)
async def test_green_flow(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        mock_get_personal_data_value_by_id,
        mock_get_personal_id_by_value,
        mock_get_ivr_info,
        mock_get_order_meta,
        mock_brands_find_by_id,
        mock_couriers_core_find_by_id,
        mock_couriers_core_find_by_phone,
        # ---- parameters ----
        ivr_info,
        order_meta,
        brand_info,
        courier_info_by_id,
        courier_info_by_phone,
        expected_result,
):
    mock_get_personal_data_value_by_id(
        personal_data_id=COURIER_PERSONAL_PHONE_ID,
        data_type='phones',
        personal_data_value=COURIER_PHONE_NUMBER,
    )

    mock_get_ivr_info(
        channel='courier',
        phone_number=COURIER_PHONE_NUMBER,
        ivr_info=ivr_info,
    )

    mock_get_order_meta(order_nr=ACTIVE_ORDER_NR, order_meta=order_meta)

    mock_get_personal_id_by_value(
        data_type='phones',
        relation_dict={RESTAURANT_PHONE_NUMBER: RESTAURANT_PERSONAL_PHONE_ID},
    )

    mock_brands_find_by_id(brand_id=BRAND_ID, brand_info=brand_info)

    mock_couriers_core_find_by_id(
        courier_id=COURIER_ID, courier_info=courier_info_by_id,
    )

    mock_couriers_core_find_by_phone(
        courier_phone=COURIER_PHONE_NUMBER, courier_info=courier_info_by_phone,
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-by-personal-phone-id',
        params={'personal_phone_id': COURIER_PERSONAL_PHONE_ID},
    )

    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert result == expected_result


@pytest.mark.parametrize(
    ('personal_status', 'expected_status'),
    [
        pytest.param(http.HTTPStatus.NOT_FOUND, http.HTTPStatus.NOT_FOUND),
        pytest.param(
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
        ),
    ],
)
async def test_error_get_courier_pd_phone_id(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        mock_fail_to_get_personal_data_value_by_id,
        # ---- parameters ----
        personal_status,
        expected_status,
):
    mock_fail_to_get_personal_data_value_by_id(
        data_type='phones',
        status=personal_status,
        error_code=str(personal_status),
        error_message='some_error_message',
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-by-personal-phone-id',
        params={'personal_phone_id': COURIER_PERSONAL_PHONE_ID},
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    ('ivr_info_status', 'expected_status', 'expected_result'),
    [
        pytest.param(
            http.HTTPStatus.NOT_FOUND,
            http.HTTPStatus.OK,
            DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER,
        ),
        pytest.param(
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            {
                'code': 'error_interacting_with_core',
                'message': (
                    'Exception occurred during search courier by '
                    'personal phone id: '
                    'Not defined in schema eats-core-integration-ivr '
                    'response, status: 500, body: b\'{}\''
                ),
            },
        ),
    ],
)
async def test_error_get_courier_info_from_ivr_info(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        _default_mock_requests,
        mock_fail_to_get_ivr_info,
        # ---- parameters ----
        ivr_info_status,
        expected_status,
        expected_result,
):
    mock_fail_to_get_ivr_info(status=ivr_info_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-by-personal-phone-id',
        params={'personal_phone_id': COURIER_PERSONAL_PHONE_ID},
    )

    assert response.status == expected_status
    result = await response.json()
    assert result == expected_result


@pytest.mark.parametrize(
    ('find_courier_by_phone_status', 'expected_status'),
    [
        pytest.param(http.HTTPStatus.BAD_REQUEST, http.HTTPStatus.NOT_FOUND),
        pytest.param(
            http.HTTPStatus.INTERNAL_SERVER_ERROR, http.HTTPStatus.NOT_FOUND,
        ),
    ],
)
async def test_error_find_courier_by_phone(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        _default_mock_requests,
        mock_fail_to_get_ivr_info,
        mock_fail_couriers_core_find_by_phone,
        # ---- parameters ----
        find_courier_by_phone_status,
        expected_status,
):
    mock_fail_to_get_ivr_info(status=http.HTTPStatus.NOT_FOUND)

    mock_fail_couriers_core_find_by_phone(
        status=find_courier_by_phone_status,
        error_domain='some_domain',
        error_code=find_courier_by_phone_status,
        error_message='some_message',
        errors={'error': ['error']},
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-by-personal-phone-id',
        params={'personal_phone_id': COURIER_PERSONAL_PHONE_ID},
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    ('ivr_info', 'get_order_meta_status', 'expected_result'),
    [
        pytest.param(
            DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
            http.HTTPStatus.NOT_FOUND,
            DEFAULT_RESPONSE_WITH_ERROR_ORDER_META,
            id='order_meta_404',
        ),
        pytest.param(
            DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            DEFAULT_RESPONSE_WITH_ERROR_ORDER_META,
            id='order_meta_500',
        ),
        pytest.param(
            utils.get_dict_copy_with_edit_items(
                DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
                update_items={'restaurant': None},
            ),
            http.HTTPStatus.NOT_FOUND,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_RESPONSE_WITH_ERROR_ORDER_META,
                update_items={
                    'active_order.delivery_type': 'undefined',
                    'active_order.partner_id': 'undefined',
                    'active_order.brand_id': 'undefined',
                    'active_order.business_type': 'undefined',
                },
                deleted_keys=['active_order.partner_personal_phone_id'],
            ),
            id='empty_ivr_info_restaurant',
        ),
        pytest.param(
            utils.get_dict_copy_with_edit_items(
                DEFAULT_COURIER_IVR_INFO_WITH_ACTIVE_ORDER,
                update_items={'restaurant.delivery_type': 'both'},
            ),
            http.HTTPStatus.NOT_FOUND,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_RESPONSE_WITH_ERROR_ORDER_META,
                update_items={'active_order.delivery_type': 'undefined'},
            ),
            id='bad_delivery_type_from_ivr_info',
        ),
    ],
)
async def test_error_get_order_meta(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        _default_mock_requests,
        mock_get_ivr_info,
        mock_fail_to_get_order_meta,
        # ---- parameters ----
        ivr_info,
        get_order_meta_status,
        expected_result,
):
    mock_get_ivr_info(
        channel='courier',
        phone_number=COURIER_PHONE_NUMBER,
        ivr_info=ivr_info,
    )

    mock_fail_to_get_order_meta(status=get_order_meta_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-by-personal-phone-id',
        params={'personal_phone_id': COURIER_PERSONAL_PHONE_ID},
    )

    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert result == expected_result


@pytest.mark.now('2021-01-01T00:30:00+03:00')
@pytest.mark.parametrize(
    ('get_brand_info_status', 'expected_result'),
    [
        pytest.param(
            http.HTTPStatus.NOT_FOUND,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                update_items={'active_order.business_type': 'undefined'},
            ),
        ),
        pytest.param(
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                update_items={'active_order.business_type': 'undefined'},
            ),
        ),
    ],
)
async def test_error_get_brand_info(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        _default_mock_requests,
        mock_fail_brands_find_by_id,
        # ---- parameters ----
        get_brand_info_status,
        expected_result,
):

    mock_fail_brands_find_by_id(
        status=get_brand_info_status,
        code='INTERNAL_ERROR',
        message='some_message',
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-by-personal-phone-id',
        params={'personal_phone_id': COURIER_PERSONAL_PHONE_ID},
    )

    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert result == expected_result


@pytest.mark.now('2021-01-01T00:30:00+03:00')
@pytest.mark.parametrize(
    ('find_courier_by_id_status', 'expected_result'),
    [
        pytest.param(
            http.HTTPStatus.NOT_FOUND,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['courier_city', 'active_order.courier_type'],
            ),
        ),
        pytest.param(
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['courier_city', 'active_order.courier_type'],
            ),
        ),
    ],
)
async def test_error_get_courier_info_by_id(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        _default_mock_requests,
        mock_fail_couriers_core_find_by_id,
        # ---- parameters ----
        find_courier_by_id_status,
        expected_result,
):
    mock_fail_couriers_core_find_by_id(
        courier_id=COURIER_ID,
        status=find_courier_by_id_status,
        error_domain='some_domain',
        error_code=find_courier_by_id_status,
        error_message='some_message',
        errors={'error': ['error']},
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-by-personal-phone-id',
        params={'personal_phone_id': COURIER_PERSONAL_PHONE_ID},
    )

    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert result == expected_result


@pytest.mark.now('2021-01-01T00:30:00+03:00')
@pytest.mark.parametrize(
    ('personal_get_id_by_data_status', 'expected_result'),
    [
        pytest.param(
            http.HTTPStatus.NOT_FOUND,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['active_order.partner_personal_phone_id'],
            ),
        ),
        pytest.param(
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['active_order.partner_personal_phone_id'],
            ),
        ),
    ],
)
async def test_error_personal_get_id_by_data(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        _default_mock_requests,
        mock_get_personal_id_by_value,
        # ---- parameters ----
        personal_get_id_by_data_status,
        expected_result,
):

    mock_get_personal_id_by_value(
        data_type='phones',
        relation_dict={
            RESTAURANT_PHONE_NUMBER: {
                'status': personal_get_id_by_data_status,
                'error_code': 'some_error_code',
                'error_message': 'some_error_message',
            },
        },
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-by-personal-phone-id',
        params={'personal_phone_id': COURIER_PERSONAL_PHONE_ID},
    )

    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert result == expected_result
