import json

import library.python.resource as lpr
import pytest

from . import formula
from sandbox.projects.eda.updater_startrek_priority.models import (
    WeightCalculator
)
from sandbox.projects.eda.updater_startrek_priority.exceptions import (
    FormulaError
)

formula = formula.formula


@pytest.fixture()
def json_tasks():
    json_data = json.loads(lpr.find('/json_data.json'))
    return json_data


def test_formula(json_tasks):
    json_data = json_tasks
    calculator = WeightCalculator(formula)
    expected_results = [FormulaError, 40.0, 1.125, 18.0, 36.0]
    for task, expected_result in zip(json_data, expected_results):
        try:
            weight = calculator.compute_weight(task)
            assert weight == expected_result
        except Exception as err:
            assert err.__class__ is expected_result
