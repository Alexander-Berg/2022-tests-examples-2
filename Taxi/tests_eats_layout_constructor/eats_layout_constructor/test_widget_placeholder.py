import pytest

from . import configs
from . import experiments
from . import utils


OPEN_LIST = 'open list'
CLOSED_CAROUSEL = 'closed carousel'


@pytest.mark.experiments3(
    name='placeholder_experiment',
    consumers=['layout-constructor/widget-placeholder'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Open List',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                    'value': 'open_list',
                },
            },
            'value': {'widget_template': OPEN_LIST},
        },
        {
            'title': 'Closed carousel',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                    'value': 'closed_carousel',
                },
            },
            'value': {'widget_template': CLOSED_CAROUSEL},
        },
    ],
)
@pytest.mark.parametrize(
    'device_id,filter_type,widget_type,data_section',
    (
        pytest.param(
            'open_list', 'open', 'places_list', 'places_lists', id='open list',
        ),
        pytest.param(
            'closed_carousel',
            'closed',
            'places_carousel',
            'places_carousels',
            id='closed carousel',
        ),
    ),
)
@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('layout', 'eats_layout_template')
async def test_widget_placeholder(
        taxi_eats_layout_constructor,
        mockserver,
        layouts,
        widget_templates,
        layout_widgets,
        device_id,
        filter_type,
        widget_type,
        data_section,
):
    'Проверяем помену виджетов по эксперименту'

    layout = utils.Layout(layout_id=1, name='layout', slug='layout')
    layouts.add_layout(layout)

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='widget_placeholder',
        name='placeholder',
        meta={'experiment_name': 'placeholder_experiment'},
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(widget_template)

    layout_widget = utils.LayoutWidget(
        name='widget placeholder',
        widget_template_id=widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )
    layout_widgets.add_layout_widget(layout_widget)

    widget_templates.add_widget_template(
        utils.WidgetTemplate(
            widget_template_id=2,
            type='places_collection',
            name=OPEN_LIST,
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
        ),
    )

    widget_templates.add_widget_template(
        utils.WidgetTemplate(
            widget_template_id=3,
            type='places_collection',
            name=CLOSED_CAROUSEL,
            meta={'place_filter_type': 'closed', 'output_type': 'carousel'},
            payload={},
            payload_schema={},
        ),
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        blocks = request.json['blocks']

        assert len(blocks) == 1
        block = blocks[0]

        assert block['type'] == filter_type
        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [
                {
                    'id': block['id'],
                    'type': filter_type,
                    'list': list(
                        {
                            'meta': {'place_id': idx, 'brand_id': idx},
                            'payload': {'id': f'id_{idx}', 'name': 'name'},
                        }
                        for idx in range(1, 3)
                    ),
                },
            ],
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': device_id,
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
    assert eats_catalog.times_called == 1

    data = response.json()

    widget_id = '1_widget_placeholder'
    assert data['layout'] == [
        {'id': widget_id, 'type': widget_type, 'payload': {}},
    ]

    assert data_section in data['data']
