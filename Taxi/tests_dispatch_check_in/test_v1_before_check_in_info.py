import pytest

DEFAULT_APPLICATION = (
    'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=4,app_brand=yataxi'
)


@pytest.mark.parametrize(
    'order_id, user_phone_id, pickup_lines_config, tariff_class, '
    'expected_response_status, expected_error_code, '
    'resources_exp3_enabled,   expected_subtitle, '
    'expected_waiting_subtitle, expected_alert_title',
    [
        (
            'order_id',
            'some_phone_id',
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            'econom',
            200,
            None,
            False,
            'Не торопитесь и следуйте инструкции',
            'Подтверждаем',
            'Заказ отменён службой такси',
        ),
        (
            'default_exp3_order_id',
            'some_phone_id',
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            'econom',
            200,
            None,
            True,
            'Default user, Не торопитесь и следуйте инструкции',
            'Default user, Подтверждаем',
            'Default user, Заказ отменён службой такси',
        ),
        (
            'exp3_order_id_2',
            'some_phone_id2',
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            'econom',
            200,
            None,
            True,
            'User 2, Не торопитесь и следуйте инструкции',
            'User 2, Подтверждаем',
            'User 2, Заказ отменён службой такси',
        ),
        (
            'order_id_with_instruction',
            'some_phone_with_qr_code',
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            'econom',
            200,
            None,
            False,
            'Не торопитесь и следуйте инструкции',
            'Подтверждаем',
            'Заказ отменён службой такси',
        ),
        (
            'order_id_with_two_button_card_type',
            'some_phone_with_two_button_card_type',
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            'econom',
            200,
            None,
            False,
            'Не торопитесь и следуйте инструкции',
            'Подтверждаем',
            'Заказ отменён службой такси',
        ),
        (
            'order_id_with_three_button_card_type',
            'some_phone_with_three_button_card_type',
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            'econom',
            200,
            None,
            False,
            'Не торопитесь и следуйте инструкции',
            'Подтверждаем',
            'Заказ отменён службой такси',
        ),
        (
            'order_id',
            'some_phone_id',
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            'comfort',
            400,
            'FAILED_TO_DEDUCE_PICKUP_LINE',
            False,
            '',
            '',
            '',
        ),
        (
            'order_id',
            'some_phone_id',
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': [],
                    'check_in_zone_coordinates': [10, 10],
                },
            },
            'econom',
            400,
            'FAILED_TO_DEDUCE_PICKUP_LINE',
            False,
            '',
            '',
            '',
        ),
        (
            'order_id',
            'some_phone_id',
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': ['econom'],
                    'pickup_points': ['test_pickup_point'],
                },
            },
            'econom',
            400,
            'FAILED_TO_DEDUCE_PICKUP_LINE',
            False,
            '',
            '',
            '',
        ),
    ],
)
@pytest.mark.experiments3(filename='before_check_in_experiments.json')
async def test_v1_before_check_in_info(
        experiments3,
        load_json,
        taxi_config,
        taxi_dispatch_check_in,
        order_id,
        user_phone_id,
        pickup_lines_config,
        tariff_class,
        expected_response_status,
        expected_error_code,
        resources_exp3_enabled,
        expected_subtitle,
        expected_waiting_subtitle,
        expected_alert_title,
):
    #
    taxi_config.set(DISPATCH_CHECK_IN_PICKUP_LINES=pickup_lines_config)

    if resources_exp3_enabled:
        experiments3.add_experiments_json(
            load_json('static_resources_experiments.json'),
        )

    headers = {
        'X-Request-Language': 'ru',
        'X-YaTaxi-PhoneId': user_phone_id,
        'X-Request-Application': DEFAULT_APPLICATION,
    }
    request_params = {
        'order_id': order_id,
        'pickup_point_uri': 'test_pickup_point',
        'tariff_class': tariff_class,
    }

    response = await taxi_dispatch_check_in.get(
        '/v1/before-check-in-info', params=request_params, headers=headers,
    )

    assert response.status == expected_response_status

    if expected_error_code is None:
        expected_action_type = (
            'qr_code'
            if user_phone_id == 'some_phone_with_qr_code'
            else 'button'
        )
        expected_card_type = {
            'some_phone_with_two_button_card_type': 'two_button',
            'some_phone_with_three_button_card_type': 'three_button',
        }.get(user_phone_id, 'classic')
        etalon = {
            'check_in_zones': [
                {'geopoint': [10.0, 10.0], 'pickup_line_id': 'svo_line_1'},
            ],
            'instruction': {
                'image_tag': 'dispatch_check_in_instruction_image_tag',
                'promo_id': 'dispatch_check_in_instruction_promo_id',
                'show_steps_button_title': 'Покажите, как туда пройти',
                'skip_steps_button_title': 'Да, я иду к зоне посадки',
                'subtitle': expected_subtitle,
                'title': 'Машины уже есть на нашей парковке',
                'hint_button_title': 'Как пройти',
                'show_by_default': order_id == 'order_id_with_instruction',
            },
            'status_info': {
                'translations': {
                    'card': {
                        'title_template': 'Нажмите, когда будете на остановке',
                        'subtitle_template': 'Назначим машину с остановки',
                    },
                },
            },
            'check_in_action': {
                'title': 'Я на месте',
                'waiting_title': 'Подтверждаем',
                'subtitle': 'Я на месте',
                'waiting_subtitle': expected_waiting_subtitle,
                'type': expected_action_type,
            },
            'order_status_alert': {
                'title': expected_alert_title,
                'text': 'Долго шёл',
                'change_params_button_text': 'Изменить',
                'retry_button_text': 'Повторить',
            },
            'ui_config': {
                'check_in_action': {
                    'title': 'Я на месте',
                    'waiting_title': 'Подтверждаем',
                    'subtitle': 'Я на месте',
                    'waiting_subtitle': expected_waiting_subtitle,
                    'type': expected_action_type,
                },
                'card_type': expected_card_type,
                'details_action': {'title': 'Детали'},
            },
        }
        assert response.json() == etalon
    else:
        assert response.json()['code'] == expected_error_code
