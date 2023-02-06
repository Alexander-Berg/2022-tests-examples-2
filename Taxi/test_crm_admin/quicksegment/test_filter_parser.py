# pylint: disable=protected-access,invalid-name,redefined-outer-name

import pytest

from crm_admin.quicksegment import error
from crm_admin.quicksegment import filter_parser as fp
from crm_admin.quicksegment import sqlike_parser


def parse_sqlike(query):
    return sqlike_parser.parse(query)


@pytest.mark.parametrize(
    'schema, ok',
    [
        (
            {
                'filters': [
                    {
                        'id': 'filt_a',
                        'enabled-if': (
                            '${var_a} is null and ${var_b} is not null'
                        ),
                        'where': 'col.a is not null',
                        'having': 'count(b) > 0',
                    },
                ],
                'targets': ['filt_a'],
                'extra_columns': [{'if': 'true', 'then': 'table.col'}],
            },
            True,
        ),
        (
            {
                'filters': [{'id': 'main', 'where': 'col.a ** col.b'}],
                'targets': ['main'],
            },
            False,
        ),
        (
            {'filters': [{'id': 'main', 'where': True}], 'targets': ['main']},
            False,
        ),
    ],
)
def test_parse_schema(schema, ok):
    if ok:
        filters = fp.parse_schema(schema)
        assert filters['filters']
        assert filters['targets']
        assert filters['extra_columns']
    else:
        with pytest.raises(error.ParseError):
            fp.parse_schema(schema)


@pytest.mark.parametrize(
    'extra_columns, error_msg',
    [
        ([{'if': 'true', 'then': 'table.col'}], None),
        ([{'if': 'true', 'then': 'col'}], 'Malformed extra column'),
        (['table.col'], 'Invalid extra columns format'),
    ],
)
def test_validate_extra_columns(extra_columns, error_msg):
    schema = {
        'filters': [{'id': 'filt', 'where': 'table.col is not null'}],
        'targets': ['filt'],
        'extra_columns': extra_columns,
    }

    if not error_msg:
        assert fp.parse_schema(schema)
    else:
        with pytest.raises(error.ValidationError, match=error_msg):
            fp.parse_schema(schema)


def test_validate_cycles():
    filters = {
        'filters': [
            {'id': 'filter1', 'where': parse_sqlike('%{filter2}')},
            {'id': 'filter2', 'where': parse_sqlike('%{filter3}')},
            {'id': 'filter3', 'where': parse_sqlike('%{filter1}')},
        ],
        'targets': ['filter1'],
    }
    with pytest.raises(RuntimeError, match='cycles detected'):
        fp.validate(filters)


@pytest.mark.parametrize(
    'clause_type, clause',
    [
        ('having', '%{filter-id}'),
        ('enabled-if', '%{filter-id}'),
        ('enabled-if', 'count(1)'),
        ('enabled-if', 'table.column'),
    ],
)
def test_validate_node_types(clause_type, clause):
    filters = {
        'filters': [{'id': 'filter1', clause_type: parse_sqlike(clause)}],
        'targets': ['filter1'],
    }
    with pytest.raises(RuntimeError, match='not allowed'):
        fp.validate(filters)


def test_validate_subfiters_with_having():
    filters = {
        'filters': [
            {'id': 'filter1', 'where': parse_sqlike('%{filter2}')},
            {'id': 'filter2', 'having': parse_sqlike('true')},
        ],
        'targets': ['filter1'],
    }
    with pytest.raises(RuntimeError, match='can not be a sub-exespression'):
        fp.validate(filters)


@pytest.mark.parametrize(
    'filt, error',
    [
        ({'id': 'id', 'where': '', 'having': '', 'enabled-if': ''}, None),
        ({'id': 'id', 'history_depth_days': ''}, None),
        ({'where': '', 'having': ''}, '"id" is a required field'),
        ({'id': 'id', 'unknown key': ''}, 'unexpected fields'),
    ],
)
def test_validate_fields(filt, error):
    if error:
        with pytest.raises(RuntimeError, match=error):
            fp._validate_keys([filt])
    else:
        fp._validate_keys([filt])


@pytest.mark.parametrize(
    'filters, ok',
    [
        (
            # check variables in sub-filters too
            [
                {
                    'id': 'filt_a',
                    'where': parse_sqlike('%{filt_b}'),
                    'enabled-if': parse_sqlike(
                        '${var_a} is null and ${var_b} is not null',
                    ),
                },
                {'id': 'filt_b', 'where': parse_sqlike('${var_b} > col_b')},
            ],
            True,
        ),
        (
            # check the `having` clause
            [
                {
                    'id': 'filt_a',
                    'having': parse_sqlike('count(col) > ${var_a}'),
                    'enabled-if': parse_sqlike('${var_a} is not null'),
                },
            ],
            True,
        ),
        (
            # no `enabled-if` clause
            [{'id': 'filt_a', 'where': parse_sqlike('count(col) > ${var_a}')}],
            True,
        ),
        (
            # `var_a` is not mentioned in `enabled-if`
            [
                {
                    'id': 'filt_a',
                    'where': parse_sqlike('count(col) > ${var_a}'),
                    'enabled-if': parse_sqlike('${var_b} is null'),
                },
            ],
            False,
        ),
    ],
)
def test_validate_enabled_if(filters, ok):
    if ok:
        fp._validate_enbaled_if(filters)
    else:
        with pytest.raises(RuntimeError, match='variables can be undefined'):
            fp._validate_enbaled_if(filters)
