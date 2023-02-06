import pytest

from taxi.internal.yt_tools import consts
from taxi.internal.yt_tools.combine_chunks import schema
from taxi_maintenance.stuff import yt_combine_chunks


class TableObj(object):
    def __init__(self, path, attrs):
        self.path = path
        self.attributes = dict(attrs)

    def __str__(self):
        return self.path


PAST = '2018-07-27T23:40:00.020544Z'

GOOD_CHUNK_SIZE = consts.ONE_MB * (500 + 10)
BAD_CHUNK_SIZE = consts.ONE_MB * (500 - 10)

ATTRS_OK = {
    'chunk_count': 300,
    'data_weight': 300 * GOOD_CHUNK_SIZE,
    'modification_time': PAST,
    'compression_codec': 'lz4',
    'revision': 119090855245611,
}

ATTRS_NEED_COMBINE = {
    'chunk_count': 300,
    'data_weight': 300 * BAD_CHUNK_SIZE,
    'modification_time': PAST,
    'compression_codec': 'lz4',
    'revision': 119090855245611,
}

ATTRS_NEED_CHANGE_CODEC = {
    'chunk_count': 300,
    'data_weight': 300 * GOOD_CHUNK_SIZE,
    'modification_time': PAST,
    'compression_codec': 'none',
    'revision': 119090855245611,
}

ATTRS_FRESH = {
    'chunk_count': 300,
    'data_weight': 300 * BAD_CHUNK_SIZE,
    'modification_time': '2018-07-27T23:50:00.020544Z',
    'compression_codec': 'lz4',
    'revision': 119090855245611,
}

TABLES = [
    TableObj('path1', ATTRS_OK),
    TableObj('path2', ATTRS_OK),
    TableObj('path-no-compressed', ATTRS_NEED_CHANGE_CODEC),
    TableObj('path-to-combine', ATTRS_NEED_COMBINE),
    TableObj('path-fresh', ATTRS_FRESH),
]


class _DummyYtClient(object):
    config = {'prefix': '//home/taxi/env/'}

    def __init__(self, tables, name):
        self.name = name
        self.data = {table.path: table for table in tables}

    def exists(self, path):
        assert path == '//home/taxi/env'
        return True

    def get_type(self, path):
        return consts.MAP_NODE

    def get(self, path):
        table, attr = path.split('/@')
        return self.data[table].attributes[attr]


@pytest.mark.now('2018-07-27 23:55:00')
def test_do_stuff(patch):
    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(name, *args, **kwargs):
        return _DummyYtClient(TABLES, name)

    default_rule = schema.SimpleCombineRule(
        'name', [''], 600, consts.ONE_MB * 500, 'lz4', None, True
    )
    client_names = ('name_1', 'name_2')

    @patch('taxi.internal.yt_tools.combine_chunks.schema.load_rules')
    def load_rules():
        return [schema.ClusterCombineRule(client_name, default_rule)
                for client_name in client_names]

    @patch('taxi.internal.yt_tools.tables_kit.search_static_tables')
    def search_static_tables(yt_client, *args, **kwargs):
        return yt_client.data.values()

    processed = {
        'name_1': {'combined': set(), 'merged': set()},
        'name_2': {'combined': set(), 'merged': set()},
    }

    @patch('taxi_maintenance.stuff.yt_combine_chunks._set_last_chunk_size')
    def _set_last_chunk_size(yt_client, table_obj, revision):
        processed[yt_client.name]['combined'].add(str(table_obj))

    @patch('taxi_maintenance.stuff.yt_combine_chunks._combine_table')
    def _combine_table(yt_client, table_obj, combine_rule, start_revision):
        assert combine_rule == default_rule
        assert yt_combine_chunks._check_codecs_and_chunk_size(
            table_obj, default_rule), str(table_obj)
        processed[yt_client.name]['merged'].add(str(table_obj))
        return True

    yt_combine_chunks.do_stuff()

    for client_name in client_names:
        assert processed[client_name]['combined'] == {
            'path1', 'path2', 'path-to-combine', 'path-no-compressed'
        }
        assert processed[client_name]['merged'] == {
            'path-to-combine', 'path-no-compressed'
        }
