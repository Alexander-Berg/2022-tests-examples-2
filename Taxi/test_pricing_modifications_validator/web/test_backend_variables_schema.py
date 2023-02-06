# flake8: noqa
# pylint: disable=redefined-outer-name
import pytest
import z3

from test_pricing_modifications_validator.plugins.mock_pricing_admin import (
    mock_pricing_admin,
)
from pricing_modifications_validator.models.numeric import (
    backend_variables_schema,
)


@pytest.mark.parametrize(
    'schema, expected_types, expected_constants',
    [
        ({'type': 'double'}, ('some.prefix', z3.RealSort()), []),
        (
            {'type': 'enum', 'value': ['a', 'b', 'c']},
            ('some.prefix', z3.IntSort()),
            [('a', 0), ('b', 1), ('c', 2)],
        ),
        (
            {'type': 'map', 'value': {'type': 'double'}},
            {'*': ('some.prefix.*', z3.RealSort())},
            [],
        ),
        (
            {
                'type': 'map',
                'value': {'type': 'map', 'value': {'type': 'double'}},
            },
            {'*': {'*': ('some.prefix.*.*', z3.RealSort())}},
            [],
        ),
        (
            {'type': 'object', 'value': {'foo': {'type': 'double'}}},
            {'foo': ('some.prefix.foo', z3.RealSort())},
            [],
        ),
    ],
)
def test_backend_variables_schema_parser(
        schema, expected_types, expected_constants,
):
    constants = []
    schema = backend_variables_schema.parse_bv_schema(
        schema, constants, 'some.prefix',
    )
    assert schema.to_dict() == expected_types
    assert [const.to_dict() for const in constants] == expected_constants


async def test_schema_cache_update(
        taxi_pricing_modifications_validator_web,
        testpoint,
        mockserver,
        load_json,
        mock_pricing_admin,
):
    @testpoint('bv_schema_cache_update')
    def bv_schema_cache_update(data):
        pass

    mock_pricing_admin.set_variables_response(load_json('variable_types.json'))

    await taxi_pricing_modifications_validator_web.tests_control(
        {'invalidate_caches': True},
    )

    await bv_schema_cache_update.wait_call()
