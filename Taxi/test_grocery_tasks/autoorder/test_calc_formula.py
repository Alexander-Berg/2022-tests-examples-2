import pandas as pd
import pytest

from grocery_tasks.autoorder.calc import formula

INPUT_DF = pd.DataFrame({'foo': [1, 2, 3], 'bar': [5, 6, 7]})


@pytest.mark.parametrize(
    'dataframe, input_formula, expected_result, expected_error',
    [
        (INPUT_DF, '=1+1', [2, 2, 2], None),
        (INPUT_DF, '1+1', None, formula.FormulaParseError),
        (INPUT_DF, '=miss+1', None, formula.FormulaArgsError),
        (INPUT_DF, '=foo+bar-1', [5, 7, 9], None),
        (INPUT_DF, '=IF(AND(foo=1,bar=5))', [True, False, False], None),
    ],
)
def test_formula(dataframe, input_formula, expected_result, expected_error):
    if expected_error is not None:
        with pytest.raises(expected_error):
            formula.apply_formula(dataframe, input_formula)
    else:
        result = formula.apply_formula(dataframe, input_formula)
        assert result == expected_result
