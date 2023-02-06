import datetime

import pytest


ARGS_1 = [
    'park_id_2',
    'DriverId',
    'order_id_2',
    'feedback_id_2',
    {'$date': '2020-03-21T15:00:00Z'},
    5,
    0,
    1,
]
KWARGS_1: dict = {'description': 'abyrvalg'}
SQL_1 = (
    'park_id_2',
    'feedback_id_2',
    datetime.datetime(2020, 3, 21, 15, 00, 00),
    1,
    0,
    'abyrvalg',
    5,
    'DriverId',
    'order_id_2',
    1,
)
ARGS_2 = [
    'park_id_3',
    'DriverId',
    'order_id_3',
    'feedback_id_3',
    {'$date': '2020-03-20T06:00:00Z'},
    4,
    0,
    1,
]
KWARGS_2: dict = {}
SQL_2 = (
    'park_id_3',
    'feedback_id_3',
    datetime.datetime(2020, 3, 20, 6, 00, 00),
    1,
    0,
    None,
    4,
    'DriverId',
    'order_id_3',
    1,
)


@pytest.mark.now('2020-03-22T00:00:00+0000')
@pytest.mark.parametrize(
    'task_args,task_kwargs,expected_sql',
    [(ARGS_1, KWARGS_1, SQL_1), (ARGS_2, KWARGS_2, SQL_2)],
)
async def test_repeater_task(
        fleet_parks_service,
        stq_runner,
        task_args,
        task_kwargs,
        expected_sql,
        pgsql,
):
    fleet_parks_service.set_feedbacks_data(0, 'feedbacks_0')
    await stq_runner.driver_feedback_repeat.call(
        task_id=task_args[3], args=task_args, kwargs=task_kwargs,
    )

    cursor = pgsql['taximeter_feedbacks@0'].cursor()
    # check all but date_last_change - it is unmockable CURRENT_TIMESTAMP
    query = """SELECT
        park_id,
        id,
        date,
        feed_type,
        status,
        description,
        score,
        driver_id,
        order_id,
        order_number
        FROM feedbacks_0"""
    cursor.execute(query)
    rows = cursor.fetchall()
    # columns order in testsuite/schemas/postgresql/taximeter_feedbacks@0.sql
    assert len(rows) == 1
    assert rows[0] == expected_sql


@pytest.mark.now('2020-03-22T00:00:00+0000')
async def test_repeater_task_with_choices(
        fleet_parks_service, stq_runner, pgsql,
):
    args = (
        'park_id_2',
        'DriverId',
        'order_id_2',
        'feedback_id_2',
        datetime.datetime(2020, 3, 21, 15, 0),
        5,
        0,
        1,
    )
    kwargs = {
        'description': 'some text about score',
        'choices': 'reason_1;reason2',
    }

    fleet_parks_service.set_feedbacks_data(0, 'feedbacks_0')
    await stq_runner.driver_feedback_repeat.call(
        task_id=args[3], args=args, kwargs=kwargs,
    )

    cursor = pgsql['taximeter_feedbacks@0'].cursor()
    # check all but date_last_change - it is unmockable CURRENT_TIMESTAMP
    query = """SELECT
        park_id,
        driver_id,
        order_id,
        id,
        date,
        score,
        status,
        feed_type,
        description,
        predefined_comments
        FROM feedbacks_0"""
    cursor.execute(query)
    rows = cursor.fetchall()
    # columns order in testsuite/schemas/postgresql/taximeter_feedbacks@0.sql
    assert len(rows) == 1
    assert rows[0] == args + (kwargs['description'], kwargs['choices'])
