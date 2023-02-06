import pytest

from sandbox.projects.release_machine.components.config_core.jg.lib.conditions import ci_conditions
from sandbox.projects.release_machine.components.config_core.jg.cube import base as cube_base


@pytest.mark.parametrize(
    "init_value,expected_str",
    [
        (1, "(1)"),
        ("1", "(1)"),
        (cube_base.Cube("test", task="t1").output.field, "(tasks.test.field)"),
    ]
)
def test__single_value(init_value, expected_str):

    c = ci_conditions.CICondition(init_value)

    assert str(c) == expected_str
    assert ci_conditions.CICondition.IF in c.to_dict()
    assert c.to_dict()[ci_conditions.CICondition.IF] == "${{{}}}".format(expected_str.lstrip("(").rstrip(")"))


def test__join_with_operator():

    c1 = ci_conditions.CICondition(1)
    c2 = c1.join_with_operator(1, "==")

    assert isinstance(c2, ci_conditions.CICondition)
    assert str(c2) == "((1) == `1`)"
    assert c2.value == "(1) == `1`"

    with pytest.raises(TypeError):
        c1.join_with_operator(True, "==")

    with pytest.raises(TypeError):
        c1.join_with_operator({"a": 1}, "==")

    assert c1.join_with_operator(None, "==") == "((1) == null)"


def test__complex_values():
    c1_1 = ci_conditions.CICondition(cube_base.Cube("test_1", task="t1").output.field_1)
    c2_1 = ci_conditions.CICondition(cube_base.Cube("test_2", task="t2").output.field_2)
    c1_2 = c1_1 == "da"
    c2_2 = c2_1 == "net"
    c3 = c1_2 & c2_2

    assert isinstance(c1_1, ci_conditions.CICondition)
    assert isinstance(c2_1, ci_conditions.CICondition)
    assert isinstance(c1_2, ci_conditions.CICondition)
    assert isinstance(c2_2, ci_conditions.CICondition)
    assert isinstance(c3, ci_conditions.CICondition)

    s_c1_1 = "(tasks.test_1.field_1)"
    s_c1_2 = "({} == 'da')".format(s_c1_1)
    s_c2_1 = "(tasks.test_2.field_2)"
    s_c2_2 = "({} == 'net')".format(s_c2_1)

    assert str(c1_1) == s_c1_1
    assert str(c1_2) == s_c1_2
    assert str(c2_1) == s_c2_1
    assert str(c2_2) == s_c2_2

    expected_value = "({} && {})".format(s_c1_2, s_c2_2)
    assert str(c3) == expected_value, "\nExpected: {}\nGot:      {}\n".format(expected_value, str(c3))


def test__and():

    c1 = ci_conditions.CICondition("c1") == 1
    c2 = ci_conditions.CICondition("c2") == 2

    c = c1 & c2

    assert isinstance(c, ci_conditions.CICondition), "Two conditions joined with `&` should result in a new condition"

    assert c1.value in c.value, "and-join lhs error: `c1` cannot be found in `c1 & c2`"
    assert c2.value in c.value, "and-join rhs error: `c2` cannot be found in `c1 & c2`"

    assert c.value == "{} && {}".format(c1, c2), "unexpected join result"


def test__or():

    c1 = ci_conditions.CICondition("c1") == 1
    c2 = ci_conditions.CICondition("c2") == 2

    c = c1 | c2

    assert isinstance(c, ci_conditions.CICondition), "Two conditions joined with `|` should result in a new condition"

    assert c1.value in c.value, "or-join lhs error: `c1` cannot be found in `c1 | c2`"
    assert c2.value in c.value, "or-join rhs error: `c2` cannot be found in `c1 | c2`"

    assert c.value == "{} || {}".format(c1, c2), "unexpected join result"


def test__xor():

    c1 = ci_conditions.CICondition("c1") == 1
    c2 = ci_conditions.CICondition("c2") == 2

    c = c1 ^ c2

    assert isinstance(c, ci_conditions.CICondition), "Two conditions joined with `^` should result in a new condition"

    assert c1.value in c.value, "xor-join lhs error: `c1` cannot be found in `c1 ^ c2`"
    assert c2.value in c.value, "xor-join rhs error: `c2` cannot be found in `c1 ^ c2`"

    assert c.value == "({c1} && (!{c2})) || ((!{c1}) && {c2})".format(c1=c1, c2=c2), "unexpected join result"


@pytest.mark.parametrize(
    "condition,expected_value",
    [
        (ci_conditions.CICondition(1) == 1, "((1) == `1`)"),
        (ci_conditions.CICondition(1) != 2, "((1) != `2`)"),
        (ci_conditions.CICondition(1) < 2,  "((1) < `2`)"),
        (ci_conditions.CICondition(1) > 0,  "((1) > `0`)"),
        (ci_conditions.CICondition(1) >= 0, "((1) >= `0`)"),
        (ci_conditions.CICondition(1) <= 2, "((1) <= `2`)"),
        (ci_conditions.CICondition(1).negate(), "(!(1))"),
        (
            ci_conditions.CICondition(cube_base.Cube("test", task="t1").output.this_works_fine) == "da",
            "((tasks.test.this_works_fine) == 'da')"
        ),
        (
            (
                (ci_conditions.CICondition(cube_base.Cube("test_1", task="t1").output.field_1) == "da")
                &
                (ci_conditions.CICondition(cube_base.Cube("test_2", task="t2").output.field_2) == "net")
            ),
            "(((tasks.test_1.field_1) == 'da') && ((tasks.test_2.field_2) == 'net'))"
        ),
        (
            (
                (ci_conditions.CICondition(cube_base.Cube("test_1", task="t1").output.field_1) == "da")
                |
                (ci_conditions.CICondition(cube_base.Cube("test_2", task="t2").output.field_2) == "net")
            ),
            "(((tasks.test_1.field_1) == 'da') || ((tasks.test_2.field_2) == 'net'))"
        ),
    ]
)
def test__basic_operations(condition, expected_value):
    assert isinstance(condition, ci_conditions.CICondition)
    assert str(condition) == expected_value, "\nExpected: {}\nGot:      {}\n".format(expected_value, str(condition))
