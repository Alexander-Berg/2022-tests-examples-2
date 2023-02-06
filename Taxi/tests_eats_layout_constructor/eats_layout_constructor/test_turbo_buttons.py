import copy
import dataclasses
import typing

import pytest

from . import configs
from . import experiments
from . import utils


@dataclasses.dataclass
class Meta:
    place_id: int = 1
    brand_id: int = 1


@dataclasses.dataclass
class Availability:
    is_available: bool = True


@dataclasses.dataclass
class Brand:
    business: str = 'shop'


@dataclasses.dataclass
class Link:
    deeplink: str


@dataclasses.dataclass
class Delivery:
    text: str = '10 min'


@dataclasses.dataclass
class Features:
    delivery: Delivery = Delivery()


@dataclasses.dataclass
class Data:
    features: Features = Features()


@dataclasses.dataclass
class Payload:
    availability: Availability = Availability()
    brand: Brand = Brand()
    data: Data = Data()
    name: str = 'place'
    slug: str = 'slug'
    link: typing.Optional[Link] = None


@dataclasses.dataclass
class Place:
    meta: Meta = Meta()
    payload: Payload = Payload()


@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('layout', 'eats_layout_template')
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_BRAND_ICONS={
        'icons': [
            {'brand_id': 1, 'icon': 'brand/lavka'},
            {'brand_id': 2, 'icon': 'brand/azbuka'},
        ],
    },
)
async def test_turbo_buttons(
        taxi_eats_layout_constructor,
        mockserver,
        load_json,
        layouts,
        widget_templates,
        layout_widgets,
):
    """
    Проверяет виджет турбо кнопок
    """
    layout = utils.Layout(layout_id=1, name='layout', slug='layout')
    layouts.add_layout(layout)

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='turbo_buttons',
        name='Turbo Buttons',
        meta=load_json('widget_settings.json'),
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(widget_template)

    layout_widget = utils.LayoutWidget(
        name='Turbo Buttons',
        widget_template_id=widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )

    layout_widgets.add_layout_widget(layout_widget)

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(_):
        lavka = copy.deepcopy(Place())
        lavka.meta.brand_id = 1
        lavka.meta.place_id = 1
        lavka.payload.name = 'lavka'
        lavka.payload.slug = 'lavka'
        lavka.payload.brand.business = 'store'
        lavka.payload.link = Link(deeplink='http://not-really-a-link.com')

        azbuka = copy.deepcopy(Place())
        azbuka.meta.brand_id = 2
        azbuka.meta.place_id = 2
        azbuka.payload.name = 'azbuka'
        azbuka.payload.slug = 'azbuka'
        azbuka.payload.brand.business = 'shop'
        azbuka.payload.data.features.delivery.text = '10 - 20min'

        return {
            'blocks': [
                {
                    'id': 'btn_open_limit_1_store',
                    'list': [dataclasses.asdict(lavka)],
                },
                {
                    'id': 'btn_collection_shops_open',
                    'list': [dataclasses.asdict(azbuka)],
                    'type': 'open',
                },
            ],
            'filters': {},
            'sort': {},
            'timepicker': [],
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert catalog.times_called == 1
    data = response.json()
    turbo_buttons = data['data']['turbo_buttons'][0]['payload']
    assert turbo_buttons == load_json('layout_response.json')


@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('layout', 'eats_layout_template')
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.translations(
    **{
        'eats-layout-constructor': {
            'widgets.turbo_buttons.collections.show_more.shops': {
                'ru': [
                    'Еще %(count)s',
                    'Еще %(count)s',
                    'Еще %(count)s',
                    'Еще %(count)s',
                ],
            },
            'widgets.turbo_buttons.collections.show_more.shops.description': {
                'ru': ['магазин', 'магазина', 'магазинов', ''],
            },
        },
    },
)
@pytest.mark.parametrize(
    'count,expected_name,expected_description',
    (
        pytest.param(25, 'Еще 21', 'магазин', id='first form'),
        pytest.param(26, 'Еще 22', 'магазина', id='second form'),
        pytest.param(30, 'Еще 26', 'магазинов', id='third form'),
    ),
)
async def test_localization(
        taxi_eats_layout_constructor,
        mockserver,
        load_json,
        layouts,
        widget_templates,
        layout_widgets,
        taxi_config,
        count,
        expected_name,
        expected_description,
):
    """
    Проверяем плюральные формы на кнопке Еще
    """

    layout = utils.Layout(layout_id=1, name='layout', slug='layout')
    layouts.add_layout(layout)

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='turbo_buttons',
        name='Turbo Buttons',
        meta=load_json('widget_settings.json'),
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(widget_template)

    layout_widget = utils.LayoutWidget(
        name='Turbo Buttons',
        widget_template_id=widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )

    layout_widgets.add_layout_widget(layout_widget)

    taxi_config.set_values(
        {
            'EATS_LAYOUT_CONSTRUCTOR_BRAND_ICONS': {
                'icons': [
                    {'brand_id': idx, 'icon': 'brand/icon'}
                    for idx in range(count)
                ],
            },
        },
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        places = []
        for idx in range(count):
            place = copy.deepcopy(Place())
            place.meta.brand_id = idx
            place.meta.place_id = idx
            places.append(dataclasses.asdict(place))

        return {
            'blocks': [
                {
                    'id': 'btn_collection_shops_open',
                    'list': places,
                    'type': 'open',
                },
            ],
            'filters': {},
            'sort': {},
            'timepicker': [],
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'x-yataxi-user': 'eats_user_id=12345',
            'x-yataxi-session': 'eats:blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'ru',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert catalog.times_called == 1
    data = response.json()
    turbo_buttons = data['data']['turbo_buttons'][0]['payload']['buttons']
    last_button = turbo_buttons[-1]
    assert last_button['name'] == expected_name
    assert last_button['description']['text'] == expected_description
    assert (
        sorted(last_button['description']['color'], key=lambda x: x['theme'])
        == [
            {'theme': 'dark', 'value': '#000000'},
            {'theme': 'light', 'value': '#FFFFFF'},
        ]
    )


@pytest.mark.parametrize(
    'filter_types',
    [
        [],
        ['open', 'closed'],
        ['closed', 'open'],
        ['open-delivery-or-pickup', 'closed'],
    ],
)
@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('layout', 'eats_layout_template')
@pytest.mark.experiments3(filename='experiments.json')
async def test_turbo_buttons_filter_type(
        taxi_eats_layout_constructor,
        mockserver,
        load_json,
        layouts,
        widget_templates,
        layout_widgets,
        filter_types,
):
    """
    Тест проверяет что в запросе к каталогу пробрасываются любые фильтры
    из настроек виджета
    """
    layout = utils.Layout(layout_id=1, name='layout', slug='layout')
    layouts.add_layout(layout)

    meta = load_json('widget_settings_collections.json')

    if filter_types:
        group = meta['collection_groups'][0]
        group['first_block_filter_type'] = filter_types[0]
        group['second_block_filter_type'] = filter_types[1]

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='turbo_buttons',
        name='Turbo Buttons',
        meta=meta,
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(widget_template)

    layout_widget = utils.LayoutWidget(
        name='Turbo Buttons',
        widget_template_id=widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )

    layout_widgets.add_layout_widget(layout_widget)

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        blocks = request.json['blocks']
        assert len(blocks) == 2

        requested = [block['type'] for block in blocks]
        if filter_types:
            assert sorted(requested) == sorted(filter_types)
        else:
            # Если фильтры не заданы то по-умолчанию должны
            # выбраться open и closed
            assert sorted(requested) == ['closed', 'open']

        return {'blocks': [], 'filters': {}, 'sort': {}, 'timepicker': []}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'ru',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert catalog.times_called == 1


@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('layout', 'eats_layout_template')
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_BRAND_ICONS={
        'icons': [
            {'brand_id': 1, 'icon': 'brand/lavka'},
            {'brand_id': 2, 'icon': 'brand/azbuka'},
        ],
    },
)
async def test_turbo_buttons_collection_not_found(
        taxi_eats_layout_constructor,
        mockserver,
        load_json,
        layouts,
        widget_templates,
        layout_widgets,
):
    """
    Проверяем что если коллекция не найдена,
    виджета в выдаче не будет
    """
    layout = utils.Layout(layout_id=1, name='layout', slug='layout')
    layouts.add_layout(layout)
    widget_settings = load_json('widget_settings_collections.json')
    widget_settings['collection_groups'][0]['slug'] = 'not_found'

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='turbo_buttons',
        name='Turbo Buttons',
        meta=widget_settings,
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(widget_template)

    layout_widget = utils.LayoutWidget(
        name='Turbo Buttons',
        widget_template_id=widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )

    layout_widgets.add_layout_widget(layout_widget)

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(_):
        assert False, 'Must be unreacheble'

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert catalog.times_called == 0
    assert 'turbo_buttons' not in response.json()['data']
