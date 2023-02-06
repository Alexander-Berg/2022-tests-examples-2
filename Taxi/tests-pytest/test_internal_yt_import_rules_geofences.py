# -*- coding: utf-8 -*-

import json

import pytest

from taxi.core import db
from taxi.internal import yt_import
from taxi.internal.yt_import import schema
import helpers


YT_IMPORT_RULE_NAME = 'geofences'

GEOFENCES_YT_SOURCE_TABLE = '//home/taxi-analytics/tst_geofences'


@pytest.fixture
def clean_rules_cache(monkeypatch):
    monkeypatch.setattr(schema, '_all_rules', {})


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    GEOFENCES_YT_SOURCE_TABLE=GEOFENCES_YT_SOURCE_TABLE,
    GEOFENCES_CHUNK_SIZE=10,
)
@pytest.inline_callbacks
def test_do_stuff(clean_rules_cache, load, patch):
    yt_zones_rows = _json_loads_byteified(load('yt_zones_rows.json'))
    expected = json.loads(
        load('expected.json'), object_hook=helpers.bson_object_hook
    )

    yt_client = _DummyYtClient({GEOFENCES_YT_SOURCE_TABLE: yt_zones_rows})

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(cluster, environment, new, **kwargs):
        assert cluster == 'hahn'
        assert environment
        assert new
        return yt_client

    yield yt_import.import_data(YT_IMPORT_RULE_NAME)

    docs = yield db.geofences.find().run()

    assert sorted(docs) == sorted(expected)


class _DummyYtClient(object):
    _TMP_TABLE_PREFIX = '//home/taxi/_tst/tmp/'
    _PHONE_ID_COLUMN = 'phone_id'

    def __init__(self, tables_data):
        self._tables_data = tables_data
        self.config = {'operation_tracker': {'stderr_logging_level': 'DEBUG'}}

    def read_table(self, table, *args, **kwargs):
        return iter(self._tables_data[table])

    def run_sort(self, source_table, destination_table, sort_by):
        assert sort_by == self._PHONE_ID_COLUMN
        data = sorted(
            self._tables_data[source_table],
            key=lambda row: row[self._PHONE_ID_COLUMN]
        )
        self._tables_data[destination_table] = data

    def exists(self, node_path):
        assert node_path == GEOFENCES_YT_SOURCE_TABLE
        return True

    def remove(self, node_path):
        self._tables_data.pop(node_path)

    def create_temp_table(self, prefix):
        table_path = '{}{}'.format(self._TMP_TABLE_PREFIX, prefix)
        self._tables_data[table_path] = []
        return table_path

    def get(self, path):
        path, attr = path.split('/@')
        return self.get_attribute(path, attr)

    def get_attribute(self, path, attribute):
        assert attribute == 'modification_time'
        return None


def _json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True,
    )


def _byteify(data, ignore_dicts=False):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True):
                _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    return data
