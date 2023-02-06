from ciso8601 import parse_datetime_as_naive

from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink
from nile.api.v1 import Record

from projects.common.learning import nile_blocks as learning_nile_blocks
from projects.common.nile import test_utils

from projects.support.nile_blocks.table import (
    drop_empty_values,
    drop_null_values,
    filter_by_dates,
)
from projects.support.factory import SupportFactory


def iter_records(data):
    for elem in data:
        params = {k: test_utils.to_bytes(v) for k, v in elem.items()}
        yield Record(**params)


def test_drop_empty_values(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')
    drop_empty_values(table=input_table, column_name='column1').label('output')

    input_records = list(iter_records(load_json('drop_functions_table.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
    assert len(output[0]) == len(output[1]) == 2
    assert output[0]['column1'] == b'value1'
    assert output[1]['column1'] == b'value2'


def test_drop_null_values(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')
    drop_null_values(
        table=input_table, column_names=['column1', 'column2'],
    ).label('output')

    input_records = list(iter_records(load_json('drop_functions_table.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 3
    assert output[0]['column1'] == b'value1' and output[0]['column2'] == b'-'
    assert output[1]['column1'] == b'value2' and output[1]['column2'] == b''
    assert output[2]['column1'] == b'' and output[2]['column2'] == b'val2'


def test_filter_by_dates(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')
    begin_dttm = parse_datetime_as_naive('2020-02-02T00:00:00Z')
    end_dttm = parse_datetime_as_naive('2020-02-10T00:00:00Z')

    filter_by_dates(
        table=input_table,
        begin_dttm=begin_dttm,
        end_dttm=end_dttm,
        column_name='creation_dttm',
    ).label('output')

    input_records = list(iter_records(load_json('date_table.json')))
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
    assert output[0]['data'] == 2
    assert output[1]['data'] == 3


def test_create_data_splits(load_json):
    job = clusters.MockCluster().job()

    factory = SupportFactory(
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-03T00:00:00Z'),
        data_splitter_params={
            'field': 'creation_dttm',
            'test_threshold': '2020-02-02T00:00:00Z',
            'val_threshold': '2020-02-03T00:00:00Z',
            'comparator': (
                'projects.support.data_splitters.comparators.'
                'str_dttm_comparator'
            ),
        },
    )

    input_table = job.table('//input').label('data')

    learning_nile_blocks.split_data(
        table=input_table.label('data'),
        create_data_splitter=factory.create_data_splitter_train_test,
        **{'output_keys': ['train', 'test']},
    )['train'].label('output1')

    learning_nile_blocks.split_data(
        table=input_table.label('data'),
        create_data_splitter=factory.create_data_splitter_train_test,
        **{'output_keys': ['train', 'test']},
    )['test'].label('output2')

    input_records = list(iter_records(load_json('data_to_split.json')))

    output = []
    job.local_run(
        sources={'data': StreamSource(input_records)},
        sinks={'output1': ListSink(output)},
    )
    assert len(output) == 1
    assert output[0]['creation_dttm'] == b'2020-02-01T00:00:00Z'

    output = []
    job.local_run(
        sources={'data': StreamSource(input_records)},
        sinks={'output2': ListSink(output)},
    )
    assert len(output) == 3
    assert output[0]['creation_dttm'] == b'2020-02-02T00:00:00Z'
    assert output[1]['creation_dttm'] == b'2020-02-03T00:00:00Z'
    assert output[2]['creation_dttm'] == b'2020-02-04T00:00:00Z'
