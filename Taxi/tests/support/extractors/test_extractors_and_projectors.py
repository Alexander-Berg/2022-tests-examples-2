from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink
from nile.api.v1 import Record

from projects.common.nile import test_utils
from projects.common.learning.factories import import_object


def iter_records(data):
    for elem in data:
        params = {k: test_utils.to_bytes(v) for k, v in elem.items()}
        yield Record(**params)


def test_is_in_list(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    extractors = import_object(
        'projects.support.extractors.filters.is_in_list',
    )(**{'column': 'line', 'values': ['first', 'second']})
    input_table.filter(extractors).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 3
    assert output[0]['line'] == b'first'
    assert output[0]['macro_id'] == 1
    assert output[1]['line'] == b'second'
    assert output[1]['macro_id'] == 2
    assert output[2]['line'] == b'first'
    assert output[2]['macro_id'] == 1


def test_is_in_dict_keys(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    extractors = import_object(
        'projects.support.extractors.filters.is_in_dict_keys',
    )(**{'column': 'macro_id', 'values': {b'1': b'one', b'2': 'two'}})
    input_table.filter(extractors).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )


def test_is_any_elem_in_list(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    extractors = import_object(
        'projects.support.extractors.filters.is_any_elem_in_list',
    )(**{'column': 'tags', 'values': ['you', 'me']})
    input_table.filter(extractors).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 3
    assert output[0]['line'] == b'first'
    assert output[0]['tags'] == [b'you', b'me']
    assert output[1]['line'] == b'second'
    assert output[1]['tags'] == [b'you', b'he']
    assert output[2]['line'] == b'first'
    assert output[2]['tags'] == [b'me', b'he']


def test_is_any_tag_in_dict(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    extractors = import_object(
        'projects.support.extractors.filters.is_any_tag_in_dict',
    )(**{'column': 'meta', 'tags': ['me']})
    input_table.filter(extractors).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
    assert output[0]['line'] == b'first'
    assert output[1]['line'] == b'third'


def test_is_any_elem_in_dict_keys(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    extractors = import_object(
        'projects.support.extractors.filters.is_any_elem_in_dict_keys',
    )(**{'column': 'tags', 'values': {'you': 1, 'me': 2}})
    input_table.filter(extractors).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 3
    assert output[0]['line'] == b'first'
    assert output[0]['tags'] == [b'you', b'me']
    assert output[1]['line'] == b'second'
    assert output[1]['tags'] == [b'you', b'he']
    assert output[2]['line'] == b'first'
    assert output[2]['tags'] == [b'me', b'he']


def test_get_identity(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    projector = import_object(
        'projects.support.extractors.extractors.get_identity',
    )(**{'from_column': 'line', 'to_column': 'output'})
    input_table.project(projector).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 4
    assert output[0]['output'] == b'first'
    assert output[1]['output'] == b'second'
    assert output[2]['output'] == b'third'
    assert output[3]['output'] == b'first'


def test_get_topic_from_macro_id(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    projector = (
        import_object(
            'projects.support.extractors.extractors.get_topic_from_macro_id',
        )(
            **{
                'from_column': 'macro_id',
                'to_column': 'output',
                'mapping': {'1': 42, '2': 21, '3': 55},
            },
        )
    )
    input_table.project(projector).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 4
    assert output[0]['output'] == 42
    assert output[1]['output'] == 21
    assert output[2]['output'] == 55
    assert output[3]['output'] == 42


def test_get_youscan_type_from_tags(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    projector = (
        import_object(
            'projects.support.extractors.extractors.'
            'get_youscan_type_from_tags',
        )(
            **{
                'from_column': 'tags_youscan',
                'to_column': 'output',
                'types': ['me'],
            },
        )
    )
    input_table.project(projector).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 4
    assert output[0]['output'] == 'me'
    assert output[1]['output'] is None
    assert output[2]['output'] is None
    assert output[3]['output'] is None


def test_get_label_from_tags(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    projector = (
        import_object(
            'projects.support.extractors.extractors.get_label_from_tags',
        )(
            **{
                'from_column': 'tags',
                'to_column': 'output',
                'mapping': {'you': 'aaa', 'me': 'bbb'},
                'priority_queue': ['aaa', 'bbb'],
            },
        )
    )
    input_table.project(projector).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 4
    assert output[0]['output'] == 'aaa'
    assert output[1]['output'] == 'aaa'
    assert output[2]['output'] is None
    assert output[3]['output'] == 'bbb'


def test_get_label_from_line(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    projector = (
        import_object(
            'projects.support.extractors.extractors.get_label_from_line',
        )(
            **{
                'from_column': 'line',
                'to_column': 'output',
                'mapping': {'first': 'aaa', 'second': 'bbb'},
            },
        )
    )
    input_table.project(projector).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 4
    assert output[0]['output'] == 'aaa'
    assert output[1]['output'] == 'bbb'
    assert output[2]['output'] is None
    assert output[3]['output'] == 'aaa'


def test_get_is_labels_in_tags(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    projector = (
        import_object(
            'projects.support.extractors.extractors.get_is_labels_in_tags',
        )(
            **{
                'from_column': 'tags',
                'to_column': 'output',
                'labels': ['you', 'me'],
            },
        )
    )
    input_table.project(projector).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 4
    assert output[0]['output']
    assert output[1]['output']
    assert not output[2]['output']
    assert output[3]['output']


def test_get_value_from_key_in_dict(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')

    projector = import_object(
        'projects.support.extractors.extractors.get_value_from_key_in_dict',
    )(**{'from_column': 'meta', 'to_column': 'output', 'key': 'val'})
    input_table.project(projector).label('output')

    input_records = list(
        iter_records(load_json('extractors_and_projector_table.json')),
    )
    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 4
    assert output[0]['output'] == 'first'
    assert output[1]['output'] == 'second'
    assert output[2]['output'] == 'third'
    assert output[3]['output'] == 'fourth'
