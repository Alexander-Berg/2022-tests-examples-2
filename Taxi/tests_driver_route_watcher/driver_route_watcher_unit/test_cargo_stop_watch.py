import pytest


@pytest.mark.servicetest
async def test_cargo_stop_watch_200(taxi_driver_route_watcher):
    body = {'courier': 'dbid_uuid'}
    response = await taxi_driver_route_watcher.post(
        'cargo/stop-watch', json=body,
    )
    assert response.status_code == 200
