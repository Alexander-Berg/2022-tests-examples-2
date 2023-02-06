import datetime

import pytest

from taxi.core import db
from taxi.internal.yt_import import importer


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
@pytest.mark.parametrize('docs,expected', [
    (None, False),
    ([{'_id': 'foo'}], False),
    ([{'_id': 'foo', 'disabled': True}], True),
])
def test_is_import_disabled(docs, expected):
    if docs:
        yield db.yt_imports.insert(docs)

    stored_meta = yield importer._get_stored_meta('foo')
    result = importer._is_import_disabled(stored_meta)

    assert result == expected


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
@pytest.mark.parametrize('docs,values,expected', [
    (
        None,
        {'last_synced': datetime.datetime(2018, 8, 3, 20, 0, 0)},
        {
            '_id': 'foo',
            'last_synced': datetime.datetime(2018, 8, 3, 20, 0, 0),
        },
    ),
    (
        [
            {
                '_id': 'foo',
                'last_synced': datetime.datetime(2018, 8, 3, 20, 0, 0),
            },
        ],
        {
            'last_synced': datetime.datetime(2018, 8, 3, 21, 30, 0),
            'last_started': datetime.datetime(2018, 8, 3, 21, 0, 0),
        },
        {
            '_id': 'foo',
            'last_synced': datetime.datetime(2018, 8, 3, 21, 30, 0),
            'last_started': datetime.datetime(2018, 8, 3, 21, 0, 0),
        },
    ),
])
def test_set_yt_import_values(docs, values, expected):
    if docs:
        yield db.yt_imports.insert(docs)

    yield importer.set_yt_import_values('foo', **values)
    result = yield db.yt_imports.find_one('foo')

    assert result == expected
