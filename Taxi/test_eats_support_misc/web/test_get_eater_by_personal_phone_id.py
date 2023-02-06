import http
import typing

import pytest

from test_eats_support_misc import utils

EATER_PERSONAL_PHONE_ID = 'eater_personal_phone_id'
EATER_PHONE_NUMBER = '+72222222222'
EATER_ID = 'some_eater_id'
ACTIVE_ORDER_NR = '1111-2222'
COURIER_ID = '12345678'
COURIER_PHONE_NUMBER = '+73333333333'
COURIER_PERSONAL_PHONE_ID = 'courier_personal_phone_id'
RESTAURANT_ID = 123
RESTAURANT_PHONE_NUMBER = '+79999999999'
RESTAURANT_NAME = 'some_restaurant_name'
RESTAURANT_PERSONAL_PHONE_ID = 'restaurant_personal_phone_id'
BRAND_ID = 999

DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER: typing.Dict[str, typing.Any] = {
    'type': 'customer',
    'has_more_than_one_active_order': False,
    'active_order': {
        'order_number': ACTIVE_ORDER_NR,
        'customer_application_type': 'app',
        'is_asap': False,
        'is_cancel_available': True,
        'status': 'taken',
        'delivery': {
            'delivery_type': 'native',
            'is_delaying': False,
            'courier': {'phone_number': COURIER_PHONE_NUMBER},
            'delivery_time': '2021-01-01T01:00:00+03:00',
            'eta': 40,
        },
        'restaurant': {
            'id': RESTAURANT_ID,
            'is_fastfood': False,
            'delivery_type': 'native',
            'phone_number': RESTAURANT_PHONE_NUMBER,
            'integration_type': 'vendor',
            'is_brand_escaping': False,
            'brand_id': str(BRAND_ID),
            'extra': {},
        },
        'courier_phone_number': COURIER_PHONE_NUMBER,
    },
}

DEFAULT_EATER_IVR_INFO_WITHOUT_ACTIVE_ORDER = {
    'type': 'customer',
    'has_more_than_one_active_order': False,
    'active_order': None,
}

DEFAULT_ACTIVE_ORDER_META = {
    'eater_id': EATER_ID,
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

DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE = {
    'eaters': [
        {
            'id': EATER_ID,
            'uuid': 'some_eater_uuid',
            'created_at': '2018-01-01T00:10:00+03:00',
            'updated_at': '2019-01-01T00:10:00+03:00',
        },
    ],
    'pagination': {'limit': 1, 'has_more': False},
}

DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER = {
    'eater_id': EATER_ID,
    'has_more_than_one_active_order': False,
}

DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER = {
    'eater_id': EATER_ID,
    'has_more_than_one_active_order': False,
    'active_order': {
        'order_id': ACTIVE_ORDER_NR,
        'caller_role': 'client',
        'order_city': 'Moscow',
        'order_status': 'order_taken',
        'delivery_type': 'native',
        'delivery_class': 'regular',
        'client_id': EATER_ID,
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

DEFAULT_RESPONSE_WITH_ERROR_ORDER_META = {
    'eater_id': EATER_ID,
    'has_more_than_one_active_order': False,
    'active_order': {
        'order_id': ACTIVE_ORDER_NR,
        'caller_role': 'client',
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
        mock_get_order_meta,
        mock_get_personal_id_by_value,
        mock_brands_find_by_id,
        mock_couriers_core_find_by_id,
        mock_eats_eaters_find_eaters_by_phone_id,
):
    mock_get_personal_data_value_by_id(
        personal_data_id=EATER_PERSONAL_PHONE_ID,
        data_type='phones',
        personal_data_value=EATER_PHONE_NUMBER,
    )

    mock_get_ivr_info(
        channel='customer',
        phone_number=EATER_PHONE_NUMBER,
        ivr_info=DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
    )

    mock_get_order_meta(
        order_nr=ACTIVE_ORDER_NR, order_meta=DEFAULT_ACTIVE_ORDER_META,
    )

    mock_get_personal_id_by_value(
        data_type='phones',
        relation_dict={
            RESTAURANT_PHONE_NUMBER: RESTAURANT_PERSONAL_PHONE_ID,
            COURIER_PHONE_NUMBER: COURIER_PERSONAL_PHONE_ID,
        },
    )

    mock_brands_find_by_id(
        brand_id=BRAND_ID, brand_info=DEFAULT_FIND_BRAND_RESPONSE,
    )

    mock_couriers_core_find_by_id(
        courier_id=COURIER_ID, courier_info=DEFAULT_COURIER_INFO,
    )

    mock_eats_eaters_find_eaters_by_phone_id(
        personal_phone_id=EATER_PERSONAL_PHONE_ID,
        list_of_eaters_info=DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE,
    )


@pytest.mark.now('2021-01-01T00:30:00+03:00')
@pytest.mark.parametrize(
    (
        'ivr_info',
        'order_meta',
        'brand_info',
        'courier_info_by_id',
        'eater_by_phone_id',
        'expected_result',
    ),
    [
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE,
            DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
            id='full_active_order',
        ),
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITHOUT_ACTIVE_ORDER,
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE,
            DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER,
            id='eater_without_active_order',
        ),
        pytest.param(
            dict(
                DEFAULT_EATER_IVR_INFO_WITHOUT_ACTIVE_ORDER,
                has_more_than_one_active_order=True,
            ),
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE,
            dict(
                DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER,
                has_more_than_one_active_order=True,
            ),
            id='has_more_than_one_active_order=True',
        ),
        pytest.param(
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
                update_items={'active_order.restaurant.brand_id': None},
            ),
            utils.get_dict_copy_with_edit_items(
                DEFAULT_ACTIVE_ORDER_META, deleted_keys=['brand_id'],
            ),
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE,
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
                DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
                update_items={'active_order.restaurant.delivery_type': 'both'},
            ),
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE,
            DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
            id='active_order_ivr_info_bad_delivery_type',
        ),
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_ACTIVE_ORDER_META,
                update_items={'delivery_type': 'marketplace'},
            ),
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                update_items={'active_order.delivery_type': 'marketplace'},
            ),
            id='active_order_marketplace_delivery_type',
        ),
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_ACTIVE_ORDER_META,
                update_items={'delivery_type': 'pickup'},
            ),
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                update_items={'active_order.is_pickup': True},
            ),
            id='active_order_is_pickup_delivery_type',
        ),
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_ACTIVE_ORDER_META,
                update_items={
                    'order_promised_at': '2021-01-01T00:29:00+03:00',
                },
            ),
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            DEFAULT_FIND_EATER_BY_PHONE_ID_RESPONSE,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                update_items={
                    'active_order.is_delaying': True,
                    'active_order.delivery_eta': '2021-01-01T00:29:00+03:00',
                },
            ),
            id='active_order_is_delaying_True',
        ),
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITHOUT_ACTIVE_ORDER,
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            {
                'eaters': [
                    {
                        'id': 'wrong_eater_id_1',
                        'uuid': 'some_eater_uuid_1',
                        'created_at': '2018-01-01T00:10:00+03:00',
                        'updated_at': '2019-01-01T00:10:00+03:00',
                    },
                    {
                        'id': EATER_ID,
                        'uuid': 'some_eater_uuid',
                        'created_at': '2019-01-01T00:10:00+03:00',
                        'updated_at': '2020-01-01T00:10:00+03:00',
                    },
                ],
                'pagination': {'limit': 2, 'has_more': False},
            },
            DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER,
            id='multiple_eater_accounts_without_login',
        ),
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITHOUT_ACTIVE_ORDER,
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            {
                'eaters': [
                    {
                        'id': 'wrong_eater_id_1',
                        'uuid': 'some_eater_uuid_1',
                        'created_at': '2019-01-01T00:10:00+03:00',
                        'updated_at': '2020-01-01T00:10:00+03:00',
                    },
                    {
                        'id': EATER_ID,
                        'uuid': 'some_eater_uuid',
                        'created_at': '2018-01-01T00:10:00+03:00',
                        'updated_at': '2019-01-01T00:10:00+03:00',
                        'last_login': '2020-06-01T00:10:00+03:00',
                    },
                ],
                'pagination': {'limit': 2, 'has_more': False},
            },
            DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER,
            id='multiple_eater_accounts_single_login',
        ),
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITHOUT_ACTIVE_ORDER,
            DEFAULT_ACTIVE_ORDER_META,
            DEFAULT_FIND_BRAND_RESPONSE,
            DEFAULT_COURIER_INFO,
            {
                'eaters': [
                    {
                        'id': 'wrong_eater_id_1',
                        'uuid': 'some_eater_uuid_1',
                        'created_at': '2019-01-01T00:10:00+03:00',
                        'updated_at': '2020-01-01T00:10:00+03:00',
                        'last_login': '2019-06-01T00:10:00+03:00',
                    },
                    {
                        'id': EATER_ID,
                        'uuid': 'some_eater_uuid',
                        'created_at': '2018-01-01T00:10:00+03:00',
                        'updated_at': '2019-01-01T00:10:00+03:00',
                        'last_login': '2020-06-01T00:10:00+03:00',
                    },
                ],
                'pagination': {'limit': 2, 'has_more': False},
            },
            DEFAULT_EXPECTED_RESPONSE_WITHOUT_ACTIVE_ORDER,
            id='multiple_eater_accounts_logins',
        ),
    ],
)
async def test_green_flow(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        mock_get_personal_data_value_by_id,
        mock_get_ivr_info,
        mock_get_order_meta,
        mock_get_personal_id_by_value,
        mock_brands_find_by_id,
        mock_eats_eaters_find_eaters_by_phone_id,
        mock_couriers_core_find_by_id,
        # ---- parameters ----
        ivr_info,
        order_meta,
        brand_info,
        courier_info_by_id,
        eater_by_phone_id,
        expected_result,
):
    mock_get_personal_data_value_by_id(
        personal_data_id=EATER_PERSONAL_PHONE_ID,
        data_type='phones',
        personal_data_value=EATER_PHONE_NUMBER,
    )

    mock_get_ivr_info(
        channel='customer', phone_number=EATER_PHONE_NUMBER, ivr_info=ivr_info,
    )

    mock_get_order_meta(order_nr=ACTIVE_ORDER_NR, order_meta=order_meta)

    mock_get_personal_id_by_value(
        data_type='phones',
        relation_dict={
            RESTAURANT_PHONE_NUMBER: RESTAURANT_PERSONAL_PHONE_ID,
            COURIER_PHONE_NUMBER: COURIER_PERSONAL_PHONE_ID,
        },
    )

    mock_brands_find_by_id(brand_id=BRAND_ID, brand_info=brand_info)

    mock_eats_eaters_find_eaters_by_phone_id(
        personal_phone_id=EATER_PERSONAL_PHONE_ID,
        list_of_eaters_info=eater_by_phone_id,
    )

    mock_couriers_core_find_by_id(
        courier_id=COURIER_ID, courier_info=courier_info_by_id,
    )
    response = await taxi_eats_support_misc_web.get(
        '/v1/eater-by-personal-phone-id',
        params={'personal_phone_id': EATER_PERSONAL_PHONE_ID},
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
async def test_error_get_eater_pd_phone_id(
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
        '/v1/eater-by-personal-phone-id',
        params={'personal_phone_id': EATER_PERSONAL_PHONE_ID},
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
                    'Exception occurred during search eater by '
                    'personal phone id: '
                    'Not defined in schema eats-core-integration-ivr '
                    'response, status: 500, body: b\'{}\''
                ),
            },
        ),
    ],
)
async def test_error_get_eater_info_from_ivr_info(
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
        '/v1/eater-by-personal-phone-id',
        params={'personal_phone_id': EATER_PERSONAL_PHONE_ID},
    )

    assert response.status == expected_status
    result = await response.json()
    assert result == expected_result


@pytest.mark.parametrize(
    (
        'find_eater_by_phone_status',
        'find_eater_by_phone_result',
        'expected_status',
    ),
    [
        pytest.param(http.HTTPStatus.OK, [], http.HTTPStatus.NOT_FOUND),
        pytest.param(
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            [],
            http.HTTPStatus.NOT_FOUND,
        ),
    ],
)
async def test_error_find_eater_by_phone(
        # ---- fixtures ----
        taxi_eats_support_misc_web,
        _default_mock_requests,
        mock_fail_to_get_ivr_info,
        mock_eats_eaters_find_eaters_by_phone_id,
        # ---- parameters ----
        find_eater_by_phone_status,
        expected_status,
        find_eater_by_phone_result,
):
    mock_fail_to_get_ivr_info(status=http.HTTPStatus.NOT_FOUND)

    mock_eats_eaters_find_eaters_by_phone_id(
        personal_phone_id=EATER_PERSONAL_PHONE_ID,
        list_of_eaters_info=find_eater_by_phone_result,
        status=find_eater_by_phone_status,
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/eater-by-personal-phone-id',
        params={'personal_phone_id': EATER_PERSONAL_PHONE_ID},
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    ('ivr_info', 'get_order_meta_status', 'expected_result'),
    [
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
            http.HTTPStatus.NOT_FOUND,
            DEFAULT_RESPONSE_WITH_ERROR_ORDER_META,
            id='order_meta_404',
        ),
        pytest.param(
            DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            DEFAULT_RESPONSE_WITH_ERROR_ORDER_META,
            id='order_meta_500',
        ),
        pytest.param(
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EATER_IVR_INFO_WITH_ACTIVE_ORDER,
                update_items={'active_order.restaurant.delivery_type': 'both'},
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
        channel='customer', phone_number=EATER_PHONE_NUMBER, ivr_info=ivr_info,
    )

    mock_fail_to_get_order_meta(status=get_order_meta_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/eater-by-personal-phone-id',
        params={'personal_phone_id': EATER_PERSONAL_PHONE_ID},
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
        '/v1/eater-by-personal-phone-id',
        params={'personal_phone_id': EATER_PERSONAL_PHONE_ID},
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
                deleted_keys=[
                    'active_order.courier_type',
                    'active_order.courier_personal_phone_id',
                ],
            ),
        ),
        pytest.param(
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=[
                    'active_order.courier_type',
                    'active_order.courier_personal_phone_id',
                ],
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
        '/v1/eater-by-personal-phone-id',
        params={'personal_phone_id': EATER_PERSONAL_PHONE_ID},
    )

    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert result == expected_result


@pytest.mark.now('2021-01-01T00:30:00+03:00')
@pytest.mark.parametrize(
    (
        'restaurant_personal_response',
        'courier_personal_response',
        'expected_result',
    ),
    [
        pytest.param(
            {
                'status': http.HTTPStatus.NOT_FOUND,
                'error_code': 'some_error_code',
                'error_message': 'some_error_message',
            },
            COURIER_PERSONAL_PHONE_ID,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['active_order.partner_personal_phone_id'],
            ),
        ),
        pytest.param(
            {
                'status': http.HTTPStatus.INTERNAL_SERVER_ERROR,
                'error_code': 'some_error_code',
                'error_message': 'some_error_message',
            },
            COURIER_PERSONAL_PHONE_ID,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['active_order.partner_personal_phone_id'],
            ),
        ),
        pytest.param(
            RESTAURANT_PERSONAL_PHONE_ID,
            {
                'status': http.HTTPStatus.NOT_FOUND,
                'error_code': 'some_error_code',
                'error_message': 'some_error_message',
            },
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['active_order.courier_personal_phone_id'],
            ),
        ),
        pytest.param(
            RESTAURANT_PERSONAL_PHONE_ID,
            {
                'status': http.HTTPStatus.NOT_FOUND,
                'error_code': 'some_error_code',
                'error_message': 'some_error_message',
            },
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_RESPONSE_WITH_ACTIVE_ORDER,
                deleted_keys=['active_order.courier_personal_phone_id'],
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
        restaurant_personal_response,
        courier_personal_response,
        expected_result,
):
    mock_get_personal_id_by_value(
        data_type='phones',
        relation_dict={
            RESTAURANT_PHONE_NUMBER: restaurant_personal_response,
            COURIER_PHONE_NUMBER: courier_personal_response,
        },
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/eater-by-personal-phone-id',
        params={'personal_phone_id': EATER_PERSONAL_PHONE_ID},
    )

    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert result == expected_result
