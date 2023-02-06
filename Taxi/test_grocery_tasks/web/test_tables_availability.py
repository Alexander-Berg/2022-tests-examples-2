import datetime

import pytest

from grocery_tasks.api.tables_availability import _should_be_checked


@pytest.mark.config(GROCERY_AUTOORDER_TABLES_TO_COPY={})
@pytest.mark.servicetest
async def test_tables_availability_200(taxi_grocery_tasks_web):
    response = await taxi_grocery_tasks_web.get('/tables-availability')
    assert response.status == 200
    content = await response.text()
    assert content == ''


@pytest.mark.config(
    GROCERY_AUTOORDER_TABLES_TO_COPY={
        'tables_availability_check': [
            {
                'time_to_check': '44:00',
                'check_duration': 2,
                'path': (
                    '//home/lavka/production/autoorders/safety_stock_ml/{}'
                ),
            },
        ],
    },
)
@pytest.mark.servicetest
async def test_tables_availability_404_bad_time(taxi_grocery_tasks_web):
    response = await taxi_grocery_tasks_web.get('/tables-availability')
    assert response.status == 404


@pytest.mark.config(
    GROCERY_AUTOORDER_TABLES_TO_COPY={
        'tables_availability_check': [
            {
                'time_to_check': '22:00',
                'check_duration': 10000,
                'path': 'invalid path',
            },
        ],
    },
)
@pytest.mark.servicetest
async def test_tables_availability_404_bad_path(taxi_grocery_tasks_web):
    response = await taxi_grocery_tasks_web.get('/tables-availability')
    assert response.status == 404


@pytest.mark.now('2020-01-01T17:30:00.000000+03:00')
def test_should_be_checked():
    assert (
        _should_be_checked(
            check_from=datetime.time(hour=17), check_to=datetime.time(hour=19),
        )
        is True
    )

    assert (
        _should_be_checked(
            check_from=datetime.time(hour=16), check_to=datetime.time(hour=17),
        )
        is False
    )

    assert (
        _should_be_checked(
            check_from=datetime.time(hour=14), check_to=datetime.time(hour=16),
        )
        is False
    )


@pytest.mark.now('2020-01-01T21:00:00.000000+03:00')
def test_should_be_checked_corner_case():
    assert (
        _should_be_checked(
            check_from=datetime.time(hour=21), check_to=datetime.time(hour=22),
        )
        is True
    )

    assert (
        _should_be_checked(
            check_from=datetime.time(hour=20), check_to=datetime.time(hour=21),
        )
        is False
    )
