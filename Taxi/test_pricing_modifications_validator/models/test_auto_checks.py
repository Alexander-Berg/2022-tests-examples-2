# pylint: disable=import-only-modules
import pytest

from generated.models.pricing_admin import Variables

from pricing_modifications_validator.models.numeric import (
    backend_variables_schema,
)
import pricing_modifications_validator.models.symbolic.dagparser as dparser
from pricing_modifications_validator.models.symbolic.parser_context import (
    ParserContext,
)
from pricing_modifications_validator.models.z3 import scan_context
from pricing_modifications_validator.models.z3.auto_checker import (
    add_auto_checks,
)


@pytest.mark.parametrize(
    'ast,expected_repr',
    [
        pytest.param(
            'R(B(x,/,y))',
            '(PROGRAM::[(BLOCKS::[(SIMPLERET::[(OPERATION:/:'
            '[(FULLYQUALIFIEDNAME::x),(ASSERTION:(OPERATION:==:'
            '[(FULLYQUALIFIEDNAME::y),(FLOAT::0)]):(FULLYQUALIFIEDNAME::y):'
            'ProofType.PROOF_NEVER:'
            '"Detected division by zero in variable y")])])])])',
            id='check_zero_division',
        ),
        pytest.param(
            'R(B(B(B(B(F(fix),.,F(exps)),.,"foo"),.,"bar"),.,F(val)))',
            '(PROGRAM::[(BLOCKS::[(SIMPLERET::[(OPERATION:__dot__:'
            '[(ASSERTION:(OPERATION:!:[(OPERATION:in:[(STRINGLITERAL::"bar"),'
            '(ASSERTION:(OPERATION:!:[(OPERATION:in:[(STRINGLITERAL::"foo"),'
            '(OPERATION:__dot__:[(NAME::fix),(NAME::exps)])])]):'
            '(OPERATION:__dot__:[(OPERATION:__dot__:'
            '[(NAME::fix),(NAME::exps)]),(STRINGLITERAL::"foo")]):'
            'ProofType.PROOF_NEVER:"Detected access to unchecked map field '
            'fix.exps with parameter "foo"")])]):(OPERATION:__dot__:['
            '(ASSERTION:(OPERATION:!:[(OPERATION:in:[(STRINGLITERAL::"foo"),'
            '(OPERATION:__dot__:[(NAME::fix),(NAME::exps)])])]):'
            '(OPERATION:__dot__:[(OPERATION:__dot__:['
            '(NAME::fix),(NAME::exps)]),(STRINGLITERAL::"foo")]):'
            'ProofType.PROOF_NEVER:"Detected access to unchecked map field '
            'fix.exps with parameter "foo""),(STRINGLITERAL::"bar")]):'
            'ProofType.PROOF_NEVER:"Detected access to unchecked map field '
            'fix.exps."foo" with parameter "bar""),(NAME::val)])])])])',
            id='check_map_unchecked_access',
        ),
        pytest.param(
            'R(SL(0,0,4,4,B(x,/,y)))',
            '(PROGRAM::[(BLOCKS::[(SIMPLERET::[(OPERATION:/:['
            '(FULLYQUALIFIEDNAME::x)[0:0-4:4],(ASSERTION:(OPERATION:==:'
            '[(FULLYQUALIFIEDNAME::y)[0:0-4:4],(FLOAT::0)]):'
            '(FULLYQUALIFIEDNAME::y)[0:0-4:4]:ProofType.PROOF_NEVER:'
            '"Detected division by zero in variable y at lines 0-4")])'
            '[0:0-4:4]])])])',
            id='with_source_code_location',
        ),
    ],
)
def test_add_auto_checks(ast, expected_repr, load_json):
    bv_schema_json = load_json('variable_types.json')
    response = Variables.deserialize(bv_schema_json)
    bv_schema = backend_variables_schema.BackendVariablesSchema(response)
    parser_context = ParserContext()
    ctx = scan_context.AstProcessingContext(
        bv_schema, parser_context=parser_context,
    )
    tree = dparser.to_dag(ast, parser_context)
    add_auto_checks(tree, ctx)
    assert repr(tree) == expected_repr
