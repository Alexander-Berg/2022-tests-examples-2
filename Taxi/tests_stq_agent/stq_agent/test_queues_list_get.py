import pytest

from testsuite.utils import ordered_object


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_list_get(taxi_stq_agent):
    response = await taxi_stq_agent.get('queues/list')
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), {'queues': ['azaza11', 'azaza12']}, ['queues'],
    )


@pytest.mark.now('2018-12-01T14:00:00Z')
@pytest.mark.filldb(stq_config='empty')
async def test_queues_list_get_empty(taxi_stq_agent, mocked_time):
    mocked_time.sleep(120)
    await taxi_stq_agent.invalidate_caches()

    response = await taxi_stq_agent.get('queues/list')
    assert response.status_code == 200
    assert response.json() == {'queues': []}
