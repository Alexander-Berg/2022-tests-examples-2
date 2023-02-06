import datetime

import pytest


@pytest.mark.parametrize(
    'at_,age,expected_year',
    [
        (datetime.datetime(2020, 1, 1), 2, 2017),
        (datetime.datetime(2020, 2, 1), 2, 2017),
        (datetime.datetime(2020, 3, 1), 2, 2018),
        (datetime.datetime(2020, 4, 1), 2, 2018),
    ],
)
@pytest.mark.config(CARS_CATALOG_MANUFACTURE_MONTH=3)  # March
async def test_age_to_year(web_context, at_, age, expected_year):
    year = web_context.age_fixer.age_to_year(age, at_)
    assert year == expected_year


@pytest.mark.parametrize(
    'at_,year,expected_age',
    [
        (datetime.datetime(2020, 1, 1), 2017, 2),
        (datetime.datetime(2020, 2, 1), 2017, 2),
        (datetime.datetime(2020, 3, 1), 2018, 2),
        (datetime.datetime(2020, 4, 1), 2018, 2),
    ],
)
@pytest.mark.config(CARS_CATALOG_MANUFACTURE_MONTH=3)  # March
async def test_year_to_age(web_context, at_, year, expected_age):
    age = web_context.age_fixer.year_to_age(year, at_)
    assert age == expected_age
