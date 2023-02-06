# pylint: disable=protected-access
import collections
import itertools
import logging
import random
import string

import bson
import yt.yson

from taxi import yt_wrapper

from replication.common.yt_tools import tables_kit
from replication.targets.yt.control.table_updater import initialize_columns
from replication.tools import yt_ctl


logger = logging.getLogger(__name__)


class DummyYtError(Exception):
    pass


# NOTE: deprecated, should refactor it with common DummyClient
# pylint: disable=too-many-locals,too-many-branches,no-self-use,unused-variable
class DummyYtClient:
    def __init__(self, name, config):
        self.name = name
        self.tables = {}
        self._attributes = {}
        self.config = config

    def __str__(self):
        return self.name

    def exists(self, path):
        node = str(path)
        if node in self.tables:
            return True
        splitted = node.split('//home/taxi/', 1)
        if len(splitted) > 1:
            return splitted[1] in self.tables
        return False

    def run_map_reduce(
            self,
            mapper,
            reducer,
            input_tables,
            output_tables,
            reduce_by,
            *args,
            **kwargs,
    ):
        class Context:
            def __init__(self, table_index):
                self.table_index = table_index

        logger.info(
            'Running map-reduce with input tables: %s, output_tables: %s',
            ', '.join(input_tables),
            ', '.join(output_tables),
        )
        all_rows = []
        if isinstance(input_tables, list):
            for index, table in enumerate(input_tables):
                if table not in self.tables:
                    raise DummyYtError
                for row in self.tables[table]:
                    new_row = row.copy()
                    context = Context(index)
                    all_rows.append((new_row, context))
        elif input_tables not in self.tables:
            raise DummyYtError
        else:
            all_rows = self.tables[input_tables]

        intermediate = []
        for row, context in all_rows:
            intermediate.extend(list(mapper(row, context)))

        rows_by_keys = collections.defaultdict(list)
        for row in intermediate:
            key = tuple(row.get(key_column) for key_column in reduce_by)
            rows_by_keys[key].append(row)

        for table in output_tables:
            self.tables.setdefault(table, [])

        for key, rows in rows_by_keys.items():
            result = list(reducer(key, rows))
            for row in result:
                if '@table_index' in row:
                    self.tables[output_tables[row.pop('@table_index')]].append(
                        row,
                    )
                elif isinstance(output_tables, list):
                    self.tables[output_tables[0]].append(row)
                else:
                    self.tables[output_tables].append(row)

        class DummyOperation:
            url = '//dummy'

            def wait(self):
                pass

        return DummyOperation()

    def create_temp_table(self, prefix, *args, **kwargs):
        new_table = prefix + ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(10)
        )
        self.tables[new_table] = []
        return new_table

    def mkdir(self, path, recursive=False):
        assert path == yt_wrapper.YT_TMP_DIRECTORY
        assert recursive

    def move(self, path_from, path_to, force=None, recursive=None):
        if force or not self.exists(path_to):
            self.tables[str(path_to)] = self.tables.pop(str(path_from))
        else:
            raise DummyYtError

    def search(self, table_path, node_type=None, attributes=None, **kwargs):
        attributes = {attr: None for attr in attributes or ()}
        assert not set(tables_kit.SEARCH_ATTRIBUTES) - set(attributes)
        res = yt.yson.to_yson_type(table_path, attributes=attributes)
        yield res

    def copy(self, path_from, path_to, force=None, recursive=None):
        if force or not self.exists(path_to):
            self.tables[str(path_to)] = list(self.tables[str(path_from)])
        else:
            raise DummyYtError

    def remove(self, path, force=False):
        if force or self.exists(path):
            self.tables.pop(str(path), None)
        else:
            raise DummyYtError

    def set(self, path, value):
        self._attributes[path] = value

    def alter_table(self, path, schema=None, dynamic=None):
        if dynamic is not None:
            self._attributes[path + '/@dynamic'] = dynamic
        if schema is not None:
            self._attributes[path + '/@schema'] = schema

    def get(self, path, attributes=None):
        if isinstance(path, str) and not isinstance(path, yt.yson.YsonString):
            if '@' in path:
                return ()
            return yt.yson.to_yson_type(
                self._attributes.get(path), attributes={},
            )
        if isinstance(path, yt.yson.YsonString):
            return path
        raise RuntimeError

    def get_attribute(self, *args, **kwargs):
        raise RuntimeError('get_attribute is deprecated')

    def reshard_table(self, path, tablet_count):
        self.set('%s/@%s' % (path, 'tablet_count'), tablet_count)

    def mount_table(self, path, sync=True):
        self.set('%s/@%s' % (path, 'tablet_state'), 'mounted')

    def unmount_table(self, path, sync=True):
        self.set('%s/@%s' % (path, 'tablet_state'), 'unmounted')

    def unfreeze_table(self, path, sync=True):
        pass

    def freeze_table(self, path, sync=True):
        pass

    def run_merge(self, input_tables, output_table, mode=None, spec=None):
        logger.info(
            'Running merge with input tables: %s, output_table: %s',
            ', '.join(input_tables)
            if isinstance(input_tables, list)
            else input_tables,
            output_table,
        )
        if isinstance(input_tables, list):
            rows = itertools.chain(
                self.tables[str(table)] for table in input_tables
            )
        else:
            rows = self.tables[input_tables]
        self.tables[output_table] = list(rows)

    def run_sort(self, table, output_table=None, sort_by=None, **kwargs):
        if not sort_by:
            raise DummyYtError
        if not output_table:
            self.tables[table].sort(
                key=lambda row: tuple(
                    row[key_column] for key_column in sort_by
                ),
            )
        else:
            self.tables[output_table] = sorted(
                self.tables[table],
                key=lambda row: tuple(
                    row[key_column] for key_column in sort_by
                ),
            )

    def create(self, *args, **kwargs):
        pass


async def test_init_columns(patch, replication_ctx, yt_config):
    all_clients = {}
    runtime_clusters = yt_config.runtime
    assert runtime_clusters

    @patch('taxi.yt_wrapper.get_client')
    def get_client(name, *args, **kwargs):
        if name not in all_clients:
            client = DummyYtClient(name, yt_config.configs[name])
            all_clients[name] = client
        else:
            client = all_clients[name]
        return client

    @patch('taxi.yt_wrapper.get_cluster_name')
    def get_cluster_name(client):
        return client.name

    @patch('taxi.yt_wrapper.transfer_manager.copy')
    def copy(paths, src_yt_client, dst_yt_clients, *args, **kwargs):
        if not isinstance(dst_yt_clients, (list, tuple)):
            dst_yt_clients = [dst_yt_clients]
        logger.info(
            'Copying %s from %s to %s',
            paths,
            src_yt_client,
            ', '.join([str(client) for client in dst_yt_clients]),
        )
        for table in paths:
            for dst_client in dst_yt_clients:
                dst_client.tables[table] = list(src_yt_client.tables[table])

    for cluster in yt_config.map_reduce:
        client = get_client(cluster)
        client.tables['test/bson_order_proc'] = []  # ensure exists
    get_client('hahn')
    all_clients['hahn'].tables['test/bson_order_proc'] = [
        {
            'id': '1',
            b'doc': bson.BSON.encode({'_id': '1', 'new_column': False}),
        },
        {
            'id': '2',
            b'doc': bson.BSON.encode({'_id': '2', 'new_column': True}),
        },
        {
            'id': '3',
            b'doc': bson.BSON.encode({'_id': '3', 'new_column': False}),
        },
    ]
    assert runtime_clusters
    for cluster in runtime_clusters:
        get_client(cluster)
        all_clients[cluster].tables['test/struct_orders_history'] = [
            {
                'id': '1',
                'hash': 'hash_1',
                'old_column': '1',
                'new_column': None,
            },
            {
                'id': '2',
                'hash': 'hash_2',
                'old_column': '2',
                'new_column': None,
            },
            {
                'id': '3',
                'hash': 'hash_3',
                'old_column': '3',
                'new_column': None,
            },
        ]

    class DummyArgs:
        dry_run = False

    await initialize_columns.initialize_columns(
        yt_ctl.BaseCommand._get_yt_helper(DummyArgs, replication_ctx),
        replace=True,
        path='test/struct_orders_history',
        target_columns=['new_column'],
        base_table_yt_cluster='hahn',
    )
    assert runtime_clusters
    for cluster in runtime_clusters:
        assert all_clients[cluster].tables['test/struct_orders_history'] == [
            {
                'id': '1',
                'hash': 'hash_1',
                'old_column': '1',
                'new_column': False,
            },
            {
                'id': '2',
                'hash': 'hash_2',
                'old_column': '2',
                'new_column': True,
            },
            {
                'id': '3',
                'hash': 'hash_3',
                'old_column': '3',
                'new_column': False,
            },
        ]
