import pytest

from eats_layout_constructor import configs


@pytest.mark.parametrize(
    'widget_template_id,expected_status,request_data,expected_data',
    [
        (
            1,
            200,
            {
                'id': 1,
                'type': 'banners',
                'name': 'Widget template 1',
                'meta_schema': {},
                'meta': {'format': 'classic', 'field_1': 'value_1'},
                'payload_schema': {'type': 'object'},
                'payload': {
                    'field_2': 'value_3',
                    'background_color_dark': '#ffffff',
                },
            },
            {
                'id': 1,
                'type': 'banners',
                'name': 'Widget template 1',
                'meta_schema': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'advert': {
                            'title': 'Только рекламные баннеры?',
                            'default': False,
                            'description': (
                                'Включает или выключает запросы на'
                                ' рекламные блоки в '
                                'eats-communications'
                            ),
                            'type': 'boolean',
                        },
                        'banner_types': {
                            'title': 'Типы баннеров',
                            'description': (
                                'Типы баннеров отображаемых в виджете'
                            ),
                            'type': 'array',
                            'x-taxi-cpp-type': 'std::unordered_set',
                            'items': {
                                'type': 'string',
                                'enum': [
                                    'place',
                                    'brand',
                                    'collection',
                                    'info',
                                    'stories',
                                ],
                            },
                        },
                        'banners_id': {
                            'title': (
                                'ID баннеров, которые должны быть в виджете'
                            ),
                            'description': 'Список конкретных id банеров',
                            'type': 'array',
                            'x-taxi-cpp-type': 'std::unordered_set',
                            'items': {'type': 'integer'},
                        },
                        'exclude': {
                            'title': (
                                'ID баннеров, которые не должны быть в виджете'
                            ),
                            'description': (
                                'Список id баннеров иключенных из выборки'
                            ),
                            'type': 'array',
                            'x-taxi-cpp-type': 'std::unordered_set',
                            'items': {'type': 'integer'},
                        },
                        'format': {
                            'description': 'Формат отображения баннеров',
                            'title': 'Формат баннеров',
                            'type': 'string',
                            'enum': ['classic', 'shortcut', 'wide_and_short'],
                        },
                        'limit': {
                            'title': 'Лимит',
                            'description': (
                                'Максимальное число баннеров в виджете'
                            ),
                            'type': 'integer',
                            'x-taxi-cpp-type': 'std::size_t',
                            'minimum': 0,
                        },
                        'offset': {
                            'title': 'Начальный индекс',
                            'description': (
                                'Индекс элмента, с которого необходимо '
                                'отображть баннеры'
                            ),
                            'type': 'integer',
                            'x-taxi-cpp-type': 'std::size_t',
                            'minimum': 0,
                        },
                        'min_count': {
                            'title': 'Минимальное количество баннеров',
                            'description': (
                                'Минимальное число элементов в '
                                'карусели для отображения'
                            ),
                            'type': 'integer',
                            'x-taxi-cpp-type': 'std::size_t',
                            'minimum': 0,
                        },
                        'randomize': {
                            'title': (
                                'Перемешивать баннеры в случайном порядке?'
                            ),
                            'type': 'boolean',
                            'description': (
                                'Нужно ли перемешать баннеры '
                                'в случайном порядке.'
                            ),
                            'default': False,
                        },
                        'surge_condition': {
                            'title': (
                                'Настройки показа баннеров в зависимости от '
                                'суржа'
                            ),
                            'additionalProperties': False,
                            'description': (
                                'Условие отображения виджета в '
                                'зависимости от количества '
                                'суржащих заведений в подвыборке '
                                'каталога'
                            ),
                            'properties': {
                                'exclude_businesses': {
                                    'title': 'Исключенные типы заведений',
                                    'description': (
                                        'Набор типов заведений, '
                                        'которые надо исключить '
                                        'из виджета'
                                    ),
                                    'items': {
                                        'enum': [
                                            'restaurant',
                                            'shop',
                                            'store',
                                        ],
                                        'type': 'string',
                                    },
                                    'type': 'array',
                                    'x-taxi-cpp-type': 'std::set',
                                },
                                'limit': {
                                    'title': (
                                        'Максимальное количество ресторанов '
                                        'в блоке'
                                    ),
                                    'description': (
                                        'Количество ресторанов, которое '
                                        'вернется в блоке из каталога.'
                                    ),
                                    'minimum': 0,
                                    'type': 'integer',
                                    'x-taxi-cpp-type': 'std::size_t',
                                },
                                'min_surge_places_count': {
                                    'title': (
                                        'Минимальное количеcтво суржащих '
                                        'заведений'
                                    ),
                                    'description': (
                                        'Минимальное количество суржащих, '
                                        'найтивных, заведений для '
                                        'отображения виджета'
                                    ),
                                    'minimum': 0,
                                    'type': 'integer',
                                    'x-taxi-cpp-type': 'std::size_t',
                                },
                                'min_radius_surge_orders_percent': {
                                    'title': (
                                        'Минимальный процент срезаемых суржом '
                                        'заказов'
                                    ),
                                    'description': (
                                        'Минимальный процент заказов в '
                                        'заведениях, '
                                        'выключенных суржом радиуса. '
                                        'Если процент меньше минимального - '
                                        'виджет не будет отображаться.'
                                    ),
                                    'minimum': 0,
                                    'maximum': 100,
                                    'type': 'integer',
                                },
                            },
                            'required': ['limit'],
                            'type': 'object',
                        },
                        'depends_on_any': {
                            'title': 'Показывать только с виджетами',
                            'description': (
                                'Массив ID виджетов от которых зависит '
                                'нужно ли рисовать Banner, если есть '
                                'хоть один из них в Layout. '
                                'Если массив пустой - Banner будет '
                                'рисоваться всегда.'
                            ),
                            'items': {'type': 'string'},
                            'type': 'array',
                            'x-taxi-cpp-type': 'std::unordered_set',
                        },
                        'not_show_with': {
                            'title': 'Не показывать с виджетами',
                            'description': (
                                'Массив ID виджетов от которых зависит '
                                'нужно ли рисовать Banner. '
                                'Если он не пустой и хоть один '
                                'из виджетов есть в Layout, '
                                'то Banner не отображается.'
                            ),
                            'items': {'type': 'string'},
                            'type': 'array',
                            'x-taxi-cpp-type': 'std::unordered_set',
                        },
                    },
                    'required': ['format'],
                },
                'meta': {'format': 'classic', 'field_1': 'value_1'},
                'payload_schema': {'type': 'object'},
                'payload': {
                    'field_2': 'value_3',
                    'background_color_dark': '#ffffff',
                },
            },
        ),
        (
            28,
            404,
            {
                'id': 1,
                'type': 'banners',
                'name': 'Widget template 1',
                'meta_schema': {},
                'meta': {'format': 'classic', 'field_1': 'value_1'},
                'payload_schema': {'type': 'object'},
                'payload': {'field_2': 'value_3'},
            },
            {
                'code': 'WIDGET_TEMPLATE_IS_NOT_FOUND',
                'message': 'Widget template with id \'28\' is not found',
            },
        ),
        (
            28,
            400,
            {
                'id': 1,
                'type': 'banners',
                'name': 'Widget template 1',
                'meta_schema': {},
                'meta': {'field_1': 'value_1'},
                'payload_schema': {'type': 'object'},
                'payload': {
                    'field_2': 'value_3',
                    'background_color_dark': '#fffff',
                },
            },
            {
                'code': 'ColorInvalidError',
                'message': (
                    '\'#fffff\' is not valid hex color for key '
                    '\'background_color_dark\''
                ),
            },
        ),
        pytest.param(
            1,
            400,
            {
                'id': 1,
                'type': 'banners',
                'name': 'Widget template 1',
                'meta_schema': {},
                'meta': {'field_1': 'value_1'},
                'payload_schema': {'type': 'object'},
                'payload': {
                    'field_2': 'value_3',
                    'background_color_dark': '#ffffff',
                },
            },
            {
                'code': 'WidgetValidationError',
                'message': (
                    'Widget with type \'banners\' is not valid: '
                    'Field \'format\' is missing'
                ),
            },
            id='missing required field',
        ),
        pytest.param(
            1,
            400,
            {
                'id': 1,
                'type': 'banners',
                'name': 'Widget template 1',
                'meta_schema': {},
                'meta': {'format': 'classic', 'limit': 2147483648},
                'payload_schema': {'type': 'object'},
                'payload': {
                    'field_2': 'value_3',
                    'background_color_dark': '#ffffff',
                },
            },
            {
                'code': 'WidgetValidationError',
                'message': (
                    'Widget with type \'banners\' is not valid: '
                    'Value of \'limit\' is out of bounds '
                    '(-2147483648 <= 2147483648 <= 2147483647)'
                ),
            },
            id='integer overflow',
        ),
        pytest.param(
            1,
            400,
            {
                'id': 1,
                'type': 'banners',
                'name': 'Widget template 1',
                'meta_schema': {},
                'meta': {'format': 'classic'},
                'payload_schema': {'type': 'object'},
                'payload': {},
            },
            {
                'code': 'WidgetTemplateUsedInFallbackLayoutError',
                'message': (
                    'Widget template is not editable because it is used '
                    'in fallback layouts. Fallback layout slugs: [layout_1].'
                ),
            },
            id='widget template used in fallback layout',
            marks=[configs.fallback_layout('layout_1')],
        ),
    ],
)
async def test_update_widget_templates(
        taxi_eats_layout_constructor,
        mockserver,
        widget_template_id,
        expected_status,
        request_data,
        expected_data,
):
    await taxi_eats_layout_constructor.run_periodic_task('layout-status')
    response = await taxi_eats_layout_constructor.put(
        'layout-constructor/v1/constructor/widget-templates/',
        params={'widget_template_id': widget_template_id},
        json=request_data,
    )
    assert response.status == expected_status
    assert response.json() == expected_data
