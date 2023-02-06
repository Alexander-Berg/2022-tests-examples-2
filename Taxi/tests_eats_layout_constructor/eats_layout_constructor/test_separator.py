import pytest

from . import configs
from . import experiments
from . import utils

HEADERS = {
    'x-device-id': 'id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
    'cookie': '{}',
    'X-Eats-User': 'user_id=12345',
    'x-request-application': 'application=1.1.0',
    'x-request-language': 'enUS',
    'Content-Type': 'application/json',
}

REQUEST_BLOCKS = [
    {
        'id': 'any_no_filters_shop_sort_default',
        'type': 'any',
        'disable_filters': True,
        'round_eta_to_hours': False,
        'sort_type': 'default',
        'compilation_type': 'retail',
        'condition': {
            'type': 'eq',
            'init': {
                'arg_name': 'business',
                'arg_type': 'string',
                'value': 'shop',
            },
        },
    },
]


def catalog_response():
    places = [
        {
            'payload': {
                'name': '-',
                'slug': 'place1',
                'availability': {'is_available': True},
            },
            'meta': {'place_id': 1, 'brand_id': 10},
        },
    ]

    return {
        'blocks': [{'id': 'any_no_filters_shop_sort_default', 'list': places}],
        'filters': {},
        'sort': {},
        'timepicker': [],
    }


CATALOG_RESPONSE = catalog_response()


def create_layout(layouts):
    layout = utils.Layout(layout_id=1, name='layout', slug='layout_1')
    layouts.add_layout(layout)


def add_widget_to_layout(layout, widget, widget_id):
    layout_widget = utils.LayoutWidget(
        name=widget.name,
        url_id=widget_id,
        widget_template_id=widget.widget_template_id,
        layout_id=1,
        meta={},
        payload={},
    )

    layout.add_layout_widget(layout_widget)


def create_master_widget(widget_templates, layout, widget_id):
    widget = utils.WidgetTemplate(
        widget_template_id=widget_id,
        type='places_multiline',
        name='Places multiline',
        meta={'place_filter_type': 'any', 'brand_ids': [10]},
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(widget)
    add_widget_to_layout(layout, widget, widget_id)


def create_separator(widget_templates, layout, widget_id, depends_on):
    widget = utils.WidgetTemplate(
        widget_template_id=widget_id,
        type='separator',
        name='Separator',
        meta={'depends_on_any': depends_on} if depends_on else {},
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(widget)
    add_widget_to_layout(layout, widget, widget_id)


def make_depends_on(ids):
    # Unfortunately it must be changed when id creation rules will changes.
    return [str(i) + '_places_multiline' for i in ids]


@pytest.mark.parametrize(
    (
        'master_widgets_ids',
        'separators_depends_on_ids',
        'separators_count_expected',
    ),
    [
        pytest.param([1], [[2]], 0),
        pytest.param([1, 3], [[2]], 0),
        pytest.param([2], [[1, 3]], 0),
        pytest.param([1], [[1]], 1),
        pytest.param([1, 2], [[1]], 1),
        pytest.param([1], [[1, 2]], 1),
        pytest.param([1, 2], [[1, 2]], 1),
        pytest.param([1, 2], [[1], [2]], 2),
        pytest.param([1, 2], [[1, 2], [2]], 2),
        pytest.param([1, 2, 3], [[1, 2], [2]], 2),
    ],
)
@experiments.layout('layout_1')
@configs.layout_experiment_name()
async def test_layout_separator(
        taxi_eats_layout_constructor,
        mockserver,
        layouts,
        widget_templates,
        layout_widgets,
        master_widgets_ids,
        separators_depends_on_ids,
        separators_count_expected,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        assert request.json['blocks'] == REQUEST_BLOCKS
        return CATALOG_RESPONSE

    separators_depends_on = [
        make_depends_on(ids) for ids in separators_depends_on_ids
    ]

    used_ids = set()
    create_layout(layouts)
    for master_id in master_widgets_ids:
        create_master_widget(widget_templates, layout_widgets, master_id)
        used_ids.add(master_id)

    widget_id = 1
    for depends_on in separators_depends_on:
        while widget_id in used_ids:
            widget_id += 1

        used_ids.add(widget_id)
        create_separator(
            widget_templates, layout_widgets, widget_id, depends_on,
        )

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200

    result = response.json()

    assert 'data' in result

    if separators_count_expected == 0:
        assert 'separators' not in result['data']
        return

    assert 'separators' in result['data']
    assert len(result['data']['separators']) == separators_count_expected

    for separator in result['data']['separators']:
        assert 'payload' in separator
