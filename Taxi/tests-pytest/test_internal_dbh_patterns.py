import bson
import pytest

from taxi.core import db
from taxi.internal import dbh


@pytest.mark.parametrize('kwargs, error_instance', [
    (
        {
            'name': 'pattern',
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'important': True,
                    'default': None,
                    'constraint': None
                }
            },
            'ticket': 'TAXIRATE-10'
        },
        None
    ),
    (
        {
            'name': 'test_pattern_1',
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'important': True,
                    'default': None,
                    'constraint': None
                }
            },
            'ticket': 'TAXIRATE-10'
        },
        dbh.patterns.DuplicateError
    ),
    (
        {
            'name': 'pattern',
            'pattern_type': 'commission1',
            'doc': {
                'vat': {
                    'important': True,
                    'default': None,
                    'constraint': None
                }
            },
            'ticket': 'TAXIRATE-10'
        },
        dbh.patterns.PatternTypeError
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_create_pattern(kwargs, error_instance):
    try:
        result = yield dbh.patterns.Doc.create_pattern(**kwargs)
        assert bool(result)
        record = yield db.patterns.find_one({'_id': result})
        assert record.pop('_id') == result
        assert record.pop('version') == 1
        assert record == kwargs
    except Exception as ex:
        assert isinstance(ex, error_instance)


@pytest.mark.parametrize('name,ident,is_found', [
    ('test_pattern_1', '', True),
    ('pattern', None, False)
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_find_by_name(name, ident, is_found):
    try:
        doc = yield dbh.patterns.Doc.find_by_name(name)
        assert doc.pk == bson.ObjectId(ident)
        assert is_found
    except dbh.patterns.NotFound:
        assert not is_found


@pytest.mark.parametrize('kwargs, error_instance', [
    (
        {
            'name': 'pattern',
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'important': True,
                    'default': None,
                    'constraint': None
                }
            },
            'ticket': 'TAXIRATE-10',
            'version': 2,
            'ident': bson.ObjectId('5cc09f28efb903fd53a793ab')
        },
        None
    ),
    (
        {
            'name': 'pattern',
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'important': True,
                    'default': None,
                    'constraint': None
                }
            },
            'ticket': 'TAXIRATE-10',
            'version': 2,
            'ident': bson.ObjectId('9cc09f28efb903fd53a793ab')
        },
        dbh.patterns.NotFound
    ),
    (
        {
            'name': 'test_pattern_1',
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'important': True,
                    'default': None,
                    'constraint': None
                }
            },
            'ticket': 'TAXIRATE-10',
            'version': 2,
            'ident': bson.ObjectId('5cc09f28efb903fd53a793ab')
        },
        dbh.patterns.DuplicateError
    ),
    (
        {
            'name': 'test_pattern_1',
            'pattern_type': 'commission1',
            'doc': {
                'vat': {
                    'important': True,
                    'default': None,
                    'constraint': None
                }
            },
            'ticket': 'TAXIRATE-10',
            'version': 2,
            'ident': bson.ObjectId('5cc09f28efb903fd53a793ab')
        },
        dbh.patterns.PatternTypeError
    ),
    (
        {
            'name': 'test_pattern_1',
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'important': True,
                    'default': None,
                    'constraint': None
                }
            },
            'ticket': 'TAXIRATE-10',
            'version': 3,
            'ident': bson.ObjectId('5cc09f28efb903fd53a793ab')
        },
        dbh.patterns.VersionMismatch
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_update_pattern(kwargs, error_instance):
    try:
        result = yield dbh.patterns.Doc.update_pattern(**kwargs)
        assert bool(result)
        record = yield db.patterns.find_one({'_id': kwargs['ident']})
        assert record.pop('_id') == kwargs.pop('ident')
        assert record.pop('version') == kwargs.pop('version') + 1
        assert record == kwargs
    except Exception as ex:
        assert isinstance(ex, error_instance)
