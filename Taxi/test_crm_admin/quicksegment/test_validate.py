# pylint: disable=bad-option-value

import pytest

from crm_admin.quicksegment import error
from crm_admin.quicksegment import validate


def get_test_schema(name, is_valid):
    if name == 'table-schema':
        schema = {
            'tables': [
                {'name': 'tableA', 'path': ''},
                {'name': 'tableB', 'path': ''},
            ],
            'root_table': 'tableA',
            'graph': [
                {
                    'how': 'left_outer',
                    'left': 'tableA',
                    'right': 'tableB',
                    'keys': 'key',
                },
            ],
        }
        if not is_valid:
            schema['root_table'] = 'tableX'
        return schema

    if name == 'filter-schema':
        schema = {
            'filters': [
                {
                    'id': 'filter-id',
                    'where': 'tableA.columnA < tableB.columnB',
                },
            ],
            'targets': ['filter-id'],
        }
        if not is_valid:
            del schema['targets']
        return schema

    assert False, 'unknown schema name: %s' % name
    return None


@pytest.mark.parametrize(
    'name, is_valid',
    [
        ('table-schema', True),
        ('table-schema', False),
        ('filter-schema', True),
        ('filter-schema', False),
    ],
)
def test_detect_schema(name, is_valid):
    schema = get_test_schema(name, is_valid)
    assert validate.detect_schema_type(schema) == name


@pytest.mark.parametrize(
    'name, is_valid',
    [
        ('table-schema', True),
        ('table-schema', False),
        ('filter-schema', True),
        ('filter-schema', False),
    ],
)
def test_validate(name, is_valid):
    schema = get_test_schema(name, is_valid)

    if is_valid:
        assert validate.validate(schema)
    else:
        with pytest.raises(error.ValidationError):
            validate.validate(schema)


@pytest.mark.parametrize(
    'first, is_valid_first, second, is_valid_second',
    [
        ('table-schema', True, 'filter-schema', True),
        ('table-schema', False, 'filter-schema', True),
        ('table-schema', True, 'filter-schema', False),
    ],
)
def test_validate_both(first, is_valid_first, second, is_valid_second):
    # pylint: disable-all

    first = get_test_schema(first, is_valid_first)
    second = get_test_schema(second, is_valid_second)

    if is_valid_first and is_valid_second:
        assert validate.validate(first, second)
        assert validate.validate(second, first)
    else:
        with pytest.raises(error.ValidationError):
            validate.validate(first, second)
            validate.validate(second, first)


@pytest.mark.parametrize(
    'keys',
    [
        ['tables', 'base_table'],
        ['tables', 'graph'],
        ['base_table', 'graph'],
        ['filters'],
        ['targets'],
    ],
)
def test_missing_keys(keys):
    schema = {key: '' for key in keys}
    with pytest.raises(error.ValidationError, match='missing keys'):
        validate.validate(schema)
