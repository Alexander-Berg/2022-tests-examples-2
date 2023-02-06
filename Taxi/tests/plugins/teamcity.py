import pytest

from taxi_buildagent.clients import teamcity


@pytest.fixture(autouse=True)
def teamcity_report_problems(patch):
    func = patch('taxi_buildagent.utils.teamcity.report_build_problem')(
        teamcity.report_build_problem,
    )
    yield func
    assert not func.calls


@pytest.fixture(autouse=True)
def teamcity_report_test_problem(patch):
    func = patch('taxi_buildagent.utils.teamcity.report_test_problem')(
        teamcity.report_test_problem,
    )
    yield func
    assert not func.calls


@pytest.fixture
def teamcity_messages(patch):
    func = patch('taxi_buildagent.utils.teamcity._send_teamcity_message')(
        teamcity._send_teamcity_message,  # pylint: disable=protected-access
    )
    return func


@pytest.fixture
def teamcity_report_build_number(patch):
    func = patch('taxi_buildagent.utils.teamcity.report_build_number')(
        teamcity.report_build_number,
    )
    return func


@pytest.fixture
def teamcity_set_parameters(patch):
    func = patch('taxi_buildagent.utils.teamcity.set_parameter')(
        teamcity.set_parameter,
    )
    return func


@pytest.fixture
def teamcity_report_statistic(patch):
    func = patch('taxi_buildagent.utils.teamcity.report_statistic')(
        teamcity.report_statistic,
    )
    return func
