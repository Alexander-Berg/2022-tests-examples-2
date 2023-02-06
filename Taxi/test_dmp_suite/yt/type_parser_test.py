import pytest

from dmp_suite.yt import table as yt
from dmp_suite.yt.type_parser import Blank, YTTypeMatcher


@pytest.mark.parametrize(
    't1,pattern,collapse,expected',
    [
        (
            yt.Int(required=True),
            yt.Int,
            True,
            True,
        ),
        (
            yt.Int(required=True),
            yt.Int,
            False,
            True,
        ),
        (
            yt.Int(required=False),
            yt.Int,
            False,
            False,
        ),
        (
            yt.Double(required=True),
            yt.Int,
            True,
            False,
        ),
        (
            yt.Double(required=True),
            yt.Int,
            False,
            False,
        ),
        (
            yt.String(required=True),
            yt.String,
            False,
            True,
        ),
        (
            yt.String(),
            yt.Bool,
            False,
            False,
        ),
    ]
)
def test_simple_match(t1, pattern, collapse, expected):
    assert YTTypeMatcher.match(t1, pattern, collapse_optional=collapse) == expected



@pytest.mark.parametrize(
    't1,pattern,collapse,expected',
    [
        (
            yt.Int(required=False),
            yt.Optional[yt.Int],
            False,
            True,
        ),
        (
            yt.Int(required=True),
            yt.Optional[yt.Int],
            False,
            False,
        ),
        (
            yt.Optional(yt.Int),
            yt.Optional[yt.Optional[yt.Int]],
            False,
            False,
        ),
        (
            yt.Optional(yt.Int),
            yt.Optional[yt.Optional[yt.Int]],
            True,
            True,
        ),
        (
            yt.List(yt.Int, comment='empty'),
            yt.List[yt.Int],
            True,
            True,
        ),
        (
            yt.List(yt.Int),
            yt.Optional[yt.List[yt.Int]],
            True,
            False,
        ),
        (
            yt.List(yt.Int),
            yt.List[yt.Optional[yt.Int]],
            True,
            False,
        ),
        (
            yt.Struct({'a': yt.Int, 'b': yt.Int}),
            yt.Struct['b': yt.Int, 'a': yt.Int],
            False,
            True,
        ),
        (
            yt.Struct({'a': yt.String, 'b': yt.Int}),
            yt.Struct['b': yt.Int, 'a': yt.String],
            False,
            True,
        ),
        (
            yt.Struct({'a': yt.String}),
            yt.Struct['b': yt.Int, 'a': yt.String],
            False,
            False,
        ),
        (
            yt.Struct({'a': yt.String, 'b': yt.Int}),
            yt.Struct['a': yt.String],
            False,
            False,
        ),
        (
            yt.Struct({'a': yt.Optional[yt.Int], 'b': yt.Int}),
            yt.Struct['a': yt.Optional[yt.Int], 'b': yt.Int],
            False,
            True,
        ),
        (
            yt.Struct({'a': yt.Optional[yt.Int], 'b': yt.Int}),
            yt.Struct['a': yt.Optional[yt.Optional[yt.Int]], 'b': yt.Int],
            False,
            False,
        ),
        (
            yt.Struct({'a': yt.Optional[yt.Int], 'b': yt.Int}),
            yt.Struct['a': yt.Optional[yt.Optional[yt.Int]], 'b': yt.Int],
            True,
            True,
        ),
        (
            yt.Struct({'a': yt.Int, 'b': yt.Int}),
            yt.VariantNamed['a': yt.Int, 'b': yt.Int],
            False,
            False,
        ),
        (
            yt.Tuple((yt.Int, yt.String)),
            yt.Tuple[yt.Int, yt.String],
            True,
            True,
        ),
        (
            yt.Tuple((yt.Int, yt.String)),
            yt.Tuple[yt.String, yt.Int],
            True,
            False,
        ),
        (
            yt.Tuple((yt.String,)),
            yt.Tuple[yt.String, yt.Int],
            True,
            False,
        ),
        (
            yt.Tuple((yt.Int, yt.String)),
            yt.Tuple[yt.Int],
            True,
            False,
        ),
        (
            yt.VariantNamed({'a': yt.String}),
            yt.VariantNamed['b': yt.Int, 'a': yt.String],
            False,
            False,
        ),
        (
            yt.VariantNamed({'a': yt.String, 'b': yt.Int}),
            yt.VariantNamed['a': yt.String],
            False,
            False,
        ),
        (
            yt.VariantUnnamed((yt.Int, yt.Int)),
            yt.VariantNamed['a': yt.Int, 'b': yt.Int],
            False,
            False,
        ),
        (
            yt.VariantUnnamed((yt.Int, yt.String)),
            yt.VariantUnnamed[yt.Int, yt.String],
            True,
            True,
        ),
        (
            yt.VariantUnnamed((yt.Int, yt.String)),
            yt.VariantUnnamed[yt.String, yt.Int],
            True,
            False,
        ),
        (
            yt.VariantUnnamed((yt.String,)),
            yt.VariantUnnamed[yt.String, yt.Int],
            True,
            False,
        ),
        (
            yt.VariantUnnamed((yt.Int, yt.String)),
            yt.VariantUnnamed[yt.Int],
            True,
            False,
        ),
        (
            yt.Dict(yt.Int, yt.String),
            yt.Dict[yt.Int, yt.String],
            True,
            True,
        ),
        (
            yt.Dict(yt.Int, yt.String),
            yt.Dict[yt.Int, yt.Int],
            True,
            False,
        ),
        (
            yt.Dict(yt.Int, yt.String),
            yt.Dict[yt.String, yt.String],
            True,
            False,
        ),
        (
            yt.Tagged("One", yt.String),
            yt.Tagged["One", yt.String],
            True,
            True,
        ),
        (
            yt.Tagged("One", yt.String),
            yt.Tagged["Two", yt.String],
            True,
            False,
        ),
        (
            yt.Tagged("One", yt.String),
            yt.Tagged["One", yt.Int],
            True,
            False,
        ),
        (
            yt.Tagged("List", yt.String),
            yt.List[yt.String],
            True,
            False,
        ),
        (
            yt.Decimal(5, 3),
            yt.Decimal[6, 3],
            False,
            False,
        ),
        (
            yt.Decimal(5, 3),
            yt.Decimal[5, 2],
            False,
            False,
        ),
        (
            yt.Decimal(5, 3),
            yt.Decimal[5, 3],
            False,
            True,
        ),
    ]
)
def test_complex_match(t1, pattern, collapse, expected):
    assert YTTypeMatcher.match(t1, pattern, collapse_optional=collapse) == expected


@pytest.mark.parametrize(
    't1,pattern,expected',
    [
        (
            yt.Decimal(5, 3),
            yt.Decimal[Blank, 3],
            True,
        ),
        (
            yt.Optional(yt.Int),
            Blank,
            True,
        ),
        (
            yt.Optional(yt.Int),
            yt.Optional[Blank],
            True,
        ),
        (
            yt.Optional(yt.List[yt.Int]),
            yt.Optional[Blank],
            True,
        ),
        (
            yt.Optional(yt.List[yt.Int]),
            yt.Optional[yt.List[Blank]],
            True,
        ),
        (
            yt.List[yt.Int],
            Blank,
            True,
        ),
        (
            yt.List[yt.Int],
            yt.List[Blank],
            True,
        ),
        (
            yt.Tuple((yt.String, yt.String)),
            yt.Tuple[yt.List[yt.String], yt.String],
            False,
        ),
        (
            yt.Tuple((yt.List[yt.String], yt.String)),
            yt.Tuple[yt.List[Blank], yt.String],
            True,
        ),
        (
            yt.Tuple((yt.List[yt.String], yt.String)),
            yt.Tuple[yt.List[yt.Int], Blank],
            False,
        ),
        (
            yt.Tuple((yt.List[yt.String], yt.String)),
            yt.Tuple[Blank, yt.String],
            True,
        ),
        (
            yt.Tuple((yt.List[yt.String], yt.String)),
            Blank,
            True,
        ),
        (
            yt.Dict(yt.String, yt.String),
            yt.Dict[Blank, yt.Int],
            False,
        ),
        (
            yt.Dict(yt.String, yt.Int),
            yt.Dict[Blank, yt.Int],
            True,
        ),
        (
            yt.Struct({'a': yt.String, 'b': yt.Int}),
            yt.Struct['a': Blank, 'c': yt.Int],
            False,
        ),
        (
            yt.Struct({'a': yt.String, 'b': yt.Int}),
            yt.Struct['c': Blank, 'b': yt.Int],
            False,
        ),
        (
            yt.Struct({'a': yt.String, 'c': yt.Int}),
            yt.Struct['a': Blank, 'b': yt.Int],
            False,
        ),
        (
            yt.Struct({'a': yt.String, 'b': yt.Int}),
            yt.Struct['a': Blank, 'b': yt.Int],
            True,
        ),
        (
            yt.Struct({'a': yt.String, 'b': yt.Int}),
            yt.Struct['b': yt.Int, 'a': Blank],
            True,
        ),
        (
            yt.Struct({'a': yt.List[yt.Optional[yt.Int]], 'b': yt.Int}),
            yt.Struct['a': Blank, 'b': yt.Int],
            True,
        ),
        (
            yt.Struct({'a': yt.List[yt.Optional[yt.Int]], 'b': yt.Int}),
            yt.Struct['a': yt.List[Blank], 'b': yt.Int],
            True,
        ),
        (
            yt.Struct({'a': yt.String, 'b': yt.Int}),
            yt.VariantNamed['a': Blank, 'b': yt.Int],
            False,
        ),
        (
            yt.VariantNamed({'a': yt.String, 'b': yt.Int}),
            yt.VariantNamed['a': Blank, 'b': yt.Int],
            True,
        ),
        (
            yt.VariantNamed({'a': yt.String, 'b': yt.Int}),
            yt.VariantNamed['a': yt.String, 'b': Blank],
            True,
        ),
        (
            yt.VariantNamed({'a': yt.String, 'b': yt.Int}),
            yt.VariantNamed['b': Blank, 'a': yt.String],
            True,
        ),
        (
            yt.VariantNamed({'a': yt.String, 'b': yt.Int}),
            yt.VariantNamed['b': Blank, 'a': yt.Int],
            False,
        ),
        (
            yt.VariantUnnamed((yt.String, yt.String)),
            yt.VariantUnnamed[yt.List[yt.String], yt.String],
            False,
        ),
        (
            yt.VariantUnnamed((yt.List[yt.String], yt.String)),
            yt.VariantUnnamed[yt.List[Blank], yt.String],
            True,
        ),
        (
            yt.VariantUnnamed((yt.String,)),
            yt.VariantUnnamed[yt.String],
            True,
        ),
        (
            yt.VariantUnnamed((yt.String,)),
            yt.VariantUnnamed[yt.String, Blank],
            False,
        ),
        (
            yt.VariantUnnamed((yt.List[yt.String], yt.String)),
            yt.VariantUnnamed[yt.List[yt.Int], Blank],
            False,
        ),
        (
            yt.Dict(yt.Int, yt.String),
            yt.Dict[yt.Int, Blank],
            True,
        ),
        (
            yt.Dict(yt.Int, yt.String),
            yt.Dict[Blank, Blank],
            True,
        ),
        (
            yt.Dict(yt.Int, yt.String),
            yt.Dict[Blank, yt.Int],
            False,
        ),
        (
            yt.Tagged("One", yt.String),
            yt.Tagged["One", Blank],
            True,
        ),
    ]
)
@pytest.mark.parametrize(
    'collapse',
    [
        True,
        False,
    ]
)
def test_partial_type_match(t1, pattern, expected, collapse):
    assert YTTypeMatcher.match(t1, pattern, collapse_optional=collapse) == expected


@pytest.mark.parametrize(
    't1,pattern,collapse,expected',
    [
        (
            yt.Decimal(5, 3, comment='some battle field'),
            yt.Decimal[Blank, Blank],
            False,
            True,
        ),
        (
            yt.Optional(yt.Decimal[5, 3], comment='some battle field'),
            yt.Decimal[Blank, Blank],
            False,
            True,
        ),
        (
            yt.Optional(yt.Optional[yt.Decimal[5, 3]], comment='some battle field'),
            yt.Decimal[Blank, Blank],
            False,
            False,
        ),
        (
            yt.Optional(yt.Optional[yt.Decimal[5, 3]], comment='some battle field'),
            yt.Decimal[Blank, Blank],
            True,
            True,
        ),
    ]
)
def test_maybe_optional_of(t1, pattern, collapse, expected):

    assert YTTypeMatcher.maybe_optional_of(t1, pattern, collapse_optional=collapse) == expected
