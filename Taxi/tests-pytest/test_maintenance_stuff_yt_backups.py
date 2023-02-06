import datetime
import os

import pytest

from taxi.core import db
from taxi.internal.yt_replication.schema import loaders
from taxi.internal.yt_tools import backups_util
from taxi_maintenance.stuff import yt_backups
from taxi_maintenance.stuff import yt_backups_rotate

DEFAULT_NODES_LIST = [
    '2018-02-18', '2018-02-17', '2018-02-16', '2018-02-15',
    '2018-02-14', '2018-02-13', '2018-02-12', '2018-02-05',
    '2018-01-29', '2018-01-22', '2018-02-01', '2018-01-01',
    # extra:
    '2018-02-11',
    # today:
    '2018-02-19',
]


class FakeTableObj(object):
    def __init__(self):
        self.attributes = {'compression_codec': 'lz4',
                           'erasure_codec': 'none'}


class DummyYtClient(object):
    nodes_list = DEFAULT_NODES_LIST

    def __init__(self, cluster):
        if cluster.endswith('backup'):
            self.config = {'prefix': 'test-backup/'}
        else:
            self.config = {'prefix': 'test/'}
        self.created = set()
        self.removed = set()

    def create(self, node_type, path=None,
               recursive=False, ignore_existing=False):
        self.created.add(path)

    def exists(self, path):
        return True

    def list(self, path):
        return self.nodes_list

    def remove(self, path, recursive=False):
        self.removed.add(path)

    def get_type(self, path):
        return 'table'

    def get(self, path, attributes=None):
        if attributes:
            return FakeTableObj()
        return []


@pytest.mark.now('2018-02-19 02:00:00')
@pytest.mark.parametrize(
    'event_monitor_doc,expected_copy_operations', [
        (
            None,
            {
                ('test/collections/table1',
                 'hahn/2018-02-19/collections/table1'),
                ('test/collections/table2',
                 'hahn/2018-02-19/collections/table2'),
            },
        ),
        (
            {
                '_id': 'id',
                'name': 'yt_backups',
                'created': datetime.datetime(2018, 2, 19, 1, 0),
                'rules': {
                    'hahn': [
                        {'source': 'collections/table1', 'status': 'waiting'},
                        {'source': 'collections/table2', 'status': 'success'},
                    ]
                },
                'start_day': datetime.datetime(2018, 2, 19, 0, 0),
            },
            {
                ('test/collections/table1',
                 'hahn/2018-02-19/collections/table1'),

            },
        ),
        (
            {
                '_id': 'id',
                'name': 'yt_backups',
                'created': datetime.datetime(2018, 2, 19, 1, 0),
                'rules': {
                    'hahn': [
                        {'source': 'collections/table1', 'status': 'waiting'},
                        {'source': 'collections/table2', 'status': 'success'},
                    ]
                },
            },
            set(),  # inconsistent state, no start_day in event
        ),
        (
            {
                '_id': 'id',
                'name': 'yt_backups',
                'created': datetime.datetime(2018, 2, 19, 1, 0),
                'rules': {
                    'hahn': [
                        {'source': 'collections/table1', 'status': 'success'},
                        {'source': 'collections/table2', 'status': 'success'},
                    ]
                },
                'start_day': datetime.datetime(2018, 2, 19, 0, 0),
            },
            set(),
        ),
        (
            {
                '_id': 'id',
                'name': 'yt_backups',
                'created': datetime.datetime(2018, 2, 18, 1, 0),
                'rules': {
                    'hahn': [
                        {'source': 'collections/table1', 'status': 'waiting'},
                        {'source': 'collections/table2', 'status': 'success'},
                    ]
                },
                'start_day': datetime.datetime(2018, 2, 18, 0, 0),
            },
            {
                ('test/collections/table1',
                 'hahn/2018-02-19/collections/table1'),
                ('test/collections/table2',
                 'hahn/2018-02-19/collections/table2'),
            },
        ),
    ]
)
@pytest.inline_callbacks
def test_do_stuff(patch, monkeypatch,
                  event_monitor_doc, expected_copy_operations):
    if event_monitor_doc:
        yield db.event_monitor.insert(event_monitor_doc)

    tests_static_basedir = os.path.join(
        os.path.dirname(__file__), 'static',
        os.path.splitext(os.path.basename(__file__))[0]
    )

    monkeypatch.setattr(
        loaders, 'RULES_DIR', os.path.join(tests_static_basedir, 'rules')
    )
    monkeypatch.setattr(
        loaders, 'MAPPERS_DIR', os.path.join(tests_static_basedir, 'mappers')
    )
    monkeypatch.setattr(
        loaders,
        'TABLES_META_DIR', os.path.join(tests_static_basedir, 'tables')
    )

    copy_operations = set()

    class DummyYtClientWithExists(DummyYtClient):
        def __init__(self, cluster):
            super(DummyYtClientWithExists, self).__init__(cluster)
            self.merged_tables = set()

        def exists(self, path):
            return path in self.merged_tables

    backup_client = DummyYtClientWithExists('hahn-backup')

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(cluster, environment=True, new=False, **kwargs):
        if environment:
            assert new is False
            assert cluster == 'hahn'
            return DummyYtClient(cluster)
        else:
            assert new is True
            assert cluster == 'hahn-backup'
            return backup_client

    @patch('taxi.internal.yt_tools.merge_table.run')
    def run(yt_client, copy_op, **kwargs):
        assert kwargs['spec']['data_size_per_job'] == (
            backups_util.BACKUP_DATA_SIZE_PER_JOB
        )
        copy_operations.add((copy_op.source, copy_op.destination))
        backup_client.merged_tables.add(copy_op.destination)

    yield yt_backups.do_stuff()

    assert copy_operations == expected_copy_operations
    if expected_copy_operations:
        assert backup_client.created == {'hahn/2018-02-19/collections'}

    # checks for consistency
    if event_monitor_doc:
        yield db.event_monitor.remove({'name': event_monitor_doc['name']})
        yield db.event_monitor.insert(event_monitor_doc)

    copy_operations = set()

    yield yt_backups.do_stuff()
    assert copy_operations == set()

    yield yt_backups.do_stuff()
    assert copy_operations == set()


@pytest.mark.now('2018-02-19 02:00:00')
@pytest.mark.parametrize('config_value,nodes_list,expected_removed',
    [
        (
            {'days': 7, 'weeks': 4, 'months': 12},
            DEFAULT_NODES_LIST,
            {'hahn/2018-02-11'},
        ),
        (
            {'days': 8, 'weeks': 4, 'months': 12},
            DEFAULT_NODES_LIST,
            set(),
        ),
        (
            {'days': 1, 'weeks': 0, 'months': 0},
            DEFAULT_NODES_LIST,
            {'hahn/2018-01-22', 'hahn/2018-02-05',
             'hahn/2018-02-13', 'hahn/2018-02-12',
             'hahn/2018-01-29', 'hahn/2018-02-17',
             'hahn/2018-02-16', 'hahn/2018-02-15',
             'hahn/2018-02-14', 'hahn/2018-02-01',
             'hahn/2018-01-01', 'hahn/2018-02-11'},
        ),
        (
            {'days': 1, 'weeks': 10, 'months': 0},
            DEFAULT_NODES_LIST,
            {'hahn/2018-02-17', 'hahn/2018-02-16',
             'hahn/2018-02-15', 'hahn/2018-02-14',
             'hahn/2018-02-13', 'hahn/2018-02-01',
             'hahn/2018-02-11'},
        ),
        (
            {'days': 1, 'weeks': 0, 'months': 2},
            DEFAULT_NODES_LIST,
            {'hahn/2018-02-17', 'hahn/2018-02-16',
             'hahn/2018-02-15', 'hahn/2018-02-14',
             'hahn/2018-02-13', 'hahn/2018-02-12',
             'hahn/2018-02-05', 'hahn/2018-01-29',
             'hahn/2018-01-22', 'hahn/2018-02-11'},
        ),
        (
            {'days': 3, 'weeks': 4, 'months': 0},
            ['2018-02-18', '2018-02-16', '2018-02-14', '2018-02-13',
             '2018-02-07', '2018-02-09',
             '2018-01-31', '2018-02-01',
             '2018-01-22', '2018-01-23', '2018-01-21',
             '2018-01-12', '2018-01-13', '2018-01-05', '2018-01-01'],
            {'hahn/2018-02-09', 'hahn/2018-02-01',
             'hahn/2018-01-21', 'hahn/2018-01-23',
             'hahn/2018-01-12', 'hahn/2018-01-13',
             'hahn/2018-01-05', 'hahn/2018-01-01'},
        ),
        (
            {'days': 1, 'weeks': 0, 'months': 0},
            ['2018-01-05', '2018-01-01'],
            {'hahn/2018-01-01'},
        ),
        (
            {'days': 2, 'weeks': 0, 'months': 0},
            ['2018-01-05', '2018-01-01'],
            set(),
        ),
        (
            {'days': 1, 'weeks': 1, 'months': 0},
            ['2018-01-05', '2018-01-01'],
            set(),
        ),
        (
            {'days': 1, 'weeks': 1, 'months': 0},
            ['2018-01-05', '2018-01-01', '2018-01-02'],
            {'hahn/2018-01-02'},
        ),
    ]
)
@pytest.inline_callbacks
def test_do_stuff_rotate(patch, config_value, nodes_list, expected_removed):
    yield db.config.insert(
        {'_id': 'YT_BACKUPS_ROTATE_RULES', 'v': config_value}
    )

    dummy_yt_client = DummyYtClient('hahn-backup')
    dummy_yt_client.nodes_list = nodes_list

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(cluster, environment=True, new=False, **kwargs):
        assert new is True
        assert environment is False
        assert cluster == 'hahn-backup'
        return dummy_yt_client

    yield yt_backups_rotate.do_stuff()
    assert dummy_yt_client.removed == expected_removed
