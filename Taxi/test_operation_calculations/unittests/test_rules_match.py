import datetime
import json

import pandas
import pytest

from operation_calculations.geosubventions.calculators import rules_match


@pytest.fixture(name='input_data')
def input_data_fixture(open_file):
    with open_file('input_data.csv') as filehandler:
        return pandas.read_csv(filehandler)


@pytest.fixture(name='expected_data')
def expected_data_fixture(open_file):
    with open_file('expected_data.csv') as filehandler:
        return pandas.read_csv(filehandler)


@pytest.fixture(name='test_data')
def test_data_fixture(open_file):
    with open_file('test_data.json') as filehandler:
        return json.load(filehandler)


def test_match_orders_with_rules(input_data, expected_data, test_data):
    result_data = rules_match.match_orders_with_rules(
        input_data,
        draft_rules=test_data['raw_rules'],
        polygons=test_data['polygons'],
        date_from=datetime.datetime.fromisoformat(test_data['date_from']),
        date_to=datetime.datetime.fromisoformat(test_data['date_to']),
    )
    assert result_data.to_json() == expected_data.to_json()
