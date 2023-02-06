import pytest

from . import configs
from . import translations
from . import utils


TRANSLATION = translations.eats_layout_constructor_ru(
    {
        'filters_v2.active_sort_message': (
            '%(sorts_block_name)s: %(active_sort_name)s'
        ),
        'filters_v2.bottom_sheet.block.filters': 'Фильтры',
        'filters_v2.bottom_sheet.block.first': 'Первая группа',
        'filters_v2.bottom_sheet.block.second': 'Кухни',
        'filters_v2.bottom_sheet.block.sorts': 'Сортировки',
        'filters_v2.bottom_sheet.delivery_time_block_name': 'Время доставки',
        'filters_v2.bottom_sheet.end_icon.name': 'Еще',
        'filters_v2.bottom_sheet.icon.name': 'Все фильтры',
        'filters_v2.empty_result_message.button_text': 'Сбросить все',
        'filters_v2.empty_result_message.message_text': (
            'Нет результатов по таким фильтрам'
        ),
        'filters_v2.found_message': 'Найден %(places_count)s ресторан',
        'filters_v2.found_message.button_text': 'Сбросить',
        'filters_v2.bottom_sheet.block.sorts_first': 'Показать сначала',
    },
)


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_template')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@TRANSLATION
async def test_filters_v2(
        taxi_eats_layout_constructor, mockserver, meta_widgets, load_json,
):
    """
    Проверяем что фильтры 2.0 объединяются
    в группы при запросе в каталог.
    При этом фильтр pizza не отображается в шторке,
    следовальено не привязан к логической группе, но
    все равно отправляется в каталог отдельной
    группой с И.
    Проверяем что LC может распарсить
    ответ каталога в формате фильтров 2.0
    """
    meta_widget_settings = load_json('meta_widget_settings.json')
    layout = load_json('filters_v2/layout.json')

    meta_widgets.add_meta_widget(
        utils.MetaWidget(
            type='filters_layout',
            slug='my_meta_widget',
            name='Filters Meta Widget',
            settings=meta_widget_settings,
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert request.json['filters_v2'] == {
            'groups': [
                {
                    'type': 'or',
                    'filters': [
                        {'type': 'quickfilter', 'slug': 'burgers'},
                        {'type': 'quickfilter', 'slug': 'sushi'},
                    ],
                },
                {
                    'type': 'and',
                    'filters': [{'type': 'quickfilter', 'slug': 'pizza'}],
                },
            ],
        }
        return load_json('filters_v2/catalog_response.json')

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'filters_v2': {
                'filters': [
                    {'type': 'quickfilter', 'slug': 'burgers'},
                    {'type': 'quickfilter', 'slug': 'sushi'},
                    {'type': 'quickfilter', 'slug': 'pizza'},
                ],
            },
        },
    )

    assert catalog.times_called == 1
    assert response.status_code == 200
    actual = response.json()
    assert actual == layout


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_template')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@TRANSLATION
async def test_filters_v2_off(
        taxi_eats_layout_constructor, mockserver, meta_widgets, load_json,
):
    """
    Проверяем, что несмотря на применненный эксперимент
    с подменой мета виджета, если в настройках мета виджета
    фильтры 2.0 выключены, шторка не отображается
    """
    meta_widget_settings = load_json('meta_widget_settings_off.json')

    meta_widgets.add_meta_widget(
        utils.MetaWidget(
            type='filters_layout',
            slug='my_meta_widget',
            name='Filters Meta Widget',
            settings=meta_widget_settings,
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return load_json('filters_v2/catalog_response.json')

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert catalog.times_called == 1
    assert response.status_code == 200
    actual = response.json()
    assert 'filters' in actual['data']
    assert 'filters_v2s' not in actual['data']


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_template')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@TRANSLATION
async def test_filters_v2_delivery_time(
        taxi_eats_layout_constructor, mockserver, meta_widgets, load_json,
):
    """
    Проверяем что фильтр времени доставки
    отображается через LC
    """
    meta_widget_settings = load_json('delivery_time/meta_widget_settings.json')
    layout = load_json('delivery_time/layout.json')

    meta_widgets.add_meta_widget(
        utils.MetaWidget(
            type='filters_layout',
            slug='my_meta_widget',
            name='Filters Meta Widget',
            settings=meta_widget_settings,
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert request.json['filters_v2'] == {
            'groups': [
                {
                    'type': 'or',
                    'filters': [
                        {
                            'type': 'delivery_time',
                            'slug': 'delivery_time',
                            'payload': {'value': {'slug': 'thirty'}},
                        },
                    ],
                },
            ],
        }
        return load_json('delivery_time/catalog_response.json')

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'filters_v2': {
                'filters': [
                    {
                        'type': 'delivery_time',
                        'slug': 'delivery_time',
                        'payload': {'value': {'slug': 'thirty'}},
                    },
                ],
            },
        },
    )

    assert catalog.times_called == 1
    assert response.status_code == 200
    actual = response.json()
    assert actual == layout


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_template')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@TRANSLATION
async def test_filters_v2_counter(
        taxi_eats_layout_constructor, mockserver, meta_widgets, load_json,
):
    """
    Проверяем, что на кнопку открытия шторки
    навершивается счетчик примененных фильтров
    При этом бейджик скрывается
    """
    meta_widget_settings = load_json('counter/meta_widget_settings.json')
    layout = load_json('counter/layout.json')

    meta_widgets.add_meta_widget(
        utils.MetaWidget(
            type='filters_layout',
            slug='my_meta_widget',
            name='Filters Meta Widget',
            settings=meta_widget_settings,
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return load_json('counter/catalog_response.json')

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'filters_v2': {
                'filters': [
                    {'type': 'quickfilter', 'slug': 'burgers'},
                    {'type': 'quickfilter', 'slug': 'sushi'},
                ],
            },
        },
    )

    assert catalog.times_called == 1
    assert response.status_code == 200
    actual = response.json()
    assert actual == layout


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_template')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@TRANSLATION
async def test_filters_v2_show_background(
        taxi_eats_layout_constructor, mockserver, meta_widgets, load_json,
):
    """
    Проверяем, что на фильтры проставляется флаг
    "показывать фон"
    """
    meta_widget_settings = load_json(
        'show_background/meta_widget_settings.json',
    )
    layout = load_json('show_background/layout.json')

    meta_widgets.add_meta_widget(
        utils.MetaWidget(
            type='filters_layout',
            slug='my_meta_widget',
            name='Filters Meta Widget',
            settings=meta_widget_settings,
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return load_json('show_background/catalog_response.json')

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert catalog.times_called == 1
    assert response.status_code == 200
    actual = response.json()
    assert actual == layout


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_template')
@pytest.mark.parametrize(
    'filters_request,catalog_response,layout',
    [
        pytest.param(
            {'filters': [{'type': 'quickfilter', 'slug': 'burgers'}]},
            'catalog_response_show_empty_message.json',
            'layout_show_empty_message.json',
            id='show empty message',
        ),
        pytest.param(
            None,
            'catalog_response_do_not_show_empty_message.json',
            'layout_do_not_show_empty_message.json',
            id='do not show empty message',
            # Т.к. ни один фильтр не выбран (а только 'enabled'),
            # по-умолчанию применяется очистка выдачи
            marks=configs.keep_empty_layout(),
        ),
    ],
)
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@TRANSLATION
async def test_filters_v2_empty_message(
        taxi_eats_layout_constructor,
        mockserver,
        meta_widgets,
        load_json,
        filters_request,
        catalog_response,
        layout,
):
    """
    Проверяем, что при пустой выдаче приходить сообщение
    """
    meta_widget_settings = load_json('empty_message/meta_widget_settings.json')
    layout = load_json(f'empty_message/{layout}')

    meta_widgets.add_meta_widget(
        utils.MetaWidget(
            type='filters_layout',
            slug='my_meta_widget',
            name='Filters Meta Widget',
            settings=meta_widget_settings,
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return load_json(f'empty_message/{catalog_response}')

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'filters_v2': filters_request,
        },
    )

    assert catalog.times_called == 1
    assert response.status_code == 200
    actual = response.json()
    assert actual == layout


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_template')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@TRANSLATION
async def test_filters_v2_empty_object(
        taxi_eats_layout_constructor, mockserver, meta_widgets, load_json,
):
    """
    Проверяем, что даже при запросе без фильтров,
    если активен мета виджет, в каталог отправляется объект
    filters_v2
    """
    meta_widget_settings = load_json('meta_widget_settings.json')

    meta_widgets.add_meta_widget(
        utils.MetaWidget(
            type='filters_layout',
            slug='my_meta_widget',
            name='Filters Meta Widget',
            settings=meta_widget_settings,
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        filters_v2 = request.json.get('filters_v2')
        assert filters_v2 is not None
        groups = filters_v2.get('groups')
        assert groups is not None
        assert not groups
        return {
            'blocks': [],
            'filters': {},
            'filters_v2': {},
            'sort': {},
            'timepicker': [],
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert catalog.times_called == 1
    assert response.status_code == 200


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_for_applied_filters_v2')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@TRANSLATION
async def test_filters_v2_kwarg(taxi_eats_layout_constructor, mockserver):
    """
    Проверяем, что при применении фильтров 2.0 в
    эксперимент выбора лейаута приходит дополнительный кварг
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return {
            'blocks': [
                {
                    'id': 'open',
                    'type': 'open',
                    'list': [
                        {
                            'meta': {'place_id': 1, 'brand_id': 1},
                            'payload': {},
                        },
                    ],
                },
            ],
            'filters': {},
            'sort': {},
            'timepicker': [],
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
            'X-Eats-Session': 'session',
        },
        json={
            'location': {'latitude': 0, 'longitude': 0},
            'filters_v2': {
                'filters': [{'type': 'quickfilter', 'slug': 'burger'}],
            },
        },
    )

    assert catalog.times_called == 1
    assert response.status_code == 200
    response_layout = response.json()['layout']
    assert len(response_layout) == 1
    assert (
        response_layout[0]['payload']['title']
        == 'Плейсы после применения фильтров 2.0'
    )


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_for_applied_filters_v2')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@TRANSLATION
async def test_filters_v2_sort_message(
        taxi_eats_layout_constructor, mockserver, meta_widgets, load_json,
):
    """
    Проверяем, что если в шторке выбрана не дефолтная сортировка,
    но не выбрано фильтров, в сообщении пишется название сортировки
    вместо количества ресторанов
    """

    meta_widget_settings = load_json('sort_message/meta_widget_settings.json')
    layout = load_json('sort_message/layout.json')

    meta_widgets.add_meta_widget(
        utils.MetaWidget(
            type='filters_layout',
            slug='my_meta_widget',
            name='Filters Meta Widget',
            settings=meta_widget_settings,
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return load_json('sort_message/catalog_response.json')

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
            'X-Eats-Session': 'session',
        },
        json={'location': {'latitude': 0, 'longitude': 0}},
    )

    assert catalog.times_called == 1
    assert response.status_code == 200
    data = response.json()

    assert data == layout


@pytest.mark.now('2020-05-07T11:30:00+0300')
@configs.layout_experiment_name(filters='eats_layout_filters')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@pytest.mark.parametrize(
    'show_selected, expected_list',
    (
        pytest.param(False, ['pickup:pickup'], id='do not show selected'),
        pytest.param(True, ['plus:plus', 'pickup:pickup'], id='show selected'),
    ),
)
@TRANSLATION
async def test_filters_v2_show_selected(
        taxi_eats_layout_constructor,
        mockserver,
        meta_widgets,
        load_json,
        show_selected,
        expected_list,
):
    """
    Проверяем, что если в шторке выбрана не дефолтная сортировка,
    но не выбрано фильтров, в сообщении пишется название сортировки
    вместо количества ресторанов
    """

    meta_widget_settings = load_json('show_selected/meta_widget_settings.json')
    meta_widget_settings['list']['show_selected'] = show_selected

    meta_widgets.add_meta_widget(
        utils.MetaWidget(
            type='filters_layout',
            slug='my_meta_widget',
            name='Filters Meta Widget',
            settings=meta_widget_settings,
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return load_json('show_selected/catalog_response.json')

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
            'X-Eats-Session': 'session',
        },
        json={'location': {'latitude': 0, 'longitude': 0}},
    )

    assert catalog.times_called == 1
    assert response.status_code == 200
    data = response.json()['data']

    filters = data['filters_v2s'][0]['payload']

    bottomsheet_filters = filters['bottom_sheet']['layout'][0]['payload'][
        'groups'
    ][0]['filters']
    assert bottomsheet_filters == ['plus:plus']

    list_filters = filters['list']
    assert list_filters == expected_list
