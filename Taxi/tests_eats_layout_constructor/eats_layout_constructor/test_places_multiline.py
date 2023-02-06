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


def create_themed_color():
    return [
        {'theme': 'light', 'value': '#ffffff'},
        {'theme': 'dark', 'value': '#ffffff'},
    ]


def create_tag(text):
    return {
        'text': {'text': text, 'color': create_themed_color()},
        'background': create_themed_color(),
    }


def create_place_tag(tag, place_ids):
    return {'tag': tag, 'places_ids': place_ids}


TAGS = [create_tag('New'), create_tag('Hello')]
PLACE_IDS = [1, 2, 3, 4, 5, 6, 7]


def catalog_response(tags=None):
    places = []
    for i in PLACE_IDS:
        places.append(
            {
                'payload': {
                    'name': '-',
                    'slug': 'place' + str(i),
                    'availability': {'is_available': True},
                },
                'meta': {'place_id': i, 'brand_id': i * 10},
            },
        )

    if tags:
        for place in places:
            place['payload']['data'] = {'features': {'tags': tags}}

    return {
        'blocks': [{'id': 'any_no_filters_shop_sort_default', 'list': places}],
        'filters': {},
        'sort': {},
        'timepicker': [],
    }


CATALOG_RESPONSE = catalog_response()
CATALOG_RESPONSE_WITH_TAGS = catalog_response(TAGS)


def create_widget(single_widget_layout, brand_ids, title_size=None):
    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='places_multiline',
        name='Places multiline',
        meta={
            'place_filter_type': 'any',
            'image_source': 'logo',
            'brands_order': [40, 30, 20, 10, 50],
            'brand_ids': brand_ids,
            'title_size': title_size,
        },
        payload={},
        payload_schema={},
    )
    single_widget_layout('layout_1', widget_template)


@pytest.mark.parametrize('title_size', ['medium', 'large', None])
@experiments.layout('layout_1')
@configs.layout_experiment_name()
async def test_eats_layout_places_multiline_title_size(
        taxi_eats_layout_constructor,
        mockserver,
        single_widget_layout,
        title_size,
):
    """
        Проверяем, что в ответе приходит title_size, если он задан
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        assert request.json['blocks'] == REQUEST_BLOCKS
        return CATALOG_RESPONSE

    brand_ids = [10, 20]
    create_widget(single_widget_layout, brand_ids, title_size)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200

    result = response.json()

    assert 'data' in result

    assert 'places_multiline' in result['data']

    assert len(result['data']['places_multiline']) == 1
    places_multiline = result['data']['places_multiline'][0]

    assert 'payload' in places_multiline

    payload = places_multiline['payload']
    if title_size is not None:
        assert payload['title_size'] == title_size
    else:
        assert 'title_size' not in payload


@pytest.mark.parametrize(
    ('brand_ids', 'expected_weights'),
    [
        pytest.param([], []),
        pytest.param([10], [6]),
        pytest.param([10, 20], [3, 3]),
        pytest.param([10, 20, 30], [2, 2, 2]),
        pytest.param([10, 20, 30, 40], [3, 3, 3, 3]),
        pytest.param([10, 20, 30, 40, 50], [3, 3, 2, 2, 2]),
        pytest.param([10, 20, 30, 40, 50, 60], [2, 2, 2, 2, 2, 2]),
        pytest.param([10, 20, 30, 40, 50, 60, 70], [3, 3, 3, 3, 2, 2, 2]),
    ],
)
@experiments.layout('layout_1')
@configs.layout_experiment_name()
async def test_eats_layout_places_multiline_weights(
        taxi_eats_layout_constructor,
        mockserver,
        single_widget_layout,
        brand_ids,
        expected_weights,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        assert request.json['blocks'] == REQUEST_BLOCKS
        return CATALOG_RESPONSE

    create_widget(single_widget_layout, brand_ids)

    count = len(expected_weights)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200

    result = response.json()

    assert 'data' in result

    if not count:
        assert not result['data']
        return

    assert 'places_multiline' in result['data']

    assert len(result['data']['places_multiline']) == 1
    places_multiline = result['data']['places_multiline'][0]

    assert 'payload' in places_multiline

    payload = places_multiline['payload']
    assert 'places' in payload
    assert 'total_columns_hint' in payload
    assert payload['total_columns_hint'] == 6

    places = payload['places']
    assert len(places) == count

    fact_weights = [
        place['layout_hints']['column_width_hint'] for place in places
    ]
    assert fact_weights == expected_weights


@pytest.mark.parametrize(
    'tags',
    [
        pytest.param([]),
        pytest.param([create_tag('New')]),
        pytest.param([create_tag('New'), create_tag('Hello')]),
    ],
)
@experiments.layout('layout_1')
@configs.layout_experiment_name()
async def test_eats_layout_places_multiline_tags(
        taxi_eats_layout_constructor, mockserver, single_widget_layout, tags,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        assert request.json['blocks'] == REQUEST_BLOCKS
        return catalog_response(tags=tags)

    brand_ids = [10, 20]
    create_widget(single_widget_layout, brand_ids)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200

    result = response.json()

    payload = result['data']['places_multiline'][0]['payload']

    places = payload['places']
    assert len(places) == len(brand_ids)

    for place in places:
        if not tags:
            assert 'data' not in place['item']
            continue

        assert 'item' in place
        assert 'data' in place['item']
        assert 'features' in place['item']['data']
        assert 'tags' in place['item']['data']['features']
        result_tags = place['item']['data']['features']['tags']
        assert result_tags == tags
