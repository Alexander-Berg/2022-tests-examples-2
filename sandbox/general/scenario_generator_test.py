import sandbox.projects.AutocheckEmulation.scenario_generator as sg

import datetime as dt


def test_generate_scenario_by_last_revisions():

    expected_scenario = '0 5\n10 6\n20 7\n30 8\n40 9'
    assert sg.generate_scenario_by_last_revisions(9, 1, 5, 10) == expected_scenario

    expected_scenario = ''
    assert sg.generate_scenario_by_last_revisions(9, 1, 0, 10) == expected_scenario

    expected_scenario = '0 3\n0 4\n0 5\n0 6'
    assert sg.generate_scenario_by_last_revisions(6, 1, 4, 0) == expected_scenario

    expected_scenario = '0 9\n10 9\n20 9\n30 9\n40 9'
    assert sg.generate_scenario_by_last_revisions(9, 0, 5, 10) == expected_scenario

    expected_scenario = '0 7\n10 6\n20 5\n30 4\n40 3'
    assert sg.generate_scenario_by_last_revisions(3, -1, 5, 10) == expected_scenario


def test_generate_scenario_by_autocheck():
    now = dt.datetime.today()

    log = [
        {
            'revision': 1,
            'date': now,
        },
        {
            'revision': 3,
            'date': now + dt.timedelta(seconds=20),
        },
        {
            'revision': 4,
            'date': now + dt.timedelta(hours=1),
        },
    ]

    expected_scenario = '0 1 0 1 30 3 30 3 3600 1 3620 3 7200 4'
    assert sg.generate_scenario_by_autocheck(log) == expected_scenario

    expected_scenario = '0 1 0 1 30 3 30 3 3600 1 3610 3 5400 4'
    assert sg.generate_scenario_by_autocheck(log, scale_factor=0.5) == expected_scenario

    expected_scenario = '0 1 0 1 30 3 30 3 100 1 110 3 1900 4'
    assert sg.generate_scenario_by_autocheck(log, scale_factor=0.5, delay=100) == expected_scenario


def test_continue_scenario():
    scenario = '0 1 0 1 30 3 30 3 3600 1 3620 3 7200 4'
    expected_scenario = '3500 1 3520 3 7100 4'
    assert sg.continue_scenario(scenario, 100) == expected_scenario

    expected_scenario = '28 3 28 3 3598 1 3618 3 7198 4'
    assert sg.continue_scenario(scenario, 2) == expected_scenario
