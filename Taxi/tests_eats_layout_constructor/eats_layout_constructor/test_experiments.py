import pytest

from . import configs
from . import utils


@pytest.mark.pgsql(
    'eats_layout_constructor', files=[], directories=[], queries=[],
)
@pytest.mark.layout(
    slug='top_layout',
    widgets=[
        utils.Widget(
            name='open',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={'title': 'top_layout'},
        ),
    ],
)
@pytest.mark.layout(
    slug='favourite_samovyvoz_layout',
    widgets=[
        utils.Widget(
            name='closed',
            type='places_collection',
            meta={'place_filter_type': 'closed', 'output_type': 'carousel'},
            payload={'title': 'favourite_samovyvoz_layout'},
        ),
    ],
)
@pytest.mark.layout(
    slug='default',
    widgets=[
        utils.Widget(
            name='new',
            type='places_collection',
            meta={'place_filter_type': 'new', 'output_type': 'list'},
            payload={'title': 'default'},
        ),
    ],
)
@configs.layout_experiment_name(filters='eats_layout_template')
@pytest.mark.experiments3(
    name='eats_layout_template',
    consumers=['layout-constructor/layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'top_layout',
            'predicate': {
                'init': {
                    'arg_name': 'filters',
                    'set_elem_type': 'string',
                    'value': 'test_type:top',
                },
                'type': 'contains',
            },
            'value': {'layout_slug': 'top_layout'},
        },
        {
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'filters',
                                'set_elem_type': 'string',
                                'value': 'test_type_1:samovyvoz',
                            },
                            'type': 'contains',
                        },
                        {
                            'init': {
                                'arg_name': 'filters',
                                'set_elem_type': 'string',
                                'value': 'test_type_2:favourite',
                            },
                            'type': 'contains',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'title': 'favourite_samovyvoz_layout',
            'value': {'layout_slug': 'favourite_samovyvoz_layout'},
        },
        {'predicate': {'type': 'true'}, 'value': {'layout_slug': 'default'}},
    ],
)
@pytest.mark.parametrize(
    'layout_request,expected_layout',
    [
        pytest.param(
            {'filters': [{'type': 'test_type', 'slug': 'top'}]},
            ['top_layout'],
        ),
        pytest.param(
            {
                'filters': [
                    {'type': 'test_type_1', 'slug': 'samovyvoz'},
                    {'type': 'test_type_2', 'slug': 'favourite'},
                ],
            },
            ['favourite_samovyvoz_layout'],
        ),
        pytest.param({'filter': 'samovyvoz'}, ['default']),
        pytest.param({}, ['default']),
    ],
)
async def test_filters_in_experiment(
        taxi_eats_layout_constructor,
        mockserver,
        layout_request,
        expected_layout,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(_):
        return {
            'blocks': [
                {
                    'id': 'new',
                    'type': 'new',
                    'list': [
                        {
                            'meta': {'place_id': 4, 'brand_id': 4},
                            'payload': {
                                'slug': 'fourth',
                                'data': {'actions': [], 'meta': []},
                                'layout': [],
                            },
                        },
                    ],
                },
                {
                    'id': 'open',
                    'type': 'open',
                    'list': [
                        {
                            'meta': {'place_id': 1, 'brand_id': 1},
                            'payload': {
                                'slug': 'first',
                                'data': {'actions': [], 'meta': []},
                                'layout': [],
                            },
                        },
                    ],
                },
                {
                    'id': 'closed',
                    'type': 'closed',
                    'list': [
                        {
                            'meta': {'place_id': 2, 'brand_id': 2},
                            'payload': {
                                'slug': 'second',
                                'data': {'actions': [], 'meta': []},
                                'layout': [],
                            },
                        },
                    ],
                },
            ],
            'filters': {},
            'sort': {},
            'timepicker': [],
        }

    layout_request['location'] = {'latitude': 0.0, 'longitude': 0.0}

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
        },
        json=layout_request,
    )

    assert response.status_code == 200
    assert catalog.times_called == 1
    data = response.json()

    assert expected_layout == [
        widget['payload']['title'] for widget in data['layout']
    ]


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_experiments_phone_id',
    },
)
@pytest.mark.experiments3(
    name='eats_layout_experiments_phone_id',
    match={'predicate': {'type': 'true'}, 'enabled': True},
    consumers=['layout-constructor/layout'],
    clauses=[
        {
            'title': 'personal phone id ok',
            'predicate': {
                'init': {
                    'arg_name': 'personal_phone_id',
                    'set_elem_type': 'string',
                    'set': ['123'],
                },
                'type': 'in_set',
            },
            'value': {'layout_slug': 'top_layout'},
        },
    ],
)
async def test_personal_phone_id_clause(
        taxi_eats_layout_constructor, mockserver,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {
            'blocks': [
                {
                    'id': 'any',
                    'type': 'any',
                    'list': [
                        {
                            'meta': {'place_id': 1, 'brand_id': 1},
                            'payload': {'id': 'id_1', 'name': 'name_1'},
                        },
                        {
                            'meta': {'place_id': 2, 'brand_id': 2},
                            'payload': {'id': 'id_2', 'name': 'name_2'},
                        },
                        {
                            'meta': {'place_id': 3, 'brand_id': 3},
                            'payload': {'id': 'id_3', 'name': 'name_3'},
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
            'x-platform': 'ios_app',
            'x-app-version': '5.4.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345,personal_phone_id=123',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
