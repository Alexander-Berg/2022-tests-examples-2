# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import bson
import copy
import json

from django.test import Client
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal.patterns_kit import patterns
from taxiadmin import audit

VALID_TAXIRATE = 'TAXIRATE-10'
EXISTED_ID = '5cc09f28efb903fd53a793ab'
NOT_EXISTED_ID = '5cc09f28efb903fd53a793ac'


@pytest.fixture(autouse=True)
def perform_mocks(patch):
    @patch('taxiadmin.audit.check_taxirate')
    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        if ticket_key != VALID_TAXIRATE:
            raise audit.TicketError
        yield async.return_value()


@pytest.mark.parametrize('request_data,expected_code,is_added', [
    (
        {
            'doc': {
                'type': {
                    'constraint': None,
                    'default': 'str',
                    'important': True
                }
            },
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions'
        },
        200,
        True
    ),
    (
        {
            'doc': {
                'completion_rate': {
                    'constraint': None,
                    'default': 1,
                    'important': True
                },
                'tariffzone': {
                    'constraint': None,
                    'default': 'dedovsk',
                    'important': True
                }
            },
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'subventions'
        },
        200,
        True
    ),
    (
        {
            'doc': {
                'type': {
                    'constraint': None,
                    'default': 'str',
                    'important': True
                }
            },
            'name': 'test_pattern_2',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions'
        },
        409,
        False
    ),
    (
        {
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0.3',
                            'end': '0.55'
                        }
                    },
                    'default': '0.27',
                    'important': False
                }
            },
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions'
        },
        400,
        False
    ),
    (
        {
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0.3',
                            'end': '0.55'
                        }
                    },
                    'default': '0.27',
                    'important': False
                }
            },
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'NO_EXISTED_TYPE'
        },
        400,
        False
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_pattern_create(request_data, expected_code, is_added):
    response = Client().post(
        '/api/patterns/create/',
        json.dumps(request_data),
        'application/json'
    )

    assert response.status_code == expected_code
    response_data = json.loads(response.content)
    if is_added:
        assert response_data['id']
        doc = yield db.patterns.find_one({
            'name': request_data['name']
        })
        assert bson.ObjectId(doc.pop('_id'))
        assert doc.pop('version') == 1
        assert request_data == doc
    elif expected_code == 200:
        assert response_data['id'] is None


@pytest.mark.parametrize('request_data,expected_code,is_deleted', [
    (
        {
            'id': EXISTED_ID,
            'ticket': VALID_TAXIRATE
        },
        200,
        True
    ),
    (
        {
            'id': NOT_EXISTED_ID,
            'ticket': VALID_TAXIRATE
        },
        200,
        False
    ),
    (
        {
            'id': 'not_object_id',
            'ticket': VALID_TAXIRATE
        },
        400,
        False
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_pattern_delete(request_data, expected_code, is_deleted):
    response = Client().post(
        '/api/patterns/delete/',
        json.dumps(request_data),
        'application/json'
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        assert json.loads(response.content)['deleted'] == is_deleted
        if is_deleted:
            result = yield db.patterns.find_one({
                '_id': bson.ObjectId(request_data['id'])
            })
            assert not result


@pytest.mark.parametrize('query_string,expected_code,expected_data', [
    (
        '?pattern_id=5cc09f28efb903fd53a793a1',
        200,
        {
            'id': '5cc09f28efb903fd53a793a1',
            'pattern_type': 'commissions',
            'name': 'test_pattern_2',
            'version': 1,
            'doc': {
                'type': {
                    'constraint': {
                        'type': 'const',
                        'const': 'test_type'
                    },
                    'default': None,
                    'important': False
                }
            }
        }
    ),
    ('', 400, None),
    ('?pattern_id=wrong_id', 400, None),
    ('?pattern_id=1cc09f28efb903fd53a793ab', 404, None)
])
@pytest.mark.asyncenv('blocking')
def test_get_pattern_and_list(query_string, expected_code, expected_data):
    _check_patterns(False, query_string, expected_code, expected_data)


@pytest.mark.parametrize('query_string,expected_code,expected_data', [
    (
        '?limit=1&offset=1&pattern_type=commissions',
        200,
        {
            'items': [{
                'id': '5cc09f28efb903fd53a793a1',
                'pattern_type': 'commissions',
                'name': 'test_pattern_2',
                'version': 1,
                'doc': {
                    'type': {
                        'constraint': {
                            'type': 'const',
                            'const': 'test_type'
                        },
                        'default': None,
                        'important': False
                    }
                }
            }]
        }
    ),
    (
        '?limit=2',
        200,
        {
            'items': [{
                'doc': {
                    'branding_discounts': {
                        'default': [{
                            'value': '0.4'
                        }, {
                            'marketing_level': ['sticker'],
                            'value': '0.4'
                        }],
                        'important': True,
                        'constraint': {
                            'items_constraint': {
                                'type': 'object_constraint',
                                'fields_constraint': {
                                    'value': {
                                        'type': 'const',
                                        'const': '0.4'
                                    }
                                }
                            },
                            'type': 'array_constraint'
                        }
                    },
                    'type': {
                        'default': None,
                        'important': True,
                        'constraint': None
                    },
                    'has_fixed_cancel_percent': {
                        'default': False,
                        'important': False,
                        'constraint': {
                            'type': 'const',
                            'const': False
                        }
                    },
                    'payment_type': {
                        'default': 'card',
                        'important': False,
                        'constraint': {
                            'enum': ['card', 'cash'],
                            'type': 'enum'
                        }
                    },
                    'expired_percent': {
                        'default': '0.01',
                        'important': True,
                        'constraint': None
                    },
                    'tariff_class': {
                        'default': None,
                        'important': False,
                        'constraint': {
                            'regex': '[a-z]+',
                            'type': 'regex'
                        }
                    },
                    'vat': {
                        'default': '0.01',
                        'important': False,
                        'constraint': {
                            'range': {
                                'start': '0',
                                'end': '0.53'
                            },
                            'type': 'range'
                        }
                    }
                },
                'id': EXISTED_ID,
                'name': 'test_pattern_1',
                'pattern_type': 'commissions',
                'version': 2
            }, {
                'id': '5cc09f28efb903fd53a793a1',
                'pattern_type': 'commissions',
                'name': 'test_pattern_2',
                'version': 1,
                'doc': {
                    'type': {
                        'constraint': {
                            'type': 'const',
                            'const': 'test_type'
                        },
                        'default': None,
                        'important': False
                    }
                }
            }]
        }
    ),
    ('?limit=z&offset=z', 400, None),
])
@pytest.mark.asyncenv('blocking')
def test_patterns_list(query_string, expected_code, expected_data):
    _check_patterns(True, query_string, expected_code, expected_data)


def _check_patterns(is_list, query_string, expected_code, expected_data):
    path = '/api/patterns/'
    if is_list:
        path += 'list/'
    path += '{}'
    response = Client().get(
        path.format(query_string)
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        response_data = json.loads(response.content)
        assert response_data == expected_data


@pytest.mark.parametrize('request_data,expected_code', [
    (
        {
            'id': EXISTED_ID,
            'version': 2,
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0'
                        }
                    },
                    'default': '1',
                    'important': False
                }
            }
        },
        200
    ),
    (
        {
            'id': 'wrong_id',
            'version': 1,
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0',
                            'end': '1'
                        }
                    },
                    'default': '1',
                    'important': False
                }
            }
        },
        400
    ),
    (
        {
            'id': EXISTED_ID,
            'version': 2,
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0',
                            'end': 1
                        }
                    },
                    'default': '1',
                    'important': False
                }
            }
        },
        400
    ),
    (
        {
            'id': EXISTED_ID,
            'version': 2,
            'name': 'pattern',
            'ticket': 'wrong_ticket',
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0',
                            'end': '1'
                        }
                    },
                    'default': '1',
                    'important': False
                }
            }
        },
        406
    ),
    (
        {
            'id': NOT_EXISTED_ID,
            'version': 2,
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0',
                            'end': '1'
                        }
                    },
                    'default': '1',
                    'important': False
                }
            }
        },
        404
    ),
    (
        {
            'id': EXISTED_ID,
            'version': 3,
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0',
                            'end': '1'
                        }
                    },
                    'default': '1',
                    'important': False
                }
            }
        },
        409
    ),
    (
        {
            'id': EXISTED_ID,
            'version': 2,
            'name': 'test_pattern_2',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0',
                            'end': '1'
                        }
                    },
                    'default': '1',
                    'important': False
                }
            }
        },
        409
    ),
    (
        {
            'id': EXISTED_ID,
            'version': 2,
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'some_type',
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0',
                            'end': '1'
                        }
                    },
                    'default': '1',
                    'important': False
                }
            }
        },
        400
    ),
    (
        {
            'id': EXISTED_ID,
            'version': 2,
            'name': 'pattern',
            'ticket': VALID_TAXIRATE,
            'pattern_type': 'commissions',
            'doc': {
                'vat': {
                    'constraint': {
                        'type': 'range',
                        'range': {
                            'start': '0',
                            'end': '1'
                        }
                    },
                    'default': '2',
                    'important': False
                }
            }
        },
        400
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_edit_pattern(request_data, expected_code):
    response = Client().post(
        '/api/patterns/edit/',
        json.dumps(request_data),
        'application/json'
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        response_data = json.loads(response.content)
        expected_data = copy.deepcopy(request_data)
        expected_data['_id'] = bson.ObjectId(expected_data.pop('id'))
        expected_data['version'] += 1
        assert response_data['updated']
        doc = yield db.patterns.find_one({
            'name': request_data['name']
        })
        assert doc == expected_data


@pytest.mark.parametrize('start,end,to_check,is_error', [
    (10, 20, 5, True),
    (10, 20, 15, False),
    (None, 20, 30, True),
    (None, 20, -10, False),
    (-10, None, -20, True),
    (-10, None, 50, False),
    (None, None, 10, False),
    (10, 10, 10, False),
    ('0.1', '1', '0.4', False),
    ('-0.1', '0.1', '1.0', True),
    ('z', 'z', 'z', True),
    ('z.z', 'z', 'z', True),
    (2, 0, 1, True)
])
@pytest.mark.asyncenv('blocking')
def test_range_constraint(start, end, to_check, is_error):
    _test_constraint_by_instance(
        to_check, is_error, patterns.RangeConstraint, start, end
    )


@pytest.mark.parametrize('enum,to_check,is_error', [
    (['a', 'b', 'c'], 'd', True),
    (['a', 'b', 'c'], 'a', False),
    ([], 'a', True),
    ([1, 2, 3], 1, False),
    (
        [{
            'args': {
                'arg': 1
            }
        }],
        {
            'args': {
                'arg': 1
            }
        },
        False
    )
])
@pytest.mark.asyncenv('blocking')
def test_enum_constraint(enum, to_check, is_error):
    _test_constraint_by_instance(
        to_check, is_error, patterns.EnumConstraint, enum
    )


@pytest.mark.parametrize('const,to_check,is_error', [
    ('abc', 'b', True),
    ('abc', 'abc', False),
    (None, None, True),
    (1, 1, False),
    (
        {
            'args': {
                'arg': 1
            }
        },
        {
            'args': {
                'arg': 1
            }
        },
        False
    )
])
@pytest.mark.asyncenv('blocking')
def test_const_constraint(const, to_check, is_error):
    _test_constraint_by_instance(
        to_check, is_error, patterns.ConstConstraint, const
    )


def _create_constraint(constraint_raw):
    return patterns.create_constraint_by_json(constraint_raw)


@pytest.mark.parametrize('regex,to_check,is_error', [
    ('[a-z]+', 'meowmeowmeow', False),
    ('[a-z]+', 'meowmeowmeow1', True)
])
@pytest.mark.asyncenv('blocking')
def test_regex_constraint(regex, to_check, is_error):
    _test_constraint_by_instance(
        to_check, is_error, patterns.RegexConstraint, regex
    )


@pytest.mark.parametrize('items_constraint,to_check,is_error', [
    (
        {
            'type': 'range',
            'range': {
                'start': -5
            }
        },
        [-4, -3, -2, -1, 0, 1, 2, 3, 4],
        False
    ),
    (
        {
            'type': 'range',
            'range': {
                'start': -2
            }
        },
        [-4, -3, -2, -1, 0, 1, 2, 3, 4],
        True
    ),
    (
        {
            'type': 'array_constraint',
            'items_constraint': {
                'type': 'range',
                'range': {
                    'end': 5
                }
            }
        },
        [
            [1, 2, 3],
            [3, 4],
            [1]
        ],
        False
    ),
    (
        {
            'type': 'array_constraint',
            'items_constraint': {
                'type': 'range',
                'range': {
                    'end': 0
                }
            }
        },
        [
            [1, 2, 3],
            [3, 4],
            [1]
        ],
        True
    )
])
@pytest.mark.asyncenv('blocking')
def test_array_constraint(items_constraint, to_check, is_error):
    array_constraint = {
        'type': 'array_constraint',
        'items_constraint': items_constraint
    }
    _test_contraint_by_raw(
        to_check, is_error, array_constraint
    )


@pytest.mark.parametrize('fields_constraint,to_check,is_error', [
    (
        {
            'meow': {
                'type': 'const',
                'const': 1
            }
        },
        {
            'meow': 1,
            'test': 2
        },
        False
    ),
    (
        {
            'meow': {
                'type': 'const',
                'const': 1
            }
        },
        {
            'test': 2
        },
        False
    ),
    (
        {
            'meow': {
                'type': 'const',
                'const': 1
            }
        },
        {
            'meow': 2,
            'test': 2
        },
        True
    ),
    (
        {
            'meow': {
                'type': 'const',
                'const': 1
            },
            'test': {
                'type': 'object_constraint',
                'fields_constraint': {
                    'field1': {
                        'type': 'const',
                        'const': 1
                    },
                    'field2': {
                        'type': 'object_constraint',
                        'fields_constraint': {
                            'test': {
                                'type': 'const',
                                'const': 2
                            }
                        }
                    }
                }
            }
        },
        {
            'meow': 1,
            'test': {
                'field': 0,
                'field1': 1,
                'field2': {
                    'test': 2
                }
            }
        },
        False
    ),
    (
        {
            'meow': {
                'type': 'const',
                'const': 1
            },
            'test': {
                'type': 'object_constraint',
                'fields_constraint': {
                    'field1': {
                        'type': 'const',
                        'const': 1
                    },
                    'field2': {
                        'type': 'object_constraint',
                        'fields_constraint': {
                            'test': {
                                'type': 'const',
                                'const': 2
                            }
                        }
                    }
                }
            }
        },
        {
            'meow': 1,
            'test': {
                'field': 0,
                'field1': 1,
                'field2': {
                    'test': 1
                }
            }
        },
        True
    )
])
@pytest.mark.asyncenv('blocking')
def test_object_constraint(fields_constraint, to_check, is_error):
    object_constraint = {
        'type': 'object_constraint',
        'fields_constraint': fields_constraint
    }
    _test_contraint_by_raw(
        to_check, is_error, object_constraint
    )


@pytest.mark.parametrize('pattern_ids,to_check,is_error', [
    (
        ['5cc09f28efb903fd53a793a1'],
        {
            'type': 'test_type',
            'meow': 'meow'
        },
        False
    ),
    (
        ['5cc09f28efb903fd53a793a1'],
        {
            'type': 'test_ty1pe',
            'meow': 'meow'
        },
        True
    ),
    (
        ['5cc09f28efb903fd53a793ab'],
        {
            'type': '',
            'payment_types': [
                'cash'
            ],
            'tariff_classes': [
                'meow'
            ],
            'expired_percent': '',
            'has_fixed_cancel_percent': False,
            'vat': '0.2',
            'branding_discounts': [{
                'value': '0.4'
            }]
        },
        False
    ),
    (
        ['5cc09f28efb903fd53a793ab', '5cc09f28efb903fd53a793a1'],
        {
            'type': 'test_type',
            'payment_types': [
                'cash'
            ],
            'tariff_classes': [
                'meow'
            ],
            'expired_percent': '',
            'has_fixed_cancel_percent': False,
            'vat': '0.2',
            'branding_discounts': [{
                'value': '0.4'
            }]
        },
        False
    ),
    (
        ['5cc09f28efb903fd53a793ab', '5cc09f28efb903fd53a793a1'],
        {
            'type': 'test_typ1e',
            'payment_types': [
                'cash'
            ],
            'tariff_classes': [
                'meow'
            ],
            'expired_percent': '',
            'has_fixed_cancel_percent': False,
            'vat': '0.2',
            'branding_discounts': [{
                'value': '0.4'
            }]
        },
        True
    )
])
@pytest.mark.asyncenv('blocking')
def test_pattern_constraint(pattern_ids, to_check, is_error):
    pattern_raw = {
        'type': 'pattern_constraint',
        'patterns': pattern_ids
    }
    _test_constraint_by_instance(
        to_check, is_error, _create_constraint, pattern_raw
    )


def _test_contraint_by_raw(to_check, is_error, raw_constraint):
    _test_constraint_by_instance(
        to_check, is_error, _create_constraint, raw_constraint
    )


def _test_constraint_by_instance(to_check, is_error, instance, *args):
    try:
        constraint = instance(*args)
        constraint.check(to_check)
    except patterns.ConstraintError as ex:
        print(ex)
        assert is_error
    else:
        assert not is_error
