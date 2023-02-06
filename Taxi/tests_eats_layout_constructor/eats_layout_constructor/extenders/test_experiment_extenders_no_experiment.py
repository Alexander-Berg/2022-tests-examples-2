import pytest

from testsuite.utils import matching

from eats_layout_constructor import configs
from eats_layout_constructor import experiments
from eats_layout_constructor import utils


@pytest.mark.parametrize(
    'places, expected',
    [
        pytest.param(
            [
                {
                    'meta': {'place_id': 2222, 'brand_id': 777},
                    'payload': {
                        'slug': 'first',
                        'data': {'actions': [], 'meta': []},
                        'layout': [],
                    },
                },
            ],
            {
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_collection',
                            'template_name': (
                                'test_experiment_extender_template'
                            ),
                            'payload': {
                                'places': [
                                    {
                                        'data': {'actions': [], 'meta': []},
                                        'layout': [
                                            {'layout': [], 'type': 'actions'},
                                            {'layout': [], 'type': 'meta'},
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                        'analytics': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
                'layout': [
                    {
                        'id': '1_places_collection',
                        'payload': {},
                        'type': 'places_list',
                    },
                ],
            },
            id='Test with one places, without experiment',
        ),
    ],
)
@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
@pytest.mark.layout(
    slug='test_place_layout',
    widgets=[
        utils.Widget(
            name='test_experiment_extender',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
            meta_widget=utils.MetaWidget(
                type='place_layout',
                name='from_experiment_extender',
                slug='from_experiment_extender',
                settings={
                    'order': ['actions', 'meta'],
                    'action_extenders': ['actions_experiment_extender'],
                    'meta_extenders': ['meta_experiment_extender'],
                },
            ),
        ),
    ],
)
async def test_experiment_extender(
        taxi_eats_layout_constructor, mockserver, places, expected,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        assert request.json == {
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'blocks': [
                {
                    'id': 'open',
                    'type': 'open',
                    'disable_filters': False,
                    'round_eta_to_hours': False,
                },
            ],
        }
        return {
            'places': [],
            'blocks': [{'id': 'open', 'list': places}],
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
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert response.json() == expected
