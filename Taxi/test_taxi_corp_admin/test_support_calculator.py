# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
async def mock_api(patch, load_json):
    @patch(
        'taxi.clients.archive_api._NoCodegenOrderArchive.order_proc_retrieve',
    )
    async def _order_proc_retrieve(*args, **kwargs) -> dict:
        return load_json('order_proc_retrieve.json')

    @patch('taxi_corp_admin.clients.corp_tariffs.CorpTariffsClient.get_tariff')
    async def _get_corp_tariff_by_id(*args, **kwargs) -> dict:
        return load_json('get_tariff_corp.json')

    @patch('taxi.clients.tariffs.TariffsClient.get_tariff')
    async def _get_tariff(*args, **kwargs) -> dict:
        return load_json('get_tariff.json')


async def test_get_order_summary_handler(
        taxi_corp_admin_client, mock_api, load_json,
):
    response = await taxi_corp_admin_client.get(
        '/v1/support_calculator/order_summary/{}'.format('order1'),
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == load_json('order_response.json')


async def test_get_new_price(taxi_corp_admin_client, mock_api):
    response = await taxi_corp_admin_client.post(
        '/v1/support_calculator/new_price',
        json={
            'order_id': 'order1',
            'city_time': 1.1,
            'city_distance': 1.2,
            'suburb_time': 1.3,
            'suburb_distance': 1.4,
            'paid_supply_time': 1.5,
        },
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'driver_price': 61.6, 'user_price': 56.4}
