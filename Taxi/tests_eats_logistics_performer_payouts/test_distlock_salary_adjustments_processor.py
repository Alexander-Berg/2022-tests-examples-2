import pytest

TASK_NAME = 'salary-adjustments-processor-periodic'

SQL_GET_CALC_RESULTS = """
    select subject_id, meta
    from eats_logistics_performer_payouts.calculation_results
    order by subject_id;
    """

SQL_GET_ADJUSTMENTS_PROCESSED_FLAGS = """
    select processed
    from eats_logistics_performer_payouts.salary_adjustments
    """


@pytest.mark.xfail(reason='salary adjustments temporarily disabled')
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts', files=['salary_adjustments.sql'],
)
async def test_salary_adjustment_processor(
        taxi_eats_logistics_performer_payouts, pgsql,
):
    cursor = pgsql['eats_logistics_performer_payouts'].cursor()

    # check that not all processed
    cursor.execute(SQL_GET_ADJUSTMENTS_PROCESSED_FLAGS)
    assert not all([x[0] for x in cursor])

    # run task
    await taxi_eats_logistics_performer_payouts.run_periodic_task(TASK_NAME)

    # check that all processed
    cursor.execute(SQL_GET_ADJUSTMENTS_PROCESSED_FLAGS)
    assert all([x[0] for x in cursor])

    # check calc results
    cursor.execute(SQL_GET_CALC_RESULTS)

    results = list(cursor)
    assert len(results) == 2

    # check first subject
    subject_id, meta = results[0]
    assert subject_id == 1
    expected = {
        'region_id': 'region_1',
        'courier_id': 'courier_1',
        'courier_name': 'user_1',
        'salary_adjustments': 124.0001,
    }
    assert expected.items() <= meta.items()

    # check second subject
    subject_id, meta = results[1]
    assert subject_id == 2
    expected = {
        'region_id': 'region_3',
        'courier_id': 'courier_3',
        'courier_name': 'user_3',
        'salary_adjustments': 10000.0,
    }
    assert expected.items() <= meta.items()
