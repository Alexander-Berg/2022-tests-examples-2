import pytest
import aiohttp
from stall.client.clickhouse import grocery_clickhouse_pool

@pytest.fixture
async def grocery_ch_client_wrong(clickhouse_client, uuid):
    # pylint: disable=unused-argument
    auth_backup = {
        client: client.base_headers['Authorization']
        for client in grocery_clickhouse_pool.clients
    }
    for client in grocery_clickhouse_pool.clients:
        client.base_headers['Authorization'] = aiohttp.BasicAuth(
            uuid(),
            uuid()
        ).encode()

    yield grocery_clickhouse_pool

    for client in grocery_clickhouse_pool.clients:
        client.base_headers['Authorization'] = auth_backup.get(client)


async def test_ping(api, tap, clickhouse_client):
    # pylint: disable=unused-argument
    tap.plan(4, 'Проверим, что кликхаус доступен')
    t = await api(role='admin')

    await t.get_ok('api_report_data_realtime_metrics_ping')
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_like('message', 'PONG', t.res['json']['message'])


async def test_fail_ping(api, tap, grocery_ch_client_wrong):
    # pylint: disable=unused-argument, redefined-outer-name
    tap.plan(4, 'Обращение по неверным кредам')

    t = await api(role='admin')

    await t.get_ok('api_report_data_realtime_metrics_ping')
    t.status_is(502, diag=True)
    t.json_is('code', 'ER_BAD_GATEWAY')
    t.json_is('message', 'PONG')
