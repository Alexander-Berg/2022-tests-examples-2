import json

import pytest

from tests_grocery_pro_bdu import models


@pytest.mark.parametrize(
    'driver_profile_id, park_id, expected_status',
    [('driver_id1', 'park_id1', 200)],
)
@models.TIMER_CONFIG_ETA_TEXT
@models.COMMON_CONFIG
async def test_simple(
        taxi_grocery_pro_bdu,
        default_order_id,
        driver_profile_id,
        park_id,
        expected_status,
        mockserver,
        my_waybill_assemble,
):
    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_assemble,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()['state']['ui']['items'][0]['items'][0] == {
            'id': 'timer_id',
            'type': 'custom',
            'subtype': 'timer',
            'data': {
                'calculation_awaited': True,
                'description': 'Заказ собирается',
                'eta': '1970-01-01T00:00:00+00:00',
                'eta_type': 'text',
            },
        }

        assert response.json()['state']['point']['actions'][1] == {
            'type': 'navigator',
            'coordinates': [37.642979, 55.734977],
        }

        assert response.json()['state']['point']['actions'][2] == {
            'calculation_awaited': True,
            'description': 'Заказ собирается',
            'eta': '1970-01-01T00:00:00+00:00',
            'eta_type': 'text',
            'type': 'eta',
        }


@models.TIMER_CONFIG_ETA_TEXT
@models.COMMON_CONFIG
async def test_first_screen_ui(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_assemble,
        load_json,
):
    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_assemble,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    example_ui = load_json('first_screen_example.json')['ui']
    assert response.json()['state']['ui'] == example_ui


async def test_never_show_order_id_before_assemble(load_json):
    example_data = load_json('first_screen_example.json')
    data = json.dumps(example_data)
    assert data.find('external_order_id') == -1


@pytest.mark.experiments3(
    name='grocery_timers_settings',
    consumers=['grocery-pro-bdu/timer'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'eta_type': 'timer',
        'description_key': 'ride_card_grocery_going_back_screen_title',
    },
    is_config=True,
)
@models.COMMON_CONFIG
async def test_return_screen_ui(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_return,
        load_json,
):
    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_return,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    example_ui = load_json('going_back_screen.json')['ui']
    assert response.json()['state']['ui'] == example_ui


@pytest.mark.experiments3(
    name='grocery_timers_settings',
    consumers=['grocery-pro-bdu/timer'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'colors': ['main_text', 'minor_blue', 'main_red'],
        'eta_type': 'timer',
        'description_key': 'ride_card_grocery_arrive_screen_title',
    },
    is_config=True,
)
@models.COMMON_CONFIG
async def test_going_to_client_screen_ui(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_going_to_client,
        load_json,
):
    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_going_to_client,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    example_ui = load_json('going_to_client.json')['ui']
    assert response.json()['state']['ui'] == example_ui


@pytest.mark.experiments3(
    name='grocery_timers_settings',
    consumers=['grocery-pro-bdu/timer'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'eta_type': 'text',
        'description_key': 'ride_card_grocery_drop_off_title',
    },
    is_config=True,
)
@models.COMMON_CONFIG
async def test_at_client_screen_ui(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_at_client,
        load_json,
):
    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_at_client,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    example_ui = load_json('at_client_screen.json')['ui']
    assert response.json()['state']['ui'] == example_ui


@pytest.mark.experiments3(
    name='grocery_timers_settings',
    consumers=['grocery-pro-bdu/timer'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'eta_type': 'text',
        'description_key': 'ride_card_grocery_drop_off_title',
    },
    is_config=True,
)
@models.COMMON_CONFIG
async def test_at_client_all_modificators(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_at_client,
        load_json,
):
    my_waybill_at_client['execution']['points'][1]['leave_under_door'] = True
    my_waybill_at_client['execution']['points'][1]['meet_outside'] = True
    my_waybill_at_client['execution']['points'][1]['no_door_call'] = True

    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_at_client,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200
    example_ui = load_json('modificators.json')
    assert response.json()['state']['ui']['items'][0]['items'][1] == example_ui


@pytest.mark.experiments3(
    name='grocery_timers_settings',
    consumers=['grocery-pro-bdu/timer'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'eta_type': 'text',
        'description_key': 'ride_card_grocery_drop_off_title',
    },
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_pro_bdu_common',
    consumers=['grocery-pro-bdu/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'support_navigate_url': 'https://taxi-frontend.taxi.tst.yandex.ru/webview/driver-support/main?order_id=ORDER_ID_PLACEHOLDER&some_stuff',  # noqa F401
        'not_answering_navigate_url': 'https://taxi-frontend.taxi.tst.yandex.ru/webview/driver-support/documents/view/taximeter-lavka/from-order/not-contacted.html?order_id=ORDER_ID_PLACEHOLDER',  # noqa F401
        'check_age_title_tanker_key': 'constructor.age_check_title',
        'check_age_title_modal_body_tanker_key': (
            'constructor.age_check_modal_body'
        ),
    },
    is_config=True,
)
async def test_replace_order_id_placeholder(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_at_client,
        load_json,
):
    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_at_client,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    assert (
        response.json()['state']['ui']['items'][2]['items'][0]['payload'][
            'url'
        ]
        == 'https://taxi-frontend.taxi.tst.yandex.ru/webview/driver-support/documents/view/taximeter-lavka/from-order/not-contacted.html?order_id=100620-760097'  # noqa F401
    )
    assert (
        response.json()['state']['ui']['items'][2]['items'][2]['payload'][
            'url'
        ]
        == 'https://taxi-frontend.taxi.tst.yandex.ru/webview/driver-support/main?order_id=100620-760097&some_stuff'  # noqa F401
    )


@pytest.mark.experiments3(
    name='grocery_pro_bdu_common',
    consumers=['grocery-pro-bdu/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'support_navigate_url': 'support_navigate_url',
        'not_answering_navigate_url': 'not_answering_navigate_url',
        'check_age_title_tanker_key': 'constructor.age_check_title',
        'check_age_title_modal_body_tanker_key': (
            'constructor.age_check_modal_body'
        ),
        'disable_slider': False,
    },
    is_config=True,
)
async def test_slider_enabled(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_pickup,
        load_json,
):
    my_waybill_pickup['execution']['points'][0]['is_resolved'] = False
    my_waybill_pickup['execution']['points'][0]['was_ready_at'] = None
    my_waybill_pickup['execution']['segments'][0][
        'status'
    ] = 'ready_for_pickup_confirmation'

    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_pickup,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    assert response.json()['state']['point']['actions'][0]['conditions'] == []


@models.TIMER_CONFIG_ETA_TEXT
@models.COMMON_CONFIG
async def test_order_cancelled(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_order_cancelled,
):
    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_order_cancelled,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    actions = response.json()['state']['point']['actions']
    dialog_action = next(
        filter(lambda x: x['type'] == 'show_dialog', actions), None,
    )

    expected_action = {
        'type': 'show_dialog',
        'tag': 'lavka_point_skipped_notify',
        'message': 'actions.show_dialog.point_skipped_message',
        'button': 'Ок',
        'title': 'actions.show_dialog.point_skipped_title',
        'notification': {
            'body': 'actions.show_dialog.point_skipped_message',
            'title': 'actions.show_dialog.point_skipped_title',
        },
        'show_mode': 'notification_and_dialog',
    }

    assert dialog_action == expected_action


@pytest.mark.experiments3(
    name='grocery_timers_settings',
    consumers=['grocery-pro-bdu/timer'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'eta_type': 'text',
        'description_key': 'ride_card_grocery_drop_off_title',
    },
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_pro_bdu_common',
    consumers=['grocery-pro-bdu/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'support_navigate_url': 'https://taxi-frontend.taxi.tst.yandex.ru/webview/driver-support/main?order_id=ORDER_ID_PLACEHOLDER&some_stuff',  # noqa F401
        'not_answering_navigate_url': 'https://taxi-frontend.taxi.tst.yandex.ru/webview/driver-support/documents/view/taximeter-lavka/from-order/not-contacted.html?order_id=ORDER_ID_PLACEHOLDER',  # noqa F401
        'check_age_title_tanker_key': 'constructor.age_check_title',
        'check_age_title_modal_body_tanker_key': (
            'constructor.age_check_modal_body'
        ),
    },
    is_config=True,
)
async def test_age_check(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_at_client,
        load_json,
):
    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_at_client,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    assert (
        response.json()['state']['ui']['items'][0]['items'][1]['items'][1][
            'payload'
        ]['items'][0]['title']
        == 'Проверьте возраст клиента.'
    )
    assert (
        response.json()['state']['ui']['items'][0]['items'][1]['items'][1][
            'payload'
        ]['items'][1]['text']
        == 'В заказе есть товары для людей старше 18 лет.'
    )
