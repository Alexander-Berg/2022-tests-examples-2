import pytest
from yaseclib import gap

invalid_dates = ["12-01-2019", "2018-24-12", "12-2007-04"]

holidays_dates = ["2017-01-01", "2018-01-02"]
work_dates = ["2018-01-26", "2018-03-19", "2017-09-19"]

date_wrong_type = [123, [1, 2], False]


@pytest.fixture()
def prepare_init_vars():
    gap_api_url = "https://staff.yandex-team.ru/gap-api/api"
    token = ""
    calendar_api_url = "http://calendar-api.tools.yandex.net/internal"

    return (gap_api_url, token, calendar_api_url)


@pytest.mark.parametrize("invalid_dates", invalid_dates)
def test_check_date_validity(invalid_dates, prepare_init_vars):
    test_object = gap.Gap(
        prepare_init_vars[0], prepare_init_vars[1], prepare_init_vars[2]
    )

    assert test_object._check_date_validity(invalid_dates) is False


@pytest.mark.parametrize("holidays_dates", holidays_dates)
def test_get_holidays_info_from_calendar(holidays_dates, prepare_init_vars):
    test_object = gap.Gap(
        prepare_init_vars[0], prepare_init_vars[1], prepare_init_vars[2]
    )

    assert test_object.get_holidays_info_from_calendar(holidays_dates) is False


@pytest.mark.parametrize("date_wrong_type", date_wrong_type)
def test_is_workday_raises_on_wrong_type(date_wrong_type, prepare_init_vars):
    test_object = gap.Gap(
        prepare_init_vars[0], prepare_init_vars[1], prepare_init_vars[2]
    )
    with pytest.raises(TypeError):
        test_object.is_workday(date=date_wrong_type)


@pytest.mark.parametrize("invalid_dates", invalid_dates)
def test_is_workday_raises_on_wrong_timeformat(invalid_dates, prepare_init_vars):
    test_object = gap.Gap(
        prepare_init_vars[0], prepare_init_vars[1], prepare_init_vars[2]
    )
    with pytest.raises(ValueError):
        test_object.is_workday(date=invalid_dates)


@pytest.mark.parametrize("work_dates", work_dates)
def test_is_workday_on_work_dates(work_dates, prepare_init_vars):
    test_object = gap.Gap(
        prepare_init_vars[0], prepare_init_vars[1], prepare_init_vars[2]
    )

    assert test_object.is_workday(date=work_dates) is True


@pytest.mark.parametrize("holidays_dates", holidays_dates)
def test_is_workday_on_holidays(holidays_dates, prepare_init_vars):
    test_object = gap.Gap(
        prepare_init_vars[0], prepare_init_vars[1], prepare_init_vars[2]
    )

    assert test_object.is_workday(date=holidays_dates) is False
