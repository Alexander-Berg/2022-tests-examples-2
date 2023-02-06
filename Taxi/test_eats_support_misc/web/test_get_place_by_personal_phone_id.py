# pylint: disable=protected-access
import typing

import pytest


PHONE_ID = 'some_phone_id'
PHONE_NUMBER = '+79123456789'
PLACE_ID = 10


DEFAULT_RESTAURANT_IVR_INFO = {
    'type': 'restaurant',
    'has_more_than_one_prepared_order': True,
    'prepared_order_nr': None,
    'restaurant': {
        'id': PLACE_ID,
        'is_fastfood': False,
        'delivery_type': 'both',
        'phone_number': PHONE_NUMBER,
        'integration_type': 'vendor',
        'is_brand_escaping': False,
        'brand_id': 'super_brand',
    },
    'courier': None,
}

DEFAULT_PLACE_INFO: typing.Dict[str, typing.Any] = {
    'id': PLACE_ID,
    'revision_id': 1,
    'updated_at': '2022-05-11T12:42:00+03:00',
}

DEFAULT_EXPECTED_DATA: typing.Dict[str, typing.Any] = {
    'place_id': str(PLACE_ID),
}


@pytest.fixture(autouse=True)
def _default_mock_requests(
        mock_get_personal_data_value_by_id,
        mock_get_ivr_info,
        mock_get_places_info,
):
    mock_get_personal_data_value_by_id(PHONE_ID, 'phones', PHONE_NUMBER)
    mock_get_ivr_info('restaurant', PHONE_NUMBER, DEFAULT_RESTAURANT_IVR_INFO)
    mock_get_places_info(
        [PLACE_ID],
        ['address', 'brand', 'business'],
        {'places': [DEFAULT_PLACE_INFO], 'not_found_place_ids': []},
    )


@pytest.mark.parametrize(
    ('place_info', 'expected_data'),
    [
        (DEFAULT_PLACE_INFO, DEFAULT_EXPECTED_DATA),
        (
            dict(
                DEFAULT_PLACE_INFO,
                brand={
                    'id': 1,
                    'name': 'super_brand',
                    'picture_scale_type': 'aspect_fit',
                    'slug': 'super',
                },
                address={'city': 'Moscow', 'short': 'Arbat, 1'},
                business='shop',
            ),
            dict(
                DEFAULT_EXPECTED_DATA,
                brand_id='1',
                place_city='Moscow',
                is_shop=True,
            ),
        ),
        (
            dict(DEFAULT_PLACE_INFO, business='pharmacy'),
            dict(DEFAULT_EXPECTED_DATA, is_shop=False),
        ),
    ],
)
async def test_green_flow(
        # ---- fixtures ----
        mock_get_personal_data_value_by_id,
        mock_get_ivr_info,
        mock_get_places_info,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        place_info,
        expected_data,
):
    mock_get_personal_data_value_by_id(PHONE_ID, 'phones', PHONE_NUMBER)
    mock_get_ivr_info('restaurant', PHONE_NUMBER, DEFAULT_RESTAURANT_IVR_INFO)
    mock_get_places_info(
        [PLACE_ID],
        ['address', 'brand', 'business'],
        {'places': [place_info], 'not_found_place_ids': []},
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/place-by-personal-phone-id',
        params={'personal_phone_id': PHONE_ID},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_data


async def test_empty_places_list(
        # ---- fixtures ----
        mock_get_personal_data_value_by_id,
        mock_get_ivr_info,
        mock_get_places_info,
        taxi_eats_support_misc_web,
):
    mock_get_personal_data_value_by_id(PHONE_ID, 'phones', PHONE_NUMBER)
    mock_get_ivr_info('restaurant', PHONE_NUMBER, DEFAULT_RESTAURANT_IVR_INFO)
    mock_get_places_info(
        [PLACE_ID],
        ['address', 'brand', 'business'],
        {'places': [], 'not_found_place_ids': [PLACE_ID]},
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/place-by-personal-phone-id',
        params={'personal_phone_id': PHONE_ID},
    )

    assert response.status == 200
    data = await response.json()
    assert data == {'place_id': str(PLACE_ID)}


@pytest.mark.parametrize(
    ('personal_response_status', 'expected_status'), [(404, 404), (500, 500)],
)
async def test_fail_to_get_phone_number_by_phone_id(
        # ---- fixtures ----
        mock_fail_to_get_personal_data_value_by_id,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        personal_response_status,
        expected_status,
):
    mock_fail_to_get_personal_data_value_by_id(
        'phones', personal_response_status, 'error_code', 'error_message',
    )

    response = await taxi_eats_support_misc_web.get(
        '/v1/place-by-personal-phone-id',
        params={'personal_phone_id': PHONE_ID},
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    ('core_response_status', 'expected_status'), [(404, 404), (500, 500)],
)
async def test_fail_to_get_ivr_info(
        # ---- fixtures ----
        mock_fail_to_get_ivr_info,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        core_response_status,
        expected_status,
):
    mock_fail_to_get_ivr_info(core_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/place-by-personal-phone-id',
        params={'personal_phone_id': PHONE_ID},
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    (
        'eats_catalog_storage_response_status',
        'expected_status',
        'expected_data',
    ),
    [(500, 200, DEFAULT_EXPECTED_DATA)],
)
async def test_fail_to_get_place_by_id(
        # ---- fixtures ----
        mock_fail_to_get_places_info,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        eats_catalog_storage_response_status,
        expected_status,
        expected_data,
):
    mock_fail_to_get_places_info(eats_catalog_storage_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/place-by-personal-phone-id',
        params={'personal_phone_id': PHONE_ID},
    )

    assert response.status == expected_status
    data = await response.json()
    assert data == expected_data
