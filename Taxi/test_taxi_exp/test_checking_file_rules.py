import typing

import pytest

from taxi_exp.lib.files import checkers
from taxi_exp.lib.files.checkers import checker
from taxi_exp.lib.files.checkers import string_checker


class Case(typing.NamedTuple):
    rule: typing.Optional[str]
    values: typing.Optional[typing.List[str]]
    is_bad_rule: bool
    is_bad_value: bool


@pytest.mark.parametrize(
    'rule,values,is_bad_rule,is_bad_value',
    [
        pytest.param(
            *Case(  # default rule
                rule=None,
                values=['aaaaa', 'bbbb', 'ccccc'],
                is_bad_rule=False,
                is_bad_value=False,
            ),
            id='default_rule_creation',
        ),
        pytest.param(
            *Case(
                rule=None,
                values=['a' * (string_checker.MAX_STRING_LENGTH + 1)],
                is_bad_rule=False,
                is_bad_value=True,
            ),
            id='check_max_length_by_default',
        ),
        pytest.param(
            *Case(
                rule=None,
                values=[chr(0)],
                is_bad_rule=False,
                is_bad_value=True,
            ),
            id='check_printable_symbols',
        ),
        pytest.param(
            *Case(  # length rule
                rule='len:10',
                values=['a'],
                is_bad_rule=False,
                is_bad_value=False,
            ),
            id='length_rule_creation',
        ),
        pytest.param(
            *Case(
                rule='len:10',
                values=['a' * 11],
                is_bad_rule=False,
                is_bad_value=True,
            ),
            id='check_max_length_by_args',
        ),
        pytest.param(
            *Case(
                rule='len', values=None, is_bad_rule=True, is_bad_value=False,
            ),
            id='fail_creation_len_rule_without_args',
        ),
        pytest.param(
            *Case(
                rule='len:10:0',
                values=None,
                is_bad_rule=True,
                is_bad_value=False,
            ),
            id='fail_creation_le_rule_with_bad_order_args',
        ),
        pytest.param(
            *Case(
                rule='len:a',
                values=None,
                is_bad_rule=True,
                is_bad_value=False,
            ),
            id='fail_creation_len_rule_with_bad_arg_type',
        ),
        pytest.param(
            *Case(  # length ranged rule
                rule='len:2:10',
                values=['aa'],
                is_bad_rule=False,
                is_bad_value=False,
            ),
            id='len_ranged_creation',
        ),
        pytest.param(
            *Case(
                rule='len:2:10',
                values=['a'],
                is_bad_rule=False,
                is_bad_value=True,
            ),
            id='fail_check_value_with_out_of_range_length',
        ),
        pytest.param(
            *Case(  # regexp rule
                rule='regexp:\\d+',
                values=['1234'],
                is_bad_rule=False,
                is_bad_value=False,
            ),
            id='regexp_rule_creation',
        ),
        pytest.param(
            *Case(
                rule='regexp:\\d+',
                values=['1234a'],
                is_bad_rule=False,
                is_bad_value=True,
            ),
            id='fail_check_non_matched_value',
        ),
        pytest.param(
            *Case(
                rule='regexp:a:b',
                values=None,
                is_bad_rule=True,
                is_bad_value=False,
            ),
            id='fail_regexp_creation_with_more_args',
        ),
        pytest.param(
            *Case(
                rule='integer',
                values=['1234', '-1234'],
                is_bad_rule=False,
                is_bad_value=False,
            ),
            id='pass_check_values_by_integer',
        ),
        pytest.param(
            *Case(
                rule='integer',
                values=['a'],
                is_bad_rule=False,
                is_bad_value=True,
            ),
            id='fail_check_value_by_integer_if_not_digits',
        ),
        pytest.param(
            *Case(
                rule='integer',
                values=['12345.678'],
                is_bad_rule=False,
                is_bad_value=True,
            ),
            id='fail_check_value_by_integer_if_float',
        ),
        pytest.param(
            *Case(
                rule='range_integer:12:23',
                values=['13'],
                is_bad_rule=False,
                is_bad_value=False,
            ),
            id='pass_check_value_by_range_integer',
        ),
    ],
)
def test_rules(rule, values, is_bad_rule, is_bad_value):
    if is_bad_rule:
        with pytest.raises(checker.BadRule):
            checkers.create_checker(rule)
    else:
        test = checkers.create_checker(rule)
        if is_bad_value:
            with pytest.raises(checker.BadValue):
                test(values)
        else:
            test(values)
