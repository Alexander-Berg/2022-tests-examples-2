import numpy as np

from ciso8601 import parse_datetime_as_naive
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
                    'projects.supportai.nile_blocks.metrics.automatization'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'values': ['close'],
                    'name': 'automatization_close',
                },
            },
            {
                'by_function': (
                    'projects.supportai.nile_blocks.metrics.automatization'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'name': 'automatization_all',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='taxi_pyml.supportai.objects.SupportResponse',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
    assert output[0]['metric'] == 'automatization_close'
    assert np.isclose(output[0]['value'], 0.375)
    assert output[1]['metric'] == 'automatization_all'
    assert np.isclose(output[1]['value'], 0.5)


def test_tags_presence(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.supportai.nile_blocks.metrics.tags_presence'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'searched_tags': [],
                    'name': 'empty_tags',
                },
            },
            {
                'by_function': (
                    'projects.supportai.nile_blocks.metrics.tags_presence'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'searched_tags': ['tag_one'],
                    'name': 'one_tag',
                },
            },
            {
                'by_function': (
                    'projects.supportai.nile_blocks.metrics.tags_presence'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'searched_tags': ['tag_one', 'tag_two'],
                    'name': 'two_tags',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='taxi_pyml.supportai.objects.SupportResponse',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 3
    assert output[0]['metric'] == 'empty_tags'
    assert np.isclose(output[0]['value'], 0.0)
    assert output[1]['metric'] == 'one_tag'
    assert np.isclose(output[1]['value'], 0.375)
    assert output[2]['metric'] == 'two_tags'
    assert np.isclose(output[2]['value'], 0.5)


def test_tags_presence_on_column(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': 'projects.supportai.nile_blocks.metrics.tags_presence_on_column',  # noqa: E501
                'function_params': {
                    'on_column': 'line',
                    'response_column': 'response_body',
                    'searched_tags': ['tag_one', 'tag_two'],
                    'name': 'two_tags',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='taxi_pyml.supportai.objects.SupportResponse',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
    assert output[0]['metric'] == 'two_tags: line_one'
    assert np.isclose(output[0]['value'], 0.4)
    assert output[1]['metric'] == 'two_tags: line_two'
    assert np.isclose(output[1]['value'], 0.6667)


def test_tags_on_string_beginning(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': 'projects.supportai.nile_blocks.metrics.tags_on_string_beginning',  # noqa: E501
                'function_params': {
                    'on_string_beginning': 'tag',
                    'response_column': 'response_body',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='taxi_pyml.supportai.objects.SupportResponse',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
    assert output[0]['metric'] == 'tag_two_fraction'
    assert np.isclose(output[0]['value'], 0.25)
    assert output[1]['metric'] == 'tag_one_fraction'
    assert np.isclose(output[1]['value'], 0.375)


def test_accuracy(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.supportai.nile_blocks.metrics.accuracy'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'topic_column': 'topic',
                },
            },
            {
                'by_function': (
                    'projects.supportai.nile_blocks.metrics.accuracy'
                ),
                'function_params': {
                    'searched_tags': ['tag_one'],
                    'response_column': 'response_body',
                    'topic_column': 'topic',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='taxi_pyml.supportai.objects.SupportResponse',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
    assert output[0]['metric'] == 'accuracy'
    assert np.isclose(output[0]['value'], 0.5)
    assert output[1]['metric'] == 'accuracy'
    assert np.isclose(output[1]['value'], 0.6667)


def test_topic_precision_and_recall(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    nile_pipe = NilePipeline(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        count_metrics_params=[
            {
                'by_function': (
                    'projects.supportai.nile_blocks.metrics.topic_precision'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'topic_column': 'topic',
                    'topic_name': 'topic_one',
                    'name': 'topic_one_precision',
                },
            },
            {
                'by_function': (
                    'projects.supportai.nile_blocks.metrics.topic_recall'
                ),
                'function_params': {
                    'response_column': 'response_body',
                    'topic_column': 'topic',
                    'topic_name': 'topic_one',
                    'name': 'topic_one_recall',
                },
            },
        ],
        factory=SupportFactory(
            begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
            end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
            response_load='taxi_pyml.supportai.objects.SupportResponse',
        ),
    )
    mr_metrics, _ = nile_pipe.count_metrics(
        data_table=input_table, data_df=pd.DataFrame({}),
    )
    mr_metrics.label('output')

    input_records = list(iter_records(load_json('data.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
    assert output[0]['metric'] == 'topic_one_precision'
    assert np.isclose(output[0]['value'], 0.5)
    assert output[1]['metric'] == 'topic_one_recall'
    assert np.isclose(output[1]['value'], 0.5)
