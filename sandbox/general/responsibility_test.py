import datetime as dt

from sandbox.projects.AutocheckResponsibility import responsibility

import pytest


test_responsibles_data = [
    ["nalpp, snowball, nslus", (["nalpp", "snowball", "nslus"], False)],
    ["nalpp snowball+nslus", (["nalpp", "snowball+nslus"], False)],
    ["nalpp:2 snowball+nslus:3 heretic", (["nalpp", "nalpp", "snowball+nslus", "snowball+nslus", "snowball+nslus", "heretic"], False)],
    ["nalpp:5 nslus:5", (["nalpp", "nalpp", "nalpp", "nalpp", "nalpp", "nslus", "nslus", "nslus", "nslus", "nslus"], True)]
]


@pytest.mark.parametrize("responsibles_str, expected_result", test_responsibles_data,
                         ids=map(str, range(1, len(test_responsibles_data) + 1)))
def test_responsibles(responsibles_str, expected_result):
    assert expected_result == responsibility.parse_responsibles(responsibles_str)


test_generate_duty_schedule_data = [
    ["nalpp, snowball, nslus", "nalpp"],
    ["nalpp, snowball, nslus", "snowball"],
    ["nalpp, snowball, nslus", "nslus"],
    ["nalpp:2 snowball+nslus:3 heretic", "snowball+nslus"],
    ["nalpp snowball nslus heretic kakabba", "kakabba"],
    ["rustammm:5, yazevnul:5", "yazevnul"],
]


@pytest.mark.parametrize("responsibles_str, start_from", test_generate_duty_schedule_data,
                         ids=map(str, range(1, len(test_generate_duty_schedule_data) + 1)))
def test_generate_duty_schedule(responsibles_str, start_from):
    return responsibility.generate_duty_schedule(responsibles_str, start_from)


test_generate_result_data = [
    ["nalpp, snowball, nslus", "nalpp", "11.01.2017"],
    ["nalpp:2 snowball+nslus:3 heretic", "snowball+nslus", "11.01.2017"],
    ["nalpp snowball nslus heretic kakabba", "kakabba", "11.01.2017"],
]


@pytest.mark.parametrize("responsibles_str, start_from, start_date_str", test_generate_result_data,
                         ids=map(str, range(1, len(test_generate_result_data) + 1)))
def test_generate_result(responsibles_str, start_from, start_date_str):
    duty_schedule = responsibility.generate_duty_schedule(responsibles_str, start_from)
    assert len(responsibility.generate_result(start_date_str, duty_schedule)) == 11


test_get_result_for_date_data = [
    ["nalpp, snowball, nslus", "nalpp", "11.01.2017", "13.01.2017", "nslus"],
    ["nalpp, snowball, nslus", "nalpp", "11.01.2017", "14.01.2017", "nslus"],  # weekend
    ["nalpp, snowball, nslus", "nalpp", "11.01.2017", "16.01.2017", "nalpp"],
    ["nalpp:2 snowball+nslus:3 heretic", "snowball+nslus", "11.01.2017", "13.01.2017", "snowball+nslus"],
    ["nalpp:2 snowball+nslus:3 heretic", "snowball+nslus", "11.01.2017", "16.01.2017", "heretic"],  # end of schedule
    ["nalpp:2 snowball+nslus:3 heretic", "snowball+nslus", "11.01.2017", "24.01.2017", "heretic"],  # end of 2nd iteration of schedule
    ["nalpp snowball nslus heretic kakabba", "kakabba", "11.01.2017", "13.01.2017", "snowball"],
    ["nalpp snowball nslus heretic kakabba", "kakabba", "11.01.2017", "20.01.2017", "nslus"],
    ["rustammm:5, yazevnul:5", "rustammm", "06.05.2019", "24.05.2019", "rustammm"],  # end of 2nd iteration of schedule
    ["rustammm:5, yazevnul:5", "rustammm", "06.05.2019", "31.05.2019", "yazevnul"],  # end of 3d iteration of schedule
    ["rustammm:5, yazevnul:5, snowball:5, heretic:5, neksard:5, workfork:5", "workfork", "08.04.2019", "24.05.2019", "workfork"],
]


@pytest.mark.parametrize("responsibles_str, start_from, start_date_str, for_date_str, expected_duty", test_get_result_for_date_data,
                         ids=map(str, range(1, len(test_get_result_for_date_data) + 1)))
def test_get_result_for_date(responsibles_str, start_from, start_date_str, for_date_str, expected_duty):
    duty_schedule = responsibility.generate_duty_schedule(responsibles_str, start_from)
    start_date = dt.datetime.strptime(start_date_str, '%d.%m.%Y')
    for_date = dt.datetime.strptime(for_date_str, '%d.%m.%Y')
    assert responsibility.get_result_for_date(start_date, for_date, duty_schedule)[2] == expected_duty


RESULT = [
    ["27.01.2017", "4", "heretic", False],
    ["28.01.2017", "5", "heretic", False],
    ["29.01.2017", "6", "heretic", False],
    ["30.01.2017", "0", "dmitko", False],
    ["31.01.2017", "1", "prettyboy", False],
    ["01.02.2017", "2", "exprmntr", False],
    ["02.02.2017", "3", "nalpp", True],
    ["03.02.2017", "4", "akastornov", False],
    ["04.02.2017", "5", "akastornov", False],
    ["05.02.2017", "6", "akastornov", False],
    ["06.02.2017", "0", "nslus+snowball", False]
]


def test_week_responsibility():
    return responsibility.week_responsibility(RESULT, today="01.02.2017")
