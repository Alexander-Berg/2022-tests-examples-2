import copy
import datetime

import bson
import pytest

from taxi.core import db
from taxi.internal import yt_import
from taxi.internal.yt_import.validation.input_validators import (
    user_antifraud_rules as uar_validation
)
from taxi.internal.yt_import import schema
from taxi.internal.yt_import import validation


_NOW = datetime.datetime(2018, 7, 19, 12, 13, 14)

_MAX_SIMPLE_RULES_COUNT = 20
_MAX_COMPLEX_RULES_COUNT = 10

_SIMPLE_RULE = {
    'type': uar_validation.SIMPLE_RULE_TYPE,
    'value': 'value_simple',
}
_COMPLEX_RULE = {'type': 'type_complex', 'value': 'value_complex'}

_YT_IMPORT_RULE_NAME = 'user_antifraud_rules'
_YT_USER_ANTIFRAUD_RULES_TABLE = (
    'fraud/user_antifraud_rules/user_antifraud_rules'
)


class DummyYtClient(object):
    def __init__(self, rows):
        self.rows = rows

    def read_table(self, table_name, format='json'):
        assert table_name == _YT_USER_ANTIFRAUD_RULES_TABLE
        return self.rows

    def exists(self, table_name):
        assert table_name == _YT_USER_ANTIFRAUD_RULES_TABLE
        return True

    def get(self, path):
        path, attr = path.split('/@')
        return self.get_attribute(path, attr)

    def get_attribute(self, path, attribute):
        assert attribute == 'modification_time'
        return None


@pytest.fixture
def custom_rules_count_limits(monkeypatch):
    monkeypatch.setattr(
        uar_validation, 'MAX_SIMPLE_RULES_COUNT', _MAX_SIMPLE_RULES_COUNT,
    )
    monkeypatch.setattr(
        uar_validation, 'MAX_COMPLEX_RULES_COUNT', _MAX_COMPLEX_RULES_COUNT,
    )


@pytest.fixture
def clean_rules_cache(monkeypatch):
    monkeypatch.setattr(schema, '_all_rules', {})


@pytest.fixture
def patch_get_yt_client(patch):
    def patcher(rows):
        yt_client = DummyYtClient(rows)

        @patch('taxi.external.yt_wrapper.get_client')
        def get_client(cluster, environment, new, **kwargs):
            assert cluster == 'hahn-dwh'
            assert environment
            assert new
            return yt_client

    return patcher


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('num_simple,num_complex', [
    (0, 1),
    (1, 0),
    (1, 1),
    (_MAX_SIMPLE_RULES_COUNT, _MAX_COMPLEX_RULES_COUNT),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.inline_callbacks
def test_import_data_do_insert(num_simple, num_complex, patch_get_yt_client,
                               custom_rules_count_limits, clean_rules_cache):
    simple_rules, complex_rules = (
        _build_yt_antifraud_rules(num_simple, num_complex)
    )
    patch_get_yt_client(complex_rules + simple_rules)

    yield yt_import.import_data(_YT_IMPORT_RULE_NAME)

    simple_rule = _build_mongo_rule(_SIMPLE_RULE)
    complex_rule = _build_mongo_rule(_COMPLEX_RULE)

    expected = [simple_rule] * num_simple + [complex_rule] * num_complex
    docs = yield db.user_antifraud_rules.find().run()

    assert sorted(_pop(docs, ('_id',))) == sorted(_pop(expected, ('_id',)))


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('num_simple,num_complex,raises', [
    (0, 0, False),
    (_MAX_SIMPLE_RULES_COUNT + 1, _MAX_COMPLEX_RULES_COUNT, True),
    (_MAX_SIMPLE_RULES_COUNT, _MAX_COMPLEX_RULES_COUNT + 1, True),
    (_MAX_SIMPLE_RULES_COUNT + 1, _MAX_COMPLEX_RULES_COUNT + 1, True),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.inline_callbacks
def test_import_data_do_not_insert(num_simple, num_complex, raises,
                                   patch_get_yt_client,
                                   custom_rules_count_limits,
                                   clean_rules_cache):
    simple_rules, complex_rules = (
        _build_yt_antifraud_rules(num_simple, num_complex)
    )
    patch_get_yt_client(complex_rules + simple_rules)

    if raises:
        with pytest.raises(validation.InputValidationError):
            yield yt_import.import_data(_YT_IMPORT_RULE_NAME)
    else:
        yield yt_import.import_data(_YT_IMPORT_RULE_NAME)

    expected = [
        {
            '_id': bson.ObjectId('5b5092636bf78eaba89a9495'),
            'type': 'geo',
            'value': {'radius': 100, 'center': [37.596675, 55.583842]},
            'created': datetime.datetime(2018, 7, 18, 17, 45),
        },
        {
            '_id': bson.ObjectId('5b5092636bf78eaba89a9496'),
            'type': 'metrica_device_id',
            'value': 'bf7d96111a1fb53b0d74df17676a35b5',
            'created': datetime.datetime(2018, 7, 18, 17, 45),
        }
    ]
    docs = yield db.user_antifraud_rules.find().run()

    assert sorted(docs) == sorted(expected)


def _build_mongo_rule(yt_base_rule):
    mongo_rule = copy.copy(yt_base_rule)
    mongo_rule['created'] = _NOW

    return mongo_rule


def _build_yt_antifraud_rules(num_simple, num_complex):
    simple_rules = [{'rule': _SIMPLE_RULE}] * num_simple
    complex_rules = [{'rule': _COMPLEX_RULE}] * num_complex

    return simple_rules, complex_rules


def _pop(docs, keys):
    cleaned_docs = copy.deepcopy(docs)

    for doc in cleaned_docs:
        for key in keys:
            doc.pop(key, None)

    return cleaned_docs
