import pytest

from test_taxi_exp.helpers import db


@pytest.mark.pgsql('taxi_exp')
async def test_adding_history(taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    parent_mds_id = await db.add_or_update_file(taxi_exp_app, 'test')

    response_history = await db.get_history(taxi_exp_app)
    assert len(response_history) == 1

    await db.add_or_update_file(taxi_exp_app, 'test')
    response_history_l3 = await db.get_history(taxi_exp_app)
    assert len(response_history_l3) == 2

    await db.delete_file(taxi_exp_app, parent_mds_id, 2)
    response_history_l5 = await db.get_history(taxi_exp_app)
    assert len(response_history_l5) == 3
