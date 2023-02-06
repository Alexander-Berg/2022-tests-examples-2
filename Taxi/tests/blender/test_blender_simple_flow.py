import datetime
import json

from nile.api.v1 import clusters, Record
from nile.api.v1.local import StreamSource, ListSink

from projects.blender.common.texts import estimate_min_width
from projects.blender.flow.factory import Factory
from projects.blender.flow.pipeline import NilePipeline
from projects.blender.flow.measures.default import calc_recall_at_domain

MAX_SHORTCUT_WIDTH = 1000


def test_estimate_min_width():
    assert estimate_min_width(
        title='Привет, как дела',
        unit_width=1,
        mdash_width=1,
        ndash_width=1,
        mdash_coeff=1,
        max_lines_in_title=1,
        max_result=MAX_SHORTCUT_WIDTH,
    ) == len('Привет, как дела')

    assert estimate_min_width(
        title='Привет, как дела',
        unit_width=1,
        mdash_width=1,
        ndash_width=1,
        mdash_coeff=1,
        max_lines_in_title=2,
        max_result=MAX_SHORTCUT_WIDTH,
    ) == len('как дела')

    assert estimate_min_width(
        title='Привет, как дела',
        unit_width=1,
        mdash_width=1,
        ndash_width=1,
        mdash_coeff=1,
        max_lines_in_title=3,
        max_result=MAX_SHORTCUT_WIDTH,
    ) == len('Привет,')

    assert estimate_min_width(
        title='Привет, как дела',
        unit_width=1,
        mdash_width=1,
        ndash_width=1,
        mdash_coeff=1,
        max_lines_in_title=4,
        max_result=MAX_SHORTCUT_WIDTH,
    ) == len('Привет,')

    assert estimate_min_width(
        title='         Привет,        как          дела        ',
        unit_width=1,
        mdash_width=1,
        ndash_width=1,
        mdash_coeff=1,
        max_lines_in_title=2,
        max_result=MAX_SHORTCUT_WIDTH,
    ) == len('как дела')


def gen_service_response(ml_request_json_str):
    ml_request = json.loads(ml_request_json_str)
    service_response = {
        'grid': {
            'width': 6,
            'cells': [
                {'width': 2, 'shortcut': {'id': shortcut['id']}}
                for top in ml_request['tops']
                for shortcut in top['shortcuts']
            ],
        },
    }
    return json.dumps(service_response)


def test_flow(load, load_json):
    job = clusters.MockCluster().job()

    factory = Factory(
        blenders=[
            {
                'name': 'empty',
                'load': (
                    'projects.blender.ml_experiments.simple.helpers'
                    '.EmptyBlender'
                ),
                'kwargs': {},
            },
            {
                'name': 'random_trivial_seed_42',
                'load': (
                    'projects.blender.ml_experiments.simple.helpers'
                    '.RandomTrivialBlender'
                ),
                'kwargs': {'seed': 42},
            },
            {
                'name': 'random_trivial_seed_13',
                'load': (
                    'projects.blender.ml_experiments.simple.helpers'
                    '.RandomTrivialBlender'
                ),
                'kwargs': {'seed': 13},
            },
        ],
        measures_load='projects.blender.flow.measures.Default',
        measures_params={
            'scenarios': [
                'taxi_expected_destination',
                'grocery_category',
                'eats_place',
            ],
            'lines_numbers': [1, 4, 7, 100],
            'top_relevance_rates': {'default': 0.5},
            'line_relevance_rate': 0.8,
            'recall_metrics': False,
        },
        metrics_load='projects.blender.flow.metrics.Default',
        metrics_params={'all_important': True},
        target_extractor_load='projects.blender.flow.target_extractors.LineAwareTargetExtractor',  # noqa: E501
        feature_extractor_params={
            'known_product_tags': ['taxi'],
            'predicted_actions': ['taxi_order'],
            'scenarios': [
                'taxi_expected_destination',
                'eats_place',
                'grocery_category',
            ],
            'use_min_width': True,
        },
        data_splitter_params={'test_begin_dttm': '2010-01-01T00:00:00'},
        sampler_params={'negative_samples_mult': 999},
    )

    nile_pipeline = NilePipeline(
        job=job,
        factory=factory,
        data_splits_params={
            'intensity': 'data',
            'output_keys': ['train', 'test'],
        },
    )

    data_table = job.table('').label('data')
    future_actions_table = job.table('').label('future_data')
    data_splits = nile_pipeline.create_data_splits(
        data_table, future_actions_table,
    )
    learning_splits = nile_pipeline.create_learning_splits(data_splits)
    responses_splits = nile_pipeline.create_responses_splits(data_splits)
    metrics_splits = nile_pipeline.create_metrics_splits(responses_splits)
    assert len(learning_splits) == 2
    assert len(metrics_splits) == 2
    metrics_splits['test'].put('').label('metrics')
    learning_splits['test'].put('').label('learning')

    request = load('request.json')
    service_response = gen_service_response(request)
    metrics = []
    learning = []
    job.local_run(
        sources={
            'data': StreamSource(
                [
                    Record(
                        grid_id='6468eb4ac4e24b71b84bffe59a2d5404',
                        request=request,
                        service_response=service_response,
                        timestamp=datetime.datetime(2020, 1, 1).timestamp(),
                    ),
                    Record(
                        grid_id='6468eb4ac4e24b71b84bffe59a2d5404',
                        request=request,
                        service_response=service_response,
                        timestamp=datetime.datetime(2020, 1, 1).timestamp(),
                    ),
                ],
            ),
            'future_data': StreamSource(
                [
                    Record(
                        grid_id='6468eb4ac4e24b71b84bffe59a2d5404',
                        clicked_objects=[
                            """
                            {
                            "shortcut_id": "d5babbca439a4864970bae166baeac1a",
                            "timestamp": 1590977744,
                            "service": "taxi", "type": "shortcut"}
                            """,
                        ],
                    ),
                ],
            ),
        },
        sinks={'metrics': ListSink(metrics), 'learning': ListSink(learning)},
    )

    req_shortcuts_count = len(
        [
            sh
            for top in load_json('request.json')['tops']
            for sh in top['shortcuts']
        ],
    )

    assert len(learning) == req_shortcuts_count * 2
    assert len(learning[0].value.split('\t')) == 22
    assert len(metrics) == 3
    assert {record.blender_name for record in metrics} == {
        'empty',
        'random_trivial_seed_42',
        'random_trivial_seed_13',
    }
    assert len(set([len(record.to_dict()) for record in metrics])) == 1
    assert {key.split('_')[0] for key in metrics[0].to_dict()} == {
        'blender',
        'mean',
        'count',
        'sum',
        'min',
        'max',
    }
    assert metrics[0] == metrics[0]
    assert metrics[0] != metrics[1]
    assert metrics[1] != metrics[2]
    assert metrics[0] != metrics[2]


def test_calc_recall(load, load_json):
    assert 1 == calc_recall_at_domain([0, 1, 2, 3], [1])
    assert 1 == calc_recall_at_domain([0, 1, 2, 3], [1, 2])
    assert 1 == calc_recall_at_domain([0, 1, 2, 3], [1, 1])
    assert 0.5 == calc_recall_at_domain([0, 1, 2, 3], [1, 5])
    assert 0 == calc_recall_at_domain([0, 1, 2, 3], [5])
