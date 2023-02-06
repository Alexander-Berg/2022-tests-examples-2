import typing

import pytest

from test_eats_support_misc import utils

ORDER_NR = '123456-123456'
PLACE_ID = 10
CLAIM_ID = 'some_claim_id'
CORP_CLIENT_ID = 'ID_with_length_equal_to_32_chars'
CLAIM_ALIAS = 'some_claim_alias'
EATER_NAME = 'Alice'


DEFAULT_ORDER_META = {
    'eater_id': 'some_id',
    'eater_name': EATER_NAME,
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

DEFAULT_POINTS_INFO = [
    {
        'address': {'fullname': 'Some name', 'coordinates': [50.0, 50.0]},
        'contact': {'phone': '+79099999998', 'name': 'Name'},
        'id': 1,
        'type': 'source',
        'visit_order': 1,
        'visit_status': 'pending',
        'visited_at': {},
    },
    {
        'address': {'fullname': 'Some name', 'coordinates': [50.0, 50.0]},
        'contact': {'phone': '+79099999998', 'name': 'Name'},
        'id': 2,
        'type': 'destination',
        'visit_order': 2,
        'visit_status': 'pending',
        'visited_at': {},
    },
]

DEFAULT_CLAIM_INFO = {
    'created_ts': '2021-01-01T01:10:00+03:00',
    'id': CLAIM_ID,
    'items': [
        {
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'Title',
            'cost_value': '1.00',
            'cost_currency': 'RUB',
            'quantity': 1,
        },
    ],
    'revision': 1,
    'route_points': DEFAULT_POINTS_INFO,
    'status': 'pickuped',
    'updated_ts': '2021-01-01T01:12:00+03:00',
    'user_request_revision': '1',
    'version': 1,
    'performer_info': {'courier_name': 'Some name', 'legal_name': 'Some name'},
}

NEGATIVE_RESULT_OF_EATER_NAME_CHECK = {
    'jsonrpc': '2.0',
    'id': 'checking text from eats-support-misc',
    'result': {
        'verdicts': [
            {
                'name': 'text_auto_good',
                'source': 'clean-web',
                'subsource': 'tmu',
                'value': False,
                'entity': 'client_name',
                'key': 'unique key',
            },
        ],
    },
}

POSITIVE_RESULT_OF_EATER_NAME_CHECK = {
    'jsonrpc': '2.0',
    'id': 'checking text from eats-support-misc',
    'result': {
        'verdicts': [
            {
                'name': 'text_auto_good',
                'source': 'clean-web',
                'subsource': 'tmu',
                'value': True,
                'entity': 'client_name',
                'key': 'unique key',
            },
        ],
    },
}

ERRORS_DURING_EATER_NAME_CHECK = {
    'jsonrpc': '2.0',
    'id': 'checking text from eats-support-misc',
    'result': {'verdicts': [], 'errors': [{'antifraud': 'timeout'}]},
}

NO_RECEIPTS: typing.Dict[str, typing.Any] = {'receipts': []}
RECEIPTS_WITH_OFD_URL = {
    'receipts': [
        {
            'order_id': ORDER_NR,
            'document_id': 'random_id',
            'is_refund': False,
            'country_code': 'rus',
            'payment_method': 'card',
            'ofd_info': {
                'reg_number': 'random',
                'document_number': 'random',
                'fiscal_sign': 'fiscal_sign',
                'ofd_name': 'ofd_name',
                'ofd_receipt_url': 'ofd_receipt_url',
            },
            'created_at': '2021-01-01T02:15:00+03:00',
        },
        {
            'order_id': ORDER_NR,
            'document_id': 'random_id_1',
            'is_refund': False,
            'country_code': 'rus',
            'payment_method': 'card',
            'ofd_info': {
                'reg_number': 'random',
                'document_number': 'random',
                'fiscal_sign': 'fiscal_sign',
                'ofd_name': 'ofd_name',
                'ofd_receipt_url': 'another_ofd_url',
            },
            'created_at': '2021-01-01T02:15:00+03:00',
        },
    ],
}

PLACE_NOT_FOUND = {'places': [], 'not_found_place_ids': [PLACE_ID]}
KALININGRAD_PLACE_INFO = {
    'places': [
        {
            'id': 11,
            'revision_id': 90,
            'updated_at': '2020-01-14T12:00:00+03:00',
            'region': {
                'id': 39,
                'geobase_ids': [32412],
                'time_zone': 'Europe/Kaliningrad',
            },
        },
    ],
    'not_found_place_ids': [],
}

DEFAULT_ROBOCALL_INFO: typing.Dict[str, typing.Any] = {}

DEFAULT_EXPECTED_META = dict(
    DEFAULT_ORDER_META,
    has_receipts=False,
    receipt_urls=[],
    was_function_client_no_responding_used=False,
)


@pytest.fixture(autouse=True)
def _default_mock_requests(
        mock_get_order_meta,
        mock_check_text,
        mock_get_claim_id_and_alias,
        mock_get_claim_info,
        mock_get_points_eta,
        mock_get_places_info,
        mock_get_receipts,
        mock_get_robocall_info,
):
    mock_get_order_meta(ORDER_NR, DEFAULT_ORDER_META)
    mock_check_text(EATER_NAME, POSITIVE_RESULT_OF_EATER_NAME_CHECK)
    mock_get_claim_id_and_alias(ORDER_NR, CLAIM_ID, CLAIM_ALIAS)
    mock_get_claim_info(CLAIM_ID, CORP_CLIENT_ID, DEFAULT_CLAIM_INFO)
    mock_get_points_eta(CLAIM_ID, CORP_CLIENT_ID, DEFAULT_POINTS_INFO)
    mock_get_places_info([PLACE_ID], ['region'], PLACE_NOT_FOUND)
    mock_get_receipts(ORDER_NR, NO_RECEIPTS)
    mock_get_robocall_info(CLAIM_ID, DEFAULT_ROBOCALL_INFO)


@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': CORP_CLIENT_ID},
    },
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=False,
    EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META='never_exclude',
)
@pytest.mark.parametrize(
    (
        'order_meta',
        'claim_info',
        'points_info',
        'places_info',
        'receipts_info',
        'robocall_info',
        'eater_name_check_result',
        'expected_meta',
    ),
    [
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            None,
            DEFAULT_EXPECTED_META,
            id='only_order_meta_from_core',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            None,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META, deleted_keys=['eater_name'],
            ),
            marks=pytest.mark.config(
                EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META=(
                    'always_exclude'
                ),
            ),
            id='eater_name_exclusion',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            POSITIVE_RESULT_OF_EATER_NAME_CHECK,
            DEFAULT_EXPECTED_META,
            marks=pytest.mark.config(
                EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META=(
                    'exclude_if_is_not_valid'
                ),
            ),
            id='valid_eater_name',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            NEGATIVE_RESULT_OF_EATER_NAME_CHECK,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META, deleted_keys=['eater_name'],
            ),
            marks=pytest.mark.config(
                EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META=(
                    'exclude_if_is_not_valid'
                ),
            ),
            id='invalid_eater_name',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            ERRORS_DURING_EATER_NAME_CHECK,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META, deleted_keys=['eater_name'],
            ),
            marks=pytest.mark.config(
                EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META=(
                    'exclude_if_is_not_valid'
                ),
            ),
            id='errors_during_eater_name_check',
        ),
        pytest.param(
            dict(
                DEFAULT_ORDER_META,
                courier_arrived_to_customer_planned_time=(
                    '2021-01-01T00:45:00+03:00'
                ),
            ),
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            None,
            dict(
                DEFAULT_EXPECTED_META,
                courier_arrived_to_customer_planned_time=(
                    '2021-01-01T00:45:00+03:00'
                ),
                courier_arrived_to_customer_from=5,
                courier_arrived_to_customer_to=10,
            ),
            marks=pytest.mark.now('2021-01-01T00:40:00+03:00'),
            id='meta_with_limits_of_delivery_time_range',
        ),
        pytest.param(
            dict(
                DEFAULT_ORDER_META,
                courier_arrived_to_customer_planned_time=(
                    '2021-01-01T00:45:00+03:00'
                ),
                courier_arrived_to_customer_actual_time=(
                    '2021-01-01T00:50:00+03:00'
                ),
            ),
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            None,
            dict(
                DEFAULT_EXPECTED_META,
                courier_arrived_to_customer_planned_time=(
                    '2021-01-01T00:45:00+03:00'
                ),
                courier_arrived_to_customer_actual_time=(
                    '2021-01-01T00:50:00+03:00'
                ),
            ),
            id='no_limits_if_meta_has_courier_arrived_to_customer_actual_time',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_CLAIM_INFO,
                update_items={'performer_info.transport_type': 'car'},
            ),
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            None,
            dict(DEFAULT_EXPECTED_META, courier_type='car'),
            id='meta_with_courier_type',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            [
                dict(
                    DEFAULT_POINTS_INFO[0],
                    visit_status='pending',
                    visited_at={'expected': '2021-01-01T00:32:00+03:00'},
                ),
                DEFAULT_POINTS_INFO[1],
            ],
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            None,
            dict(DEFAULT_EXPECTED_META, place_eta='2021-01-01T00:32:00+03:00'),
            id='order_meta_with_place_eta',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            [
                DEFAULT_POINTS_INFO[0],
                dict(
                    DEFAULT_POINTS_INFO[1],
                    visit_status='pending',
                    visited_at={'expected': '2021-01-01T00:51:00+03:00'},
                ),
            ],
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            None,
            dict(DEFAULT_EXPECTED_META, eater_eta='2021-01-01T00:51:00+03:00'),
            id='order_meta_with_eater_eta',
        ),
        pytest.param(
            dict(
                DEFAULT_ORDER_META,
                order_created_at='2020-12-31 23:10:00+02:00',
                order_promised_at='2021-01-01 02:00:00+04:00',
            ),
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            None,
            DEFAULT_EXPECTED_META,
            id='format_timestamps',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            KALININGRAD_PLACE_INFO,
            NO_RECEIPTS,
            DEFAULT_ROBOCALL_INFO,
            None,
            dict(
                DEFAULT_EXPECTED_META,
                readable_order_created_at='23:10',
                readable_order_promised_at='01.01.2021 00:00',
                local_time='23:15',
                local_date='31.12.2020',
            ),
            marks=pytest.mark.now('2021-01-01T00:15:00+03:00'),
            id='localization_of_time',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            RECEIPTS_WITH_OFD_URL,
            DEFAULT_ROBOCALL_INFO,
            None,
            dict(
                DEFAULT_EXPECTED_META,
                has_receipts=True,
                receipt_urls=['ofd_receipt_url', 'another_ofd_url'],
            ),
            id='receipts_with_ofd_url',
        ),
        pytest.param(
            DEFAULT_ORDER_META,
            DEFAULT_CLAIM_INFO,
            DEFAULT_POINTS_INFO,
            PLACE_NOT_FOUND,
            NO_RECEIPTS,
            dict(
                DEFAULT_ROBOCALL_INFO,
                robocall_requested_at='2021-01-01T01:15:00+03:00',
            ),
            None,
            dict(
                DEFAULT_EXPECTED_META,
                was_function_client_no_responding_used=True,
            ),
            id='client_not_responding',
        ),
    ],
)
async def test_green_flow(
        # ---- fixtures ----
        mock_get_order_meta,
        mock_check_text,
        mock_get_claim_id_and_alias,
        mock_get_claim_info,
        mock_get_points_eta,
        mock_get_places_info,
        mock_get_receipts,
        mock_get_robocall_info,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        order_meta,
        claim_info,
        points_info,
        places_info,
        receipts_info,
        robocall_info,
        eater_name_check_result,
        expected_meta,
):
    mock_get_order_meta(ORDER_NR, order_meta)
    mock_get_claim_info(CLAIM_ID, CORP_CLIENT_ID, claim_info)
    mock_get_claim_id_and_alias(ORDER_NR, CLAIM_ID, CLAIM_ALIAS)
    mock_get_points_eta(CLAIM_ID, CORP_CLIENT_ID, points_info)
    mock_get_places_info([PLACE_ID], ['region'], places_info)
    mock_get_receipts(ORDER_NR, receipts_info)
    mock_check_text(EATER_NAME, eater_name_check_result)
    mock_get_robocall_info(CLAIM_ID, robocall_info)

    response = await taxi_eats_support_misc_web.get(
        '/v1/client-task-metadata', params={'order_nr': ORDER_NR},
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
        '/v1/client-task-metadata', params={'order_nr': ORDER_NR},
    )
    assert response.status == expected_status


@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': CORP_CLIENT_ID},
    },
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=False,
    EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META='exclude_if_is_not_valid',
)
@pytest.mark.parametrize(
    ('clean_web_response_status', 'expected_meta'),
    [
        (
            500,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META, deleted_keys=['eater_name'],
            ),
        ),
    ],
)
async def test_fail_to_check_eater_name(
        # ---- fixtures ----
        mock_fail_to_check_text,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        clean_web_response_status,
        expected_meta,
):
    mock_fail_to_check_text(clean_web_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/client-task-metadata', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_meta


@pytest.mark.config(
    EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META='never_exclude',
)
@pytest.mark.parametrize(
    ('eats_orders_tracking_response_status', 'expected_meta'),
    [
        (
            400,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META,
                deleted_keys=['was_function_client_no_responding_used'],
            ),
        ),
        (
            500,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META,
                deleted_keys=['was_function_client_no_responding_used'],
            ),
        ),
    ],
)
async def test_fail_to_get_claim_id_and_alias(
        # ---- fixtures ----
        mock_fail_to_get_claim_id_and_alias,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        eats_orders_tracking_response_status,
        expected_meta,
):
    mock_fail_to_get_claim_id_and_alias(eats_orders_tracking_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/client-task-metadata', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_meta


@pytest.mark.config(
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=False,
    EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META='never_exclude',
)
@pytest.mark.parametrize(
    ('cargo_claims_response_status', 'expected_meta'),
    [
        (
            403,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META,
                deleted_keys=['was_function_client_no_responding_used'],
            ),
        ),
        (
            404,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META,
                deleted_keys=['was_function_client_no_responding_used'],
            ),
        ),
        (
            500,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META,
                deleted_keys=['was_function_client_no_responding_used'],
            ),
        ),
    ],
)
async def test_fail_to_get_claim_info(
        # ---- fixtures ----
        mock_fail_to_get_claim_info,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        cargo_claims_response_status,
        expected_meta,
):
    mock_fail_to_get_claim_info(cargo_claims_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/client-task-metadata', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_meta


@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': CORP_CLIENT_ID},
    },
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=False,
    EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META='never_exclude',
)
@pytest.mark.parametrize(
    ('cargo_claims_response_status', 'expected_meta'),
    [
        (404, DEFAULT_EXPECTED_META),
        (409, DEFAULT_EXPECTED_META),
        (500, DEFAULT_EXPECTED_META),
    ],
)
async def test_fail_to_get_points_info(
        # ---- fixtures ----
        mock_fail_to_get_points_eta,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        cargo_claims_response_status,
        expected_meta,
):
    mock_fail_to_get_points_eta(cargo_claims_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/client-task-metadata', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_meta


@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': CORP_CLIENT_ID},
    },
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=False,
    EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META='never_exclude',
)
@pytest.mark.parametrize(
    ('eats_catalog_storage_response_status', 'expected_meta'),
    [(500, DEFAULT_EXPECTED_META)],
)
async def test_fail_to_get_place_info(
        # ---- fixtures ----
        mock_get_order_meta,
        mock_check_text,
        mock_get_claim_id_and_alias,
        mock_get_claim_info,
        mock_get_points_eta,
        mock_fail_to_get_places_info,
        mock_get_receipts,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        eats_catalog_storage_response_status,
        expected_meta,
):
    mock_fail_to_get_places_info(eats_catalog_storage_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/client-task-metadata', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_meta


@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': CORP_CLIENT_ID},
    },
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=False,
    EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META='never_exclude',
)
@pytest.mark.parametrize(
    ('eats_receipts_response_status', 'expected_meta'),
    [(404, DEFAULT_EXPECTED_META), (500, DEFAULT_EXPECTED_META)],
)
async def test_fail_to_get_receipts(
        # ---- fixtures ----
        mock_fail_to_get_receipts,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        eats_receipts_response_status,
        expected_meta,
):
    mock_fail_to_get_receipts(eats_receipts_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/client-task-metadata', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_meta


@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID={
        CLAIM_ALIAS: {'client_id': CORP_CLIENT_ID},
    },
    EATS_SUPPORT_MISC_USE_EATS_ETA_TO_GET_POINTS_ETA=False,
    EATS_SUPPORT_MISC_EXCLUDE_EATER_NAME_FROM_META='never_exclude',
)
@pytest.mark.parametrize(
    ('cargo_orders_response_status', 'expected_meta'),
    [
        (
            500,
            utils.get_dict_copy_with_edit_items(
                DEFAULT_EXPECTED_META,
                deleted_keys=['was_function_client_no_responding_used'],
            ),
        ),
    ],
)
async def test_fail_to_get_robocall_info(
        # ---- fixtures ----
        mock_fail_to_get_robocall_info,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        cargo_orders_response_status,
        expected_meta,
):
    mock_fail_to_get_robocall_info(cargo_orders_response_status)

    response = await taxi_eats_support_misc_web.get(
        '/v1/client-task-metadata', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_meta
