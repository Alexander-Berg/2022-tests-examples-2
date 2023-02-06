import pytest


def get_data(meta=None, payload=None):
    if not meta:
        meta = {'format': 'classic', 'field_1': 'value_1'}
    if not payload:
        payload = {'field_2': 'value_2', 'background_color_dark': '#ffffff'}
    return {
        'type': 'banners',
        'name': 'Widget template 1',
        'meta_schema': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'advert': {
                    'default': False,
                    'description': (
                        'Включает или выключает запросы на '
                        'рекламные блоки в eats-communications'
                    ),
                    'type': 'boolean',
                    'title': 'Только рекламные баннеры?',
                },
                'banner_types': {
                    'title': 'Типы баннеров',
                    'description': 'Типы баннеров отображаемых в виджете',
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
                    'title': 'ID баннеров, которые должны быть в виджете',
                    'description': 'Список конкретных id банеров',
                    'type': 'array',
                    'x-taxi-cpp-type': 'std::unordered_set',
                    'items': {'type': 'integer'},
                },
                'exclude': {
                    'title': 'ID баннеров, которые не должны быть в виджете',
                    'description': 'Список id баннеров иключенных из выборки',
                    'type': 'array',
                    'x-taxi-cpp-type': 'std::unordered_set',
                    'items': {'type': 'integer'},
                },
                'format': {
                    'title': 'Формат баннеров',
                    'description': 'Формат отображения баннеров',
                    'type': 'string',
                    'enum': ['classic', 'shortcut', 'wide_and_short'],
                },
                'limit': {
                    'title': 'Лимит',
                    'description': 'Максимальное число баннеров в виджете',
                    'type': 'integer',
                    'minimum': 0,
                    'x-taxi-cpp-type': 'std::size_t',
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
                    'minimum': 0,
                    'x-taxi-cpp-type': 'std::size_t',
                },
                'randomize': {
                    'title': 'Перемешивать баннеры в случайном порядке?',
                    'type': 'boolean',
                    'default': False,
                    'description': (
                        'Нужно ли перемешать баннеры в случайном порядке.'
                    ),
                },
                'surge_condition': {
                    'title': (
                        'Настройки показа баннеров в зависимости от суржа'
                    ),
                    'additionalProperties': False,
                    'description': (
                        'Условие отображения виджета в зависимости '
                        'от количества суржащих заведений '
                        'в подвыборке каталога'
                    ),
                    'properties': {
                        'exclude_businesses': {
                            'title': 'Исключенные типы заведений',
                            'description': (
                                'Набор типов заведений, которые '
                                'надо исключить из виджета'
                            ),
                            'items': {
                                'enum': ['restaurant', 'shop', 'store'],
                                'type': 'string',
                            },
                            'type': 'array',
                            'x-taxi-cpp-type': 'std::set',
                        },
                        'limit': {
                            'title': (
                                'Максимальное количество ресторанов в блоке'
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
                                'Минимальное количеcтво суржащих заведений'
                            ),
                            'description': (
                                'Минимальное количество суржащих, '
                                'найтивных, заведений для отображения '
                                'виджета'
                            ),
                            'minimum': 0,
                            'type': 'integer',
                            'x-taxi-cpp-type': 'std::size_t',
                        },
                        'min_radius_surge_orders_percent': {
                            'title': (
                                'Минимальный процент срезаемых суржом заказов'
                            ),
                            'description': (
                                'Минимальный процент заказов в заведениях, '
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
                        'Массив ID виджетов от которых зависит нужно ли '
                        'рисовать Banner, если есть хоть один из них '
                        'в Layout. '
                        'Если массив пустой - Banner будет рисоваться всегда.'
                    ),
                    'items': {'type': 'string'},
                    'type': 'array',
                    'x-taxi-cpp-type': 'std::unordered_set',
                },
                'not_show_with': {
                    'title': 'Не показывать с виджетами',
                    'description': (
                        'Массив ID виджетов от которых зависит нужно ли '
                        'рисовать Banner. Если он не пустой и хоть один '
                        'из виджетов есть в Layout, то Banner не отображается.'
                    ),
                    'items': {'type': 'string'},
                    'type': 'array',
                    'x-taxi-cpp-type': 'std::unordered_set',
                },
            },
            'required': ['format'],
        },
        'meta': meta,
        'payload_schema': {'type': 'object'},
        'payload': payload,
    }


@pytest.mark.parametrize(
    'widget_template_id,expected_status,data,expected_data',
    [
        (1, 200, get_data(), get_data()),
        (
            1,
            400,
            get_data(
                payload={
                    'field_2': 'value_2',
                    'background_color_dark': '#fffff',
                },
            ),
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
            get_data(meta={'field_1': 'value_1'}),
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
            get_data(meta={'format': 'classic', 'limit': 2147483648}),
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
        (
            1,
            200,
            {
                'type': 'stories',
                'name': 'Widget template 2',
                'meta_schema': {
                    'additionalProperties': False,
                    'properties': {
                        'groups': {
                            'description': (
                                'Список групп сторизов, которое '
                                'необходимо поместить в виджет'
                            ),
                            'items': {'type': 'string'},
                            'type': 'array',
                            'x-taxi-cpp-type': 'std::unordered_set',
                        },
                        'limit': {
                            'description': (
                                'Максимальное число сторизов в виджете'
                            ),
                            'type': 'integer',
                        },
                        'min_count': {
                            'description': (
                                'Минимальное число сторизов для того чтобы '
                                'виджет\nотобразился в выдаче\n'
                            ),
                            'type': 'integer',
                        },
                    },
                    'type': 'object',
                },
                'meta': {'field_1': 'value_1'},
                'payload_schema': {'type': 'object'},
                'payload': {'field_2': 'value_2'},
            },
            {
                'type': 'stories',
                'name': 'Widget template 2',
                'meta_schema': {
                    'additionalProperties': False,
                    'properties': {
                        'groups': {
                            'description': (
                                'Список групп сторизов, которое '
                                'необходимо поместить в виджет'
                            ),
                            'items': {'type': 'string'},
                            'type': 'array',
                            'x-taxi-cpp-type': 'std::unordered_set',
                        },
                        'limit': {
                            'description': (
                                'Максимальное число сторизов в виджете'
                            ),
                            'type': 'integer',
                        },
                        'min_count': {
                            'description': (
                                'Минимальное число сторизов для того чтобы '
                                'виджет\nотобразился в выдаче\n'
                            ),
                            'type': 'integer',
                        },
                    },
                    'type': 'object',
                },
                'meta': {'field_1': 'value_1'},
                'payload_schema': {'type': 'object'},
                'payload': {'field_2': 'value_2'},
            },
        ),
        pytest.param(
            1,
            200,
            {
                'name': 'PLUS_BANNER',
                'type': 'plus_banner',
                'meta': {},
                'meta_schema': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {},
                },
                'payload': {},
                'payload_schema': {},
            },
            {
                'id': 1,
                'meta': {},
                'meta_schema': {
                    'additionalProperties': False,
                    'properties': {},
                    'type': 'object',
                },
                'name': 'PLUS_BANNER',
                'payload': {},
                'payload_schema': {},
                'type': 'plus_banner',
            },
            id='plus_banner success',
        ),
    ],
)
@pytest.mark.pgsql('eats_layout_constructor', files=[])
async def test_insert_widget_templates(
        taxi_eats_layout_constructor,
        mockserver,
        widget_template_id,
        expected_status,
        data,
        expected_data,
):
    response = await taxi_eats_layout_constructor.post(
        'layout-constructor/v1/constructor/widget-templates/', json=data,
    )
    assert response.status == expected_status
    if response.status == 200:
        expected_data['id'] = widget_template_id
    assert response.json() == expected_data


async def test_inster_widget_template_complex_payload(
        taxi_eats_layout_constructor,
):
    """
    Тестирует, что сохранение шаблона виджета с payload,
    содержащим вложенный объект происходит успешно
    Relates: EDADEV-36491
    """

    response = await taxi_eats_layout_constructor.post(
        'layout-constructor/v1/constructor/widget-templates/',
        json={
            'type': 'filters',
            'name': 'angry_2',
            'meta_schema': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {},
            },
            'meta': {},
            'payload_schema': {
                'type': 'object',
                'properties': {
                    'foo': {'type': 'string'},
                    'bar': {
                        'type': 'object',
                        'properties': {'baz': {'type': 'string'}},
                    },
                },
            },
            'payload': {'foo': '123', 'bar': {'baz': '123'}},
        },
    )

    assert response.status == 200


@pytest.mark.parametrize(
    'widget_template_type',
    [
        pytest.param('places_list'),
        pytest.param('places_carousel'),
        pytest.param('places_selection'),
    ],
)
@pytest.mark.pgsql('eats_layout_constructor', files=[])
async def test_insert_deprecated_template(
        taxi_eats_layout_constructor, mockserver, widget_template_type,
):
    """
    Проверяем, что нельзя создать устаревший виджет
    """

    data = {
        'type': widget_template_type,
        'name': 'Widget template 1',
        'meta_schema': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {'place_filter_type': 'open'},
            'required': ['place_filter_type'],
        },
        'meta': {},
        'payload_schema': {'type': 'object'},
        'payload': {},
    }

    response = await taxi_eats_layout_constructor.post(
        'layout-constructor/v1/constructor/widget-templates/', json=data,
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'DeprecatedWidgetTemplateTypeError',
        'message': (
            'Widget template type \'{}\' is deprecated. '
            'Consider to use \'places_collection\' instead.'.format(
                widget_template_type,
            )
        ),
    }
