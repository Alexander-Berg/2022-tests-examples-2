import json
import os

import pytest

from taxi.internal.yt_import.schema import loaders
import helpers


TESTCASES_DIRNAME = 'testcases'

NOW = '2018-08-21 00:00:00.0'


def flatten_dict_all_levels(dct, start_level=0, prefix='', delimiter='.'):
    """
    :param dct: dict to flatten
    :param start_level: the least included output level,
           zero includes dict itself
    :param prefix: paths prefix
    :param delimiter: delimeter to use in path
    :return: flattened dict

        >>> dct = {
        ...     'foo': {
        ...          'bar': {
        ...             'baz': 1,
        ...             'qux': 1
        ...         }
        ...     }
        ... }
        >>> flatten_dict_all_levels(dct)
        ... {
        ...    # level 0
        ...    'foo': {'bar': {'baz': 1, 'qux': 1}},
        ...    # level 1
        ...    'foo.bar': {'baz': 1, 'qux': 1},
        ...    # level 2
        ...    'foo.bar.baz': 1,
        ...    'foo.bar.qux': 1
        ... }
    """
    return dict(
        (key, value)
        for level, key, value in
        _flatten_items_all_levels(dct, prefix=prefix, delimiter=delimiter)
        if level >= start_level
    )


def _flatten_items_all_levels(dct, prefix='', delimiter='.', level=0):
    for key, value in dct.iteritems():
        if isinstance(value, dict):
            for sublevel, subkey, subvalue in _flatten_items_all_levels(
                    value,
                    prefix='{}{}{}'.format(prefix, key, delimiter),
                    delimiter=delimiter,
                    level=level + 1
            ):
                yield sublevel, subkey, subvalue
            yield level, '{}{}'.format(prefix, key), value
        else:
            yield level, '{}{}'.format(prefix, key), value


def _parametrize_mapper_testcase():
    import_rules = loaders.load_all_rules()

    parameters, ids = [], []
    for import_rule in import_rules:
        parameters.append(import_rule)
        ids.append(import_rule.name)

    return pytest.mark.parametrize('import_rule', parameters, ids=ids)


@pytest.mark.now(NOW)
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
@_parametrize_mapper_testcase()
def test_mapper(import_rule, load):
    testcase_path = os.path.join(
        TESTCASES_DIRNAME, '%s.json' % import_rule.name
    )
    testcases = json.loads(
        load(testcase_path), object_hook=helpers.bson_object_hook
    )

    for index, testcase in enumerate(testcases):
        if testcase.get('$byteify_input'):
            testcase['input'] = _byteify(testcase['input'])

        mapper = import_rule.mapper_builder(
            attributes=testcase.get('attributes')
        )
        result = mapper(testcase['input'])
        if result != testcase['expected']:
            testcase_description = (
                'Mapper output does not match expected values %s, '
                'document index %d. The exact difference in ' % (
                    testcase_path, index
                )
            )
            helpers.check_difference(
                result, testcase['expected'], testcase_description
            )

    _check_testcase_fullness(import_rule, testcase_path, testcases)


def _check_testcase_fullness(import_rule, testcase_path, testcases):
    columns = []
    for column_mapper in (import_rule.mapper_builder.column_mappers or []):
        if not column_mapper.current_date:
            columns.append(column_mapper.output_column)

    for attr_mapper in (import_rule.mapper_builder.attribute_mappers or []):
        columns.append(attr_mapper.output_column)

    unmapped_columns = set(columns)
    for index, testcase in enumerate(testcases):
        flatten_all_levels_expected = (
            flatten_dict_all_levels(testcase['expected'])
        )
        for field, value in flatten_all_levels_expected.iteritems():
            if value is not None and field in unmapped_columns:
                unmapped_columns.remove(field)
    assert not unmapped_columns, (
        '%s: please, add not only "value -> None" mapper '
        'tests for %s output columns' % (testcase_path, unmapped_columns)
    )


def _byteify(data):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    if isinstance(data, list):
        return [_byteify(item) for item in data]
    if isinstance(data, dict):
        return {
            _byteify(key): _byteify(value)
            for key, value in data.iteritems()
        }
    return data
