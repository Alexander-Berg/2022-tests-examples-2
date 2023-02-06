# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_blender import shortcuts_grid_helpers as helpers


@pytest.fixture(name='response_fetcher')
def _response_fetcher(taxi_blender, load_json):
    return helpers.ResponceFetcher(taxi_blender, load_json)


@pytest.mark.parametrize(
    'metric_labels',
    [
        (
            {
                'collection_0': 1,
                'collection_1': 1,
                'collection_2': 1,
                'collection_slug_custom': 1,
                'organic': 1,
            }
        ),
    ],
)
async def test_showcases(
        response_fetcher,
        load_json,
        experiments3,
        taxi_blender_monitor,
        metric_labels,
):
    exp3_json = load_json('experiments3_grid_rules.json')
    exp3_json['experiments'][0]['clauses'][0]['value'].update(
        {'enable_showcases': True},
    )
    experiments3.add_experiments_json(exp3_json)

    scenario_to_top = {
        'taxi_expected_destination': [f'taxi {i}' for i in range(3)],
        'eats_place': [f'eats {i}' for i in range(5)],
        'media_stories': ['media 0'],
        'deeplink_scenario': [],
    }
    scenario_to_top['eats_place'].append(
        helpers.Shortcut('eats 5', ['tag_for_collection']),
    )
    scenario_to_top['media_stories'].append(
        helpers.Shortcut(
            'media 0', [], '2002deea5f2c40ab9dce96727bc2bb30:version',
        ),
    )
    scenario_to_top['deeplink_scenario'].append(
        helpers.Shortcut(
            'deeplink 0', ['t'], '718a22793e804b45bbcae4f8c1cdba5e:version',
        ),
    )

    showcases = load_json('showcases.json')['showcases']
    showcases[1]['blocks'].insert(1, load_json('tricky_collection.json'))

    async with metrics_helpers.MetricsCollector(
            taxi_blender_monitor,
            sensor='blender_collection_slug_metrics',
            labels={},
    ) as collector:
        resp = await response_fetcher.response(
            scenario_to_top=scenario_to_top, showcases=showcases,
        )
    block_slugs = [b.slug for b in resp.blocks]
    assert block_slugs == [
        'organic',
        'collection_0',  # f'collection_{i}
        'collection_1',  # f'collection_{i}
        'collection_2',
        'collection_slug_custom',  # slug from collection
    ]
    metrics = collector.collected_metrics
    metrics = {
        metric.labels['collection_slug']: metric.value for metric in metrics
    }
    assert metrics == metric_labels
    other_titles = [
        b.titles for b in resp.blocks if b.slug.startswith('collection')
    ]
    assert other_titles == [
        ['eats 0', 'eats 1'],
        ['eats 2', 'eats 3', 'eats 4'],
        ['media 0', 'deeplink 0'],
        ['eats 5'],
    ]
    assert resp.layout == [
        ['taxi 0', 2],
        ['taxi 1', 2],
        ['taxi 2', 2],
        # collection 0
        ['eats 0', 3, 2],  # based on scenario
        ['eats 1', 3, 2],  # based on scenario
        # collection 1
        ['eats 2', 3, 2],
        ['eats 3', 3, 4],
        ['eats 4', 3, 2],
        # collection 2
        ['media 0', 3, 2],  # based on promotion_id
        ['deeplink 0', 3, 2],  # based on promotion_id
        # collection 3
        ['eats 5', 6, 2],  # based on tag
    ]

    block_titles = [b.title for b in resp.blocks]
    assert block_titles == [
        None,  # organic has no title
        'collection_0_name',  # collection_0 has a valid title
        'tricky_collection',  # collection with tricky layout
        'collection_2_name',  # collection with promotions
        None,  # collection_1 has no title
    ]


@pytest.mark.parametrize(
    'metric_labels', [({'grocery_category': 1, 'organic': 1})],
)
async def test_broken_showcase(
        response_fetcher,
        load_json,
        experiments3,
        taxi_blender_monitor,
        get_metrics_by_label_values,
        metric_labels,
):
    """
    Blender can't build a showcase, let's
    fallback to other shortcuts
    """
    exp3_json = load_json('experiments3_grid_rules.json')
    exp3_json['experiments'][0]['clauses'][0]['value'].update(
        {'enable_showcases': True},
    )
    experiments3.add_experiments_json(exp3_json)

    scenario_to_top = {
        'taxi_expected_destination': [f'taxi {i}' for i in range(3)],
        'eats_place': [f'eats {i}' for i in range(4)],
    }
    # let's break the showcase so that it is not built
    showcases = load_json('showcases.json')['showcases']
    showcase = showcases[1]
    showcase['blocks'][0]['cells'][0]['one_of'][0][
        'scenario'
    ] = 'unknown_scenario'
    showcase['blocks'][1]['cells'][0]['one_of'][0]['tag'] = 'unknown_tag'

    async with metrics_helpers.MetricsCollector(
            taxi_blender_monitor,
            sensor='blender_collection_slug_metrics',
            labels={},
    ) as collector:
        resp = await response_fetcher.response(
            scenario_to_top=scenario_to_top, showcases=showcases,
        )
    block_slugs = [b.slug for b in resp.blocks]
    assert block_slugs == ['organic', 'grocery_category']
    metrics = collector.collected_metrics
    metrics = {
        metric.labels['collection_slug']: metric.value for metric in metrics
    }
    assert metrics == metric_labels
    assert resp.layout == [
        ['taxi 0', 2],
        ['taxi 1', 2],
        ['taxi 2', 2],
        # no showcases shortcuts
        ['eats 0', 4],  # width got from ml_lib
        ['eats 1', 2],  # width got from ml_lib
    ]

    block_title_keys = [b.title_key for b in resp.blocks]
    # organic and grocery_category have no title
    assert block_title_keys == [None, None]


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'metric_labels, include_scenario_predictions,'
    'expected_shortcuts_to_screen_ratio, known_orders',
    [
        ({'organic': 1}, True, 0.45, None),
        ({'organic': 1}, False, 0.55, None),
        ({'organic': 1}, True, 0.54, ['taxi:order_id:version']),
        ({'organic': 1}, True, 0.54, ['taxi']),  # full name must be parsed
        ({'organic': 1}, True, 0.53, ['taxi::', 'eats::']),
    ],
)
async def test_showcase_lift(
        taxi_blender,
        load_json,
        taxi_blender_monitor,
        get_metrics_by_label_values,
        metric_labels,
        include_scenario_predictions,
        expected_shortcuts_to_screen_ratio,
        known_orders,
):
    req_body = load_json('simple_request.json')
    if known_orders:
        req_body['state'] = {}
        req_body['state']['known_orders'] = known_orders
    if not include_scenario_predictions:
        req_body.pop('scenario_predictions')
    async with metrics_helpers.MetricsCollector(
            taxi_blender_monitor,
            sensor='blender_collection_slug_metrics',
            labels={},
    ) as collector:
        response = await taxi_blender.post(
            'blender/v1/shortcuts-grid',
            json=req_body,
            headers=helpers.MEANINGLESS_HEADERS,
        )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['showcase_appearance']['showcase_lift'] == {
        'shortcuts_to_screen_ratio': expected_shortcuts_to_screen_ratio,
    }
    metrics = collector.collected_metrics
    metrics = {
        metric.labels['collection_slug']: metric.value for metric in metrics
    }
    assert metrics == metric_labels

    req_body = load_json('simple_request.json')
    req_body['grid_restriction']['media_size_info']['scale'] = 4.0
    async with metrics_helpers.MetricsCollector(
            taxi_blender_monitor,
            sensor='blender_collection_slug_metrics',
            labels={},
    ) as collector:
        response = await taxi_blender.post(
            'blender/v1/shortcuts-grid',
            json=req_body,
            headers=helpers.MEANINGLESS_HEADERS,
        )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['showcase_appearance']['showcase_lift'] == {
        'shortcuts_to_screen_ratio': 0.35,
    }
    metrics = collector.collected_metrics
    metrics = {
        metric.labels['collection_slug']: metric.value for metric in metrics
    }
    assert metrics == metric_labels

    req_body = load_json('simple_request.json')
    req_body['grid_restriction']['media_size_info']['scale'] = 5.0
    async with metrics_helpers.MetricsCollector(
            taxi_blender_monitor,
            sensor='blender_collection_slug_metrics',
            labels={},
    ) as collector:
        response = await taxi_blender.post(
            'blender/v1/shortcuts-grid',
            json=req_body,
            headers=helpers.MEANINGLESS_HEADERS,
        )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['showcase_appearance']['showcase_lift'] == {
        'shortcuts_to_screen_ratio': 0.25,
    }
    metrics = collector.collected_metrics
    metrics = {
        metric.labels['collection_slug']: metric.value for metric in metrics
    }
    assert metrics == metric_labels

    req_body = load_json('simple_request.json')
    req_body['grid_restriction']['media_size_info']['scale'] = 1.0
    async with metrics_helpers.MetricsCollector(
            taxi_blender_monitor,
            sensor='blender_collection_slug_metrics',
            labels={},
    ) as collector:
        response = await taxi_blender.post(
            'blender/v1/shortcuts-grid',
            json=req_body,
            headers=helpers.MEANINGLESS_HEADERS,
        )
    assert response.status_code == 200
    resp_body = response.json()
    assert 'showcase_appearance' not in resp_body
    metrics = collector.collected_metrics
    metrics = {
        metric.labels['collection_slug']: metric.value for metric in metrics
    }
    assert metrics == metric_labels

    req_body = load_json('empty_request.json')
    async with metrics_helpers.MetricsCollector(
            taxi_blender_monitor,
            sensor='blender_collection_slug_metrics',
            labels={},
    ) as collector:
        response = await taxi_blender.post(
            'blender/v1/shortcuts-grid',
            json=req_body,
            headers=helpers.MEANINGLESS_HEADERS,
        )
    assert response.status_code == 200
    resp_body = response.json()
    assert 'showcase_appearance' not in resp_body
    metrics = collector.collected_metrics
    metrics = {
        metric.labels['collection_slug']: metric.value for metric in metrics
    }
    assert metrics == {}
