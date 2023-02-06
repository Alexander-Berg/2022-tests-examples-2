import pytest


@pytest.mark.servicetest
async def test_debug_control(driver_route_watcher_ng_adv):
    drw = driver_route_watcher_ng_adv

    body = {
        'driver_id': {'uuid': 'driver0_uuid', 'dbid': 'driver0_dbid'},
        'order_id': 'order_id_1',
        'verbose_log': True,
    }
    response = await drw.post('/debug/control', json=body)
    assert response.status_code == 200
