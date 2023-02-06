import datetime
import json

import pandas
import pytest

from operation_calculations.geosubventions.calculators import (
    simple_rush_hours_calculator as rh_lib,
)
from operation_calculations.geosubventions.calculators import utils


@pytest.fixture(name='test_data')
def data_fixture(open_file):
    with open_file('test_data.csv') as handler:
        return pandas.read_csv(handler)


@pytest.fixture(name='test_params')
def params_fixture(open_file):
    with open_file('test_data.json') as handler:
        params = json.load(handler)

    draft_rules = params['draft_rules']
    for i, rule in enumerate(draft_rules):
        draft_rules[i]['interval'] = utils.interval_dict_to_pair(
            rule['interval'],
        )

    rush_hours = params['rush_hours']
    for rh_group, intervals in rush_hours.items():
        rush_hours[rh_group] = [
            (datetime.datetime(*i[0]), datetime.datetime(*i[1]))
            for i in intervals
        ]

    return params


@pytest.mark.parametrize(
    'interval,span,expected',
    [
        (1, 3, [[0, 1]]),
        (2, 3, [[0, 2]]),
        (3, 3, [[0, 3]]),
        (4, 3, [[0, 4]]),
        (5, 3, [[0, 5]]),
        (6, 3, [[0, 3], [3, 6]]),
        (7, 3, [[0, 3], [3, 7]]),
        (8, 3, [[0, 3], [3, 8]]),
        (9, 3, [[0, 3], [3, 6], [6, 9]]),
        (10, 3, [[0, 3], [3, 6], [6, 10]]),
    ],
)
def test_split_interval(interval, span, expected):
    result = rh_lib.RushHoursDetector.split_interval(0, interval, span)
    assert result == expected


@pytest.mark.parametrize(
    'input_data_file,expected_data_file',
    [
        ['invalid_case_input.csv', 'invalid_case_expected.csv'],
        ['ok_1_case_input.csv', 'ok_1_case_expected.csv'],
        ['ok_2_case_input.csv', 'ok_2_case_expected.csv'],
        ['ok_3_case_input.csv', 'ok_3_case_expected.csv'],
    ],
)
def test_filter_invalid_case(input_data_file, expected_data_file, open_file):
    with open_file(input_data_file) as handler:
        input_data = pandas.read_csv(handler)
    with open_file(expected_data_file) as handler:
        expected_data = pandas.read_csv(handler)
    result = rh_lib.RushHoursDetector.filter_invalid_case(input_data)
    result.reset_index(drop=True, inplace=True)
    assert result.to_json() == expected_data.to_json()


def test_run(test_data, test_params):
    rhd = rh_lib.RushHoursDetector(surge_threshold=0, group_min_total_span=10)
    result = rhd.run(test_data)
    assert result == test_params['rush_hours']
