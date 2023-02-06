import pytest

from taxi_tests.utils import json_variables


@pytest.mark.parametrize(
    'obj, kwargs, final_obj',
    [
        (
            {'test': 'test'},
            {},
            {'test': 'test'},
        ),
        (
            {'test2': '$test_var2'},
            {'test_var2': 'test_var_value_2'},
            {'test2': 'test_var_value_2'},
        ),
        (
            {'test3': '$test_var3', 'test': 'test'},
            {'test_var3': 'test_var_value_3'},
            {'test3': 'test_var_value_3', 'test': 'test'},
        ),
        (
            {'test4': 'test_${test_var4}_test', 'test': 'test'},
            {'test_var4': 'test_var_value_4'},
            {'test4': 'test_test_var_value_4_test', 'test': 'test'},
        ),
        (
            {'test5': '${test_var5}_test', 'test5_2': 'test_${test_var5_2}'},
            {'test_var5': 'test_value_5', 'test_var5_2': 'test_value_5_2'},
            {'test5': 'test_value_5_test', 'test5_2': 'test_test_value_5_2'},
        ),
        (
            {'test6': '$test_var6', 'test6_2': 'test_${test_var6_2}'},
            {'test_var6': 'test_value_6', 'test_var6_2': 'test_value_6_2'},
            {'test6': 'test_value_6', 'test6_2': 'test_test_value_6_2'},
        ),
        (
            {'test7': 'test_${test_var7_1}sda${test_var7_2}'},
            {'test_var7_1': 'test_value_7_1', 'test_var7_2': 'test_value_7_2'},
            {'test7': 'test_test_value_7_1sdatest_value_7_2'},
        ),
        (
            {'test8': 'test8'},
            {'test8': 'test8_1'},
            {'test8': 'test8'},
        ),
        (
            {'test9': 'test$test9'},
            {'test9': 'test9'},
            {'test9': 'test$test9'},
        ),
    ],
)
def test_create_secdist(obj, kwargs, final_obj):
    test_object = json_variables.substitute_vars(obj, **kwargs)
    assert test_object == final_obj


@pytest.mark.parametrize(
    'obj, kwargs',
    [
        (
            {'test': '$test'},
            {},
        ),
        (
            {'test2': '${test2}'},
            {},
        ),
        (
            {'test3': '$test3test'},
            {'test3': 'test3'},
        ),
    ],
)
def test_create_secdist_raise_error(obj, kwargs):
    with pytest.raises(json_variables.GetOptionError):
        json_variables.substitute_vars(obj, **kwargs)
