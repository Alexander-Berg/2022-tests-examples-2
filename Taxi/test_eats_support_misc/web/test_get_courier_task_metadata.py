import typing

import pytest


ORDER_NR = '123456-123456'
EATER_PHONE_ID = 'some_phone_id'
BRAND_ID = '123'


DEFAULT_ORDER_META = {
    'eater_id': 'some_id',
    'eater_name': 'Alice',
    'eater_decency': 'good',
    'is_first_order': True,
    'is_blocked_user': False,
    'order_status': 'order_taken',
    'order_type': 'native',
    'delivery_type': 'pickup',
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
    'place_id': '10',
    'place_name': 'some_place_name',
    'is_sent_to_restapp': False,
    'is_sent_to_integration': True,
    'integration_type': 'native',
}

DEFAULT_EATER_TAGS: typing.List[str] = []
VIP_EATER_TAGS = ['vip_eater']

DEFAULT_EXPECTED_META = {
    'city_label': DEFAULT_ORDER_META['city_label'],
    'order_total_amount': DEFAULT_ORDER_META['order_total_amount'],
}


@pytest.mark.parametrize(
    ('order_meta', 'eater_tags', 'expected_meta'),
    [
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_EATER_TAGS,
            DEFAULT_EXPECTED_META,
            id='base_case',
        ),
        pytest.param(
            dict(DEFAULT_ORDER_META, brand_id=BRAND_ID),
            DEFAULT_EATER_TAGS,
            dict(DEFAULT_EXPECTED_META, brand_id=BRAND_ID),
            id='meta_with_brand_id',
        ),
        pytest.param(
            dict(DEFAULT_ORDER_META, eater_phone_id=EATER_PHONE_ID),
            VIP_EATER_TAGS,
            dict(DEFAULT_EXPECTED_META, is_vip_eater=True),
            id='vip_eater',
        ),
    ],
)
async def test_green_flow(
        # ---- fixtures ----
        mock_get_order_meta,
        mock_get_eater_tags,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        order_meta,
        eater_tags,
        expected_meta,
):
    mock_get_order_meta(ORDER_NR, order_meta)
    mock_get_eater_tags(EATER_PHONE_ID, eater_tags)

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-task-metadata', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_meta


@pytest.mark.parametrize(
    ('core_response_status', 'expected_status'), [(404, 404), (500, 500)],
)
async def test_fail_to_get_order_meta(
        # ---- fixtures ----
        mock_fail_to_get_order_meta,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        core_response_status,
        expected_status,
):
    mock_fail_to_get_order_meta(core_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-task-metadata', params={'order_nr': ORDER_NR},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    ('eats_tags_response_status', 'expected_meta'),
    [(500, DEFAULT_EXPECTED_META)],
)
async def test_fail_to_get_eater_tags(
        # ---- fixtures ----
        mock_get_order_meta,
        mock_fail_to_get_eater_tags,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        eats_tags_response_status,
        expected_meta,
):
    mock_get_order_meta(
        ORDER_NR, dict(DEFAULT_ORDER_META, eater_phone_id=EATER_PHONE_ID),
    )
    mock_fail_to_get_eater_tags(eats_tags_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/courier-task-metadata', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_meta
