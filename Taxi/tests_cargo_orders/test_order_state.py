# pylint: disable=C0302,W0102

import datetime
import json
import operator

import pytest

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

DOOR_CODE_COMMENT = 'Код от подъезда/домофона: A2_door_code.\n'
ESCAPED_DOOR_CODE_COMMENT = 'Код от подъезда/домофона: A2\\_door\\_code\\.\n'
CLIENT_COMMENT = 'Комментарий: A2_comment'
ESCAPED_CLIENT_COMMENT = 'Комментарий: A2\\_comment'

TEST_SIMPLE_CURRENT_POINT = {
    'id': 3,
    'label': 'Точка А2',
    'need_confirmation': True,
    'leave_under_door': True,
    'meet_outside': False,
    'no_door_call': True,
    'modifier_age_check': True,
    'client_name': 'Иван',
    'actions': [{'type': 'arrived_at_point'}, {'type': 'show_act'}],
    'phones': [
        {
            'background_loading': False,
            'label': 'Отправитель2',
            'type': 'source',
            'view': 'main',
        },
    ],
    'type': 'source',
    'visit_order': 2,
    'comment': (DOOR_CODE_COMMENT + CLIENT_COMMENT),
    'segment_id': 'seg_2',
    'number_of_parcels': 1,
}

TEST_SIMPLE_JSON_RESULT = {
    'current_route': [
        {
            'id': 1,
            'items': [],
            'label': 'Получение 1',
            'phones': [
                {
                    'background_loading': False,
                    'label': 'Отправитель1',
                    'type': 'source',
                    'view': 'main',
                },
            ],
            'type': 'source',
            'address': {
                'fullname': 'Точка А1',
                'coordinates': [1, 2],
                'sflat': '123',
                'shortname': 'Точка А1',
            },
            'number_of_parcels': 1,
        },
        {
            'id': 3,
            'contact_name': 'Иван',
            'items': [],
            'label': 'Получение 2',
            'phones': [
                {
                    'background_loading': False,
                    'label': 'Отправитель2',
                    'type': 'source',
                    'view': 'main',
                },
            ],
            'type': 'source',
            'address': {
                'fullname': 'Точка А2',
                'shortname': 'Точка А2',
                'coordinates': [3, 4],
                'comment': 'A2_comment',
                'door_code': 'A2_door_code',
            },
            'number_of_parcels': 1,
        },
        {
            'id': 4,
            'items': [],
            'label': 'Выдача 1',
            'phones': [
                {
                    'background_loading': False,
                    'label': 'Получатель2',
                    'type': 'destination',
                    'view': 'main',
                },
            ],
            'type': 'destination',
            'address': {
                'coordinates': [5, 6],
                'fullname': 'Точка Б21',
                'shortname': 'Точка Б21',
            },
            'number_of_parcels': 1,
        },
        {
            'id': 2,
            'items': [],
            'label': 'Выдача 2',
            'phones': [
                {
                    'background_loading': False,
                    'label': 'Получатель1',
                    'type': 'destination',
                    'view': 'main',
                },
            ],
            'type': 'destination',
            'address': {
                'coordinates': [7, 8],
                'fullname': 'Точка Б11',
                'shortname': 'Точка Б11',
            },
            'number_of_parcels': 1,
        },
    ],
    'status': 'delivering',
    'total_point_count': 4,
    'phones': [],
    'state_version': 'v0_2',
    'order_comment_type': 'plain',
    'order_comment': (
        'Заказ с подтверждением по СМС.\n'
        'Комментарий: seg_2_claim_comment\n'
        'Количество точек маршрута: 3.'
    ),
}


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {
                'cargo_batch_screen_comments': '8.00',
                'markdown': '8.00',
            },
        },
    },
)
@pytest.mark.parametrize(
    'new_flow_enabled, markdown_enabled',
    [(False, False), (False, True), (True, False), (True, True)],
)
async def test_simple(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        experiments3,
        new_flow_enabled,
        markdown_enabled,
        mock_driver_tags_v1_match_profile,
):
    if new_flow_enabled:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_newflow_comments_settings',
            consumers=['cargo/newflow-comments-settings'],
            clauses=[],
            default_value={'enabled': True},
        )
    if markdown_enabled:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_build_point_comment',
            consumers=['cargo-orders/build-point-comment'],
            clauses=[],
            default_value={
                'markdown_special_requirement': 'markdown',
                'markdown_enabled': True,
                'escape_client_comment': False,
            },
        )
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    comment_type = 'markdown' if markdown_enabled else 'plain'
    current_point = TEST_SIMPLE_CURRENT_POINT.copy()
    current_point['comment_type'] = comment_type
    if new_flow_enabled:
        current_point['comment'] += '\n\nseg_2_claim_comment'

    if markdown_enabled:
        current_point['comment'] = (
            'Код от подъезда/домофона: A2\\_door\\_code\\.\n'
            'Комментарий: A2_comment'
        )
        if new_flow_enabled:
            current_point['comment'] += '\n\nseg\\_2\\_claim\\_comment'

    json_result = TEST_SIMPLE_JSON_RESULT.copy()
    json_result['current_route'][1]['address']['comment_type'] = comment_type
    json_result['current_point'] = current_point

    if new_flow_enabled:
        json_result['order_comment'] = (
            'Заказ с подтверждением по СМС.\n' 'Количество точек маршрута: 3.'
        )

    assert response.status_code == 200
    assert response.json() == json_result


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {
                'cargo_batch_screen_comments': '8.00',
                'markdown': '8.00',
            },
        },
    },
)
async def test_404_waybill_info(
        taxi_cargo_orders,
        mock_waybill_info_404,
        default_order_id,
        my_batch_waybill_info,
        experiments3,
        mock_driver_tags_v1_match_profile,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_newflow_comments_settings',
        consumers=['cargo/newflow-comments-settings'],
        clauses=[],
        default_value={'enabled': True},
    )
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 404


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {
                'cargo_batch_screen_comments': '8.00',
                'markdown': '8.00',
            },
        },
    },
)
@pytest.mark.parametrize(
    'markdown_enabled, escape_client_comment',
    [(False, False), (True, False), (True, True)],
)
async def test_escape_client_comment(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        experiments3,
        markdown_enabled,
        escape_client_comment,
        mock_driver_tags_v1_match_profile,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_build_point_comment',
        consumers=['cargo-orders/build-point-comment'],
        clauses=[],
        default_value={
            'markdown_special_requirement': 'markdown',
            'markdown_enabled': markdown_enabled,
            'escape_client_comment': escape_client_comment,
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    comment_type = 'markdown' if markdown_enabled else 'plain'
    current_point = TEST_SIMPLE_CURRENT_POINT.copy()
    current_point['comment_type'] = comment_type

    if markdown_enabled:
        # when using markdown, always escape door code
        if escape_client_comment:
            current_point['comment'] = (
                ESCAPED_DOOR_CODE_COMMENT + ESCAPED_CLIENT_COMMENT
            )
        else:
            current_point['comment'] = (
                ESCAPED_DOOR_CODE_COMMENT + CLIENT_COMMENT
            )

    json_result = TEST_SIMPLE_JSON_RESULT.copy()
    json_result['current_route'][1]['address']['comment_type'] = comment_type
    json_result['current_point'] = current_point

    assert response.status_code == 200
    assert response.json() == json_result


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {
                'cargo_batch_screen_comments': '8.00',
                'markdown': '8.00',
            },
        },
    },
)
@pytest.mark.parametrize(
    'new_flow_enabled, markdown_enabled',
    [(False, False), (False, True), (True, False), (True, True)],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_driver_state_ui',
    consumers=['cargo-orders/ui'],
    clauses=[],
    default_value={'enable_rear_card': True},
)
async def test_simple_with_ui(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        experiments3,
        new_flow_enabled,
        markdown_enabled,
        mock_driver_tags_v1_match_profile,
):
    if new_flow_enabled:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_newflow_comments_settings',
            consumers=['cargo/newflow-comments-settings'],
            clauses=[],
            default_value={'enabled': True},
        )
    if markdown_enabled:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_build_point_comment',
            consumers=['cargo-orders/build-point-comment'],
            clauses=[],
            default_value={
                'markdown_special_requirement': 'markdown',
                'markdown_enabled': True,
                'escape_client_comment': False,
            },
        )
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    comment_type = 'markdown' if markdown_enabled else 'plain'
    current_point = TEST_SIMPLE_CURRENT_POINT.copy()
    current_point['comment_type'] = comment_type

    if new_flow_enabled:
        current_point['comment'] += '\n\nseg_2_claim_comment'

    if markdown_enabled:
        current_point['comment'] = (
            'Код от подъезда/домофона: A2\\_door\\_code\\.\n'
            'Комментарий: A2_comment'
        )
        if new_flow_enabled:
            current_point['comment'] += '\n\nseg\\_2\\_claim\\_comment'

    json_result = TEST_SIMPLE_JSON_RESULT.copy()
    json_result['current_route'][1]['address']['comment_type'] = comment_type
    json_result['current_point'] = current_point
    json_result['ui'] = {
        'rear_card': {
            'background_color': '#000000',
            'text_color': '#ffffff',
            'title': 'Мультизаказ - 2 заказа',
        },
        'rear_card_title': 'Мультизаказ - 2 заказа',
    }

    if new_flow_enabled:
        json_result['order_comment'] = (
            'Заказ с подтверждением по СМС.\n' 'Количество точек маршрута: 3.'
        )

    assert response.status_code == 200
    assert response.json() == json_result


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_enable_taximeter_tracking_ui',
    consumers=['cargo-orders/taximeter-constructor'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
    default_value={'enabled': False},
)
async def test_constructor_ui(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        load_json,
        my_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    expected_constructor = load_json('expected_constructor.json')

    assert response.json()['tracking_ui'] == expected_constructor
    assert response.status_code == 200


@pytest.mark.experiments3(
    match={'predicate': {'type': 'false'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_enable_taximeter_constructor',
    consumers=['cargo-orders/taximeter-constructor'],
    clauses=[],
    default_value={'enabled': False},
)
async def test_turned_off_constructor_ui(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        load_json,
        my_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert 'tracking_ui' not in response.json()
    assert response.status_code == 200


@pytest.mark.parametrize('is_hide', [True, False])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_hide_address',
    consumers=['cargo-orders/address-hiding'],
    clauses=[
        {
            'value': {
                'items_to_hide': ['porch', 'door_code'],
                'value_to_replace': '...',
            },
            'predicate': {'type': 'true'},
        },
    ],
    default_value={'items_to_hide': []},
)
async def test_hide_address(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        load_json,
        my_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
        is_hide,
):
    if not is_hide:
        my_multipoints_waybill_info['execution']['points'][1][
            'visit_status'
        ] = 'arrived'
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    if is_hide:
        assert 'porch' in response.json()['current_route'][0]['address']
        assert 'porch' not in response.json()['current_route'][1]['address']
    else:
        assert 'porch' in response.json()['current_route'][0]['address']
        assert 'porch' in response.json()['current_route'][1]['address']
    assert response.status_code == 200


@pytest.mark.now('2022-07-18T11:27:44+00:00')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_pro_orders_bdu_actions_when_performer_late',
    consumers=['eats-pro-orders-bdu/performer-late'],
    default_value={
        'actions': [
            {
                'action_type': 'late_popup',
                'delay_between_attempts': 60,
                'time_after_timer_expire': 10,
                'time_before_client_promise': 10,
                'try_count': 5,
                'tanker_key_with_message': (
                    'constructor.actions.performer_late.message'
                ),
            },
        ],
    },
)
async def test_do_not_show_performer_late_popup(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        load_json,
        mock_driver_tags_v1_match_profile,
        my_waybill_info,
):
    my_waybill_info['execution']['points'][0][
        'due'
    ] = '2022-07-18T11:27:44+00:00'
    my_waybill_info['execution']['points'][0][
        'eta'
    ] = '2022-07-18T11:17:44+00:00'
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    tag = 'performer_late_source_'
    for action in response.json()['current_point']['actions']:
        assert not hasattr(action, 'tag') or action['tag'] is not tag


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_driver_state_ui',
    consumers=['cargo-orders/ui'],
    clauses=[],
    default_value={'enable_rear_card': True},
)
@pytest.mark.parametrize('segment_skip_index', [0, 1])
async def test_with_skipped_point_no_ui(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        segment_skip_index,
        mock_driver_tags_v1_match_profile,
):
    my_batch_waybill_info['execution']['segments'][segment_skip_index][
        'is_skipped'
    ] = True

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    assert 'ui' not in response.json()


async def test_not_found(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/00000000-0000-0000-0000-000000000000'},
    )
    assert response.status_code == 404


async def test_performer_not_found(
        taxi_cargo_orders, order_id_without_performer,
):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + order_id_without_performer},
    )
    assert response.status_code == 404
    assert response.json()['message'] == 'Performer was not found'


def set_point_visited(waybill_info, idx: int):
    point = waybill_info['execution']['points'][idx]
    point['is_resolved'] = True
    point['resolution'] = {'is_visited': True, 'is_skipped': False}


def set_point_skipped(waybill_info, idx: int):
    point = waybill_info['execution']['points'][idx]
    point['is_resolved'] = True
    point['resolution'] = {'is_visited': False, 'is_skipped': True}
    point['is_return_required'] = True
    point['visit_status'] = 'skipped'


# TODO: remove in <Задача на исправление тестов>
def set_each_point_resolved(waybill_info):
    for point in waybill_info['execution']['points']:
        if point['type'] == 'return':
            continue
        point['is_resolved'] = True
        point['resolution'] = {'is_visited': True, 'is_skipped': False}


# TODO: remove in <Задача на исправление тестов>
def set_last_dest_point_skipped(waybill_info):
    last_point = waybill_info['execution']['points'][3]
    last_point['is_resolved'] = True
    last_point['resolution'] = {'is_visited': False, 'is_skipped': True}
    last_point['is_return_required'] = True


def set_last_dest_point_pending(waybill_info):
    last_point = waybill_info['execution']['points'][3]
    last_point['is_resolved'] = False
    last_point['resolution'] = None


async def test_waybill_resolved(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    The last request from taximeter. No 'current_point'
    """
    set_each_point_resolved(my_batch_waybill_info)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    assert 'current_point' not in response.json()


async def test_waybill_resolved_with_skipped_point(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    The last request from taximeter.
    Check that return point will by in 'current_point'
    """
    set_each_point_resolved(my_batch_waybill_info)
    set_last_dest_point_skipped(my_batch_waybill_info)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    assert response.json()['current_point']['visit_order'] == 5


# TODO: remove in <Задача на исправление тестов>
def set_segment_status(waybill_info, segment_status: str):
    for segment in waybill_info['execution']['segments']:
        segment['status'] = segment_status


@pytest.mark.experiments3(filename='exp3_action_checks.json')
async def test_skip_segment_actions(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    set_segment_status(my_batch_waybill_info, 'pickup_arrived')

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    skip_action = next(
        a
        for a in response.json()['current_point']['actions']
        if a['type'] == 'skip_source_point'
    )
    assert skip_action == {
        'force_allowed': False,
        'force_punishments': [],
        'free_conditions': [
            {'type': 'time_after', 'value': '2020-06-17T19:39:50.000000Z'},
            {'type': 'min_call_count', 'value': '3'},
        ],
        'type': 'skip_source_point',
    }


# TODO: remove in <Задача на исправление тестов>
def set_skipped_seg_1(waybill_info, segment_id: str = 'seg_1'):
    for segment in waybill_info['execution']['segments']:
        if segment['id'] == segment_id:
            segment['is_skipped'] = True
    for point in waybill_info['execution']['points']:
        if point['segment_id'] == segment_id:
            point['is_segment_skipped'] = True
            point['is_resolved'] = True
            point['visit_status'] = 'skipped'


async def test_skip_segment_route(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    set_skipped_seg_1(my_batch_waybill_info)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    route = [
        p['address']['fullname'] for p in response.json()['current_route']
    ]
    # check source points of skipped segments contains in route,
    # but destination points are dropped
    assert route == ['Точка А1', 'Точка А2', 'Точка Б21']


def set_first_point_visited(waybill_info):
    first_point = waybill_info['execution']['points'][0]
    first_point['is_resolved'] = True
    first_point['resolution'] = {'is_visited': True, 'is_skipped': False}
    first_point['visit_status'] = 'visited'


def set_second_seg_status_arrived(waybill_info):
    for segment in waybill_info['execution']['segments']:
        if segment['id'] == 'seg_2':
            segment['status'] = 'pickup_arrived'
        if segment['id'] == 'seg_1':
            segment['status'] = 'pickuped'


@pytest.mark.experiments3(filename='exp3_action_checks.json')
async def test_skip_second_segment_actions(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    A1 -> A2 -> ...
    Driver pickuped items on point A1
    Check that on point A2 he has skip action too
    """
    set_first_point_visited(my_batch_waybill_info)
    set_second_seg_status_arrived(my_batch_waybill_info)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    skip_action = next(
        a
        for a in response.json()['current_point']['actions']
        if a['type'] == 'skip_source_point'
    )
    assert skip_action == {
        'force_allowed': False,
        'force_punishments': [],
        'free_conditions': [
            {'type': 'time_after', 'value': '2020-06-17T19:39:50.000000Z'},
            {'type': 'min_call_count', 'value': '3'},
        ],
        'type': 'skip_source_point',
    }

    # Test no cancel action
    with pytest.raises(StopIteration):
        next(
            a
            for a in response.json()['current_point']['actions']
            if a['type'] == 'cancel'
        )


@pytest.mark.config(CARGO_ORDERS_AUTH_ORDER_CORE_ENABLED=True)
async def test_auth_order_core_notfound(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mockserver,
        mock_driver_tags_v1_match_profile,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def mock_order_core(request):
        assert request.json['order_id'] == 'taxi-order'
        return mockserver.make_response(
            status=404, json={'code': 'not-found', 'message': 'not found'},
        )

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers={
            **DEFAULT_HEADERS,
            'X-YaTaxi-Driver-Profile-Id': 'new-driver',
            'X-YaTaxi-Park-Id': 'new-park',
        },
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert mock_order_core.times_called == 1
    assert response.status_code == 404


@pytest.mark.parametrize(
    ('order_park', 'order_driver', 'expect_success'),
    (
        ('new-park', 'new-driver', True),
        ('other-park', 'new-driver', False),
        ('new-park', 'other-driver', False),
    ),
)
@pytest.mark.config(CARGO_ORDERS_AUTH_ORDER_CORE_ENABLED=True)
async def test_auth_order_core(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mockserver,
        expect_success,
        order_driver,
        order_park,
        mock_driver_tags_v1_match_profile,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def mock_order_core(request):
        assert request.json['order_id'] == 'taxi-order'
        return {
            'order_id': request.json['order_id'],
            'replica': 'secondary',
            'version': 'xxx',
            'fields': {
                'order': {
                    'performer': {
                        'uuid': order_driver,
                        'db_id': order_park,
                        'tariff': {'class': 'courier'},
                    },
                },
            },
        }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers={
            **DEFAULT_HEADERS,
            'X-YaTaxi-Driver-Profile-Id': 'new-driver',
            'X-YaTaxi-Park-Id': 'new-park',
        },
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert mock_order_core.times_called == 1
    if expect_success:
        assert response.status_code == 200
    else:
        assert response.status_code == 404


async def test_segment_status_performer_draft(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    set_segment_status(my_waybill_info, 'performer_draft')

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['status'] == 'new'

    actions = [
        action['type'] for action in response_body['current_point']['actions']
    ]
    assert actions == ['arrived_at_point', 'cancel', 'show_act']


@pytest.fixture(name='mock_yamaps')
async def _mock_yamaps(yamaps, load_json):
    def _wrapper(
            coordinates_override=None,
            fullname_override=None,
            uri_override=None,
    ):
        @yamaps.set_fmt_geo_objects_callback
        def _get_geo_objects(request):
            response = load_json('yamaps_response.json')
            if 'll' in request.args:
                coordinates = [float(x) for x in request.args['ll'].split(',')]
            else:
                coordinates = None

            if coordinates_override is not None:
                for override_coordinates, shortname in coordinates_override:
                    if override_coordinates == coordinates:
                        response['name'] = shortname
            if fullname_override is not None:
                for override_fullname, shortname in fullname_override:
                    if override_fullname == request.args.get('text'):
                        response['name'] = shortname
            if uri_override is not None:
                for override_uri, shortname in uri_override:
                    if override_uri == request.args.get('uri'):
                        response['name'] = shortname

            return [response]

    return _wrapper


@pytest.mark.parametrize(
    'expected_method, use_uri, use_fullname',
    [
        ('Coordinates', False, False),
        ('Fullname', False, True),
        ('Uri', True, False),
        ('Uri', True, True),
    ],
)
async def test_address_localization(
        taxi_cargo_orders,
        mock_yamaps,
        set_up_cargo_orders_performer_localization_exp,
        my_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
        expected_method: str,
        use_uri: bool,
        use_fullname: bool,
):
    """
        Check address localization happy path.
        Localize address according to Accept-Language header.
    """
    await set_up_cargo_orders_performer_localization_exp(
        use_uri=use_uri, use_fullname=use_fullname,
    )
    mock_yamaps(
        coordinates_override=[
            ([37.642979, 55.734977], 'Aurora_By_Coordinates'),
        ],
        fullname_override=[('БЦ Аврора', 'Aurora_By_Fullname')],
        uri_override=[
            (
                'ymapsbm1://geo?ll=34.822%2C32.072&spn=0.001%2C0.001'
                '&text=%D7%99%D7%A9%D7%A8%D7%90%D7%9C%2C%20%D7%A8%D7'
                '%9E%D7%AA%20%D7%92%D7%9F%2C%20%D7%90%D7%9C%D7%A8%D7'
                '%95%D7%90%D7%99%2C%2045',
                'Aurora_By_Uri',
            ),
        ],
    )

    my_waybill_info['execution']['points'][0]['address']['sflat'] = '5A'
    my_waybill_info['execution']['points'][0]['address']['sfloor'] = '15'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    resp_body = response.json()
    address_localized = [
        {'shortname': p['address']['shortname']}
        for p in resp_body['current_route']
    ]
    assert address_localized == [
        {'shortname': f'Aurora_By_{expected_method}'},
        {'shortname': 'Sadovnicheskaya street, 3, entrance 1'},
    ]

    current_point_address = resp_body['current_route'][0]['address']
    assert current_point_address['shortname'] == f'Aurora_By_{expected_method}'
    assert (
        current_point_address['apartment_info']
        == 'entrance 4, floor 15, apartment 5A. Door code: 123.'
    )


async def test_address_localization_max_distance(
        taxi_cargo_orders,
        mock_yamaps,
        set_up_cargo_orders_performer_localization_exp,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    """
        Check address no localized due to
        result is too far from origin point.
    """
    await set_up_cargo_orders_performer_localization_exp(
        use_uri=False, use_fullname=True, max_distance=1000,
    )
    mock_yamaps()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    address_localized = [
        {'shortname': p['address']['shortname']}
        for p in response.json()['current_route']
    ]
    assert address_localized == [
        {'shortname': 'Садовническая, 82'},
        {'shortname': 'Sadovnicheskaya street, 3, entrance 1'},
    ]


async def test_address_localization_with_city(
        taxi_cargo_orders,
        mock_yamaps,
        set_up_cargo_orders_performer_localization_exp,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    """
        Check address localization city added to shortname.
        Shortname format example: '{city}, {shortname}'
        Configured in CARGO_ADDRESS_SHORTTEXT_FORMAT_BY_LOCALE
        Localize address according to Accept-Language header.
    """
    await set_up_cargo_orders_performer_localization_exp(
        add_city_to_shortname=True, use_uri=False,
    )
    mock_yamaps(coordinates_override=[([37.642979, 55.734977], 'Aurora')])

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    address_localized = [
        {'shortname': p['address']['shortname']}
        for p in response.json()['current_route']
    ]
    assert address_localized == [
        {'shortname': 'Moscow, Aurora'},
        {'shortname': 'Moscow, Sadovnicheskaya street, 3, entrance 1'},
    ]


@pytest.mark.parametrize('shortname_no_entrance', [False, True])
async def test_address_localization_without_entrance(
        taxi_cargo_orders,
        mock_yamaps,
        set_up_cargo_orders_performer_localization_exp,
        shortname_no_entrance,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    """
        Check address localization with shortname without entrance.
        Shortname format example: '{short_text_no_entrance}'
        Localize address according to Accept-Language header.
    """
    await set_up_cargo_orders_performer_localization_exp(
        shortname_no_entrance=shortname_no_entrance, use_uri=False,
    )
    mock_yamaps(coordinates_override=[([37.642979, 55.734977], 'Aurora')])

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    address_localized = [
        {'shortname': p['address']['shortname']}
        for p in response.json()['current_route']
    ]
    assert address_localized == [
        {'shortname': 'Aurora'},
        {
            'shortname': (
                'Sadovnicheskaya street, 3'
                if shortname_no_entrance
                else 'Sadovnicheskaya street, 3, entrance 1'
            ),
        },
    ]


async def test_address_localization_cache(
        taxi_cargo_orders,
        mock_yamaps,
        set_up_cargo_orders_performer_localization_exp,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    """
        Check localization cache happy path.

        Get value from yamaps on first request.
        On second request get value from cache.
    """
    mock_yamaps()

    # cache miss, store response to cache
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    # no effect becouse value will be fetched from cache
    mock_yamaps(coordinates_override=[([37.642979, 55.734977], 'Aurora')])

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    address_localized = [
        {'shortname': p['address']['shortname']}
        for p in response.json()['current_route']
    ]
    assert address_localized == [
        {'shortname': 'Sadovnicheskaya street, 3, entrance 1'},
        {'shortname': 'Sadovnicheskaya street, 3, entrance 1'},
    ]


async def test_address_localization_off(
        taxi_cargo_orders,
        yamaps,
        set_up_cargo_orders_performer_localization_exp,
        my_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    await set_up_cargo_orders_performer_localization_exp(enabled=False)

    @yamaps.set_fmt_geo_objects_callback
    def _mock_yamaps(request):
        assert False

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    resp_body = response.json()
    address_not_localized = [
        {'shortname': p['address']['shortname']}
        for p in resp_body['current_route']
    ]
    assert address_not_localized == [
        {'shortname': f'Садовническая, 82'},
        {'shortname': 'Украина'},
    ]

    current_point_address = resp_body['current_route'][0]['address']
    assert current_point_address['fullname'] == 'БЦ Аврора'
    assert current_point_address['country'] == 'Россия'
    assert current_point_address['city'] == 'Москва'
    assert current_point_address['street'] == 'Садовническая улица'


async def test_address_localization_check_building(
        taxi_cargo_orders,
        mock_yamaps,
        my_waybill_info,
        set_up_cargo_orders_performer_localization_exp,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    """
        Check localization cache happy path.

        Get value from yamaps on first request.
        On second request get value from cache.
    """
    await set_up_cargo_orders_performer_localization_exp(
        check_shortname_building=True,
    )
    # Set 'building' to check matching
    my_waybill_info['execution']['points'][0]['address']['building'] = '3'
    my_waybill_info['execution']['points'][0]['address'][
        'fullname'
    ] = 'Point 1 fullname'
    my_waybill_info['execution']['points'][1]['address'][
        'fullname'
    ] = 'Point 2 fullname'

    # cache miss, store response to cache
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    # # no effect because value will be fetched from cache
    mock_yamaps(coordinates_override=[([37.642979, 55.734977], 'Aurora')])

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    address_localized = [
        {'shortname': p['address']['shortname']}
        for p in response.json()['current_route']
    ]
    assert address_localized == [
        {'shortname': 'Sadovnicheskaya street, 3, entrance 1'},
        {'shortname': 'Point 2 fullname'},
    ]


async def test_address_localization_bad_gateway(
        taxi_cargo_orders,
        set_up_cargo_orders_performer_localization_exp,
        mockserver,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    """
        Check use of non-localized address on yamaps errors.

        Such behavior is enabled by skip_on_error: true
    """

    @mockserver.json_handler('/addrs.yandex/search')
    async def _mock_search(request):
        return mockserver.make_response('invalid', status=500)

    # gateway error
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    address_localized = [
        {'shortname': p['address']['shortname']}
        for p in response.json()['current_route']
    ]
    assert address_localized == [
        {'shortname': 'Садовническая, 82'},
        {'shortname': 'Украина'},
    ]


async def test_address_localization_required_bad(
        taxi_cargo_orders,
        set_up_cargo_orders_performer_localization_exp,
        mockserver,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    """
        Check /state, /exchange/*, /arrive_at_point failure on yamaps errors.

        Such behavior is enabled by skip_on_error: false
    """

    await set_up_cargo_orders_performer_localization_exp(skip_on_error=False)

    @mockserver.json_handler('/addrs.yandex/search')
    async def _mock_search(request):
        return mockserver.make_response('invalid', status=500)

    # gateway error
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 500


async def test_address_localization_no_config(
        taxi_cargo_orders,
        mockserver,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    """
        Check /state, /exchange/*, /arrive_at_point localization disabled
        if no such config3.0 exists.
    """

    @mockserver.json_handler('/addrs.yandex/search')
    async def _mock_search(request):
        return mockserver.make_response('invalid', status=500)

    # gateway error
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200


async def test_segment_delivered_finish(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    set_segment_status(my_waybill_info, 'delivered_finish')

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'complete'


@pytest.mark.parametrize('point_status', ['pending', 'arrived'])
async def test_no_eta_after_pending(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        exp_cargo_orders_timers_settings,
        mock_driver_tags_v1_match_profile,
        point_status: str,
):
    for waybill in waybill_state.waybills.values():
        points = waybill['execution']['points']
        for point in points:
            point['eta'] = '2020-07-20T11:08:00+00:00'
            if point['visit_status'] == 'pending':
                point['visit_status'] = point_status

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    has_eta_action = False
    for action in response.json()['current_point']['actions']:
        if action['type'] == 'eta':
            assert not action['calculation_awaited']
            has_eta_action = True

    assert has_eta_action == (point_status == 'pending')


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 2,
                                'arg_name': 'active_segments_count',
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'value': 1,
                                'arg_name': (
                                    'prev_source_points_duplicates_count'
                                ),
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'enabled': True,
                'skip_arrive_screen': True,
                'pickup_label_tanker_key': 'actions.pickup.title',
            },
        },
    ],
    default_value={'enabled': False, 'skip_arrive_screen': False},
)
async def test_batch_skip_arrive_action(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    Point A1 == A2
    Skip action 'arrive_at_point'
    """
    coordinates = [1, 2]
    my_batch_waybill_info['execution']['points'][0]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['points'][1]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'performer_found'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 3

    assert response_body['current_point']['actions'] == [
        {
            'conditions': [],
            'need_confirmation': True,
            'title': 'Забрал посылку №2',
            'type': 'pickup',
        },
        {
            'force_allowed': True,
            'force_punishments': [],
            'free_conditions': [
                {'type': 'arrive_at_point', 'value': 'source'},
            ],
            'type': 'cancel',
            'blocked_restrictions': [],
            'constructor_items': [],
            'performer_cancel_reason_menu': {'reason_list': []},
        },
        {'type': 'show_act'},
    ]


@pytest.mark.translations(
    cargo={
        'actions.pickup.sms_code.title': {
            'en': 'Enter SMS code #%(package_number)s',
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[],
    default_value={
        'enable': True,
        'skip_arrive_screen': True,
        'pickup_label_tanker_key': 'actions.pickup.title',
        'sms_code_label_tanker_key': 'actions.pickup.sms_code.title',
    },
)
async def test_batch_sms_code_text(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    Point A1 == A2
    Skip action 'arrive_at_point'
    """
    coordinates = [1, 2]
    my_batch_waybill_info['execution']['points'][0]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['points'][1]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'performer_found'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 3

    assert response_body['current_point']['actions'] == [
        {
            'conditions': [],
            'need_confirmation': True,
            'title': 'Enter SMS code #2',
            'type': 'pickup',
        },
        {
            'force_allowed': True,
            'force_punishments': [],
            'free_conditions': [
                {'type': 'arrive_at_point', 'value': 'source'},
            ],
            'type': 'cancel',
            'blocked_restrictions': [],
            'constructor_items': [],
            'performer_cancel_reason_menu': {'reason_list': []},
        },
        {'type': 'show_act'},
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 2,
                                'arg_name': 'active_segments_count',
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'value': 1,
                                'arg_name': (
                                    'prev_source_points_duplicates_count'
                                ),
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'enable': True,
                'skip_arrive_screen': True,
                'pickup_label_tanker_key': 'actions.pickup.title',
                'dialog_between_source_points': {
                    'title_tanker_key': (
                        'actions.show_dialog.default_batch_title'
                    ),
                    'message_tanker_key': (
                        'actions.show_dialog.default_batch_message'
                    ),
                    'button_tanker_key': (
                        'actions.show_dialog.default_batch_button'
                    ),
                    'block_button_duration_ms': 15000,
                },
            },
        },
    ],
    default_value={'enabled': False, 'skip_arrive_screen': False},
)
async def test_batch_show_dialog_action_after_a1(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    Point A1 == A2
    Show action 'show_dialog'
    """
    coordinates = [1, 2]
    my_batch_waybill_info['execution']['points'][0]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['points'][1]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'performer_found'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 3

    assert response_body['current_point']['actions'] == [
        {
            'type': 'show_dialog',
            'tag': 'batch_same_point_pickup',
            'message': 'Не забудьте забрать второй заказ',
            'button': 'Ок',
            'timer': {'block_button_duration_ms': 15000},
            'title': 'Еще заказ',
        },
        {
            'conditions': [],
            'need_confirmation': True,
            'title': 'Забрал посылку №2',
            'type': 'pickup',
        },
        {
            'force_allowed': True,
            'force_punishments': [],
            'free_conditions': [
                {'type': 'arrive_at_point', 'value': 'source'},
            ],
            'type': 'cancel',
            'blocked_restrictions': [],
            'constructor_items': [],
            'performer_cancel_reason_menu': {'reason_list': []},
        },
        {'type': 'show_act'},
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 2,
                                'arg_name': 'active_segments_count',
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'value': 1,
                                'arg_name': (
                                    'prev_source_points_duplicates_count'
                                ),
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'skip_arrive_screen': True,
                'dialog_between_source_points': {
                    'title_tanker_key': (
                        'actions.show_dialog.default_batch_title'
                    ),
                    'message_tanker_key': (
                        'actions.show_dialog.default_batch_message'
                    ),
                    'button_tanker_key': (
                        'actions.show_dialog.default_batch_button'
                    ),
                },
            },
        },
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 2,
                                'arg_name': 'active_segments_count',
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'skip_arrive_screen': False,
                'dialog_after_last_source_point': {
                    'title_tanker_key': (
                        'actions.show_dialog.default_batch_title'
                    ),
                    'message_tanker_key': (
                        'actions.show_dialog.default_batch_message'
                    ),
                    'button_tanker_key': (
                        'actions.show_dialog.default_batch_button'
                    ),
                },
                'dialog_after_new_points_added': {
                    'title_tanker_key': (
                        'actions.show_dialog.default_batch_title'
                    ),
                    'message_tanker_key': (
                        'actions.show_dialog.default_batch_message'
                    ),
                    'button_tanker_key': (
                        'actions.show_dialog.default_batch_button'
                    ),
                },
            },
        },
    ],
    default_value={'enabled': False, 'skip_arrive_screen': False},
)
async def test_batch_show_dialog_action_new_point_in_batch(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    my_batch_waybill_info['dispatch']['previous_waybill_ref'] = 'some_ref_id'
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'performer_found'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 3

    assert response_body['current_point']['actions'] == [
        {'type': 'arrived_at_point'},
        {
            'type': 'show_dialog',
            'tag': 'batch_new_point_added_some_ref_id',
            'message': 'Не забудьте забрать второй заказ',
            'button': 'Ок',
            'title': 'Еще заказ',
        },
        {
            'force_allowed': True,
            'force_punishments': [],
            'free_conditions': [
                {'type': 'arrive_at_point', 'value': 'source'},
            ],
            'type': 'cancel',
            'blocked_restrictions': [],
            'constructor_items': [],
            'performer_cancel_reason_menu': {'reason_list': []},
        },
        {'type': 'show_act'},
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 2,
                                'arg_name': 'active_segments_count',
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'value': 1,
                                'arg_name': (
                                    'prev_source_points_duplicates_count'
                                ),
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'enable': True,
                'skip_arrive_screen': True,
                'pickup_label_tanker_key': 'actions.pickup.title',
                'dialog_between_source_points': {
                    'title_tanker_key': (
                        'actions.show_dialog.default_batch_title'
                    ),
                    'message_tanker_key': (
                        'actions.show_dialog.default_batch_message'
                    ),
                    'button_tanker_key': (
                        'actions.show_dialog.default_batch_button'
                    ),
                },
            },
        },
    ],
    default_value={'enabled': False, 'skip_arrive_screen': False},
)
async def test_batch_not_show_dialog_action_new_point_in_batch_skipped(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    Point A1 == A2
    Show action 'show_dialog'
    """
    coordinates = [1, 2]
    my_batch_waybill_info['execution']['points'][0]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['points'][1]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['segments'][0]['is_skipped'] = True
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'performer_found'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 3
    for action in response_body['current_point']['actions']:
        if action['type'] == 'show_dialog':
            assert action['tag'] != 'batch_same_point_pickup'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[],
    default_value={
        'enabled': True,
        'skip_arrive_screen': False,
        'dialog_after_last_source_point': {
            'title_tanker_key': 'actions.show_dialog.default_batch_title',
            'message_tanker_key': 'actions.show_dialog.default_batch_message',
            'button_tanker_key': 'actions.show_dialog.default_batch_button',
        },
    },
)
async def test_batch_show_dialog_action_no_last_source_point(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'performer_found'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 3

    assert response_body['current_point']['actions'] == [
        {'type': 'arrived_at_point'},
        {
            'force_allowed': True,
            'force_punishments': [],
            'free_conditions': [
                {'type': 'arrive_at_point', 'value': 'source'},
            ],
            'type': 'cancel',
            'blocked_restrictions': [],
            'constructor_items': [],
            'performer_cancel_reason_menu': {'reason_list': []},
        },
        {'type': 'show_act'},
    ]


@pytest.mark.now('2020-12-11 13:01:53.000000+03')
@pytest.mark.parametrize(
    'exp_blocked_restriction, resp_blocked_restrictions',
    [
        (
            {
                'call_request': {
                    'title_tanker_key': (
                        'actions.cancel.restriction_call_request_title'
                    ),
                    'message_tanker_key': (
                        'actions.cancel.restriction_call_request_message'
                    ),
                },
            },
            [
                {
                    'type': 'call_request',
                    'message': 'Запрос на звонок в КЦ',
                    'title': 'Запрос в КЦ',
                },
            ],
        ),
        (None, []),
    ],
)
async def test_blocked_restrictions(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        experiments3,
        exp_blocked_restriction,
        resp_blocked_restrictions,
        mock_driver_tags_v1_match_profile,
):
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'pickup_arrived'

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_claims_action_checks',
        consumers=['cargo-claims/driver'],
        clauses=[],
        default_value={
            'cancel': {
                'min_waiting_time_seconds': 0,
                'use_free_waiting_time_rules': False,
            },
        },
    )

    exp_value = {}
    if exp_blocked_restriction:
        exp_value.update(exp_blocked_restriction)
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_cancel_blocked_restrictions',
        consumers=['cargo-claims/driver'],
        clauses=[],
        default_value=exp_value,
    )
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 3

    assert response_body['current_point']['actions'] == [
        {'conditions': [], 'need_confirmation': True, 'type': 'pickup'},
        {
            'force_allowed': True,
            'force_punishments': [],
            'free_conditions': [
                {'type': 'time_after', 'value': '2020-12-11T10:01:53.000000Z'},
            ],
            'type': 'cancel',
            'blocked_restrictions': resp_blocked_restrictions,
            'constructor_items': [],
            'performer_cancel_reason_menu': {'reason_list': []},
        },
        {'type': 'show_act'},
    ]


@pytest.mark.parametrize('segment_skip_act', [True, False])
async def test_show_act_action(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        segment_skip_act,
        mock_driver_tags_v1_match_profile,
):
    my_waybill_info['execution']['segments'][0]['skip_act'] = segment_skip_act
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    show_act_action_exists = 'show_act' in [
        action['type']
        for action in response.json()['current_point']['actions']
    ]
    assert show_act_action_exists != segment_skip_act


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_newflow_comments_settings',
    consumers=['cargo/newflow-comments-settings'],
    clauses=[],
    default_value={'enabled': True},
)
async def test_newflow_comments_not_supported(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    Experiment enabled, but feature does not supported for taximeter version
    """
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert (
        resp_body['current_point']['comment']
        == 'Код от подъезда/домофона: A2_door_code.\nКомментарий: A2_comment'
    )
    assert (
        resp_body['order_comment'] == 'Заказ с подтверждением по СМС.\n'
        'Комментарий: seg_2_claim_comment\nКоличество точек маршрута: 3.'
    )


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {
                'cargo_batch_screen_comments': '8.00',
                'markdown': '8.00',
            },
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_newflow_comments_settings',
    consumers=['cargo/newflow-comments-settings'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_build_point_comment',
    consumers=['cargo-orders/build-point-comment'],
    clauses=[],
    default_value={'markdown_enabled': True, 'escape_client_comment': False},
)
async def test_newflow_markdown_comments_state(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    Experiment enabled. Feature supported for taximeter version
    """
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert (
        resp_body['order_comment']
        == 'Заказ с подтверждением по СМС.\nКоличество точек маршрута: 3.'
    )

    assert resp_body['current_point']['comment'] == (
        'Код от подъезда/домофона: A2\\_door\\_code\\.\n'
        'Комментарий: A2_comment\n\n'
        'seg\\_2\\_claim\\_comment'
    )


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_batch_screen_comments': '8.00'},
        },
    },
    CARGO_ORDERS_COMMENT_OVERWRITE_SETTINGS={
        'enabled': True,
        'allowed_tariffs': ['eda', 'cargo'],
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_newflow_comments_settings',
    consumers=['cargo/newflow-comments-settings'],
    clauses=[],
    default_value={'enabled': True},
)
async def test_newflow_comments_overwrite_for_eda(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'overwrites_for_courier': [
            {'tariff': 'eda', 'comment': 'comment for eda'},
            {'tariff': 'cargo', 'comment': 'comment for cargo'},
        ],
    }
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['order_comment'] == 'Заказ с подтверждением по СМС.'
    assert resp_body['current_point']['comment'] == (
        'Код от подъезда/домофона: 123.\n'
        'Комментарий: comment 123\n\n'
        'comment for cargo'
    )


@pytest.mark.config(
    CARGO_ORDERS_COMMENT_OVERWRITE_SETTINGS={
        'enabled': True,
        'allowed_tariffs': ['eda', 'cargo'],
    },
)
async def test_comments_overwrite_for_eda(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    # Old flow comments
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'overwrites_for_courier': [
            {'tariff': 'eda', 'comment': 'comment for eda'},
            {'tariff': 'cargo', 'comment': 'comment for cargo'},
        ],
    }
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert (
        resp_body['order_comment']
        == 'Заказ с подтверждением по СМС.\nКомментарий: comment for cargo'
    )
    assert resp_body['current_point']['comment'] == (
        'Код от подъезда/домофона: 123.\n' 'Комментарий: comment 123'
    )


@pytest.mark.translations(
    cargo={'custom.pull_dispatch.title': {'en': 'Custom pull dispatch title'}},
)
async def test_pull_dispatch_skip_arrive(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_multipoints_waybill_info,
        experiments3,
        mock_driver_tags_v1_match_profile,
):
    """
    Point A1 == A2
    Show action 'show_dialog'
    """
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_batch_skip_arrive_screen',
        consumers=['cargo-orders/taximeter-api'],
        clauses=[
            {
                'title': 'clause',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {'arg_name': 'is_pull_dispatch'},
                                'type': 'bool',
                            },
                            {
                                'init': {
                                    'value': 'destination',
                                    'arg_name': 'point_type',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'value': 2,
                                    'arg_name': 'point_index_in_segment',
                                    'arg_type': 'int',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'enable': True,
                    'skip_arrive_screen': True,
                    'pickup_label_tanker_key': 'actions.pickup.title',
                },
            },
        ],
        default_value={'enabled': False, 'skip_arrive_screen': False},
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_localize_actions',
        consumers=['cargo-orders/build-actions'],
        clauses=[
            {
                'title': 'pull-dispatch override',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': True,
                        'arg_name': 'is_pull_dispatch',
                        'arg_type': 'bool',
                    },
                },
                'value': {
                    'dropoff_action_tanker_key': 'custom.pull_dispatch.title',
                },
            },
        ],
        default_value={},
    )
    await taxi_cargo_orders.invalidate_caches()

    my_multipoints_waybill_info['execution']['segments'][0][
        'custom_context'
    ] = {'dispatch_type': 'pull-dispatch'}
    my_multipoints_waybill_info['dispatch']['is_pull_dispatch'] = True
    set_point_visited(my_multipoints_waybill_info, 0)
    set_point_visited(my_multipoints_waybill_info, 1)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 642501
    assert response_body['current_point']['actions'] == [
        {
            'need_confirmation': True,
            'type': 'dropoff',
            'conditions': [],
            'title': 'Custom pull dispatch title',
        },
        {'type': 'show_act'},
    ]


@pytest.mark.translations(
    cargo={
        'custom.point_label.pull_dispatch_return': {
            'en': 'pull_dispatch_return_label',
        },
    },
)
async def test_pull_dispatch_return_label(
        taxi_cargo_orders,
        default_order_id,
        my_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    my_multipoints_waybill_info['dispatch']['is_pull_dispatch'] = True
    my_multipoints_waybill_info['execution']['points'][2][
        'location'
    ] = my_multipoints_waybill_info['execution']['points'][0]['location']
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert len(resp_body['current_route']) == 3

    labels = list(map(lambda x: x['label'], resp_body['current_route']))
    assert labels == ['Получение', 'Выдача 1', 'pull_dispatch_return_label']


@pytest.mark.parametrize('with_dropoff_title', [True, False])
async def test_post_payment_flow_action(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        exp_cargo_orders_post_payment_flow,
        mock_driver_tags_v1_match_profile,
        with_dropoff_title: bool,
):
    await exp_cargo_orders_post_payment_flow(
        with_dropoff_title=with_dropoff_title,
    )

    waybill_state.set_segment_status('delivery_arrived')
    waybill_state.set_post_payment()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    actions = sorted(
        response.json()['current_point']['actions'],
        key=operator.itemgetter('type'),
    )
    dropoff_action = {
        'need_confirmation': True,
        'type': 'dropoff',
        'conditions': [],
    }
    if with_dropoff_title:
        # this title is shown on slider
        # https://st.yandex-team.ru/CARGODEV-4751
        dropoff_action['title'] = 'Получил оплату'

    expected_actions = [
        dropoff_action,
        {
            'type': 'external_flow',
            'service': 'cargo-payments',
            'title': 'Получил оплату',
            'payload': {'payment_ref_id': '123'},
        },
        {'type': 'show_act'},
    ]
    assert actions == expected_actions


async def test_alive_batch_action(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    my_waybill_info['execution']['active_update_proposition'] = {
        'waybill_ref': 'new_waybill',
        'revision': 3,
    }
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    show_update_action = next(
        a
        for a in response.json()['current_point']['actions']
        if a['type'] == 'show_update_proposition'
    )
    assert show_update_action == {
        'type': 'show_update_proposition',
        'offer_id': 'new_waybill',
        'offer_revision': 3,
    }


@pytest.mark.parametrize(
    'corp_client_id, expected_actions',
    [
        (
            None,
            [
                {
                    'conditions': [
                        {'type': 'seen_pick_up_data_dialog', 'value': ''},
                    ],
                    'need_confirmation': True,
                    'type': 'pickup',
                },
                {'type': 'show_pickup_code'},
                {
                    'blocked_restrictions': [],
                    'constructor_items': [],
                    'force_allowed': True,
                    'force_punishments': [],
                    'free_conditions': [],
                    'performer_cancel_reason_menu': {'reason_list': []},
                    'type': 'cancel',
                },
                {'type': 'show_act'},
            ],
        ),
        (
            '5e36732e2bc54e088b1466e08e31c486',
            [
                {
                    'conditions': [],
                    'need_confirmation': True,
                    'type': 'pickup',
                },
                {
                    'blocked_restrictions': [],
                    'constructor_items': [],
                    'force_allowed': True,
                    'force_punishments': [],
                    'free_conditions': [],
                    'performer_cancel_reason_menu': {'reason_list': []},
                    'type': 'cancel',
                },
                {'type': 'show_act'},
            ],
        ),
    ],
)
async def test_pickup_code(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        corp_client_id,
        expected_actions,
        mock_driver_tags_v1_match_profile,
):
    my_waybill_info['execution']['points'][0]['pickup_code'] = 'qwerty123'
    my_waybill_info['execution']['segments'][0][
        'corp_client_id'
    ] = corp_client_id
    my_waybill_info['execution']['segments'][0]['status'] = 'pickup_arrived'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    assert response.json()['current_point']['actions'] == expected_actions


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_scooters': '8.00'}},
    },
    CARGO_ORDERS_SCOOTERS_PARAMS={
        'enabled': True,
        'corp_client_ids': ['5e36732e2bc54e088b1466e08e31c486'],
        'actions': {
            '__default__': {
                'icon': 'default',
                'title_key': 'default',
                'deeplink_tpl': 'default',
            },
            'find_vehicle': {
                'icon': 'find_vehicle',
                'title_key': 'find_vehicle',
                'deeplink_tpl': (
                    'task_id={source_point_external_order_id}&'
                    'item_id={current_point_external_order_id}'
                ),
            },
            'open_battery_door': {
                'icon': 'open_battery_door',
                'title_key': 'open_battery_door',
                'deeplink_tpl': (
                    'task_id={source_point_external_order_id}&'
                    'item_id={current_point_external_order_id}'
                ),
            },
            'battery_exchange': {
                'icon': 'battery_exchange',
                'title_key': 'battery_exchange',
                'deeplink_tpl': (
                    'task_id={source_point_external_order_id}&'
                    'current_point_id={current_point_id}&'
                    'current_claim_point_id={current_claim_point_id}'
                ),
            },
            'battery_exchange_for_return': {
                'icon': 'battery_exchange_for_return',
                'title_key': 'battery_exchange_for_return',
                'deeplink_tpl': 'task_id={source_point_external_order_id}',
            },
            'find_vehicle.scooters_ops': {
                'icon': 'find_vehicle',
                'title_key': 'find_vehicle',
                'deeplink_tpl': (
                    'missions/task_id={source_point_external_order_id}&'
                    'item_id={current_point_external_order_id}'
                ),
            },
            'open_battery_door.scooters_ops': {
                'icon': 'open_battery_door',
                'title_key': 'open_battery_door',
                'deeplink_tpl': (
                    'missions/task_id={source_point_external_order_id}&'
                    'item_id={current_point_external_order_id}'
                ),
            },
            'battery_exchange.scooters_ops': {
                'icon': 'battery_exchange',
                'title_key': 'battery_exchange',
                'deeplink_tpl': (
                    'missions/task_id={source_point_external_order_id}'
                ),
            },
            'battery_exchange_for_return.scooters_ops': {
                'icon': 'battery_exchange_for_return',
                'title_key': 'battery_exchange_for_return',
                'deeplink_tpl': (
                    'missions/task_id={source_point_external_order_id}'
                ),
            },
        },
    },
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_claims_action_checks',
    consumers=['cargo-claims/driver'],
    default_value={
        'return': {
            'enable': True,
            'min_waiting_time_seconds': 0,
            'allow_optional_return_by_driver': False,
        },
    },
)
@pytest.mark.translations(
    cargo={
        'find_vehicle': {'ru': 'Побибикать'},
        'open_battery_door': {'ru': 'Отваряй'},
        'battery_exchange': {'ru': 'Забрать батарейки'},
        'battery_exchange_for_return': {'ru': 'Вернуть батарейки'},
    },
)
@pytest.mark.parametrize(
    [
        'current_point_type',
        'claim_status',
        'source_points_eoid',
        'destination_point_eoid',
        'expected_actions',
    ],
    [
        pytest.param(
            'destination',
            'pickuped',
            'task_id_1',
            'item_id_1',
            [
                {'type': 'arrived_at_point'},
                {
                    'icon': 'find_vehicle',
                    'title': 'Побибикать',
                    'url': 'task_id=task_id_1&item_id=item_id_1',
                    'type': 'deeplink',
                },
                {'type': 'show_act'},
            ],
            id='find_vehicle action',
        ),
        pytest.param(
            'destination',
            'pickuped',
            'missions/mission_id',
            'missions/mission_id',
            [
                {'type': 'arrived_at_point'},
                {
                    'icon': 'find_vehicle',
                    'title': 'Побибикать',
                    'url': 'missions/task_id=mission_id&item_id=mission_id',
                    'type': 'deeplink',
                },
                {'type': 'show_act'},
            ],
            id='find_vehicle action for scooters-ops',
        ),
        pytest.param(
            'destination',
            'delivery_arrived',
            'task_id_1',
            'item_id_1',
            [
                {
                    'icon': 'open_battery_door',
                    'title': 'Отваряй',
                    'url': 'task_id=task_id_1&item_id=item_id_1',
                    'type': 'deeplink',
                },
                {
                    'need_confirmation': True,
                    'type': 'dropoff',
                    'conditions': [],
                },
                {
                    'need_return': True,
                    'free_conditions': [],
                    'force_allowed': False,
                    'force_punishments': [],
                    'type': 'return',
                },
                {'type': 'show_act'},
            ],
            id='open_battery_door action',
        ),
        pytest.param(
            'destination',
            'delivery_arrived',
            'missions/mission_id',
            'missions/mission_id',
            [
                {
                    'icon': 'open_battery_door',
                    'title': 'Отваряй',
                    'url': 'missions/task_id=mission_id&item_id=mission_id',
                    'type': 'deeplink',
                },
                {
                    'need_confirmation': True,
                    'type': 'dropoff',
                    'conditions': [],
                },
                {
                    'need_return': True,
                    'free_conditions': [],
                    'force_allowed': False,
                    'force_punishments': [],
                    'type': 'return',
                },
                {'type': 'show_act'},
            ],
            id='open_battery_door action for scooters-ops',
        ),
        pytest.param(
            'source',
            'pickup_arrived',
            'task_id_1',
            'item_id_1',
            [
                {
                    'free_conditions': [],
                    'force_allowed': True,
                    'force_punishments': [],
                    'blocked_restrictions': [],
                    'constructor_items': [],
                    'performer_cancel_reason_menu': {'reason_list': []},
                    'type': 'cancel',
                },
                {
                    'icon': 'battery_exchange',
                    'title': 'Забрать батарейки',
                    'url': (
                        'task_id=task_id_1&'
                        'current_point_id=seg_1_point_1&'
                        'current_claim_point_id=642499'
                    ),
                    'type': 'deeplink',
                },
                {
                    'need_confirmation': True,
                    'conditions': [],
                    'type': 'pickup',
                },
                {'type': 'show_act'},
            ],
            id='battery_exchange action',
        ),
        pytest.param(
            'source',
            'pickup_arrived',
            'missions/mission_id',
            'missions/mission_id',
            [
                {
                    'free_conditions': [],
                    'force_allowed': True,
                    'force_punishments': [],
                    'blocked_restrictions': [],
                    'constructor_items': [],
                    'performer_cancel_reason_menu': {'reason_list': []},
                    'type': 'cancel',
                },
                {
                    'icon': 'battery_exchange',
                    'title': 'Забрать батарейки',
                    'url': 'missions/task_id=mission_id',
                    'type': 'deeplink',
                },
                {
                    'need_confirmation': True,
                    'conditions': [],
                    'type': 'pickup',
                },
                {'type': 'show_act'},
            ],
            id='battery_exchange action for scooters-ops',
        ),
        pytest.param(
            'last_destination',
            'delivery_arrived',
            'task_id_1',
            'item_id_1',
            [
                {
                    'icon': 'battery_exchange_for_return',
                    'title': 'Вернуть батарейки',
                    'url': 'task_id=task_id_1',
                    'type': 'deeplink',
                },
                {
                    'need_confirmation': True,
                    'type': 'dropoff',
                    'conditions': [],
                },
                {'type': 'show_act'},
            ],
            id='battery_exchange_for_return action',
        ),
        pytest.param(
            'last_destination',
            'delivery_arrived',
            'missions/mission_id',
            'missions/mission_id',
            [
                {
                    'icon': 'battery_exchange_for_return',
                    'title': 'Вернуть батарейки',
                    'url': 'missions/task_id=mission_id',
                    'type': 'deeplink',
                },
                {
                    'need_confirmation': True,
                    'type': 'dropoff',
                    'conditions': [],
                },
                {'type': 'show_act'},
            ],
            id='battery_exchange_for_return action for scooters-ops',
        ),
    ],
)
async def test_scooters_actions(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_multipoints_waybill_info,
        current_point_type,
        claim_status,
        source_points_eoid,
        destination_point_eoid,
        expected_actions,
        mock_driver_tags_v1_match_profile,
):
    my_multipoints_waybill_info['execution']['segments'][0][
        'status'
    ] = claim_status

    source_point = my_multipoints_waybill_info['execution']['points'][0]
    destination_point = my_multipoints_waybill_info['execution']['points'][1]

    if current_point_type == 'source':
        pass
    elif current_point_type == 'destination':
        set_point_visited(my_multipoints_waybill_info, 0)
    elif current_point_type == 'last_destination':
        destination_points_ids = [
            i
            for (i, point) in enumerate(
                my_multipoints_waybill_info['execution']['points'],
            )
            if point['type'] == 'destination'
        ]
        last_dest_point_idx = destination_points_ids[-1]
        for i, _ in enumerate(
                my_multipoints_waybill_info['execution']['points'],
        ):
            if i < last_dest_point_idx:
                set_point_visited(my_multipoints_waybill_info, i)
    else:
        raise ValueError(f'Unknown current_point_type: {current_point_type}')

    source_point['external_order_id'] = source_points_eoid
    destination_point['external_order_id'] = destination_point_eoid

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    def _actions_sort_fn(action):
        return (action['type'], action.get('url', ''))

    response_actions = sorted(
        response.json()['current_point']['actions'], key=_actions_sort_fn,
    )
    expected_actions.sort(key=_actions_sort_fn)

    assert response_actions == expected_actions


# f
async def test_post_payment_comment(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        exp_cargo_point_comment_features,
        mock_driver_tags_v1_match_profile,
):
    """
        Check post_payment reminder is added to comment.
    """
    waybill_state.set_segment_status('delivery_arrived')
    waybill_state.set_post_payment()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    current_point = response.json()['current_point']
    assert (
        current_point['comment'] == '**Безналичная оплата при передаче**\n'
        'Код от подъезда/домофона: 123.\n'
        'Комментарий: comment 123'
    )
    assert (
        response.json()['order_comment']
        == 'Заказ с наложенным платежом.\nЗаказ с подтверждением по СМС.'
    )


@pytest.mark.now('2020-12-11 13:01:53.000000+03')
async def test_performer_cancel_reason_menu(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        experiments3,
        mock_driver_tags_v1_match_profile,
        insert_performer_order_cancel_statistics,
):
    insert_performer_order_cancel_statistics(
        dbid_uuid_='park_id1_driver_id1', cancel_count=3,
    )

    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'pickup_arrived'

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_claims_action_checks',
        consumers=['cargo-claims/driver'],
        clauses=[],
        default_value={
            'cancel': {
                'min_waiting_time_seconds': 0,
                'use_free_waiting_time_rules': False,
            },
        },
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_performer_order_cancel_reasons',
        consumers=['cargo-claims/driver'],
        clauses=[],
        default_value={
            'reason_list': [
                {
                    'reason_title_tanker_key': 'title',
                    'reason_subtitle_tanker_key': 'subtitle',
                    'id': 'id',
                    'taxi_id': 'taxi_id',
                    'use_blocked_restrictions': True,
                    'need_reorder': True,
                },
            ],
        },
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_performer_fines_performer_cancellations_limits',
        consumers=['cargo-orders/performer-cancellations-limits'],
        clauses=[],
        default_value={
            'free_cancellation_limit': 2,
            'required_completed_orders_to_reset_cancellation_limit': 30,
            'title_tanker_key': 'performer_cancel_limit_title',
            'subtitle_tanker_key': 'performer_cancel_limit_subtitle',
            'detail_tanker_key': 'performer_cancel_limit_detail',
            'right_icon_payload': {
                'text_tanker_key': 'performer_cancel_limit_right_icon',
            },
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 3

    assert response_body['current_point']['actions'] == [
        {'conditions': [], 'need_confirmation': True, 'type': 'pickup'},
        {
            'force_allowed': True,
            'force_punishments': [],
            'free_conditions': [
                {'type': 'time_after', 'value': '2020-12-11T10:01:53.000000Z'},
            ],
            'type': 'cancel',
            'blocked_restrictions': [],
            'constructor_items': [
                {
                    'accent': True,
                    'right_icon': 'more_info',
                    'type': 'detail',
                    'detail': '2 из 2',
                    'subtitle': 'Дальше штраф',
                    'title': 'Количество бесплатных отмен',
                    'right_icon_payload': {
                        'type': 'show_tooltip',
                        'tooltip': {
                            'text': (
                                'Нужно выполнить 30 заказов, '
                                'чтобы обнулить счётчик'
                            ),
                        },
                    },
                },
            ],
            'performer_cancel_reason_menu': {
                'reason_list': [
                    {
                        'reason_title': 'title',
                        'reason_subtitle': 'subtitle',
                        'id': 'id',
                    },
                ],
            },
        },
        {'type': 'show_act'},
    ]


@pytest.fixture(name='get_state')
async def _get_state(taxi_cargo_orders, default_order_id):
    async def wrapper(order_id=default_order_id):
        response = await taxi_cargo_orders.post(
            '/driver/v1/cargo-claims/v1/cargo/state',
            headers=DEFAULT_HEADERS,
            json={'cargo_ref_id': 'order/' + order_id},
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.mark.config(CARGO_ORDERS_RESTRICT_B_PHONE_ACCESS=True)
async def test_extra_phone_on_point(
        get_state,
        mock_waybill_info,
        waybill_state,
        exp_cargo_orders_on_point_phones,
        mock_driver_tags_v1_match_profile,
):
    """
        Check payment_on_delivery_support phone is added
        via config3.0 cargo_orders_on_point_phones.
    """
    await exp_cargo_orders_on_point_phones()

    waybill_state.set_segment_status('delivery_arrived')
    waybill_state.set_post_payment()

    response = await get_state()

    current_phones = sorted(
        response['current_point']['phones'], key=operator.itemgetter('type'),
    )
    assert current_phones == [
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
        {
            'background_loading': False,
            'label': 'Не получается провести оплату',
            'type': 'payment_on_delivery_support',
            'view': 'extra',
        },
        {
            'background_loading': False,
            'label': 'Пункт выдачи',
            'type': 'source',
            'view': 'main',
        },
    ]


@pytest.mark.config(CARGO_ORDERS_RESTRICT_B_PHONE_ACCESS=True)
async def test_phone_override(
        get_state,
        mock_waybill_info,
        waybill_state,
        exp_cargo_orders_on_point_phones,
        mock_driver_tags_v1_match_profile,
):
    """
        Check emergency phone label is overriden
        via config3.0 cargo_orders_on_point_phones.
    """
    await exp_cargo_orders_on_point_phones(
        overrides=[
            {
                'phone_type': 'emergency',
                'visible': {
                    'tanker_key': (
                        'yandex_pro.phones.payment_on_delivery_support'
                    ),
                    'view': 'extra',
                },
            },
        ],
    )

    waybill_state.set_segment_status('delivery_arrived')
    waybill_state.set_post_payment()

    response = await get_state()

    current_phones = sorted(
        response['current_point']['phones'], key=operator.itemgetter('type'),
    )
    assert current_phones == [
        {
            'background_loading': False,
            'label': 'Не получается провести оплату',
            'type': 'emergency',
            'view': 'extra',
        },
        {
            'background_loading': False,
            'label': 'Пункт выдачи',
            'type': 'source',
            'view': 'main',
        },
    ]


@pytest.mark.config(CARGO_ORDERS_RESTRICT_B_PHONE_ACCESS=True)
async def test_phone_override_hide(
        get_state,
        mock_waybill_info,
        waybill_state,
        exp_cargo_orders_on_point_phones,
        mock_driver_tags_v1_match_profile,
):
    """
        Check emergency phone is hidden
        via config3.0 cargo_orders_on_point_phones.
    """
    await exp_cargo_orders_on_point_phones(
        overrides=[{'phone_type': 'emergency'}],
    )

    waybill_state.set_segment_status('delivery_arrived')
    waybill_state.set_post_payment()

    response = await get_state()

    current_phones = sorted(
        response['current_point']['phones'], key=operator.itemgetter('type'),
    )
    assert current_phones == [
        {
            'background_loading': False,
            'label': 'Пункт выдачи',
            'type': 'source',
            'view': 'main',
        },
    ]


@pytest.mark.parametrize(
    ['source_phones', 'distination_phones'],
    [
        pytest.param(
            [
                {
                    'background_loading': False,
                    'label': 'Пункт выдачи',
                    'type': 'source',
                    'view': 'main',
                },
                {
                    'background_loading': False,
                    'label': 'Контакт для экстренных случаев',
                    'type': 'emergency',
                    'view': 'extra',
                },
            ],
            [
                {
                    'background_loading': False,
                    'label': 'Контакт для экстренных случаев',
                    'type': 'emergency',
                    'view': 'extra',
                },
            ],
            marks=pytest.mark.config(
                CARGO_ORDERS_RESTRICT_B_PHONE_ACCESS=True,
            ),
        ),
        pytest.param(
            [
                {
                    'background_loading': False,
                    'label': 'Пункт выдачи',
                    'type': 'source',
                    'view': 'main',
                },
                {
                    'background_loading': False,
                    'label': 'Получатель',
                    'type': 'destination',
                    'view': 'extra',
                },
                {
                    'background_loading': False,
                    'label': 'Контакт для экстренных случаев',
                    'type': 'emergency',
                    'view': 'extra',
                },
            ],
            [
                {
                    'background_loading': False,
                    'label': 'Получатель',
                    'type': 'destination',
                    'view': 'extra',
                },
                {
                    'background_loading': False,
                    'label': 'Контакт для экстренных случаев',
                    'type': 'emergency',
                    'view': 'extra',
                },
            ],
            marks=pytest.mark.config(
                CARGO_ORDERS_RESTRICT_B_PHONE_ACCESS=False,
            ),
        ),
    ],
)
async def test_distination_phone_unavalible(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        exp_cargo_orders_post_payment_flow,
        source_phones,
        distination_phones,
        mock_driver_tags_v1_match_profile,
):
    # Don't access destination phone while current_point is source
    waybill_state.set_segment_status('performer_found')

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    current_point = response.json()['current_point']
    assert current_point['phones'] == source_phones

    source_point = response.json()['current_route'][0]
    assert source_point['phones'] == source_phones

    destination_point = response.json()['current_route'][1]
    assert destination_point['phones'] == distination_phones


@pytest.mark.config(
    CARGO_ORDERS_RESTRICT_B_PHONE_ACCESS=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_scooters': '8.00'}},
    },
)
@pytest.mark.parametrize(
    ['current_point_type', 'claim_status', 'expected_deeplinks'],
    [
        pytest.param(
            'source',
            'pickup_arrived',
            [
                {
                    'type': 'deeplink',
                    'icon': 'battery_exchange',
                    'title': 'Забрать батарейки',
                    'url': 'task_id=task_id_1',
                },
            ],
            id='battery_exchange action',
        ),
    ],
)
async def test_distination_phone_unavalible_batched_order_before_point_a(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_multipoints_waybill_info,
        current_point_type,
        claim_status,
        expected_deeplinks,
        mock_driver_tags_v1_match_profile,
):
    my_multipoints_waybill_info['execution']['segments'][0][
        'status'
    ] = claim_status

    source_point = my_multipoints_waybill_info['execution']['points'][0]
    destination_point = my_multipoints_waybill_info['execution']['points'][1]

    source_point['external_order_id'] = 'task_id_1'
    destination_point['external_order_id'] = 'item_id_1'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    current_point = response.json()['current_point']
    assert current_point['phones'] == [
        {
            'background_loading': False,
            'label': 'Пункт выдачи',
            'type': 'source',
            'view': 'main',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]

    source_point = response.json()['current_route'][0]
    assert source_point['phones'] == [
        {
            'background_loading': False,
            'label': 'Пункт выдачи',
            'type': 'source',
            'view': 'main',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]

    destination_point_1 = response.json()['current_route'][1]
    assert destination_point_1['phones'] == [
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]

    destination_point_2 = response.json()['current_route'][2]
    assert destination_point_2['phones'] == [
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]


@pytest.mark.config(
    CARGO_ORDERS_RESTRICT_B_PHONE_ACCESS=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_scooters': '8.00'}},
    },
)
@pytest.mark.parametrize(
    ['current_point_type', 'claim_status', 'expected_deeplinks'],
    [
        pytest.param(
            'source',
            'pickup_arrived',
            [
                {
                    'type': 'deeplink',
                    'icon': 'battery_exchange',
                    'title': 'Забрать батарейки',
                    'url': 'task_id=task_id_1',
                },
            ],
            id='battery_exchange action',
        ),
    ],
)
async def test_distination_phone_avalible_batched_order_after_point_a(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_multipoints_waybill_info,
        current_point_type,
        claim_status,
        expected_deeplinks,
        mock_driver_tags_v1_match_profile,
):
    my_multipoints_waybill_info['execution']['segments'][0][
        'status'
    ] = claim_status

    source_point = my_multipoints_waybill_info['execution']['points'][0]
    destination_point = my_multipoints_waybill_info['execution']['points'][1]

    set_point_visited(my_multipoints_waybill_info, 0)
    my_multipoints_waybill_info['execution']['points'][0][
        'visit_status'
    ] = 'visited'

    source_point['external_order_id'] = 'task_id_1'
    destination_point['external_order_id'] = 'item_id_1'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    current_point = response.json()['current_point']
    # Source visited, it's destination
    assert current_point['phones'] == [
        {
            'background_loading': False,
            'label': 'Получатель',
            'type': 'destination',
            'view': 'extra',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]

    source_point = response.json()['current_route'][0]
    assert source_point['phones'] == [
        {
            'background_loading': False,
            'label': 'Пункт выдачи',
            'type': 'source',
            'view': 'main',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]

    destination_point_1 = response.json()['current_route'][1]
    assert destination_point_1['phones'] == [
        {
            'background_loading': False,
            'label': 'Получатель',
            'type': 'destination',
            'view': 'extra',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]

    destination_point_2 = response.json()['current_route'][2]
    assert destination_point_2['phones'] == [
        {
            'background_loading': False,
            'label': 'Получатель',
            'type': 'destination',
            'view': 'extra',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]


@pytest.mark.config(
    CARGO_ORDERS_RESTRICT_B_PHONE_ACCESS=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_scooters': '8.00'}},
    },
)
@pytest.mark.parametrize(
    ['current_point_type', 'claim_status', 'expected_deeplinks'],
    [
        pytest.param(
            'source',
            'pickup_arrived',
            [
                {
                    'type': 'deeplink',
                    'icon': 'battery_exchange',
                    'title': 'Забрать батарейки',
                    'url': 'task_id=task_id_1',
                },
            ],
            id='battery_exchange action',
        ),
    ],
)
async def test_distination_phone_avalible_on_c2c_order(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_multipoints_waybill_info,
        current_point_type,
        claim_status,
        expected_deeplinks,
        mock_driver_tags_v1_match_profile,
):
    my_multipoints_waybill_info['execution']['segments'][0][
        'status'
    ] = claim_status

    my_multipoints_waybill_info['execution']['segments'][0].pop(
        'corp_client_id',
    )

    source_point = my_multipoints_waybill_info['execution']['points'][0]
    destination_point = my_multipoints_waybill_info['execution']['points'][1]

    source_point['external_order_id'] = 'task_id_1'
    destination_point['external_order_id'] = 'item_id_1'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    current_point = response.json()['current_point']
    # Source visited, it's destination
    assert current_point['phones'] == [
        {
            'background_loading': False,
            'label': 'Пункт выдачи',
            'type': 'source',
            'view': 'main',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]

    source_point = response.json()['current_route'][0]
    assert source_point['phones'] == [
        {
            'background_loading': False,
            'label': 'Пункт выдачи',
            'type': 'source',
            'view': 'main',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]

    destination_point_1 = response.json()['current_route'][1]
    assert destination_point_1['phones'] == [
        {
            'background_loading': False,
            'label': 'Получатель',
            'type': 'destination',
            'view': 'extra',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]

    destination_point_2 = response.json()['current_route'][2]
    assert destination_point_2['phones'] == [
        {
            'background_loading': False,
            'label': 'Получатель',
            'type': 'destination',
            'view': 'extra',
        },
        {
            'background_loading': False,
            'label': 'Контакт для экстренных случаев',
            'type': 'emergency',
            'view': 'extra',
        },
    ]


@pytest.mark.parametrize('num_of_external_id', [1, 3])
async def test_external_order_id_returning_point_not_visited_all(
        taxi_cargo_orders,
        default_order_id,
        my_multipoints_waybill_info,
        num_of_external_id,
        mock_driver_tags_v1_match_profile,
):
    my_multipoints_waybill_info['execution']['points'][num_of_external_id][
        'external_order_id'
    ] = 'task_id_1'

    set_point_skipped(my_multipoints_waybill_info, 1)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    return_point = response.json()['current_route'][3]
    external_order_id = '1' if num_of_external_id == 3 else 'task_id_1'
    assert return_point['external_order_id'] == external_order_id


@pytest.mark.parametrize('num_of_external_id', [1, 3])
async def test_external_order_id_returning_point_current_point_visited_all(
        taxi_cargo_orders,
        default_order_id,
        my_multipoints_waybill_info,
        num_of_external_id,
        mock_driver_tags_v1_match_profile,
):
    my_multipoints_waybill_info['execution']['points'][num_of_external_id][
        'external_order_id'
    ] = 'task_id_1'

    set_point_skipped(my_multipoints_waybill_info, 1)
    for i in range(0, 3):
        if i != 1:
            set_point_visited(my_multipoints_waybill_info, i)
            my_multipoints_waybill_info['execution']['points'][i][
                'visit_status'
            ] = 'visited'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    current_point = response.json()['current_point']
    external_order_id = '1' if num_of_external_id == 3 else 'task_id_1'
    assert current_point['external_order_id'] == external_order_id
    assert current_point['type'] == 'return'
    return_point = response.json()['current_route'][3]
    assert return_point['external_order_id'] == external_order_id
    assert return_point['type'] == 'return'


@pytest.mark.parametrize(
    ['num_of_external_id_first', 'num_of_external_id_second'],
    [(3, 2), (4, 5)],
)
async def test_external_order_id_returning_points_from_batch_order(
        taxi_cargo_orders,
        my_batch_waybill_info,
        default_order_id,
        num_of_external_id_first,
        num_of_external_id_second,
        mock_driver_tags_v1_match_profile,
):
    my_batch_waybill_info['execution']['points'][num_of_external_id_first][
        'external_order_id'
    ] = 'task_id_1'
    my_batch_waybill_info['execution']['points'][num_of_external_id_second][
        'external_order_id'
    ] = 'task_id_2'

    set_point_skipped(my_batch_waybill_info, 2)
    set_point_skipped(my_batch_waybill_info, 3)
    for i in range(0, 2):
        set_point_visited(my_batch_waybill_info, i)
        my_batch_waybill_info['execution']['points'][i][
            'visit_status'
        ] = 'visited'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    current_point = response.json()['current_point']
    assert current_point['external_order_id'] == 'task_id_1'
    assert current_point['type'] == 'return'
    return_point = response.json()['current_route'][4]
    assert return_point['external_order_id'] == 'task_id_1'
    assert return_point['type'] == 'return'

    return_point_2 = response.json()['current_route'][5]
    assert return_point_2['external_order_id'] == 'task_id_2'
    assert return_point_2['type'] == 'return'


@pytest.mark.parametrize(
    ['markdown_enabled', 'escape_client_comment'],
    [(True, True), (True, False), (False, False)],
)
async def test_comment_and_multi_ids_check_config(
        taxi_cargo_orders,
        default_order_id,
        my_multipoints_waybill_info,
        experiments3,
        markdown_enabled,
        escape_client_comment,
        mock_driver_tags_v1_match_profile,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_build_point_comment',
        consumers=['cargo-orders/build-point-comment'],
        clauses=[],
        default_value={
            'external_order_ids_delimiter': '\n',
            'markdown_enabled': markdown_enabled,
            'escape_client_comment': escape_client_comment,
            'comment_multi_id_delimiters': {
                'between_ids': '\n ',
                'between_default_and_ids': '. ',
            },
        },
    )
    await taxi_cargo_orders.invalidate_caches()
    my_multipoints_waybill_info['execution']['points'][1][
        'external_order_id'
    ] = 'task_id_1'
    my_multipoints_waybill_info['execution']['points'][2][
        'external_order_id'
    ] = 'task_id_2'
    my_multipoints_waybill_info['execution']['points'][3]['address'][
        'comment'
    ] = 'A2_comment'

    set_point_skipped(my_multipoints_waybill_info, 1)
    set_point_skipped(my_multipoints_waybill_info, 2)

    set_point_visited(my_multipoints_waybill_info, 0)
    my_multipoints_waybill_info['execution']['points'][0][
        'visit_status'
    ] = 'visited'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    return_point = response.json()['current_route'][3]
    current_point = response.json()['current_point']
    assert return_point['external_order_id'] == 'task_id_1\ntask_id_2'
    assert current_point['external_order_id'] == 'task_id_1\ntask_id_2'
    if markdown_enabled:
        assert (
            return_point['address']['comment'] == 'A2_comment'
            '\\. Номер заказа: task\\_id\\_1\n task\\_id\\_2'
        )
        if escape_client_comment:
            assert (
                current_point['comment']
                == ESCAPED_CLIENT_COMMENT
                + '\\. Номер заказа: task\\_id\\_1\n task\\_id\\_2'
            )
        else:
            assert (
                current_point['comment']
                == CLIENT_COMMENT
                + '\\. Номер заказа: task\\_id\\_1\n task\\_id\\_2'
            )
    else:
        assert (
            return_point['address']['comment']
            == 'A2_comment. Номер заказа: task_id_1\n task_id_2'
        )
        assert (
            current_point['comment']
            == CLIENT_COMMENT + '. Номер заказа: task_id_1\n task_id_2'
        )


async def test_comment_and_multi_ids_check_no_config(
        taxi_cargo_orders,
        default_order_id,
        my_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    my_multipoints_waybill_info['execution']['points'][2][
        'external_order_id'
    ] = 'task_id_2'
    my_multipoints_waybill_info['execution']['points'][1][
        'external_order_id'
    ] = 'task_id_1'

    set_point_skipped(my_multipoints_waybill_info, 1)
    set_point_skipped(my_multipoints_waybill_info, 2)
    set_point_visited(my_multipoints_waybill_info, 0)
    my_multipoints_waybill_info['execution']['points'][0][
        'visit_status'
    ] = 'visited'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    current_point = response.json()['current_point']
    assert current_point['comment'] == ''


async def test_delivery_arrived_actions(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        exp_cargo_orders_post_payment_flow,
        mock_driver_tags_v1_match_profile,
):
    waybill_state.set_segment_status('delivery_arrived')
    waybill_state.set_payment_type('cash')
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    actions = sorted(
        response.json()['current_point']['actions'],
        key=operator.itemgetter('type'),
    )
    expected_actions = [
        {'need_confirmation': True, 'type': 'dropoff', 'conditions': []},
        {'type': 'show_act'},
        {'type': 'show_cash'},
    ]
    assert actions == expected_actions


async def test_background_loading(
        taxi_cargo_orders,
        experiments3,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_phone_background_loading',
        consumers=['cargo-orders/phone_background_loading'],
        clauses=[],
        default_value={'enabled': True},
    )

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'point_id': 1,
            'idempotency_token': 'some_token',
        },
    )

    assert response.status_code == 200
    phones = response.json()['current_point']['phones']
    assert phones[0]['background_loading']
    assert phones[1]['background_loading']
    assert phones[2]['background_loading']


@pytest.mark.config(
    CARGO_ORDERS_ROBO_WAREHOUSE_PARAMS={
        'enabled': True,
        'action': {
            'icon': 'icon_test',
            'title_key': 'title_test',
            'deeplink_tpl': 'link_test?link={link}',
        },
    },
)
@pytest.mark.translations(cargo={'title_test': {'ru': 'Заголовок экшена'}})
async def test_robo_warehouse_action(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    set_segment_status(my_waybill_info, 'pickup_arrived')
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'robo_warehouse': {
            'link_for_pickup_order': 'www.warehouse.com/open?orderId=1',
        },
    }
    my_waybill_info['execution']['segments'][0]['claim_features'] = [
        {'id': 'robo_warehouse'},
    ]

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    deeplink_action = next(
        a
        for a in response.json()['current_point']['actions']
        if a['type'] == 'deeplink'
    )
    assert deeplink_action == {
        'icon': 'icon_test',
        'type': 'deeplink',
        'url': 'link_test?link=www.warehouse.com/open?orderId=1',
        'title': 'Заголовок экшена',
    }


@pytest.mark.config(
    CARGO_ORDERS_ROBO_WAREHOUSE_PARAMS={
        'enabled': True,
        'action': {
            'icon': 'icon_test',
            'title_key': 'title_test',
            'deeplink_tpl': 'link_test?link={failed _ link}',
        },
    },
)
@pytest.mark.translations(cargo={'title_test': {'ru': 'Заголовок экшена'}})
async def test_robo_warehouse_wrong_deepling_tpl(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    set_segment_status(my_waybill_info, 'pickup_arrived')
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'robo_warehouse': {
            'link_for_pickup_order': 'www.warehouse.com/open?orderId=1',
        },
    }
    my_waybill_info['execution']['segments'][0]['claim_features'] = [
        {'id': 'robo_warehouse'},
    ]

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 500


def find_action(json_act, action_type):
    for action in json_act['current_point']['actions']:
        if action['type'] == action_type:
            return action
    return None


def find_condition_value(conditions, condition_type):
    for condition in conditions:
        if condition['type'] == condition_type:
            return condition['value']
    return None


async def test_robocall_action_is_created(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_orders_robocall_actions()

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',  # any time
    }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    assert find_action(response.json(), 'robocall') is not None


async def test_robocall_action_is_disabled_by_status(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_orders_robocall_actions()

    my_waybill_info['execution']['segments'][0]['status'] = 'pickuped'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',  # any time
    }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    assert find_action(response.json(), 'robocall') is None


@pytest.mark.parametrize(
    ['last_status_change_ts', 'expected_robocall'],
    [
        # last_status_change_ts is compared to promise_min_at.
        # The limit is configured in parameter
        # disable_robocall_if_courier_is_too_early_sec of experiment
        # cargo_orders_robocall_actions.
        pytest.param('2021-10-10T09:40:00+03:00', False, id='too early'),
        pytest.param('2021-10-10T09:40:01+03:00', True, id='not too early'),
    ],
)
async def test_robocall_action_check_too_early(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        mock_driver_tags_v1_match_profile,
        last_status_change_ts,
        expected_robocall,
):
    await exp_cargo_orders_robocall_actions()

    my_waybill_info['execution']['points'][0]['visit_status'] = 'arrived'
    my_waybill_info['execution']['points'][0][
        'last_status_change_ts'
    ] = last_status_change_ts

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',
    }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    robocall_is_found = find_action(response.json(), 'robocall') is not None
    assert robocall_is_found == expected_robocall


@pytest.mark.parametrize(
    [
        'promise_min_at',
        'time_after_signed_offset_sec',
        'expected_robocall',
        'expected_time_after',
    ],
    [
        pytest.param(
            '2021-10-10T22:22:22+00:00',
            0,
            True,
            '2021-10-10T22:22:22.000000Z',
            id='promise_min_at is specified',
        ),
        pytest.param(
            '2021-10-10T22:22:22+00:00',
            -10,
            True,
            '2021-10-10T22:22:12.000000Z',
            id='promise_min_at and offset are specified',
        ),
        pytest.param(
            None, 0, False, None, id='promise_min_at is not specified',
        ),
    ],
)
async def test_robocall_action_time_after(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        promise_min_at,
        time_after_signed_offset_sec,
        expected_robocall,
        expected_time_after,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_orders_robocall_actions(
        time_after_signed_offset_sec=time_after_signed_offset_sec,
    )

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    if promise_min_at is not None:
        my_waybill_info['execution']['segments'][0]['custom_context'] = {
            'promise_min_at': promise_min_at,
        }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    robocall_action = find_action(response.json(), 'robocall')
    if expected_robocall:
        value = find_condition_value(
            robocall_action['free_conditions'], 'time_after',
        )
        assert value == expected_time_after
    else:
        assert robocall_action is None


@pytest.mark.now('2021-10-10T10:10:00+03:00')
@pytest.mark.parametrize(
    ['robocall_status', 'promise_max_at', 'expected_robocall_action'],
    [
        pytest.param(
            None,
            None,
            {
                'type': 'robocall',
                'title': 'Клиент не отвечает',
                'robocall_reason': 'client_not_responding',
                'free_conditions': [
                    {
                        'type': 'time_after',
                        'value': '2021-10-10T07:00:00.000000Z',
                    },
                    {
                        'type': 'min_call_count',
                        # exp_cargo_orders_robocall_actions.min_call_count
                        'value': '1',
                    },
                ],
            },
        ),
        pytest.param(
            'calling',
            # promise_max_at is before end of total_timeout_sec.
            '2021-10-10T10:09:59+03:00',
            {
                'type': 'robocall',
                'title': 'Звоним клиенту',
                'robocall_reason': 'client_not_responding',
                'free_conditions': [
                    {
                        'type': 'time_after',
                        'value': '2021-10-10T07:00:00.000000Z',
                    },
                    {
                        'type': 'min_call_count',
                        # exp_cargo_orders_robocall_actions.min_call_count
                        'value': '1',
                    },
                ],
                # CARGO_ORDERS_EATS_CORE_ROBOCALL.total_timeout_sec +
                #   exp_cargo_orders_robocall_actions.
                #     robocall_timer_additional_time_sec
                'calling': {'calling_till': '2021-10-10T07:11:00+00:00'},
            },
        ),
        pytest.param(
            'calling',
            # promise_max_at is after end of total_timeout_sec.
            '2021-10-10T10:10:01+03:00',
            {
                'type': 'robocall',
                'title': 'Звоним клиенту',
                'robocall_reason': 'client_not_responding',
                'free_conditions': [
                    {
                        'type': 'time_after',
                        'value': '2021-10-10T07:00:00.000000Z',
                    },
                    {
                        'type': 'min_call_count',
                        # exp_cargo_orders_robocall_actions.min_call_count
                        'value': '1',
                    },
                ],
                # promise_max_at +
                #   exp_cargo_orders_robocall_actions.
                #     robocall_timer_additional_time_sec
                'calling': {'calling_till': '2021-10-10T07:11:01+00:00'},
            },
        ),
        pytest.param('finished', None, None),
    ],
)
async def test_robocall_action_by_status(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        prepare_order_client_robocall,
        robocall_status,
        promise_max_at,
        expected_robocall_action,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_orders_robocall_actions()

    if robocall_status is not None:
        prepare_order_client_robocall(
            default_order_id,
            my_waybill_info['execution']['points'][0]['point_id'],
            status=robocall_status,
        )

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',  # any time in the past
        'promise_max_at': promise_max_at,
    }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    robocall_action = find_action(response.json(), 'robocall')
    assert robocall_action == expected_robocall_action


SHOW_DIALOG_CLIENT_NOT_ANSWERED = {
    'type': 'show_dialog',
    'tag': 'robocall_client_not_answered',
    'title': 'Не дозвонились',
    'message': 'Позвоните в поддержку',
    'button': 'Хорошо4',
}


@pytest.mark.now('1970-01-01T03:10:00+03:00')
@pytest.mark.parametrize(
    [
        'robocall_status',
        'robocall_resolution',
        'robocall_updated_at',
        'expected_dialog_action',
        'expected_delayed_action_datetime',
        'expected_delayed_action_timestamp',
    ],
    [
        pytest.param(
            None, None, '1970-01-01T03:10:00+03:00', None, None, None,
        ),
        pytest.param(
            'calling',
            None,
            '1970-01-01T03:10:00+03:00',  # any time
            {
                'type': 'show_dialog',
                'tag': 'robocall_in_progress',
                'title': 'Пытаемся дозвониться',
                'message': 'Не уходите',
                'button': 'Хорошо1',
            },
            None,
            None,
        ),
        pytest.param(
            'finished',
            'order_cancelled',
            '1970-01-01T03:10:00+03:00',  # any time
            {
                'type': 'show_dialog',
                'tag': 'robocall_order_cancelled',
                'title': 'Заказ отменён',
                'message': 'Приятного аппетита',
                'button': 'Хорошо3',
            },
            None,
            None,
        ),
        pytest.param(
            'finished',
            'finished_by_attempts_limit',
            '1970-01-01T03:10:00+03:00',  # any time
            SHOW_DIALOG_CLIENT_NOT_ANSWERED,
            None,
            None,
        ),
        pytest.param(
            'finished',
            'finished_by_timeout',
            '1970-01-01T03:10:00+03:00',
            SHOW_DIALOG_CLIENT_NOT_ANSWERED,
            None,
            None,
        ),
        pytest.param(
            'finished',
            'finished_by_error',
            '1970-01-01T03:10:00+03:00',  # any time
            SHOW_DIALOG_CLIENT_NOT_ANSWERED,
            None,
            None,
        ),
        pytest.param(
            'finished',
            'disabled_by_experiment',
            '1970-01-01T03:10:00+03:00',  # any time
            SHOW_DIALOG_CLIENT_NOT_ANSWERED,
            None,
            None,
        ),
        pytest.param(
            'finished',
            'client_answered',
            # client_contacts_courier_timeout_sec is configured in
            # EXP_ROBOCALL_ACTIONS.
            # now < updated_at + client_contacts_courier_timeout_sec
            '1970-01-01T03:01:01+03:00',
            {
                'type': 'show_dialog',
                'tag': 'robocall_client_answered',
                'title': 'Дозвонились',
                'message': 'Ждите звонок клиента',
                'button': 'Хорошо2',
            },
            datetime.datetime(1970, 1, 1, 0, 10, 1),
            # '03:01:01+03:00'(61 sec) +
            # client_contacts_courier_timeout_sec(540 sec) =
            # 601 sec.
            # 601000000000 nanoseconds since '1970-01-01T03:00:00+03:00'
            601000000000,
        ),
        pytest.param(
            'finished',
            'client_answered',
            # client_contacts_courier_timeout_sec is configured in
            # EXP_ROBOCALL_ACTIONS.
            # now >= updated_at + client_contacts_courier_timeout_sec
            '1970-01-01T03:01:00+03:00',
            {
                'type': 'show_dialog',
                'tag': 'robocall_client_answered_long_ago',
                'title': 'Клиент позвонил?',
                'message': 'Если нет, свяжитесь с поддержкой',
                'button': 'Хорошо5',
            },
            None,
            None,
        ),
        pytest.param(
            'finished',
            'aborted_by_changed_order',
            '1970-01-01T03:10:00+03:00',  # any time
            None,
            None,
            None,
        ),
    ],
)
async def test_robocall_dialog_actions(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        prepare_order_client_robocall,
        robocall_status,
        robocall_resolution,
        robocall_updated_at,
        expected_dialog_action,
        expected_delayed_action_datetime,
        expected_delayed_action_timestamp,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_orders_robocall_actions()

    point_id = my_waybill_info['execution']['points'][0]['point_id']
    driver_id = my_waybill_info['execution']['taxi_order_info'][
        'performer_info'
    ]['driver_id']
    park_id = my_waybill_info['execution']['taxi_order_info'][
        'performer_info'
    ]['park_id']

    if robocall_status is not None:
        prepare_order_client_robocall(
            default_order_id,
            point_id,
            status=robocall_status,
            resolution=robocall_resolution,
            updated_ts=robocall_updated_at,
        )

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '1970-01-01T03:00:00+03:00',  # any time in the past
    }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    dialog_action = find_action(response.json(), 'show_dialog')
    assert dialog_action == expected_dialog_action

    if expected_delayed_action_datetime is not None:
        assert (
            stq.cargo_increment_and_update_setcar_state_version.times_called
            == 1
        )
        stq_call = (
            stq.cargo_increment_and_update_setcar_state_version.next_call()
        )
        assert (
            stq_call['id']
            == f'{default_order_id}_{park_id}_{driver_id}_'
            + f'{expected_delayed_action_timestamp}'
        )

        kwargs = stq_call['kwargs']
        assert kwargs['cargo_order_id'] == default_order_id
        assert kwargs['driver_profile_id'] == driver_id
        assert kwargs['park_id'] == park_id

        assert stq_call['eta'] == expected_delayed_action_datetime
    else:
        assert (
            stq.cargo_increment_and_update_setcar_state_version.times_called
            == 0
        )


async def test_hiding_next_unresolved_destination_route_points(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        experiments3,
        mock_driver_tags_v1_match_profile,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_hide_next_unresolved_destination_route_points',
        consumers=[
            'cargo-orders/hide-next-unresolved-destination-route-points',
        ],
        clauses=[
            {
                'title': 'Clause #1',
                'predicate': {
                    'init': {
                        'arg_name': 'driver_tags',
                        'value': 'eats_courier_from_region_1',
                        'set_elem_type': 'string',
                    },
                    'type': 'contains',
                },
                'value': {
                    'should_hide': True,
                    'additional_time_to_build_route_sec': 60,
                },
            },
        ],
        default_value={
            'should_hide': False,
            'additional_time_to_build_route_sec': 0,
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    for point in my_batch_waybill_info['execution']['points']:
        point['eta'] = '2020-07-20T11:08:00+00:00'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    assert {
        'calculation_awaited': False,
        'eta': '2020-07-20T11:08:00+00:00',
        'type': 'eta',
    } in response.json()['current_point']['actions']

    assert len(response.json()['current_route']) == 2

    # Simulate picking up both parcels and expect another point in route with
    # additional time
    for i in [0, 1]:
        set_point_visited(my_batch_waybill_info, i)
        my_batch_waybill_info['execution']['points'][i][
            'visit_status'
        ] = 'visited'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    assert {
        'calculation_awaited': False,
        'eta': '2020-07-20T11:09:00+00:00',
        'type': 'eta',
    } in response.json()['current_point']['actions']

    assert len(response.json()['current_route']) == 3


def check_prep_late_empty_reponse(response_body):
    dialog_action = find_action(response_body, 'show_dialog')
    assert dialog_action is None

    assert (
        'ui' not in response_body or 'screen_title' not in response_body['ui']
    )


def check_prep_late_valid_reponse(response_body):
    dialog_action = find_action(response_body, 'show_dialog')
    assert dialog_action == {
        'type': 'show_dialog',
        'tag': 'order_preparation_late',
        'title': 'Диалог - Заказ опаздывает',
        'message': 'Диалог - Обратитесь в поддержку',
        'button': 'Ок',
        'show_mode': 'notification_and_dialog',
        'notification': {
            'title': 'Нотификация - Заказ опаздывает',
            'body': 'Нотификация - Обратитесь в поддержку',
        },
        'buttons': [
            {
                'text': 'Ок',
                'appearance': 'secondary',
                'action': {'type': 'close_dialog'},
            },
            {
                'text': 'Перейти в поддержку',
                'appearance': 'main',
                'action': {'type': 'deeplink', 'url': 'https://url'},
            },
        ],
    }

    assert response_body['ui']['screen_title'] == {
        'appearance': 'screen_title_attention',
        'text': 'Заказ опаздывает',
    }


async def test_preparation_late_another_status(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        exp_cargo_preparation_late,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_preparation_late()

    my_waybill_info['execution']['cargo_order_info'] = {
        'order_id': default_order_id,
        'use_cargo_pricing': True,
    }
    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    check_prep_late_empty_reponse(response.json())

    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 0
    )


@pytest.mark.now('1970-01-01T03:10:00+03:00')
async def test_preparation_not_late(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        exp_cargo_preparation_late,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_preparation_late()

    driver_id = my_waybill_info['execution']['taxi_order_info'][
        'performer_info'
    ]['driver_id']
    park_id = my_waybill_info['execution']['taxi_order_info'][
        'performer_info'
    ]['park_id']

    my_waybill_info['execution']['cargo_order_info'] = {
        'order_id': default_order_id,
        'use_cargo_pricing': True,
    }
    my_waybill_info['execution']['segments'][0]['status'] = 'pickup_arrived'
    my_waybill_info['execution']['points'][0][
        'due'
    ] = '1970-01-01T03:10:00+03:00'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {}

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    check_prep_late_empty_reponse(response.json())

    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
    stq_call = stq.cargo_increment_and_update_setcar_state_version.next_call()
    # 1200000000000 nanoseconds since 1970-1-1
    assert (
        stq_call['id']
        == f'{default_order_id}_{park_id}_{driver_id}_1200000000000'
    )

    kwargs = stq_call['kwargs']
    assert kwargs['cargo_order_id'] == default_order_id
    assert kwargs['driver_profile_id'] == driver_id
    assert kwargs['park_id'] == park_id

    assert stq_call['eta'] == datetime.datetime(1970, 1, 1, 0, 20, 0)


@pytest.mark.now('1970-01-01T03:20:00+03:00')
async def test_preparation_late(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        exp_cargo_preparation_late,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_preparation_late()

    my_waybill_info['execution']['cargo_order_info'] = {
        'order_id': default_order_id,
        'use_cargo_pricing': True,
    }
    my_waybill_info['execution']['segments'][0]['status'] = 'pickup_arrived'
    my_waybill_info['execution']['points'][0][
        'due'
    ] = '1970-01-01T03:10:00+03:00'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {}

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    check_prep_late_valid_reponse(response.json())

    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 0
    )


@pytest.mark.now('1970-01-01T03:20:00+03:00')
async def test_preparation_late_fast_food(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        exp_cargo_preparation_late,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_preparation_late()

    driver_id = my_waybill_info['execution']['taxi_order_info'][
        'performer_info'
    ]['driver_id']

    my_waybill_info['execution']['cargo_order_info'] = {
        'order_id': default_order_id,
        'use_cargo_pricing': True,
    }
    my_waybill_info['execution']['segments'][0]['status'] = 'pickup_arrived'
    my_waybill_info['execution']['points'][0]['changelog'][0] = {
        'driver_id': driver_id,
        'cargo_order_id': default_order_id,
        'status': 'arrived',
        'timestamp': '1970-01-01T03:10:00+03:00',
    }
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'is_fast_food': True,
    }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    check_prep_late_valid_reponse(response.json())

    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 0
    )


@pytest.mark.parametrize(
    [
        'place_ids_list',
        'skip_points_list',
        'corp_client_ids_list',
        'coordinates_list',
        'current_point_number_of_parcels',
        'current_route_number_of_parcels_list',
    ],
    [
        pytest.param(
            [123456, 654321],
            None,
            None,
            [[1, 2], [2, 3], [3, 4], [4, 5]],
            1,
            [1, 1, 1, 1],
            id='Different source points place_ids',
        ),
        pytest.param(
            [123456, 123456],
            None,
            None,
            [[1, 2], [2, 3], [3, 4], [4, 5]],
            2,
            [2, 1, 1, 1],
            id='Same source points place_ids',
        ),
        pytest.param(
            [123456, 123456],
            [1, 2, 3, 4],
            None,
            [[1, 2], [2, 3], [3, 4], [4, 5]],
            2,
            [2, 1, 1, 1, 2, 1],
            id='Same return points place_ids',
        ),
        pytest.param(
            None,
            None,
            [None, None],
            [[1, 2], [2, 3], [3, 4], [4, 5]],
            1,
            [1, 1, 1, 1],
            id='Distant coordinates',
        ),
        pytest.param(
            None,
            None,
            ['corp1', None],
            [[1, 2], [2, 3], [3, 4], [4, 5]],
            1,
            [1, 1, 1, 1],
            id='Different corp_client_ids',
        ),
        pytest.param(
            None,
            None,
            ['corp1', 'corp1'],
            [[1, 2], [1, 2], [2, 3], [3, 4]],
            2,
            [2, 1, 1, 1],
            id='Same corp_client_ids and source coordinates',
        ),
        pytest.param(
            None,
            None,
            [None, None],
            [[1, 2], [1, 2], [2, 3], [3, 4]],
            2,
            [2, 1, 1, 1],
            id='Two c2c segments with same source coordinates',
        ),
    ],
)
async def test_number_of_parcels(
        taxi_cargo_orders,
        mock_driver_tags_v1_match_profile,
        mock_waybill_info,
        my_batch_waybill_info,
        default_order_id,
        place_ids_list,
        skip_points_list,
        corp_client_ids_list,
        coordinates_list,
        current_point_number_of_parcels,
        current_route_number_of_parcels_list,
):
    my_batch_waybill_info['execution']['points'][0]['is_resolved'] = False

    if place_ids_list is not None:
        for i, place_id in enumerate(place_ids_list):
            if place_id is None:
                continue
            my_batch_waybill_info['execution']['segments'][i][
                'custom_context'
            ] = {'place_id': place_id}

    if skip_points_list is not None:
        for i in skip_points_list:
            set_point_skipped(my_batch_waybill_info, i)

    if corp_client_ids_list is not None:
        for i, corp_client_id in enumerate(corp_client_ids_list):
            my_batch_waybill_info['execution']['segments'][i][
                'corp_client_id'
            ] = corp_client_id

    if coordinates_list is not None:
        for i, coordinates in enumerate(coordinates_list):
            my_batch_waybill_info['execution']['points'][i]['location'][
                'coordinates'
            ] = coordinates

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['current_route']) == len(
        current_route_number_of_parcels_list,
    )
    for i, number_of_parcels in enumerate(
            current_route_number_of_parcels_list,
    ):
        assert (
            resp_json['current_route'][i]['number_of_parcels']
            == number_of_parcels
        )

    assert (
        resp_json['current_point']['number_of_parcels']
        == current_point_number_of_parcels
    )


@pytest.mark.parametrize(
    [
        'visit_points_list',
        'skip_points_list',
        'current_point_number_of_parcels',
        'current_route_number_of_parcels_list',
    ],
    [
        pytest.param(None, None, 2, [2, 1, 1], id='Source point parcels'),
        pytest.param([0], [1], 1, [2, 1, 1, 1], id='Return a parcel'),
    ],
)
async def test_multipoints_number_of_parcels(
        taxi_cargo_orders,
        mock_driver_tags_v1_match_profile,
        mock_waybill_info,
        my_multipoints_waybill_info,
        default_order_id,
        visit_points_list,
        skip_points_list,
        current_point_number_of_parcels,
        current_route_number_of_parcels_list,
):
    if visit_points_list is not None:
        for i in visit_points_list:
            set_point_visited(my_multipoints_waybill_info, i)
    if skip_points_list is not None:
        for i in skip_points_list:
            set_point_skipped(my_multipoints_waybill_info, i)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    current_route = response.json()['current_route']
    assert len(current_route) == len(current_route_number_of_parcels_list)
    for i, number_of_parcels in enumerate(
            current_route_number_of_parcels_list,
    ):
        assert current_route[i]['number_of_parcels'] == number_of_parcels

    assert (
        response.json()['current_point']['number_of_parcels']
        == current_point_number_of_parcels
    )


@pytest.mark.parametrize(
    'external_order_id,external_order_id_markdown',
    [
        ('test_external_order_id', None),
        ('123123-', None),
        ('123123-456456', '123123-**456456**'),
        ('123123-456456-789789', '123123-456456-**789789**'),
    ],
)
async def test_external_order_id_markdown(
        taxi_cargo_orders,
        default_order_id,
        my_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
        external_order_id,
        external_order_id_markdown,
):
    my_multipoints_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = external_order_id

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    response_json = response.json()

    current_point = response_json['current_point']
    current_route = response_json['current_route']

    if external_order_id_markdown:
        assert (
            current_point['external_order_id_markdown']
            == external_order_id_markdown
        )

        assert (
            current_route[0]['external_order_id_markdown']
            == external_order_id_markdown
        )
        for index in range(1, len(current_route)):
            assert 'external_order_id_markdown' not in current_route[index]
    else:
        assert 'external_order_id_markdown' not in current_point
        for route_point in current_route:
            assert 'external_order_id_markdown' not in route_point


@pytest.mark.parametrize(
    'add_city_to_shortname,shortname_no_entrance',
    [(False, False), (True, False), (False, True), (True, True)],
)
async def test_address_localization_build_shortname(
        taxi_cargo_orders,
        mock_yamaps,
        my_waybill_info,
        set_up_cargo_orders_performer_localization_exp,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
        add_city_to_shortname,
        shortname_no_entrance,
        building='12c3',
        city='some_city',
        street='some_street',
        porch='4',
):
    """
        Check localization cache happy path.

        Get value from yamaps on first request.
        On second request get value from cache.
    """
    await set_up_cargo_orders_performer_localization_exp(
        check_shortname_building=True,
        build_shortname=True,
        add_city_to_shortname=add_city_to_shortname,
        shortname_no_entrance=shortname_no_entrance,
    )
    # Set 'building' to check matching
    my_waybill_info['execution']['points'][1]['address'][
        'fullname'
    ] = 'Point 2 fullname'
    my_waybill_info['execution']['points'][1]['address']['city'] = city
    my_waybill_info['execution']['points'][1]['address']['street'] = street
    my_waybill_info['execution']['points'][1]['address']['building'] = building
    my_waybill_info['execution']['points'][1]['address']['porch'] = porch

    # cache miss, store response to cache
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    # # no effect because value will be fetched from cache
    mock_yamaps(coordinates_override=[([37.642979, 55.734977], 'Aurora')])

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    address_localized = response.json()['current_route'][1]['address'][
        'shortname'
    ]
    address = my_waybill_info['execution']['points'][1]['address']
    shortname = ''
    if add_city_to_shortname:
        shortname += address['city'] + ', '
    shortname += '{}, {}'.format(address['street'], address['building'])
    if not shortname_no_entrance:
        shortname += ', ' + address['porch']
    assert address_localized == shortname


async def test_state_wrong_params(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        mock_driver_tags_v1_match_profile,
):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': ''},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'Bad cargo_ref_id ',
    }


async def test_replace_tag_comment(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        exp_cargo_point_comment_features,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_point_comment_features(
        post_payment_comment='comment.on_point.photo_control_parcel',
    )

    waybill_state.set_segment_status('delivery_arrived')
    waybill_state.set_post_payment()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    current_point = response.json()['current_point']
    assert (
        current_point['comment']
        == 'Если получатель предложил оставить посылку у двери,'
        '  сфотографируйте посылку там, где её оставите,'
        ' и [прикрепите фото в форму]'
        '(https://forms.yandex.ru/surveys/13304407.'
        '00e5b245e2e146a2adbdc094e190574c95ac4c7a/'
        '?lang=ru&?answer_short_text_111222=driver_id1'
        '&answer_short_text_111333=park_id1).\n'
        'Код от подъезда/домофона: 123.\n'
        'Комментарий: comment 123'
    )
    assert (
        response.json()['order_comment']
        == 'Заказ с наложенным платежом.\nЗаказ с подтверждением по СМС.'
    )


async def test_route_id_comment(
        taxi_cargo_orders,
        mock_driver_tags_v1_match_profile,
        mock_waybill_info,
        my_waybill_info,
        default_order_id,
        get_state,
        route_id='12345',
):
    my_waybill_info['execution']['cargo_order_info'] = {
        'order_id': default_order_id,
        'use_cargo_pricing': True,
        'route_id': route_id,
    }

    response = await get_state()
    assert 'Номер маршрута: 12345.' in response['order_comment']


@pytest.mark.parametrize(
    'driver_loyalty, exp_enabled, route_points',
    [
        (None, False, ['source', 'destination']),
        ({}, False, ['source', 'destination']),
        (None, True, ['source', 'destination']),
        ({}, True, ['source', 'destination']),
        (
            {
                'matched_driver_rewards': {
                    'point_b': {'show_point_b': False, 'lock_reasons': {}},
                },
            },
            False,
            ['source', 'destination'],
        ),
        (
            {
                'matched_driver_rewards': {
                    'point_b': {'show_point_b': False, 'lock_reasons': {}},
                },
            },
            True,
            ['source'],
        ),
        (
            {
                'matched_driver_rewards': {
                    'point_b': {'show_point_b': True, 'lock_reasons': {}},
                },
            },
            False,
            ['source', 'destination'],
        ),
        (
            {
                'matched_driver_rewards': {
                    'point_b': {'show_point_b': True, 'lock_reasons': {}},
                },
            },
            True,
            ['source', 'destination'],
        ),
    ],
)
async def test_hiding_points_by_loyalty(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_waybill_info,
        experiments3,
        mock_driver_tags_v1_match_profile,
        pgsql,
        driver_loyalty,
        exp_enabled,
        route_points,
):
    if driver_loyalty:
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
            UPDATE cargo_orders.orders_performers
            SET loyalty_rewards = %s
            """,
            (json.dumps(driver_loyalty),),
        )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_hide_points_by_loyalty',
        consumers=[
            'cargo-orders/hide-next-unresolved-destination-route-points',
        ],
        clauses=[],
        default_value={'enabled': exp_enabled},
    )
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    resp_body = response.json()
    point_types = [point['type'] for point in resp_body['current_route']]
    assert point_types == route_points

    # Simulate arriving
    for i in [0, 1]:
        my_waybill_info['execution']['points'][i]['visit_status'] = 'arrived'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    resp_body = response.json()
    point_types = [point['type'] for point in resp_body['current_route']]
    assert point_types == ['source', 'destination']


@pytest.mark.now('2020-12-11 13:01:53.000000+03')
async def test_new_cancellations_counter(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        my_batch_waybill_info,
        experiments3,
        mock_driver_tags_v1_match_profile,
        insert_performer_order_cancel_statistics,
        mockserver,
        exp_cargo_orders_use_performer_fines_service,
):
    @mockserver.json_handler('/cargo-performer-fines/performer/statistics')
    def mock_performer_statistics(request):
        assert request.query == {
            'driver_id': 'driver_id1',
            'park_id': 'park_id1',
        }
        return mockserver.make_response(
            status=200,
            json={
                'driver_id': 'driver_id1',
                'park_id': 'park_id1',
                'cancellations_statistics': {
                    'cancellation_count_after_last_reset': 1,
                    'completed_orders_count_after_last_cancellation': 6,
                    'updated_ts': '2020-07-20T11:08:00+00:00',
                },
            },
        )

    insert_performer_order_cancel_statistics(
        dbid_uuid_='park_id1_driver_id1', cancel_count=3,
    )

    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'pickup_arrived'

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_claims_action_checks',
        consumers=['cargo-claims/driver'],
        clauses=[],
        default_value={
            'cancel': {
                'min_waiting_time_seconds': 0,
                'use_free_waiting_time_rules': False,
            },
        },
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_performer_order_cancel_reasons',
        consumers=['cargo-claims/driver'],
        clauses=[],
        default_value={
            'reason_list': [
                {
                    'reason_title_tanker_key': 'title',
                    'reason_subtitle_tanker_key': 'subtitle',
                    'id': 'id',
                    'taxi_id': 'taxi_id',
                    'use_blocked_restrictions': True,
                    'need_reorder': True,
                },
            ],
        },
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_performer_fines_performer_cancellations_limits',
        consumers=['cargo-orders/performer-cancellations-limits'],
        clauses=[],
        default_value={
            'free_cancellation_limit': 3,
            'required_completed_orders_to_reset_cancellation_limit': 35,
            'title_tanker_key': 'performer_cancel_limit_title',
            'subtitle_tanker_key': 'performer_cancel_limit_subtitle',
            'detail_tanker_key': 'performer_cancel_limit_detail',
            'right_icon_payload': {
                'text_tanker_key': 'performer_cancel_limit_right_icon',
            },
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['current_point']['id'] == 3

    assert response_body['current_point']['actions'] == [
        {'conditions': [], 'need_confirmation': True, 'type': 'pickup'},
        {
            'force_allowed': True,
            'force_punishments': [],
            'free_conditions': [
                {'type': 'time_after', 'value': '2020-12-11T10:01:53.000000Z'},
            ],
            'type': 'cancel',
            'blocked_restrictions': [],
            'constructor_items': [
                {
                    'accent': True,
                    'right_icon': 'more_info',
                    'type': 'detail',
                    'detail': '1 из 3',
                    'subtitle': 'Дальше штраф',
                    'title': 'Количество бесплатных отмен',
                    'right_icon_payload': {
                        'type': 'show_tooltip',
                        'tooltip': {
                            'text': (
                                'Нужно выполнить 29 заказов, '
                                'чтобы обнулить счётчик'
                            ),
                        },
                    },
                },
            ],
            'performer_cancel_reason_menu': {
                'reason_list': [
                    {
                        'reason_title': 'title',
                        'reason_subtitle': 'subtitle',
                        'id': 'id',
                    },
                ],
            },
        },
        {'type': 'show_act'},
    ]
    assert mock_performer_statistics.times_called == 1


@pytest.mark.experiments3(
    is_config=True,
    name='cargo_orders_add_sdd_comment',
    consumers=['cargo-orders/add-sdd-comment'],
    default_value={
        'enabled': True,
        'tanker_key': 'comment.sdd_extra_pay_comment',
    },
)
@pytest.mark.translations(
    cargo={'comment.sdd_extra_pay_comment': {'ru': 'СДД КОММЕНТ'}},
)
async def test_sdd_comment(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        waybill_state,
        exp_cargo_point_comment_features,
        mock_driver_tags_v1_match_profile,
):
    waybill_state.set_segment_status('delivery_arrived')
    my_waybill_info['waybill']['router_id'] = 'cargo_same_day_delivery_router'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    assert (
        response.json()['order_comment']
        == 'СДД КОММЕНТ\nЗаказ с подтверждением по СМС.'
    )
