import os

import pytest

from replication_core import transform
from replication_core.mapping import context as context_mod
from replication_core.parsers import mappers as mappers_parser
from replication_core.pytest_plugins import mappers as parametrize_mappers

_RULES_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    'static/test_mappers',
))


MAP_DATA_PARAMS = pytest.mark.parametrize('src_row,expected_output', [
    ({'foo': 'bar', 'x': 1}, [{'foo': 'bar', 'x2': 1, 'x3': 1}]),
    ({'foo': 'bar', 'x': 2}, [{'foo': 'bar', 'x2': 4, 'x3': 8}]),
    ({'dummy': 'nope'}, [{'foo': None, 'x2': None, 'x3': None}]),
])


@MAP_DATA_PARAMS
def test_mapper(get_file_path, src_row, expected_output):
    context = context_mod.MapBuildingContext(
        cast_models={
            'pow2': _pow2_cast,
            'pow3': _pow3_cast,
        },
        input_transform_models={},
        premap_models={
            'rename_foo': _rename_foo,
        },
    )
    mapper = mappers_parser.load_yaml(
        get_file_path(
            'single_scope/mappers/mapper-basic.yaml'), context=context)

    rows = [row for row in mapper.transform(src_row)]
    assert rows == expected_output


@transform.castfunction
def _pow2_cast(arg):
    return arg ** 2


@transform.castfunction
def _pow3_cast(arg):
    return arg ** 3


def _rename_foo(doc):
    yield {
        key if key != 'foo' else 'bar': value for key, value in doc.items()
    }


@parametrize_mappers.parametrize_mappers(_RULES_DIR)
@MAP_DATA_PARAMS
def test_mappers_parametrize(mapper_check, rule_scope, mapper_path, mapper,
                             testcase_path,
                             src_row, expected_output):
    mapper_check(
        mapper_path, mapper,
        testcase_docs=[{'input': src_row, 'expected': expected_output}],
        check_fullness=False,
    )
