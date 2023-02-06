import pytest

from eats_layout_constructor import configs


@pytest.mark.parametrize(
    'meta_widget_id,expected_status,request_data,expected_data',
    [
        (
            1,
            200,
            {
                'id': 1,
                'type': 'place_layout',
                'slug': 'first_meta_widget',
                'name': 'first meta widget',
                'settings_schema': {
                    'hero_photo': {
                        'type': 'object',
                        'additionalProperties': False,
                        'description': (
                            'Настройки фотографий на карточке заведения.'
                        ),
                        'properties': {
                            'limit': {
                                'description': (
                                    'Ограничение количества '
                                    'фотографий на карточке.\n'
                                    'Если значение меньше еденицы, '
                                    'ограничение не применяется.\n'
                                ),
                                'minimum': 0,
                                'type': 'integer',
                            },
                        },
                        'required': ['limit'],
                    },
                },
                'settings': {
                    'hero_photo': {'limit': 1},
                    'order': ['meta', 'actions'],
                    'action_extenders': ['actions_info'],
                    'meta_extenders': ['meta_info'],
                },
            },
            {
                'id': 1,
                'type': 'place_layout',
                'slug': 'order_existing',
                'name': 'first meta widget',
                'settings_schema': {
                    'additionalProperties': False,
                    'properties': {
                        'hero_photo': {
                            'type': 'object',
                            'additionalProperties': False,
                            'description': (
                                'Настройки фотографий на карточке заведения.'
                            ),
                            'properties': {
                                'limit': {
                                    'description': (
                                        'Ограничение количества '
                                        'фотографий на карточке.\n'
                                        'Если значение меньше еденицы, '
                                        'ограничение не применяется.\n'
                                    ),
                                    'minimum': 0,
                                    'type': 'integer',
                                },
                            },
                            'required': ['limit'],
                        },
                        'action_extenders': {
                            'items': {
                                'type': 'string',
                                'enum': [
                                    'actions_review',
                                    'actions_info',
                                    'actions_plus_promo',
                                    'actions_promo',
                                    'actions_repeat_order',
                                    'actions_zen',
                                    'actions_experiment_extender',
                                    'actions_special_project',
                                    'actions_badge_extender',
                                ],
                            },
                            'type': 'array',
                        },
                        'max_actions_count': {'type': 'integer'},
                        'max_meta_count': {'type': 'integer'},
                        'meta_extenders': {
                            'items': {
                                'type': 'string',
                                'enum': [
                                    'meta_rating',
                                    'meta_price_category',
                                    'meta_info',
                                    'meta_advertisements',
                                    'meta_experiment_extender',
                                    'meta_yandex_plus',
                                ],
                            },
                            'type': 'array',
                        },
                        'order': {
                            'items': {
                                'enum': ['actions', 'meta'],
                                'type': 'string',
                            },
                            'type': 'array',
                        },
                    },
                    'required': [
                        'action_extenders',
                        'meta_extenders',
                        'order',
                    ],
                    'type': 'object',
                },
                'settings': {
                    'hero_photo': {'limit': 1},
                    'order': ['meta', 'actions'],
                    'action_extenders': ['actions_info'],
                    'meta_extenders': ['meta_info'],
                },
            },
        ),
        (
            1,
            400,
            {
                'id': 1,
                'type': 'place_layout',
                'slug': 'first_meta_widget',
                'name': 'first meta widget',
                'settings_schema': {},
                'settings': {
                    'action_extenders': ['actions_info'],
                    'meta_extenders': ['meta_info'],
                },
            },
            {
                'code': 'INVALID_SETTINGS',
                'message': 'Can\'t parse meta widget settings',
            },
        ),
        (
            1,
            400,
            {
                'id': 1,
                'type': 'super_unknown_type',
                'slug': 'first_meta_widget',
                'name': 'first meta widget',
                'settings_schema': {},
                'settings': {
                    'action_extenders': ['actions_info'],
                    'meta_extenders': ['meta_info'],
                },
            },
            {
                'code': 'UNKNOWN_TYPE',
                'message': 'Got unknown meta widget type: super_unknown_type',
            },
        ),
        (
            100500,
            404,
            {
                'id': 100500,
                'type': 'place_layout',
                'slug': 'first_meta_widget',
                'name': 'first meta widget',
                'settings_schema': {},
                'settings': {
                    'order': ['meta', 'actions'],
                    'action_extenders': ['actions_info'],
                    'meta_extenders': ['meta_info'],
                },
            },
            {
                'code': 'META_WIDGET_NOT_FOUND',
                'message': 'Meta widget with id \'100500\' is not found',
            },
        ),
        pytest.param(
            1,
            400,
            {
                'id': 1,
                'type': 'place_layout',
                'slug': 'first_meta_widget',
                'name': 'first meta widget',
                'settings_schema': {},
                'settings': {
                    'action_extenders': ['actions_info'],
                    'meta_extenders': ['meta_info'],
                    'order': ['meta', 'actions'],
                },
            },
            {
                'code': 'WidgetTemplateUsedInFallbackLayoutError',
                'message': (
                    'Meta widget is not editable because it is used '
                    'in fallback layouts. Fallback layout slugs: [layout_1].'
                ),
            },
            id='widget template used in fallback layout',
            marks=[configs.fallback_layout('layout_1')],
        ),
    ],
)
async def test_put_meta_widgets(
        taxi_eats_layout_constructor,
        mockserver,
        meta_widget_id,
        expected_status,
        request_data,
        expected_data,
):
    await taxi_eats_layout_constructor.run_periodic_task('layout-status')
    response = await taxi_eats_layout_constructor.put(
        'layout-constructor/v1/constructor/meta-widgets/',
        json=request_data,
        params={'meta_widget_id': meta_widget_id},
    )
    assert response.status == expected_status
