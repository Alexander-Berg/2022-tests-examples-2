from ciso8601 import parse_datetime_as_naive
import numpy as np
import pandas as pd

from nile.api.v1 import clusters, Record
from nile.api.v1.local import StreamSource, ListSink

from projects.common.nile import test_utils

from projects.support.pipeline import NilePipeline
from projects.support.factory import SupportFactory


def iter_records(data):
    for elem in data:
        params = {k: test_utils.to_bytes(v) for k, v in elem.items()}
        yield Record(**params)


def test_automatization(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.support.nile_blocks.metrics.automatization'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'values': ['not_reply', 'ok', 'waiting'],
                    'name': 'automatization',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='client_autoreply',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data_metrics.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0]['metric'] == 'automatization'
    assert np.isclose(output[0]['value'], 0.5)


def test_tag_presence(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.support.nile_blocks.metrics.tags_presence'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'searched_tags': ['ar_done'],
                    'name': 'ar_done_fraction',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='client_autoreply',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data_metrics.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0]['metric'] == 'ar_done_fraction'
    assert np.isclose(output[0]['value'], 0.55)


def test_accuracy(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': 'projects.support.nile_blocks.metrics.accuracy',
                'function_params': {
                    'response_column': 'response_body',
                    'topic_column': 'topic',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='client_autoreply',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data_metrics.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0]['metric'] == 'accuracy'
    assert np.isclose(output[0]['value'], 0.3)


def test_topic_precision(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.support.nile_blocks.metrics.topic_precision'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'topic_column': 'topic',
                    'topic_name': (
                        'rd_feedback_professionalism_cancel_before_trip'
                    ),
                    'name': 'precision',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='client_autoreply',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data_metrics.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0]['metric'] == 'precision'
    assert np.isclose(output[0]['value'], 0.75)


def test_topic_recall(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.support.nile_blocks.metrics.topic_recall'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'topic_column': 'topic',
                    'topic_name': (
                        'rd_feedback_professionalism_cancel_before_trip'
                    ),
                    'name': 'recall',
                    'round_decimals': 3,
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='client_autoreply',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data_metrics.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0]['metric'] == 'recall'
    assert np.isclose(output[0]['value'], 0.375)


def test_tags_presence_on_column(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.support.nile_blocks.'
                    'metrics.tags_presence_on_column'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'on_column': 'line',
                    'name': 'line: ar_done',
                    'searched_tags': ['ar_done'],
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='client_autoreply',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data_metrics.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
    assert output[0]['metric'] in [
        'line: ar_done: first',
        'line: ar_done: second',
    ]
    assert output[1]['metric'] in [
        'line: ar_done: first',
        'line: ar_done: second',
    ]
    if output[0]['metric'] == 'line: ar_done: first':
        assert np.isclose(output[0]['value'], 0.6)
        assert np.isclose(output[1]['value'], 0.5)
    else:
        assert np.isclose(output[1]['value'], 0.5)
        assert np.isclose(output[0]['value'], 0.6)


def test_weighted_precision(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.support.nile_blocks.metrics.weighted_precision'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'topic_column': 'topic',
                    'name': 'weighted_precision',
                    'round_decimals': 2,
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='client_autoreply',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data_metrics.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0]['metric'] == 'weighted_precision'
    assert np.isclose(output[0]['value'], 0.5)


def test_tags_on_string_beginning(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.support.nile_blocks.metrics.'
                    'tags_on_string_beginning'
                ),
                'function_params': {
                    'on_string_beginning': 'ar_',
                    'response_column': 'response_body',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='client_autoreply',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data_metrics.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 3
    assert set(map(lambda x: x['metric'], output)) == {
        'ar_checked_fraction',
        'ar_done_fraction',
        'ar_model3_fraction',
    }
    for metric in output:
        if metric['metric'] == 'ar_checked_fraction':
            assert np.isclose(metric['value'], 1.0)
        if metric['metric'] == 'ar_done_fraction':
            assert np.isclose(metric['value'], 0.55)
        if metric['metric'] == 'ar_model3_fraction':
            assert np.isclose(metric['value'], 1.0)
    assert output[0]['value'] <= output[1]['value'] <= output[2]['value']


def test_filter_automatization(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.support.nile_blocks.metrics.tags_presence'
                ),
                'function_params': {
                    'searched_tags': ['ar_done'],
                    'response_column': 'response_body',
                    'name': 'ar_done_fraction',
                },
                'filters': [
                    {
                        'by_function': (
                            'projects.support.extractors.'
                            'filters.is_any_tag_in_dict'
                        ),
                        'function_params': {
                            'column': 'test_response_body',
                            'tags': ['ar_done'],
                        },
                    },
                ],
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='client_autoreply',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data_metrics.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0]['metric'] == 'ar_done_fraction'
    assert np.isclose(output[0]['value'], 0.7692)
