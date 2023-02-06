# pylint: disable=too-many-lines
import pytest

MOCKED_NOW = '2021-10-20T09:00:00+03:00'


def _set_fields_to_candidate(
        order_proc,
        driver_metrics,
        udid,
        add_chain_parent,
        tags,
        tariff_zone=None,
):
    order_proc['fields']['candidates'][0]['driver_metrics'] = driver_metrics
    order_proc['fields']['candidates'][0]['udid'] = udid

    if tags is not None:
        order_proc['fields']['candidates'][0]['tags'] = tags

    if tariff_zone is not None:
        order_proc['fields']['order']['nz'] = tariff_zone

    if add_chain_parent:
        order_proc['fields']['candidates'][0]['cp'] = {
            'dest': [1.1, 2.2],
            'id': 'asdasdasdas',
        }


def _get_penalty_info(
        is_blocking,
        new_value,
        blocking_value,
        blocking_hours,
        blocking_prediction,
):
    wait_title = 'Риск потери доступа'
    wait_subtitle = (
        f'Приоритет за заказы без пропусков снизится до {new_value} '
        f'балла, а уже при {blocking_value} наступит блокировка'
    )

    if is_blocking:
        wait_title = 'Потеря доступа'
        wait_subtitle = (
            'Отмена снизит Приоритет за заказы'
            ' без пропусков. Вы сможете принимать заказы '
            f'только через {blocking_hours} часа.'
        )

        if blocking_hours == 1:
            wait_subtitle = (
                'Отмена снизит Приоритет за заказы'
                ' без пропусков. Вы сможете принимать заказы '
                f'только через {blocking_hours} час.'
            )
    return {
        'cancel_screen': {
            'regular_wait_penalty_exists': True,
            'regular_wait_title': wait_title,
            'regular_wait_subtitle': wait_subtitle,
            'long_wait_title': 'Укажите причину отмены',
            'long_wait_subtitle': '',
        },
        'reject_notification_text': (
            f'Приоритет понижен {blocking_prediction["n"]}\nПропуск заказа'
        ),
        'regular_wait_cancel_notification_text': (
            'Приоритет '
            f'понижен {blocking_prediction["a"]}\n'
            'Отмена принятого заказа'
        ),
        'auto_cancel_notification_text': (
            f'Приоритет понижен {blocking_prediction["o"]}\nПропуск заказа'
        ),
    }


@pytest.mark.experiments3(filename='exp3_replace_activity_with_priority.json')
@pytest.mark.parametrize(
    'udid,driver_metrics,add_chain_parent,'
    'expected_points_info,expected_penalty_info,tags,tariff_zone',
    [
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'activity': 60,
                'activity_blocking': {
                    'activity_threshold': 20,
                    'duration_sec': 3600,
                },
                'activity_prediction': {'c': 5, 'n': -5, 'p': 0},
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {
                'c': 5,
                'n': -5,
                'p': 0,
                'long_wait_cancel': 0,
                'c_title': 'Активность: 5 баллов',
                'long_wait_cancel_title': 'Укажите причину отмены',
                'n_subtitle': (
                    'При потере ещё 36 баллов наступит блокировка на 1 час'
                ),
                'n_title': 'Активность: -5 баллов',
                'p_subtitle': (
                    'Примите следующий заказ, чтобы восстановить показатель'
                ),
                'p_title': 'Активность: 0 баллов',
            },
            None,
            [],
            None,
        ),
        (
            'udid-with-enabled-false',
            {
                'activity': 60,
                'activity_blocking': {
                    'activity_threshold': 20,
                    'duration_sec': 3600,
                },
                'activity_prediction': {'c': 5, 'n': -5, 'p': 0},
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {
                'c': 5,
                'n': -5,
                'p': 0,
                'long_wait_cancel': 0,
                'c_title': 'Активность: 5 баллов',
                'long_wait_cancel_title': 'Укажите причину отмены',
                'n_subtitle': (
                    'При потере ещё 36 баллов наступит блокировка на 1 час'
                ),
                'n_title': 'Активность: -5 баллов',
                'p_subtitle': (
                    'Примите следующий заказ, чтобы восстановить показатель'
                ),
                'p_title': 'Активность: 0 баллов',
            },
            None,
            [],
            None,
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(True, 0, -3, 2, {'a': -5, 'n': -4, 'o': -3}),
            [],
            'moscow',
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(True, 0, -3, 2, {'a': -5, 'n': -4, 'o': -3}),
            [],
            'kazan',
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(True, 0, -3, 2, {'a': -5, 'n': -4, 'o': -3}),
            [],
            'kirov',
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(True, 0, -3, 2, {'a': -5, 'n': -4, 'o': -3}),
            ['test_tag', 'another'],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'activity': 60,
                'activity_blocking': {
                    'activity_threshold': 20,
                    'duration_sec': 3600,
                },
                'activity_prediction': {'c': 5, 'n': -5, 'p': 0},
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            None,
            None,
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(True, 0, -3, 2, {'a': -5, 'n': -4, 'o': -3}),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 5,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(False, 0, -3, 2, {'a': -5, 'n': -4, 'o': -3}),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 5,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -1},
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(False, 0, -1, 2, {'a': -5, 'n': -4, 'o': -3}),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 5,
                'priority_blocking': {'duration_sec': 7200, 'threshold': 0},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            None,
            {
                'cancel_screen': {
                    'long_wait_title': 'Укажите причину отмены',
                    'long_wait_subtitle': '',
                },
            },
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 5,
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(False, 0, -10, 1, {'a': -5, 'n': -4, 'o': -3}),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': -7,
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(True, -12, -10, 1, {'a': -5, 'n': -4, 'o': -3}),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 400,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -500},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            True,
            {'a': -5},
            _get_penalty_info(
                True, -100, 0, 2, {'a': -500, 'n': -500, 'o': -500},
            ),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 400,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -500},
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -500},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            True,
            {'a': -5},
            _get_penalty_info(
                False, -100, -500, 2, {'a': -500, 'n': -500, 'o': -500},
            ),
            [],
            None,
        ),
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_driver_points_info(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        udid,
        driver_metrics,
        add_chain_parent,
        expected_points_info,
        expected_penalty_info,
        setcar_create_params,
        tags,
        tariff_zone,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response1.json')
    _set_fields_to_candidate(
        order_proc.order_proc,
        driver_metrics,
        udid,
        add_chain_parent,
        tags,
        tariff_zone,
    )

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert (
        response_json.get('driver_points_info', None) == expected_points_info
    )
    assert (
        response_json.get('priority_penalty_info', None)
        == expected_penalty_info
    )


@pytest.mark.experiments3(filename='exp3_replace_activity_with_priority.json')
@pytest.mark.parametrize(
    'udid,driver_metrics,add_chain_parent,'
    'expected_points_info,expected_penalty_info,tags',
    [
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 5,
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -5},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(False, 0, -77, 4, {'a': -5, 'n': -4, 'o': -3}),
            [],
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': -76,
                'priority_prediction': {'a': -5, 'n': -4, 'o': -3, 'p': -5},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {'a': -5},
            _get_penalty_info(True, -81, -77, 4, {'a': -5, 'n': -4, 'o': -3}),
            [],
        ),
    ],
)
@pytest.mark.now(MOCKED_NOW)
@pytest.mark.config(
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 1}},
            'letter_events': {'c': {'activity': 1}},
            'priority_blocking': {'threshold': -77, 'duration_sec': 4 * 3600},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 300,
        'tags': {
            'multioffer_order': {'offer_timeout': ['chained_order']},
            'order': {'auto_reorder': ['long_waiting', 'eta_autoreorder']},
        },
    },
)
async def test_driver_points_info_with_config_fallback(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        udid,
        driver_metrics,
        add_chain_parent,
        expected_points_info,
        expected_penalty_info,
        setcar_create_params,
        tags,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response1.json')
    _set_fields_to_candidate(
        order_proc.order_proc, driver_metrics, udid, add_chain_parent, tags,
    )

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert (
        response_json.get('driver_points_info', None) == expected_points_info
    )
    assert (
        response_json.get('priority_penalty_info', None)
        == expected_penalty_info
    )


def _get_priority_element(bonus):
    return {
        'accent_title': True,
        'horizontal_divider_type': 'full',
        'left_icon': {
            'icon_size': 'large',
            'icon_type': 'radar',
            'tint_color': 'main_control',
        },
        'primary_text_color': 'minor_amber',
        'reverse': True,
        'subtitle': f'+{bonus}',
        'title': 'Приоритет',
        'type': 'icon_detail',
    }


def _get_cancel_button_blocking():
    return {
        'title': 'Пропустить',
        'title_text_color': '#FFFFFF',
        'subtitle': 'Риск ограничения доступа',
        'subtitle_text_color': '#FFFFFF',
        'background_color': '#F5523A',
    }


def _get_cancel_button_notify(value_change):
    return {
        'title': 'Пропустить',
        'title_text_color': 'main_text',
        'subtitle': f'Приоритет {value_change}',
        'subtitle_text_color': 'main_text',
        'background_color': 'main_bg',
    }


def _get_cancel_button_empty():
    return {
        'title': 'Пропустить',
        'title_text_color': 'main_text',
        'background_color': 'main_bg',
    }


CANCEL_DIALOG_TEMPLATE = (
    'При пропуске Приоритет снизится и вы '
    'будете заблокированы на {duration} {measure}'
)
MINUTES = 'минуты'
HOURS = 'час'


def _get_cancel_dialog_params(duration, minutes_test: bool = False):
    if minutes_test:
        text = CANCEL_DIALOG_TEMPLATE.format(
            duration=duration, measure=MINUTES,
        )
    elif duration == 1:
        text = CANCEL_DIALOG_TEMPLATE.format(duration=duration, measure=HOURS)
    else:
        text = CANCEL_DIALOG_TEMPLATE.format(
            duration=duration, measure=f'{HOURS}а',
        )

    return {'text': text}


@pytest.mark.experiments3(filename='exp3_replace_activity_with_priority.json')
@pytest.mark.parametrize(
    'udid,driver_metrics,add_chain_parent,'
    'expected_priority_or_activity_item, '
    'expected_cancel_button, expected_cancel_dialog,'
    'tags, tariff_zone',
    [
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'activity': 60,
                'activity_blocking': {
                    'activity_threshold': 20,
                    'duration_sec': 3600,
                },
                'activity_prediction': {'c': 5, 'n': -5, 'p': 0},
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {
                'accent_title': True,
                'horizontal_divider_type': 'full',
                'left_icon': {
                    'icon_size': 'large',
                    'icon_type': 'activity',
                    'tint_color': '#00ca50',
                },
                'primary_text_color': '#00945e',
                'reverse': True,
                'subtitle': '+5',
                'title': 'Активность',
                'type': 'icon_detail',
            },
            None,
            None,
            [],
            None,
        ),
        (
            'udid-with-enabled-false',
            {
                'activity': 60,
                'activity_blocking': {
                    'activity_threshold': 20,
                    'duration_sec': 3600,
                },
                'activity_prediction': {'c': 5, 'n': -5, 'p': 0},
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            {
                'accent_title': True,
                'horizontal_divider_type': 'full',
                'left_icon': {
                    'icon_size': 'large',
                    'icon_type': 'activity',
                    'tint_color': '#00ca50',
                },
                'primary_text_color': '#00945e',
                'reverse': True,
                'subtitle': '+5',
                'title': 'Активность',
                'type': 'icon_detail',
            },
            None,
            None,
            [],
            None,
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {
                    'a': -1,
                    'n': -4,
                    'o': -1,
                    'p': -1,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_blocking(),
            _get_cancel_dialog_params(2),
            ['test_tag', 'another'],
            None,
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {
                    'a': -1,
                    'n': -4,
                    'o': -1,
                    'p': -1,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_blocking(),
            _get_cancel_dialog_params(2),
            [],
            'moscow',
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {
                    'a': -1,
                    'n': -4,
                    'o': -1,
                    'p': -1,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_blocking(),
            _get_cancel_dialog_params(2),
            [],
            'kazan',
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {
                    'a': -1,
                    'n': -4,
                    'o': -1,
                    'p': -1,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_blocking(),
            _get_cancel_dialog_params(2),
            [],
            'kirov',
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {
                    'a': -1,
                    'n': -4,
                    'o': -1,
                    'p': -1,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_blocking(),
            _get_cancel_dialog_params(2),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 120, 'threshold': -3},
                'priority_prediction': {
                    'a': -1,
                    'n': -4,
                    'o': -1,
                    'p': -1,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_blocking(),
            _get_cancel_dialog_params(2, minutes_test=True),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -2},
                'priority_prediction': {
                    'a': -5,
                    'o': -5,
                    'p': -5,
                    'n': -2,
                    'c': 4,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(4),
            _get_cancel_button_notify(-2),
            None,
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -2},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            None,
            _get_cancel_button_empty(),
            None,
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {
                    'a': -5,
                    'n': -5,
                    'o': -5,
                    'p': -3,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            True,
            _get_priority_element(3),
            _get_cancel_button_notify(-3),
            None,
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {
                    'a': -1,
                    'n': -1,
                    'o': -1,
                    'p': -5,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            True,
            _get_priority_element(3),
            _get_cancel_button_blocking(),
            _get_cancel_dialog_params(2),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_prediction': {
                    'a': -1,
                    'n': -12,
                    'o': -1,
                    'p': -5,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_blocking(),
            _get_cancel_dialog_params(1),
            [],
            None,
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_prediction': {
                    'a': -1,
                    'n': -7,
                    'o': -1,
                    'p': -5,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_notify(-7),
            None,
            [],
            None,
        ),
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_cancel_params(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        udid,
        driver_metrics,
        add_chain_parent,
        expected_priority_or_activity_item,
        expected_cancel_button,
        expected_cancel_dialog,
        setcar_create_params,
        tags,
        tariff_zone,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response1.json')
    _set_fields_to_candidate(
        order_proc.order_proc,
        driver_metrics,
        udid,
        add_chain_parent,
        tags,
        tariff_zone,
    )

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    if expected_priority_or_activity_item is None:
        assert 'left' not in response_json['ui']['acceptance_items'][0]
    else:
        assert (
            response_json['ui']['acceptance_items'][0]['left']
            == expected_priority_or_activity_item
        )
    assert (
        response_json['ui'].get('cancel_button_params', None)
        == expected_cancel_button
    )
    assert (
        response_json['ui'].get('confirm_cancel_dialog_params', None)
        == expected_cancel_dialog
    )


@pytest.mark.experiments3(filename='exp3_replace_activity_with_priority.json')
@pytest.mark.parametrize(
    'udid,driver_metrics,add_chain_parent,'
    'expected_priority_or_activity_item, '
    'expected_cancel_button, expected_cancel_dialog,'
    'tags',
    [
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_prediction': {
                    'a': -1,
                    'n': -78,
                    'o': -1,
                    'p': -1,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_blocking(),
            _get_cancel_dialog_params(4),
            [],
        ),
        (
            '5e31a8cba11531e403ad310a',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_prediction': {
                    'a': -75,
                    'n': -76,
                    'o': -75,
                    'p': -75,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            False,
            _get_priority_element(3),
            _get_cancel_button_notify(-76),
            None,
            [],
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 1}},
            'letter_events': {'c': {'activity': 1}},
            'priority_blocking': {'threshold': -77, 'duration_sec': 4 * 3600},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 300,
        'tags': {
            'multioffer_order': {'offer_timeout': ['chained_order']},
            'order': {'auto_reorder': ['long_waiting', 'eta_autoreorder']},
        },
    },
)
@pytest.mark.now(MOCKED_NOW)
async def test_cancel_params_config_fallback(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        udid,
        driver_metrics,
        add_chain_parent,
        expected_priority_or_activity_item,
        expected_cancel_button,
        expected_cancel_dialog,
        setcar_create_params,
        tags,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response1.json')
    _set_fields_to_candidate(
        order_proc.order_proc, driver_metrics, udid, add_chain_parent, tags,
    )

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    if expected_priority_or_activity_item is None:
        assert 'left' not in response_json['ui']['acceptance_items'][0]
    else:
        assert (
            response_json['ui']['acceptance_items'][0]['left']
            == expected_priority_or_activity_item
        )
    assert (
        response_json['ui'].get('cancel_button_params', None)
        == expected_cancel_button
    )
    assert (
        response_json['ui'].get('confirm_cancel_dialog_params', None)
        == expected_cancel_dialog
    )
