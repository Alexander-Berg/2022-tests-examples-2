# pylint: disable=import-only-modules
import typing

import pytest
import z3

from generated.models.pricing_admin import Variables

from pricing_modifications_validator.models.numeric import (
    backend_variables_schema,
)
from pricing_modifications_validator.models.symbolic import (
    constraint_parser as cparser,
)
import pricing_modifications_validator.models.symbolic.dagparser as dparser
from pricing_modifications_validator.models.symbolic.parser_context import (
    ParserContext,
)
from pricing_modifications_validator.models.z3 import assertion_builder
from pricing_modifications_validator.models.z3 import auto_checker
from pricing_modifications_validator.models.z3 import model_builder
from pricing_modifications_validator.models.z3 import pretty_printer
from pricing_modifications_validator.models.z3 import scan_context
from pricing_modifications_validator.models.z3 import z3_expression
from pricing_modifications_validator.models.z3.scan_context import (
    AstProcessingContext,
)
from pricing_modifications_validator.models.z3.z3_expression import (
    NamedExpressionValue,
)


def __normalize_str(value):
    return ' '.join(filter(len, value.replace('\n', '').split(' ')))


@pytest.mark.parametrize(
    'ast, expected_sexprs',
    [
        pytest.param(
            'R(B(x,/,PROOF_NEVER(B(B(y,+,x),<,0),B(y,+,x))))',
            [{'0 > y + x'}],
            id='simple_check',
        ),
        pytest.param(
            'R(T(B(B(x,==,42),&&,PROOF_NEVER(B(x,==,0),true)),1,2))',
            [{'0 == x', '42 == x'}],
            id='check_with_lazy_and_evaluation',
        ),
        pytest.param(
            'R(T(B(B(x,==,42),||,PROOF_NEVER(B(x,==,0),true)),1,2))',
            [{'0 == x', 'Not(42 == x)'}],
            id='check_with_lazy_or_evaluation',
        ),
        pytest.param(
            'IF(B(x,>,0),R(PROOF_NEVER(B(B(x,+,y),<,0),x)));R(1)',
            [{'0 < x', '0 > x + y'}],
            id='with_condition_context',
        ),
        pytest.param(
            'IF(B(x,>,0),R(1),R(PROOF_NEVER(B(B(x,+,y),<,0),x)));R(1)',
            [{'Not(0 < x)', '0 > x + y'}],
            id='else_branch',
        ),
        pytest.param(
            'IF(B(x,>,0),R(1));R(PROOF_NEVER(B(x,<,0),x))',
            [{'Not(0 < x)', '0 > x'}],
            id='early_return',
        ),
        pytest.param(
            'IF(U(?,B(F(fix),.,F(b))),R(1));R(PROOF_NEVER(B(F(x),<,0),'
            'B(F(fix),.,F(x))))',
            [{'Not(True)', '0 > x'}],
            id='check_non_opt_field_is_initialized',
        ),
        pytest.param(
            'IF(U(?,B(F(fix),.,F(b_opt))),R(1));R(PROOF_NEVER(B(F(x),<,0),'
            'B(F(fix),.,F(x))))',
            [{'Not(is_initialized(fix.b_opt_opt) == True)', '0 > x'}],
            id='check_field_is_initialized',
        ),
        pytest.param(
            'IF(B("b",in,B(F(fix),.,F(map_field))),R(1));R(PROOF_NEVER'
            '(B(F(x),<,0),B(F(fix),.,F(x))))',
            [{'Not(has_key(fix.map_field, "b") == True)', '0 > x'}],
            id='check_field_contains',
        ),
        pytest.param(
            'R(T(B(x,<,y),PROOF_NEVER(B(VA(x),<,0),F(x)),F(x)))',
            [{'x < y', '0 > x'}],
            id='ternary_check',
        ),
        pytest.param(
            'FUNC(min,ARGS((a,double),(b,double)),B(IF(B(FA(a,double),<,'
            'FA(b,double)),CR(res=FA(a,double)),CR(res=FA(b,double)))));'
            'R(PROOF_NEVER(B(B(FC(min,NT(a=B(x,+,2),b=24),R(res=double)),.,'
            'TF(res)),<,0),1))',
            [{'0 > If(24 > x + 2, x + 2, 24)'}],
            id='function_call',
        ),
        pytest.param(
            'FUNC(min,ARGS((a,double),(b,double)),B(IF(B(FA(a,double),<,FA'
            '(b,double)),CR(res=FA(a,double)),CR(res=FA(b,double)))));'
            'SV(a,42);R(PROOF_NEVER(B(B(FC(min,NT(a=B(x,+,B(2,*,VA(a))),b=24),'
            'R(res=double)),.,TF(res)),<,0),1))',
            [{'0 > If(24 > x + 2*42, x + 2*42, 24)'}],
            id='variable_override',
        ),
        pytest.param(
            'FUNC(min,ARGS((a,double),(b,double)),B(SV(z,3);IF(B(FA(a,double),'
            '<,B(FA(b,double),+,z)),CR(res=FA(a,double)),'
            'CR(res=FA(b,double)))));R(PROOF_NEVER(B(B(FC(min,NT(a=5,b=24),'
            'R(res=double)),.,TF(res)),<,0),1))',
            [{'0 > If(5 < 24 + 3, 5, 24)'}],
            id='store_value_info_function',
        ),
        pytest.param(
            'FUNC(min,ARGS((a,double),(b,double)),B(CR(res=T(B(FA(a,double),'
            '<,FA(b,double)),FA(a,double),FA(b,double)))));'
            'R(PROOF_NEVER(B(B(FC(min,NT(a=1,b=2),R(res=double)),.,'
            'TF(res)),<,0),1))',
            [{'0 > If(1 < 2, 1, 2)'}],
            id='min_with_ternary',
        ),
        pytest.param(
            'FUNC(min,ARGS((a,double),(b,double)),B(CR(res=T(PROOF_NEVER(B'
            '(FA(a,double),<,FA(b,double)),true),FA(a,double),FA(b,double))))'
            ');R(B(FC(min,NT(a=x,b=y),R(res=double)),.,TF(res)))',
            [{'x < y'}],
            id='assert_inside_function',
        ),
        pytest.param(
            'FUNC(foo,ARGS((x,double)),B(IF(B(FA(x,double),<,1),CR(res=1));'
            'CR(res=PROOF_NEVER(B(FA(x,double),<,0),1))));'
            'R(B(FC(foo,NT(a=x),R(res=double)),.,TF(res)))',
            [{'0 > x', 'Not(1 > x)'}],
            id='early_return_inside_function',
        ),
        pytest.param(
            'FUNC(foo,ARGS((arg1,int),(arg2,y),(elem,someCppType)),'
            'B(CR(arg1=PROOF_NEVER(B(B(FA(arg1,int),+,FA(arg2,double)),<,0)'
            ',B(FA(arg1,int),+,1)),arg2=B(FA(arg2,double),*,2))));SV(tmp,FL'
            '(B(F(fix),.,F(arr)),elem,NT(arg1=1,arg2=y),FC(foo,NT(elem=VA'
            '(elem),arg1=VA(arg1),arg2=VA(arg2)),R(arg1=int,arg2=double))));'
            'R(1)',
            [
                {
                    '_fold_result_23_m[1].arg1 == '
                    '_fold_result_23_m[0].arg1 + 1',
                    '_fold_result_23 != _fold_result_23_m.*',
                    '_fold_result_23_m[1].arg2 == _fold_result_23_m[0].arg2*2',
                    '_fold_result_23_m[0].arg2 == y',
                    '0 >_fold_result_23_m[iter_23].arg1 +'
                    '_fold_result_23_m[iter_23].arg2',
                    'sizeof(fix.arr) >= 0',
                    'sizeof(fix.arr) < 3',
                    '1 == _fold_result_23_m[0].arg1',
                    'iter_23 >= 1',
                    'iter_23 < sizeof(fix.arr)',
                    '_fold_result_23_m[2].arg1 == '
                    '_fold_result_23_m[1].arg1 + 1',
                    '_fold_result_23_m[2].arg2 == _fold_result_23_m[1].arg2*2',
                },
            ],
            id='assert_inside_fold',
        ),
        pytest.param(
            'FUNC(foo,ARGS((arg1,int),(arg2,y),(elem,someCppType)),B(CR(arg1=B'
            '(FA(arg1,int),+,1),arg2=B(FA(arg2,double),*,2))));SV(tmp,B(FL(B(F'
            '(fix),.,F(arr)),elem,NT(arg1=1,arg2=y),FC(foo,NT(elem=VA(elem),'
            'arg1=VA(arg1),arg2=VA(arg2)),R(arg1=int,arg2=double))),.,F(arg2))'
            ');R(PROOF_NEVER(B(VA(tmp),>,42),1))',
            [
                {
                    '_fold_result_18_m[0].arg2 == y',
                    '_fold_result_18_m[1].arg1 == '
                    '_fold_result_18_m[0].arg1 + 1',
                    '_fold_result_18_m.* != _fold_result_18',
                    '42 < _fold_result_18_m[sizeof(fix.arr)].arg2',
                    '_fold_result_18_m[2].arg2 == _fold_result_18_m[1].arg2*2',
                    '_fold_result_18_m[1].arg2 == _fold_result_18_m[0].arg2*2',
                    '1 == _fold_result_18_m[0].arg1',
                    '_fold_result_18_m[2].arg1 == '
                    '_fold_result_18_m[1].arg1 + 1',
                    'sizeof(fix.arr) >= 0',
                    'sizeof(fix.arr) < 3',
                },
            ],
            id='assert_with_fold_result',
        ),
        pytest.param(
            'FUNC(bar,ARGS((acc,int),(elem,double)),B(CR(acc=B(FA(acc,double),'
            '+,FA(elem,double)))));FUNC(foo,ARGS((arg1,int),(arg2,y),'
            '(elem,someCppType)),B(CR(arg1=B(FL(B(FA(elem,double),.,'
            'F(nested_array)),elem,NT(acc=0),FC(bar,NT(elem=VA(elem),'
            'acc=VA(acc)),R(acc=double))),.,F(acc)),arg2=B(FA(arg2,double),*,'
            '2))));SV(tmp,B(FL(B(F(fix),.,F(arr)),elem,NT(arg1=1,arg2=y),'
            'FC(foo,NT(elem=VA(elem),arg1=VA(arg1),arg2=VA(arg2)),R(arg1=int,'
            'arg2=double))),.,F(arg2)));R(PROOF_NEVER(B(VA(tmp),>,42),1))',
            [
                {
                    '0 == _fold_result_18_m[1].acc[0]',
                    '0 == _fold_result_18_m[2].acc[0]',
                    '1 == _fold_result_40_m[0].arg1',
                    '42 < _fold_result_40_m[sizeof(fix.arr)].arg2',
                    '_fold_result_18_m[1].acc[1] =='
                    '_fold_result_18_m[1].acc[0] + fix.arr[1].nested_array[1]',
                    '_fold_result_18_m[1].acc[2] =='
                    '_fold_result_18_m[1].acc[1] + fix.arr[1].nested_array[2]',
                    '_fold_result_18_m[2].acc[1] =='
                    '_fold_result_18_m[2].acc[0] + fix.arr[2].nested_array[1]',
                    '_fold_result_18_m[2].acc[2] =='
                    '_fold_result_18_m[2].acc[1] + fix.arr[2].nested_array[2]',
                    '_fold_result_40_m[0].arg2 == y',
                    '_fold_result_40_m[1].arg1 =='
                    '_fold_result_18_m[1]'
                    '.acc[sizeof(fix.arr[1].nested_array)]',
                    '_fold_result_40_m[1].arg2 == '
                    '_fold_result_40_m[0].arg2*2',
                    '_fold_result_40_m[2].arg1 =='
                    '_fold_result_18_m[2]'
                    '.acc[sizeof(fix.arr[2].nested_array)]',
                    '_fold_result_40_m[2].arg2 == _fold_result_40_m[1].arg2*2',
                    'sizeof(fix.arr) >= 0',
                    'sizeof(fix.arr[1].nested_array) >= 0',
                    'sizeof(fix.arr[1].nested_array) < 3',
                    'sizeof(fix.arr[2].nested_array) >= 0',
                    'sizeof(fix.arr[2].nested_array) < 3',
                    'sizeof(fix.arr) < 3',
                    '_fold_result_40 != _fold_result_40_m.*',
                },
            ],
            id='nested_fold',
        ),
        pytest.param(
            'FG(test_guard,R(42));R(PROOF_NEVER(B(B(y,+,x),<,0),0))',
            [{'0 > y + x', 'Not(test_guard)'}],
            id='feature_guard',
        ),
        pytest.param(
            'SV(tmp0,MAP(B("x",+,"y")=42));'
            'R(PROOF_NEVER(B(B(VA(tmp0),.,B("x",+,"z")),>,100),0))',
            [
                {
                    '42 == optional<Real>::deref(value(42))',
                    'ForAll(_tmp0_i, _tmp0[_tmp0_i] == nil)',
                    '100 <optional<Real>::deref(Store(_tmp0, '
                    'Concat("x", "y"), value(42))[Concat("x", "z")])',
                },
            ],
            id='dynamic_map',
        ),
        pytest.param(
            'FUNC(test,ARGS(),B(IF(U(?,B(fix,.,F(b_opt))),CR(v=0.000000));'
            'CR()));SV(r,FC(test,NT(),R(v=std::optional<double>)));'
            'IF(U(?,B(VA(r),.,F(v))),CR(boarding=B(1.000000,/,'
            'PROOF_NEVER(B(U(*,B(VA(r),.,F(v))),==,0),U(*,B(VA(r),.,'
            'F(v)))))));CR()',
            [
                {
                    '0 == 0',
                    'fix.b_opt_opt != fix',
                    'is_initialized(_opt_tmp0) == True',
                    'is_initialized(_opt_tmp0) =='
                    '(is_initialized(fix.b_opt_opt) == True)',
                },
            ],
            id='empty_complex_return',
        ),
        pytest.param(
            'ASSERT(B(2,>,3));CR()', [{'Not(2 > 3)'}], id='assertion',
        ),
        pytest.param(
            'ASSERT(B(2,>,3),"message");CR()',
            [{'Not(2 > 3)'}],
            id='assertion_with_message',
        ),
        pytest.param(
            'ASSUME(B(42,>,11));ASSERT(B(2,>,3));CR()',
            [{'Not(2 > 3)', '42 > 11'}],
            id='assumption',
        ),
        pytest.param(
            'IF(B(B(fix,.,F(b)),>,4.000000),IF(B(B(fix,.,'
            'F(b)),<,10.000000),ASSUME(B(B(fix,.,'
            'F(b)),>,109.000000));SV(x,1.000000));'
            'ASSERT(B(B(fix,.,F(b)),>=,100.000000)));CR()',
            [{'Not(100 <= fix.b)', '4 < fix.b'}],
            id='assertion_with_assumptions_in_another_scope',
        ),
        pytest.param(
            'IF(B(B(fix,.,F(b)),>,4.000000),ASSUME(B(B(fix,.,F(b)),>,'
            '109.000000));ASSERT(B(B(fix,.,F(b)),>=,100.000000)));CR()',
            [{'4 < fix.b', '109 < fix.b', 'Not(100 <= fix.b)'}],
            id='assertion_with_assumptions_in_same_scope',
        ),
        pytest.param(
            'SV(x,NT(a=2.000000));SV(y,NT(b=3.000000));SV(z,CONCAT(VA(x),'
            'VA(y)));ASSERT(B(B(VA(z),.,F(b)),>=,3.000000));CR()',
            [{'Not(3 >= 3)'}],
            id='concat_operation',
        ),
    ],
)
def test_build_z3_model(ast, expected_sexprs):
    tree = dparser.to_dag(ast)
    response = Variables.deserialize(
        {
            'fix': {
                'arr': {
                    'type': 'array',
                    'value': {
                        'type': 'object',
                        'value': {
                            'one': {'type': 'double'},
                            'nested_array': {
                                'type': 'array',
                                'value': {'type': 'double'},
                            },
                        },
                    },
                },
                'b': {'type': 'double'},
                'b_opt': {'type': 'optional', 'value': {'type': 'double'}},
                'map_field': {'type': 'map', 'value': {'type': 'double'}},
            },
            'ride': {},
            'trip': {},
        },
    )
    bv_schema = backend_variables_schema.BackendVariablesSchema(response)
    ctx = AstProcessingContext(
        bv_schema,
        {
            'x': NamedExpressionValue('x', z3.Const('x', z3.RealSort())),
            'y': NamedExpressionValue('y', z3.Const('y', z3.RealSort())),
        },
    )
    systems = assertion_builder.build_assertions(tree, ctx)
    result_reprs = [
        {
            value
            for value in s.as_system_repr()
            if not value.startswith('Distinct')
        }
        for s in systems
    ]
    assert list(sorted(result_reprs)) == list(sorted(expected_sexprs))


@pytest.mark.parametrize(
    'ast, expected_error',
    [
        pytest.param('R(PROOF_NEVER(B(x,<,0),1))', True, id='simple_case'),
        pytest.param(
            'R(PROOF_NEVER(B(x,<,0),1,"test message"))',
            True,
            id='simple_case_with_comment',
        ),
        pytest.param(
            'R(T(B(x,>,1),PROOF_NEVER(B(x,<,0),1),1))',
            False,
            id='checked_with_ternary',
        ),
        pytest.param(
            'R(T(B(x,>,-0.0001),PROOF_NEVER(B(x,==,0),1),1))',
            True,
            id='checked_with_ternary_error',
        ),
        pytest.param(
            'IF(B(x,<,0),R(2));R(PROOF_NEVER(B(x,<,0),1))',
            False,
            id='checked_with_early_return',
        ),
        pytest.param(
            'IF(B(x,<,-1),R(2));R(PROOF_NEVER(B(x,<,0),1))',
            True,
            id='checked_with_early_return_not_all_cases',
        ),
        pytest.param(
            'FUNC(foo,ARGS((x,double)),B(CR(res=PROOF_NEVER(B(FA(x,double),'
            '<,0),1))));R(B(FC(foo,NT(a=x),R(res=double)),.,TF(res)))',
            True,
            id='error_inside_function',
        ),
        pytest.param(
            'FUNC(foo,ARGS((x,double)),B(IF(B(FA(x,double),<,1),CR(res=1));'
            'CR(res=PROOF_NEVER(B(FA(x,double),<,0),1))));'
            'R(B(FC(foo,NT(a=x),R(res=double)),.,TF(res)))',
            False,
            id='error_inside_function_early_return',
        ),
        pytest.param(
            'FUNC(bar,ARGS((x,double)),B(IF(B(FA(x,double),<,1),CR(res=1));'
            'CR(res=B(FC(foo,NT(a=FA(x,double)),R(res=double)),.,TF(res)))));'
            'FUNC(foo,ARGS((x,double)),B(CR(res=PROOF_NEVER(B(FA(x,double),'
            '<,0),1))));R(B(FC(bar,NT(a=x),R(res=double)),.,TF(res)))',
            False,
            id='early_return_in_upper_function',
        ),
    ],
)
def test_model_error_checker(ast, expected_error):
    tree = dparser.to_dag(ast)
    response = Variables.deserialize(
        {'fix': {'b': {'type': 'double'}}, 'ride': {}, 'trip': {}},
    )
    bv_schema = backend_variables_schema.BackendVariablesSchema(response)
    ctx = AstProcessingContext(
        bv_schema,
        {
            'x': NamedExpressionValue('x', z3.Real('x')),
            'y': NamedExpressionValue('y', z3.Real('y')),
        },
    )
    systems = assertion_builder.build_assertions(tree, ctx)
    has_error = any((system.evaluate() is not None for system in systems))
    assert has_error == expected_error


@pytest.mark.parametrize(
    'expr,expected_tree',
    [
        ('1', '(FLOAT::1)'),
        (
            '2+2*2',
            '(OPERATION:+:[(FLOAT::2),(OPERATION:*:[(FLOAT::2),(FLOAT::2)])])',
        ),
        (
            '2*2+2',
            '(OPERATION:+:[(OPERATION:*:[(FLOAT::2),(FLOAT::2)]),(FLOAT::2)])',
        ),
        (
            '2+2*2 >= 42',
            '(OPERATION:>=:[(OPERATION:+:[(FLOAT::2),'
            '(OPERATION:*:[(FLOAT::2),(FLOAT::2)])]),(FLOAT::42)])',
        ),
        (
            'a.b.c && x == false',
            '(OPERATION:&&:[(OPERATION:__dot__:[(OPERATION:__dot__:['
            '(NAME::a),(NAME::b)]),(NAME::c)]),(OPERATION:==:'
            '[(NAME::x),(NAME::false)])])',
        ),
        ('x==-x', '(OPERATION:==:[(NAME::x),(OPERATION:minus:[(NAME::x)])])'),
        (
            '*ride.price==42',
            '(OPERATION:==:[(DEREFERENCE::(OPERATION:__dot__:'
            '[(NAME::ride),(NAME::price)])),(FLOAT::42)])',
        ),
        (
            'a.b.c["test"] == d.e[42]',
            '(OPERATION:==:[(OPERATION:__dot__:[(OPERATION:__dot__:'
            '[(OPERATION:__dot__:[(NAME::a),(NAME::b)]),(NAME::c)]),'
            '(STRINGLITERAL::"test")]),(OPERATION:__dot__:[(OPERATION:__dot__:'
            '[(NAME::d),(NAME::e)]),(FLOAT::42)])])',
        ),
        (
            '((2 + 2 == 4)?x:7) == 3',
            '(OPERATION:==:[(TERNARYEXPR::[(OPERATION:==:[(OPERATION:+:'
            '[(FLOAT::2),(FLOAT::2)]),(FLOAT::4)]),(NAME::x),(FLOAT::7)]),'
            '(FLOAT::3)])',
        ),
        (
            '((x.y as v)?v.x:-1) > 0',
            '(OPERATION:>:[(TERNARYEXPR::[(OPERATION:?:[(OPERATION:__dot__:['
            '(NAME::x),(NAME::y)])]),(OPERATION:__dot__:[(DEREFERENCE::('
            'OPERATION:__dot__:[(NAME::x),(NAME::y)])),(NAME::x)]),('
            'OPERATION:minus:[(FLOAT::1)])]),(FLOAT::0)])',
        ),
        (
            'forAll(x: real, y: real => x + y < 100)',
            '(FOR_ALL:[(\'y\', \'real\'), (\'x\', \'real\')]:[(OPERATION:<:'
            '[(OPERATION:+:[(VALUE_ACCESS::(NAME::x)),(VALUE_ACCESS::'
            '(NAME::y))]),(FLOAT::100)])])',
        ),
        (
            'forAll(x: real, y: real implies (x >0 && y > 0) => x + y < 100)',
            '(FOR_ALL:[(\'y\', \'real\'), (\'x\', \'real\')]:[(OPERATION:&&'
            ':[(OPERATION:>:[(VALUE_ACCESS::(NAME::x)),(FLOAT::0)]),'
            '(OPERATION:>:[(VALUE_ACCESS::(NAME::y)),(FLOAT::0)])]),'
            '(OPERATION:<:[(OPERATION:+:[(VALUE_ACCESS::(NAME::x)),'
            '(VALUE_ACCESS::(NAME::y))]),(FLOAT::100)])])',
        ),
    ],
)
def test_constraint_parser(expr, expected_tree):
    result = cparser.parse_constraint(expr)
    assert repr(result) == expected_tree


def pprint_all(expr: z3_expression.ExpressionValue) -> typing.List[str]:
    return list(
        sorted(
            __normalize_str(pretty_printer.pprint(decl).replace('\n', ''))
            for decl in expr.get_z3_value_with_decls()
        ),
    )


def pprint_expr(expr: z3.ExprRef) -> str:
    return __normalize_str(pretty_printer.pprint(expr).replace('\n', ' '))


def test_merge_optionals():
    bv_schema = backend_variables_schema.BackendVariablesSchema(
        Variables.deserialize({'fix': {}, 'ride': {}, 'trip': {}}),
    )
    ctx = AstProcessingContext(bv_schema)
    _opt_1 = z3_expression.OptionalExpressionValue(
        z3.Bool('expr_cond'),
        z3_expression.AnonimousExpressionValue(z3.IntVal(1)),
        1,
        ctx,
    )
    _opt_2 = z3_expression.OptionalExpressionValue(
        z3.Bool('expr_cond2'),
        z3_expression.AnonimousExpressionValue(z3.IntVal(2)),
        2,
        ctx,
    )
    _5 = z3_expression.AnonimousExpressionValue(z3.IntVal(5))
    _3 = z3_expression.AnonimousExpressionValue(z3.IntVal(3))

    assert pprint_all(model_builder.do_concat(_5, _3, ctx)) == ['3']

    assert pprint_all(model_builder.do_concat(_opt_1, _5, ctx)) == ['5']

    concated = model_builder.do_concat(_5, _opt_1, ctx)
    assert pprint_all(concated) == [
        'If(is_initialized(_opt_1) == True, _opt_1, _opt_tmp0)',
        'is_initialized(_opt_1) == expr_cond',
        'is_initialized(_opt_tmp0) == True',
    ]
    assert (
        pprint_expr(z3_expression.is_initialized(concated.get_z3_value()))
        == 'is_initialized(If(is_initialized(_opt_1)'
        ' == True, _opt_1, _opt_tmp0)) == True'
    )
    assert pprint_all(concated.dereference()) == [
        'If(is_initialized(_opt_1) == True, 1, 5)',
        'is_initialized(_opt_1) == expr_cond',
        'is_initialized(_opt_tmp0) == True',
    ]

    concated_opts = model_builder.do_concat(_opt_1, _opt_2, ctx)
    assert pprint_all(concated_opts) == [
        'If(is_initialized(_opt_2) == True, _opt_2, _opt_1)',
        'is_initialized(_opt_1) == expr_cond',
        'is_initialized(_opt_2) == expr_cond2',
    ]
    assert (
        pprint_expr(z3_expression.is_initialized(concated_opts.get_z3_value()))
        == 'is_initialized(If(is_initialized(_opt_2)'
        ' == True, _opt_2, _opt_1)) == True'
    )
    assert pprint_all(concated_opts.dereference()) == [
        'If(is_initialized(_opt_2) == True, 2, 1)',
        'is_initialized(_opt_1) == expr_cond',
        'is_initialized(_opt_2) == expr_cond2',
    ]


def test_merge_named_tuples():
    bv_schema = backend_variables_schema.BackendVariablesSchema(
        Variables.deserialize({'fix': {}, 'ride': {}, 'trip': {}}),
    )
    ctx = AstProcessingContext(bv_schema)
    _opt_1 = z3_expression.OptionalExpressionValue(
        z3.Bool('expr_cond'),
        z3_expression.AnonimousExpressionValue(z3.IntVal(1)),
        1,
        ctx,
    )
    x = z3_expression.NamedTupleExpressionValue(
        'x',
        ctx.current_scope().create_any_field_const('x'),
        {
            'x_field': z3_expression.AnonimousExpressionValue(z3.IntVal(1)),
            'opt_field': _opt_1,
            'subtuple_field': z3_expression.NamedTupleExpressionValue(
                'subtuple_field',
                ctx.current_scope().create_any_field_const('subtuple_field'),
                {
                    'x_st_field': z3_expression.AnonimousExpressionValue(
                        z3.IntVal(42),
                    ),
                    'common_field': z3_expression.AnonimousExpressionValue(
                        z3.IntVal(1),
                    ),
                },
            ),
        },
    )
    y = z3_expression.NamedTupleExpressionValue(
        'y',
        ctx.current_scope().create_any_field_const('y'),
        {
            'y_field': z3_expression.AnonimousExpressionValue(z3.IntVal(5)),
            'opt_field': z3_expression.AnonimousExpressionValue(z3.IntVal(77)),
            'subtuple_field': z3_expression.NamedTupleExpressionValue(
                'subtuple_field',
                ctx.current_scope().create_any_field_const('subtuple_field'),
                {
                    'y_st_field': z3_expression.AnonimousExpressionValue(
                        z3.IntVal(111),
                    ),
                    'common_field': z3_expression.AnonimousExpressionValue(
                        z3.IntVal(4),
                    ),
                },
            ),
        },
    )
    concated = model_builder.do_concat(x, y, ctx)
    assert pprint_all(concated) == ['tmp1']
    assert set(concated.keys()) == {
        'x_field',
        'y_field',
        'opt_field',
        'subtuple_field',
    }
    assert pprint_all(concated.get_field('opt_field')) == ['77']
    assert set(concated.get_field('subtuple_field').keys()) == {
        'x_st_field',
        'y_st_field',
        'common_field',
    }
    assert pprint_all(
        concated.get_field('subtuple_field').get_field('common_field'),
    ) == ['4']


@pytest.mark.parametrize(
    'expr, expected_model',
    [
        ('fix.category == "econom"', 'fix.category == "econom"'),
        (
            'forAll(requirement_name: string => '
            '(fix.editable_requirements as er)?'
            '((er[requirement_name].max_value as mv)?mv:0):0 < 1000)',
            'ForAll(requirement_name, '
            '1000 > If(is_initialized(fix.editable_requirements_opt) == True, '
            'If(is_initialized(fix.editable_requirements[requirement_name]'
            '.max_value_opt) == True, deref_Real(fix.editable_requirements'
            '[requirement_name].max_value_opt), 0), 0))',
        ),
        (
            'forAll(i: real implies (i >= 0 && i < 10) => '
            'fix.user_tags[i] == "someTag")',
            'ForAll(i, Implies(And(0 <= i, 10 > i), '
            'fix.user_tags[i] == "someTag"))',
        ),
    ],
)
def test_constraint_builder(expr, expected_model, load_json):
    parse_ctx = ParserContext()
    constraint = cparser.parse_constraint(expr, parse_ctx)
    bv_schema_json = load_json('variable_types.json')
    response = Variables.deserialize(bv_schema_json)
    bv_schema = backend_variables_schema.BackendVariablesSchema(response)
    ctx = AstProcessingContext(bv_schema, parser_context=parse_ctx)
    constraint_expr = model_builder.build_z3_model(constraint, ctx)
    str_repr = pretty_printer.pprint(constraint_expr.get_z3_value())
    str_repr = __normalize_str(str_repr)
    assert str_repr == expected_model


@pytest.mark.parametrize(
    'ast_name,expected_auto_checks',
    [
        ('prod_surge', 5),
        ('prod_discount', 26),
        ('prod_yaplus_cashback_usermeta_driver', 9),
        ('return_optional_test', 7),
        ('prod_yaplus_cashback_user', 15),
        ('marketing_cashback_business', 8),
        ('surge_fixprice_user', 36),
        ('implicit_discount', 27),
        ('requirements_with_generate', 0),
        ('function_with_different_return_values', 25),
        ('marketing_cashback_with_fold', 0),
        ('simple_assertion', 3),
        ('assume_with_assertions_diff_scopes', 1),
        ('new_discount_rule', 24),
        ('marketing_cashback', 3),
        ('surge_taximeter_user', 29),
    ],
)
def test_build_complex_model(ast_name, expected_auto_checks, load, load_json):
    parse_ctx = ParserContext()
    tree = dparser.to_dag(load(ast_name), parse_ctx)
    bv_schema_json = load_json('variable_types.json')
    response = Variables.deserialize(bv_schema_json)
    bv_schema = backend_variables_schema.BackendVariablesSchema(response)
    ctx = scan_context.AstProcessingContext(
        bv_schema, parser_context=parse_ctx,
    )
    scope = ctx.global_scope()
    auto_checker.add_auto_checks(tree, ctx)
    scope.add_constraint(
        z3.Real('*ride.price')
        == (
            z3.Real('ride.price.boarding')
            + z3.Real('ride.price.distance')
            + z3.Real('ride.price.time')
            + z3.Real('ride.price.requirements')
            + z3.Real('ride.price.waiting')
            + z3.Real('ride.price.transit_waiting')
            + z3.Real('ride.price.destination_waiting')
            + z3.Real('ride.price.distance')
        ),
    )
    scope.add_constraint(z3.Real('ride.price.boarding') >= 0)
    scope.add_constraint(z3.Real('ride.price.distance') >= 0)
    scope.add_constraint(z3.Real('ride.price.time') >= 0)
    scope.add_constraint(z3.Real('ride.price.requirements') >= 0)
    scope.add_constraint(z3.Real('ride.price.waiting') >= 0)
    scope.add_constraint(z3.Real('ride.price.transit_waiting') >= 0)
    scope.add_constraint(z3.Real('ride.price.destination_waiting') >= 0)
    scope.add_constraint(z3.Real('ride.price.distance') >= 0)
    scope.add_constraint(z3.Real('fix.surge_params.surcharge_beta') > 0)

    assertions = assertion_builder.build_assertions(tree, ctx)
    assert len(assertions) == expected_auto_checks
    result = []
    for assertion in assertions:
        result.append(assertion.evaluate())


@pytest.mark.parametrize(
    'constraints,rule_file_name',
    [
        (
            [
                'forAll(category: string => "main" in '
                '(*(fix.previously_calculated_categories))[category]'
                '.user.final_prices)',
                'forAll(category: string => "main" in (*(fix.previously_'
                'calculated_categories))[category].driver.final_prices)',
            ],
            'driver-funded-discount_for_user',
        ),
    ],
)
def test_fix_checks_with_external_constraint(
        constraints, rule_file_name, load, load_json,
):
    parse_ctx = ParserContext()
    tree = dparser.to_dag(load(rule_file_name), parse_ctx)
    bv_schema_json = load_json('variable_types.json')
    response = Variables.deserialize(bv_schema_json)
    bv_schema = backend_variables_schema.BackendVariablesSchema(response)
    ctx = scan_context.AstProcessingContext(
        bv_schema, parser_context=parse_ctx,
    )
    scope = ctx.global_scope()
    auto_checker.add_auto_checks(tree, ctx)

    assertions = assertion_builder.build_assertions(tree, ctx)
    has_error = any(
        assertion.evaluate() is not None for assertion in assertions
    )
    assert has_error

    for constr in constraints:
        constr_ast = cparser.parse_constraint(constr, parse_ctx)
        constr_expr = model_builder.build_z3_model(constr_ast, ctx)
        scope.add_constraint(constr_expr.get_z3_value())

    assertions = assertion_builder.build_assertions(tree, ctx)
    has_error = any(
        assertion.evaluate() is not None for assertion in assertions
    )
    assert not has_error
