# pylint: disable=C5521


async def test_run(taxi_reposition_api):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': 'drivers-state-monitor'},
        )
    ).status_code == 200
