import copy
import datetime
import json

import pytest

import helpers
from taxi.core import db
from taxi.internal import yt_import
from taxi.internal.yt_import import schema


_NOW = datetime.datetime(2018, 9, 3, 12, 13, 14)


_YT_SURGE_TRENDS_TABLE = ('//home/taxi-crm/production/'
                          'logs/surge_predictions/actual_data')
_YT_IMPORT_RULE_NAME = 'surge_trends'


class _DummyYtClient(object):
    def __init__(self, rows):
        self.rows = rows

    def read_table(self, table_name, format='json'):
        assert table_name == _YT_SURGE_TRENDS_TABLE
        return self.rows

    def exists(self, table_name):
        assert table_name == _YT_SURGE_TRENDS_TABLE
        return True

    def get(self, path):
        path, attr = path.split('/@')
        return self.get_attribute(path, attr)

    def get_attribute(self, path, attribute):
        assert attribute == 'modification_time'
        return None


@pytest.fixture
def clean_rules_cache(monkeypatch):
    monkeypatch.setattr(schema, '_all_rules', {})


@pytest.fixture
def patch_get_yt_client(patch):
    def patcher(rows):
        yt_client = _DummyYtClient(rows)

        @patch('taxi.external.yt_wrapper.get_client')
        def get_client(cluster, environment, new, **kwargs):
            assert cluster == 'hahn'
            assert environment
            assert new
            return yt_client

    return patcher


@pytest.mark.asyncenv('blocking')
@pytest.mark.now(_NOW.isoformat())
@pytest.inline_callbacks
def test_import_data_do_insert(patch_get_yt_client, clean_rules_cache, load):
    source_data = json.loads(load('source_data.json'))
    expected = json.loads(load('expected.json'), object_hook=helpers.bson_object_hook)

    patch_get_yt_client(source_data)

    yield yt_import.import_data(_YT_IMPORT_RULE_NAME)

    result = yield db.surge_trends.find().run()

    result = sorted(_pop(result, ('_id', 'updated')))

    assert result == expected


def _pop(docs, keys):
    cleaned_docs = copy.deepcopy(docs)

    for doc in cleaned_docs:
        for key in keys:
            doc.pop(key, None)

    return cleaned_docs
