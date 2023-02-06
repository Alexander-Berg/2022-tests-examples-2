import datetime
import json
import pathlib

import pandas
import pytest

from operation_calculations.geosubventions.calculators import classes
from operation_calculations.geosubventions.calculators import (
    guarantee_calculator,
)


TEST_PARAMS_PATH = (
    pathlib.Path(__file__).parent / 'static' / 'test_guarantee_calculator'
)


def load_intervals(rules):
    for rule in rules:
        rule['interval'] = (
            datetime.datetime(*rule['interval'][0]),
            datetime.datetime(*rule['interval'][1]),
        )


def load_common_test_params():
    test_params_file = TEST_PARAMS_PATH / 'common.json'
    with open(test_params_file) as handler:
        params = json.load(handler)

    for intervals in params['task']['rush_hours'].values():
        for interval in intervals:
            interval[0] = datetime.datetime(*interval[0])
            interval[1] = datetime.datetime(*interval[1])

    load_intervals(params['task']['intervals_geo'])
    load_intervals(params['task']['draft_rules'])

    return params


def load_test_cases():
    all_test_cases = []
    for test_params_file in TEST_PARAMS_PATH.glob('test_case_*.json'):
        with open(test_params_file) as handler:
            test_case_params = json.load(handler)
            test_case_params['id'] = test_params_file.with_suffix('').name
            all_test_cases.append(test_case_params)
    return all_test_cases


@pytest.fixture(name='test_data')
def data_fixture(open_file):
    with open_file('test_data.csv') as handler:
        return pandas.read_csv(handler)


@pytest.fixture(
    name='test_params', params=load_test_cases(), ids=lambda x: x['id'],
)
def params_fixture(request, open_file):
    test_params = request.param
    if 'overrides' in test_params:
        task_overrides = test_params.pop('overrides')
        load_intervals(task_overrides['draft_rules'])
    else:
        task_overrides = {}
    params = load_common_test_params()
    params.update(test_params)
    params['task'].update(task_overrides)
    load_intervals(params['expected'])
    return params


def test_recalculate_rules(test_params, test_data):
    task = classes.CalculatorTask(
        **test_params['task'], gmv_summary=classes.GmvSummary(),
    )
    gcalc = guarantee_calculator.GuaranteeCalculator(**test_params['params'])
    gcalc.recalculate_rules(test_data, task)
    assert task.draft_rules == test_params['expected']
