import pytest

from taxi.core import db
from taxi.internal import localization_update as locs


SERIALIZE_DATA = {
    'key.with.dots': [1, 2, 3],
    'object_wih_numbers_keys': {
        1: 'one int',
        2.0: 'two float'
    },
    'array': [
        1, 2.0, 'some', False,
    ],
    False: 'false',
    1: 1,
    None: None,
}


def test_serialization():
    assert SERIALIZE_DATA == locs.deserialize(locs.serialize(SERIALIZE_DATA))


@pytest.inline_callbacks
def test_serialization_and_db():
    yield db.localizations_cache.update(
        {'_id': 'test'},
        {'value': locs.serialize(SERIALIZE_DATA)},
        upsert=True,
    )

    data = yield db.localizations_cache.find_one({
        '_id': 'test',
    })
    assert SERIALIZE_DATA == locs.deserialize(data['value'])
