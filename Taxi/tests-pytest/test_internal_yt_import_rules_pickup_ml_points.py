import json

from yt.yson import yson_types
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import yt_import
from taxi.internal.yt_import import schema
import helpers


YT_IMPORT_RULE_NAME = 'pickup_ml_points'

PICKUP_POINTS_ML_YT_SOURCE_TABLE = 'tst/pickup_ml_points'
PICKUP_POINTS_ML_YT_SOURCE_TABLE_MOD_TIME = (
    'tst/pickup_ml_points/@modification_time'
)
YT_SOURCE_TABLE_MODIFICATION_TIME = '2018-08-01T17:00:00.0Z'


@pytest.fixture
def clean_rules_cache(monkeypatch):
    monkeypatch.setattr(schema, '_all_rules', {})


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    PICKUP_POINTS_ML_YT_SOURCE_TABLE=PICKUP_POINTS_ML_YT_SOURCE_TABLE,
    PICKUP_POINTS_ML_YT_CHUNK_SIZE=10,
)
@pytest.inline_callbacks
def test_do_stuff(clean_rules_cache, load, patch, monkeypatch):
    original_bulk_init = db.pickup_ml_points.initialize_unordered_bulk_op

    @patch('taxi.core.db.pickup_ml_points.initialize_unordered_bulk_op')
    def initialize_unordered_bulk_op():
        bulk = original_bulk_init()
        bulk_wrapper = _BulkWrapper(bulk)

        return bulk_wrapper

    yt_pickup_ml_points = json.loads(load('yt_pickup_ml_points.json'))
    expected = json.loads(
        load('expected.json'), object_hook=helpers.bson_object_hook
    )

    yt_client = _DummyYtClient(
        tables_data={PICKUP_POINTS_ML_YT_SOURCE_TABLE: yt_pickup_ml_points}
    )

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(cluster, environment, new, **kwargs):
        assert cluster == 'hahn'
        assert environment
        assert new
        return yt_client

    yield yt_import.import_data(YT_IMPORT_RULE_NAME)

    docs = yield db.pickup_ml_points.find().run()

    assert sorted(docs) == sorted(expected)

    assert _BulkWrapper.inserted == ['to_insert']
    assert _BulkWrapper.updated == ['to_update']
    assert _BulkWrapper.removed == ['to_remove']


class _DummyYtClient(object):
    _TMP_TABLE_PREFIX = '//home/taxi/_tst/tmp/'
    _ID_COLUMN = 'id'

    def __init__(self, tables_data):
        self._tables_data = tables_data
        self.config = {'operation_tracker': {'stderr_logging_level': 'DEBUG'}}

    def read_table(self, table, *args, **kwargs):
        return iter(self._tables_data[table])

    def run_sort(self, source_table, destination_table, sort_by):
        assert source_table == PICKUP_POINTS_ML_YT_SOURCE_TABLE
        assert sort_by == self._ID_COLUMN

        data = sorted(
            self._tables_data[source_table],
            key=lambda row: row[self._ID_COLUMN]
        )
        self._tables_data[destination_table] = data

    def exists(self, node_path):
        assert node_path == PICKUP_POINTS_ML_YT_SOURCE_TABLE

        return True

    def get(self, path, attributes=None):
        if attributes is None:
            assert path == PICKUP_POINTS_ML_YT_SOURCE_TABLE_MOD_TIME
            return YT_SOURCE_TABLE_MODIFICATION_TIME
        else:
            assert path == PICKUP_POINTS_ML_YT_SOURCE_TABLE
            assert attributes == ('modification_time',)

        yson_entity = yson_types.YsonEntity()
        yson_entity.attributes['modification_time'] = (
            YT_SOURCE_TABLE_MODIFICATION_TIME
        )

        return yson_entity

    def remove(self, node_path):
        self._tables_data.pop(node_path)

    def create_temp_table(self, prefix, attributes=None):
        table_path = '{}{}'.format(self._TMP_TABLE_PREFIX, prefix)
        self._tables_data[table_path] = []

        return table_path


class _BulkWrapper(object):
    inserted = []
    removed = []
    updated = []

    def __init__(self, bulk):
        self.bulk = bulk
        self._pre_inserted = []
        self._pre_removed = []
        self._pre_updated = []

    def insert(self, doc):
        self._pre_inserted.append(doc['_id'])
        return self.bulk.insert(doc)

    def update(self, spec, document):
        self._pre_updated.append(spec['_id'])
        return self.bulk.update(spec, document)

    def find(self, doc):
        return _FindWrapper(self.bulk.find(doc), doc, self._pre_removed)

    @async.inline_callbacks
    def execute(self):
        self.inserted.extend(self._pre_inserted)
        self.removed.extend(self._pre_removed)
        self.updated.extend(self._pre_updated)

        async.return_value((yield self.bulk.execute()))


class _FindWrapper(object):
    def __init__(self, bulk_write_op, query, pre_removed):
        self.bulk_write_op = bulk_write_op
        self._query = query
        self._pre_removed = pre_removed

    def remove(self):
        self._pre_removed.append(self._query['_id'])
        return self.bulk_write_op.remove()
