import collections
import contextlib
import datetime
import json
import uuid

import bson
import pytest

from taxi.conf import settings
from taxi.config import api as config_api
from taxi.core import async
from taxi.core import db
from taxi.internal.yt_replication.rules import rule_names
from taxi_maintenance.stuff import process_mia_requests

ERROR_MSG = 'MIA test failure'


@pytest.mark.config(MIA_MAP_REDUCE_SETTINGS={
    'pool': 'production',
    'job_spec': {'data_weight_per_job': 10000},
    'client': 'arnold',
})
@pytest.inline_callbacks
def test_get_yt_client(monkeypatch, patch):
    monkeypatch.setattr(
        settings, 'YT_POOLS', {'production': {'arnold': 'taxi-production'}}
    )
    monkeypatch.setattr(settings, 'YT_MAPREDUCE_USE_CACHE_IN_JOBS', False)

    @patch('taxi.external.yt_wrapper.create_client_with_config')
    def create_client_with_config(config, *args, **kwargs):
        assert (
            config.get('spec_overrides', {}).get('pool') == 'taxi-production'
        )
        assert (
            config.get('spec_defaults', {}).get('data_weight_per_job') == 10000
        )
        return DummyYtClient({})
    yield process_mia_requests._get_yt_client()


class DummyFilterInfo(object):
    def __init__(self, interval, no_join=True):
        self.interval = interval
        self.filter_query = interval
        self.no_join = no_join


@pytest.mark.parametrize(
    'force_batch,requests_filters,expected', [
        (
            False,
            {
                'query1': DummyFilterInfo((
                    datetime.datetime(2018, 4, 28),
                    datetime.datetime(2018, 5, 28),
                )),
                'query2': DummyFilterInfo((
                    datetime.datetime(2018, 1, 28),
                    datetime.datetime(2018, 1, 29),
                )),
                'query3': DummyFilterInfo((
                    datetime.datetime(2018, 1, 28),
                    datetime.datetime(2018, 1, 29),
                )),
                'query4': DummyFilterInfo((
                    datetime.datetime(2018, 1, 28),
                    datetime.datetime(2018, 1, 29),
                ), no_join=False),
            },
            {
                ('2018-04', '2018-05'): {('query1',)},
                ('2018-01',): {('query4',), ('query2', 'query3')},
            }
        ),
        (
            True,
            {
                'query1': DummyFilterInfo((
                    datetime.datetime(2018, 4, 28),
                    datetime.datetime(2018, 5, 28),
                )),
                'query2': DummyFilterInfo((
                    datetime.datetime(2018, 1, 28),
                    datetime.datetime(2018, 1, 29),
                )),
                'query3': DummyFilterInfo((
                    datetime.datetime(2018, 1, 28),
                    datetime.datetime(2018, 1, 29),
                )),
                'query4': DummyFilterInfo((
                    datetime.datetime(2018, 1, 28),
                    datetime.datetime(2018, 1, 29),
                ), no_join=False),
            },
            {
                ('2018-01', '2018-04', '2018-05'): {
                    ('query1', 'query2', 'query3'),
                },
                ('2018-01',): {('query4',)},
            }
        )
    ]
)
@pytest.mark.asyncenv('blocking')
def test_group_requests(force_batch, requests_filters, expected, patch):
    @patch('taxi.internal.mia.filters.get_query_interval')
    def get_query_interval(query):
        return query

    batches = process_mia_requests._group_requests(
        requests_filters, force_batch
    )
    batches_dict = collections.defaultdict(set)

    for batch in batches:
        batches_dict[tuple(batch.tables)].add(tuple(batch.requests_ids))

    assert dict(batches_dict) == expected


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
@pytest.mark.parametrize('too_many_results, results_expected', [
    (1, False), (3, True)
])
@pytest.mark.now('2019-01-01 00:00:00')
def test_process_requests(patch, monkeypatch, load, too_many_results,
                          replication_yt_target_info,
                          results_expected):
    yield config_api.save('MIA_MAX_RESULTS', too_many_results)

    def load_table(name, is_bson=False):
        rows = bson.json_util.loads(
            load('table_' + name.replace('/', '_') + '.json')
        )
        if is_bson:
            return_rows = [
                {
                    'id': row['_id'],
                    'doc': byteify(row),
                }
                for row in rows
            ]
            return return_rows
        return byteify(rows)

    tables = {
        'replica/mongo/struct/orders_full': load_table(
            'collections/struct/orders_full'
        ),
        'replica/mongo/struct/drivers': load_table(
            'collections/struct/drivers'
        ),
        'filtered_tmp': load_table(
            'filtered_tmp'
        ),
        'private/mongo/bson/user_phones': load_table(
            'collections/bson/user_phones',
            is_bson=True,
        ),
        'private/mongo/bson/parks': load_table(
            'collections/parks',
            is_bson=True,
        ),
        'private/mongo/bson/dba_parks': load_table(
            'collections/dba_parks',
            is_bson=True,
        ),
        'private/mongo/bson/cities': load_table(
            'collections/cities',
            is_bson=True,
        ),
        'private/mongo/bson/drivers': load_table(
            'collections/bson/drivers',
            is_bson=True,
        ),
        'private/mongo/bson/order_proc': load_table(
            'collections/bson/order_proc',
            is_bson=True,
        ),
        'private/mongo/struct/order_proc_mia/candidates': load_table(
            'collections/struct/mia/candidates',
        ),
    }
    yt_client = DummyYtClient(tables)

    replication_tables = {
        'drivers_struct': 'replica/mongo/struct/drivers',
        'parks': 'private/mongo/bson/parks',
        'dbparks_pda_parks_bson': 'private/mongo/bson/dba_parks',
        'cities': 'private/mongo/bson/cities',
        'user_phones_bson': 'private/mongo/bson/user_phones',
        'drivers': 'private/mongo/bson/drivers',
        rule_names.orders_full_orders: 'replica/mongo/struct/orders_full',
        rule_names.order_proc_bson: 'private/mongo/bson/order_proc',
        rule_names.order_proc_mia_candidates: (
            'private/mongo/struct/order_proc_mia/candidates'
        ),
    }
    replication_yt_target_info(
        {target_name: {'table_path': table}
         for target_name, table in replication_tables.iteritems()}
    )

    mds_uploads = []

    @patch('taxi.external.yt_wrapper.tmp_tables')
    @contextlib.contextmanager
    def tmp_tables(prefixes, yt_client, clean=True, attributes=None):
        table_names = [prefix + '_tmp' for prefix in prefixes]
        yield table_names

    @patch('taxi.external.yt_wrapper.get_client')
    @async.inline_callbacks
    def get_client(cluster, dyntable=False, environment=True, fail=True,
                   new=False, extra_config_overrides=None, pool=None):
        yield async.return_value(yt_client)

    @patch('taxi.external.mds.upload')
    @async.inline_callbacks
    def upload(fileobj, log_extra=None):
        mds_uploads.append(fileobj.read())
        yield async.return_value(len(mds_uploads) - 1)

    monkeypatch.setattr(bson, 'BSON', FakeBSON)

    yield process_mia_requests.do_stuff()
    request = yield db.mia_requests.find_one('query_id')
    if results_expected:
        assert len(mds_uploads) == 2
        result = json.loads(mds_uploads[0])

        assert [
            (order['driver_name'], order['driver_phone'])
            for order in result['umbrella_orders']
        ] == [
            ('C', '3'),
            ('A', '1'),
            ('B', '2'),
        ]

        assert request['status'] == 'succeeded'
        assert len(result['umbrella_orders']) == 3
        assert len(result['orders']) == 0
        for umbrella_order in result['umbrella_orders']:
            assert len(umbrella_order['embedded_orders']) == 1
    else:
        assert request['status'] == 'failed'
        assert request['error'] == 'Search has returned too many results (3)'
        assert len(mds_uploads) == 0


class DummyYtClient(object):
    def __init__(self, tables):
        self.tables = tables

    def TablePath(self, name, **kwargs):
        return name

    def run_map(self, mapper, input_tables, output_path,
                format=None, sync=True):
        if not sync:
            return DummyYtOperation('/operations/' + uuid.uuid4().hex)

    def run_map_reduce(self, mapper, reducer, input_tables, output_path,
                       reduce_by, format, sort_by, sync=True):
        if not sync:
            return DummyYtOperation('/operations/' + uuid.uuid4().hex)

    def row_count(self, table_name):
        return len(self.tables[table_name])

    def read_table(self, table_name, **kwargs):
        return byteify(self.tables[table_name])

    def write_table(self, table_name, rows):
        self.tables[table_name] = list(rows)

    def run_sort(self, table_name, sort_by):
        def sort_key(row):
            return [row[key] for key in sort_by]

        self.tables[table_name].sort(key=sort_key)

    def lookup_rows(self, path, query, column_names=None):
        table = self.tables[path]
        result = []
        for row in table:
            match = any(
                self.row_matches_query_item(row, query_item)
                for query_item
                in query
            )
            if match:
                result.append(self.filter_columns(row, column_names))
        return result

    def row_matches_query_item(self, row, query_item):
        for key, value in query_item.iteritems():
            if key not in row or row[key] != value:
                return False
        return True

    def filter_columns(self, row, column_names):
        if column_names is None:
            return row
        return {
            key: value
            for key, value
            in row.iteritems()
            if key in column_names
        }


class DummyYtOperation(object):
    def __init__(self, url):
        self.url = url

    def wait(self):
        pass


class FakeBSON(object):
    def __init__(self, doc):
        self.doc = doc

    def decode(self):
        return self.doc


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
