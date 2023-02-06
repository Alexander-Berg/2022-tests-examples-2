import pytest

from testsuite.utils import http


@pytest.fixture(name='fleet_parks_fixture')
def _fleet_parks_fixture(mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/list')
    async def _handle_fleet_parks(request):
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'park_id',
                    'name': 'park_id',
                    'is_active': True,
                    'city_id': 'park_id',
                    'locale': 'park_id',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'park_id',
                    'demo_mode': False,
                    'provider_config': {
                        'type': 'production',
                        'clid': '100500',
                    },
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
async def test_debt_amounts_ok(
        web_app_client, fleet_parks_fixture, mock_billing_reports, load_json,
):
    @mock_billing_reports('/v1/docs/select')
    async def _get_docs(request: http.Request):
        if 'cursor' in request.json:
            return {'cursor': {}, 'docs': []}
        topic = request.json['external_obj_id']
        if topic == 'taxi/periodic_payment/clid/100500/park_id_4':
            return load_json('billing_reports_big.json')
        if topic == 'taxi/periodic_payment/clid/100500/park_id_4/1':
            return load_json('billing_reports_detailed1.json')
        if topic == 'taxi/periodic_payment/clid/100500/park_id_4/3':
            return load_json('billing_reports_detailed3.json')
        assert False, request.json

    response = await web_app_client.post(
        '/v1/park/rents/external-debt-cancellation/amounts',
        params={
            'park_id': 'park_id',
            'user_id': 'user',
            'serial_id': 4,
            'cancellation_id': 'id4',
        },
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body == {
        'requested': {'amount': '176.0', 'currency': 'RUB'},
        'cancelled': {'amount': '86', 'currency': 'RUB'},
        'processed': {'amount': '90', 'currency': 'RUB'},
    }


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
async def test_debt_amounts_unready(web_app_client):
    response = await web_app_client.post(
        '/v1/park/rents/external-debt-cancellation/amounts',
        params={
            'park_id': 'park_id',
            'user_id': 'user',
            'serial_id': 4,
            'cancellation_id': 'id',
        },
    )
    assert response.status == 409, await response.text()


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
async def test_debt_amounts_invalid_park(web_app_client):
    response = await web_app_client.post(
        '/v1/park/rents/external-debt-cancellation/amounts',
        params={
            'park_id': 'park_id23',
            'user_id': 'user',
            'serial_id': 4,
            'cancellation_id': 'id4',
        },
    )
    assert response.status == 403, await response.text()


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
async def test_debt_amounts_not_found(web_app_client):
    response = await web_app_client.post(
        '/v1/park/rents/external-debt-cancellation/amounts',
        params={
            'park_id': 'park_id23',
            'user_id': 'user',
            'serial_id': 4,
            'cancellation_id': 'id10',
        },
    )
    assert response.status == 404, await response.text()
