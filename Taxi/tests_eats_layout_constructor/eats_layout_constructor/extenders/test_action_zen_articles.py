import pytest

from eats_layout_constructor import configs
from eats_layout_constructor import experiments
from eats_layout_constructor import utils

CATALOG_PLACES = [
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
            {
                'meta': {'place_id': 2, 'brand_id': 1},
                'payload': {
                    'slug': 'second',
                    'data': {'actions': [], 'meta': []},
                    'layout': [],
                },
            },
        ],
    },
]


@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
@pytest.mark.layout(
    slug='test_place_layout',
    widgets=[
        utils.Widget(
            name='list',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
            meta_widget=utils.MetaWidget(
                type='place_layout',
                name='meta_widget',
                slug='meta_widget',
                settings={
                    'order': ['actions'],
                    'action_extenders': ['actions_zen'],
                    'meta_extenders': [],
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'zen_actions',
    [
        pytest.param(
            {
                'first': [
                    {
                        'id': 'zen_articles',
                        'payload': {
                            'icon_url': 'iurl',
                            'description': 'описание',
                            'title': 'заголовок',
                            'url': 'http://url',
                        },
                        'type': 'zen',
                    },
                ],
                'second': [
                    {
                        'id': 'zen_articles',
                        'payload': {
                            'icon_url': 'iurl',
                            'description': 'описание',
                            'title': 'заголовок',
                            'url': 'http://url',
                        },
                        'type': 'zen',
                    },
                ],
            },
            id='zen enabled',
        ),
        pytest.param(
            {'first': [], 'second': []},
            marks=experiments.DISABLE_ZEN,
            id='zen disabled',
        ),
    ],
)
async def test_actions_zen(layout_constructor, mockserver, zen_actions):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {
            'blocks': CATALOG_PLACES,
            'filters': {},
            'sort': {},
            'timepicker': [],
        }

    response = await layout_constructor.post()

    assert response.status_code == 200

    data = response.json()
    assert len(data['data']['places_lists']) == 1

    palces = data['data']['places_lists'][0]['payload']['places']
    assert len(palces) == len(zen_actions)

    for place in palces:
        assert place['slug'] in zen_actions
        assert zen_actions[place['slug']] == place['data']['actions']
