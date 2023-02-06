import pytest


@pytest.mark.servicetest
async def test_cargo_stop_watch_200(driver_route_watcher_ng_adv):
    drw = driver_route_watcher_ng_adv

    body = {'courier': 'dbid_uuid'}
    response = await drw.post('cargo/stop-watch', json=body)
    assert response.status_code == 200
