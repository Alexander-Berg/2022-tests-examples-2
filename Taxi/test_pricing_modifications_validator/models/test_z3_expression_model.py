# pylint: disable=import-only-modules
import pytest
import z3

from generated.models.pricing_admin import Variables

from pricing_modifications_validator.models.numeric import (
    backend_variables_schema,
)
from pricing_modifications_validator.models.z3 import pretty_printer
from pricing_modifications_validator.models.z3 import scan_context
from pricing_modifications_validator.models.z3 import z3_expression

SCHEMA_EXAMPLE = {
    'type': 'object',
    'value': {
        'x': {'type': 'double'},
        'obj_field': {'type': 'object', 'value': {'y': {'type': 'string'}}},
        'map_field': {
            'type': 'map',
            'value': {
                'type': 'object',
                'value': {
                    'z': {'type': 'boolean'},
                    'foo': {'type': 'object', 'value': {}},
                },
            },
        },
    },
}


def fetch_meta_type(schema, name) -> z3_expression.ExpressionType:
    current_type = schema
    path = name if isinstance(name, list) else name.split('.')
    for name_it in path:
        current_type = current_type.get_field(name_it)
    return current_type


@pytest.mark.parametrize(
    'name,expected_type',
    [
        ('x', ('x', z3.RealSort())),
        ('obj_field', {'y': ('obj_field.y', z3.StringSort())}),
        ('obj_field.y', ('obj_field.y', z3.StringSort())),
        (
            'map_field',
            {'*': {'z': ('map_field.*.z', z3.BoolSort()), 'foo': {}}},
        ),
        ('map_field.some.z', ('map_field.*.z', z3.BoolSort())),
    ],
)
def test_simple_z3_expr_models_get_type(name, expected_type):
    schema = backend_variables_schema.parse_bv_schema(SCHEMA_EXAMPLE, [], '')
    result_type = fetch_meta_type(schema, name)
    assert result_type.to_dict() == expected_type


def any_field_const(name):
    return z3.Const(name, z3_expression.ANY_FIELD)


@pytest.mark.parametrize(
    'name, expected_name, z3_value',
    [
        ('obj_field', 'obj_field', any_field_const('obj_field')),
        ('map_field', 'map_field', any_field_const('map_field')),
    ],
)
def test_simple_z3_expr_models_get_name(name, expected_name, z3_value):
    schema = backend_variables_schema.parse_bv_schema(SCHEMA_EXAMPLE, [], '')
    result_type = fetch_meta_type(schema, name)
    assert result_type.get_name() == expected_name


def _map_model(imap: z3_expression.MapExpressionValue):
    solver = z3.Solver()
    for decl in imap.get_z3_value_with_decls():
        if z3.is_bool(decl):
            solver.add(decl)
    # solver = z3.Solver()
    # solver.set('timeout', 600)
    new_solver = z3.Solver(ctx=z3.Context())
    new_solver.from_string(solver.to_smt2())
    assert new_solver.check() == z3.sat
    model = new_solver.model()
    return model.translate(z3.main_ctx())


def _map_set(imap: z3_expression.MapExpressionValue, key: str, value: float):
    imap[
        z3_expression.AnonimousExpressionValue(z3.StringVal(key))
    ] = z3_expression.AnonimousExpressionValue(z3.RealVal(value))


def _map_at(imap: z3_expression.MapExpressionValue, key: str) -> z3.ExprRef:
    return _map_model(imap).evaluate(imap[z3.StringVal(key)].get_z3_value())


def _map_has_key(
        imap: z3_expression.MapExpressionValue, key: str,
) -> z3.ExprRef:
    return _map_model(imap).evaluate(
        imap.has_field(z3.StringVal(key)).get_z3_value(),
    )


def _map_no_key(imap: z3_expression.MapExpressionValue, key: str) -> bool:
    return _map_has_key(imap, key) == z3.BoolVal(False)


def test_dynamic_empty_map():
    empty_map = z3_expression.MapExpressionValue('m')
    assert _map_no_key(empty_map, 'test')


def test_dynamic_map_insertion():
    map_with_one_value = z3_expression.MapExpressionValue('m')
    _map_set(map_with_one_value, 'test', 11)
    assert _map_no_key(map_with_one_value, 'some-key')
    assert _map_at(map_with_one_value, 'test') == z3.RealVal(11)


def test_dynamic_map_merge():
    map_a = z3_expression.MapExpressionValue('map_a')
    _map_set(map_a, 'test', 42)
    map_b = z3_expression.MapExpressionValue('map_b')
    _map_set(map_b, 'test', 43)
    _map_set(map_b, 'another_test', -1)
    map_c = map_a.merge(map_b)
    assert _map_at(map_c, 'test') == z3.RealVal(43)
    assert _map_at(map_c, 'another_test') == z3.RealVal(-1)


def test_external_map():
    meta_type = z3_expression.DynamicMapExpressionType(
        z3.StringSort(), z3.RealSort(),
    )
    external_map = z3.Const('external_map', meta_type.get_z3_type())
    imap = z3_expression.MapExpressionValue('map_a', value=external_map)
    _map_set(imap, 'test', 42)
    assert _map_at(imap, 'test') == z3.RealVal(42)
    assert not z3.is_const(_map_has_key(imap, 'another_test'))


class DummyAstProcessingContext(scan_context.AstProcessingContext):
    def __init__(self):
        backend_variables = backend_variables_schema.BackendVariablesSchema(
            Variables.deserialize({'fix': {}, 'ride': {}, 'trip': {}}),
        )
        super().__init__(backend_variables)


def test_ternary_object_access():
    ctx = DummyAstProcessingContext()
    real_opt_type = z3_expression.OptionalExpressionType(
        z3_expression.AnonimousExpressionType(z3.RealSort()),
    )
    obj_type = z3_expression.NamedTupleExpressionType(
        'Object', {'sub_value': real_opt_type},
    )
    obj_a = z3_expression.AnonimousExpressionValue(
        ctx.current_scope().create_any_field_const('a'), obj_type,
    )
    obj_b = z3_expression.AnonimousExpressionValue(
        ctx.current_scope().create_any_field_const('b'), obj_type,
    )
    expr = z3_expression.AnonimousLazyCondExpressionValue(
        z3.BoolVal(True), obj_a, ctx, obj_b,
    )
    sub_field = expr.get_field('sub_value')
    assert sub_field.is_optional()
    assert (
        pretty_printer.pprint(sub_field.dereference().get_z3_value())
        == 'If(True, deref_Real(Object._opt), deref_Real(Object._opt))'
    )
