import pytest


# For catching distlocked periodic task
@pytest.fixture(name='testpoint_taxi_maestro')
def _testpoint_taxi_maestro(testpoint):
    class Context:
        @staticmethod
        @testpoint('taxi_maestro-switched-off')
        def switched_off(data):
            pass

        @staticmethod
        @testpoint('taxi_maestro-finished')
        def finished(data):
            pass

    return Context()


@pytest.mark.config(
    PERSEY_TAXI_MAESTRO={
        'check_period': 60,
        'enabled': False,
        'search_period': 100,
    },
)
async def test_switched_off(taxi_persey_labs, testpoint_taxi_maestro):
    async with taxi_persey_labs.spawn_task('distlock-taxi-maestro-task'):
        await testpoint_taxi_maestro.switched_off.wait_call()


@pytest.mark.now('2020-11-10T08:35:00+0300')
@pytest.mark.parametrize(
    'tasks_created, shift_ids',
    [
        pytest.param(
            1,
            [2],
            marks=pytest.mark.config(
                PERSEY_TAXI_MAESTRO={
                    'check_period': 60,
                    'enabled': True,
                    'search_period': 1800,
                },
            ),
        ),
        pytest.param(
            2,
            [2, 3],
            marks=pytest.mark.config(
                PERSEY_TAXI_MAESTRO={
                    'check_period': 60,
                    'enabled': True,
                    'search_period': 1800,
                    'retry_incomplete': True,
                },
            ),
        ),
    ],
)
async def test_new_tasks(
        fill_labs,
        taxi_persey_labs,
        testpoint_taxi_maestro,
        stq,
        load_json,
        tasks_created,
        shift_ids,
):
    fill_labs.load_lab_entities(load_json('labs.json'))
    fill_labs.load_employees('my_lab_id_1', load_json('employees.json'))

    async with taxi_persey_labs.spawn_task('distlock-taxi-maestro-task'):
        await testpoint_taxi_maestro.finished.wait_call()
    assert stq.persey_taxi_order_create.times_called == tasks_created
    while stq.persey_taxi_order_create.times_called != 0:
        stq_call = stq.persey_taxi_order_create.next_call()
        assert int(stq_call['id']) in shift_ids
