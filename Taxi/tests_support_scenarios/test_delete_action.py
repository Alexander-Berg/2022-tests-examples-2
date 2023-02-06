import pytest


@pytest.mark.parametrize(['action_id'], [('action_1',), ('action_1dsddsfsf',)])
async def test_delete_action(taxi_support_scenarios, pgsql, action_id):
    response = await taxi_support_scenarios.delete(
        f'v1/actions/?action_id={action_id}',
    )
    assert response.status_code == 200

    cursor = pgsql['support_scenarios'].cursor()
    cursor.execute(f'SELECT * FROM scenarios.action')
    ids = list(row[0] for row in cursor)
    assert action_id not in ids
