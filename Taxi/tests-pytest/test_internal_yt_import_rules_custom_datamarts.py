import json
import datetime

import pytest

from taxi.core import db
from taxi.internal import yt_import
from taxi.internal.yt_import import schema

_NOW = datetime.datetime(2018, 5, 28, 12, 13, 14)

YT_IMPORT_RULE_NAME = 'custom_datamarts_driver_license'

YT_SOURCE_TABLE = 'custom_datamarts/driver_license'


@pytest.fixture
def clean_rules_cache(monkeypatch):
    monkeypatch.setattr(schema, '_all_rules', {})


@pytest.mark.parametrize('prefill', [True, False])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_import(clean_rules_cache, load, patch, prefill):
    yt_table = json.loads(load('yt_table.json'))
    expected = json.loads(load('expected.json'))

    yt_client = _DummyYtClient(
        tables_data={YT_SOURCE_TABLE: yt_table},
        mod_time=None,
    )

    if prefill:
        existing = json.loads(load('existing.json'))
        yield db.antifraud_custom_datamarts_driver_license.insert(existing)

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(cluster, environment, new, **kwargs):
        assert cluster == 'hahn-fraud'
        assert environment
        assert new
        return yt_client

    yield yt_import.import_data(YT_IMPORT_RULE_NAME)

    docs = yield db.antifraud_custom_datamarts_driver_license.find().run()

    for doc in docs:
        created = doc.pop('created')
        assert created == _NOW

    assert sorted(docs) == sorted(expected)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_import_no_updates(clean_rules_cache, load, patch):
    yt_table = json.loads(load('yt_table.json'))
    existing = json.loads(load('existing.json'))

    yield db.antifraud_custom_datamarts_driver_license.insert(existing)
    yield db.yt_imports.insert({
        '_id': 'custom_datamarts_driver_license',
        'last_yt_modification_time': _NOW.isoformat(),
    })

    yt_client = _DummyYtClient(
        tables_data={YT_SOURCE_TABLE: yt_table},
        mod_time=_NOW.isoformat(),
    )

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(cluster, environment, new, **kwargs):
        assert cluster == 'hahn-fraud'
        assert environment
        assert new
        return yt_client

    yield yt_import.import_data(YT_IMPORT_RULE_NAME)

    docs = yield db.antifraud_custom_datamarts_driver_license.find().run()

    assert sorted(docs) == sorted(existing)


class _DummyYtClient(object):
    def __init__(self, tables_data, mod_time):
        self._tables_data = tables_data
        self._mod_time = mod_time

    def read_table(self, table, *args, **kwargs):
        return iter(self._tables_data[table])

    def exists(self, node_path):
        assert node_path == YT_SOURCE_TABLE

        return True

    def get(self, path):
        path, attr = path.split('/@')
        return self.get_attribute(path, attr)

    def get_attribute(self, table, attribute):
        assert attribute == 'modification_time'
        return self._mod_time
