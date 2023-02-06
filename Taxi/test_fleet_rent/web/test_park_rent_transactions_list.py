import aiohttp.web
import pytest


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     owner_park_id, owner_serial_id, asset_type, asset_params,
     driver_id,
     begins_at_tz,
     charging_type,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz,
     transfer_order_number)
    VALUES ('record_id', 'idempotency_token',
     'park_id', 1, 'other', '{"subtype": "misc"}',
     'driver_id',
     '2020-01-01+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00',
     'park_id_1')
        """,
    ],
)
@pytest.mark.now('2020-01-10T00:00:00')
async def test_get(web_app_client, load_json, mock_fleet_transactions_api):
    mock_data = load_json('fta.json')
    mock_requests = mock_data['requests']
    mock_responses = mock_data['responses']

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/transactions/list')
    async def _list(request):
        assert request.json == mock_requests.pop(0)
        return aiohttp.web.json_response(mock_responses.pop(0))

    response1 = await web_app_client.post(
        '/v1/park/rents/transactions/list',
        params={'park_id': 'park_id', 'record_id': 'record_id'},
        json={'limit': 2},
    )
    assert await response1.json() == {
        'transactions': [
            {
                'id': '1',
                'event_at': '2020-01-01T03:00:00+03:00',
                'category_id': 'category',
                'category_name': 'Category Name',
                'amount': '100',
                'currency_code': 'RUB',
                'description': 'Что-то №1 (title)',
            },
            {
                'id': '3',
                'event_at': '2020-01-01T03:00:00+03:00',
                'category_id': 'category',
                'category_name': 'Category Name',
                'amount': '100',
                'currency_code': 'RUB',
                'description': 'Что-то №1 (title)',
            },
            {
                'id': '4',
                'event_at': '2020-01-01T03:00:00+03:00',
                'category_id': 'category',
                'category_name': 'Category Name',
                'amount': '100',
                'currency_code': 'RUB',
                'description': 'Что-то №1 (title)',
            },
        ],
        'cursor': '2',
    }
    response2 = await web_app_client.post(
        '/v1/park/rents/transactions/list',
        params={'park_id': 'park_id', 'record_id': 'record_id'},
        json={'limit': 2, 'cursor': '2'},
    )
    assert await response2.json() == {
        'transactions': [
            {
                'id': '7',
                'event_at': '2020-01-02T03:00:00+03:00',
                'category_id': 'category',
                'category_name': 'Category Name',
                'amount': '100',
                'currency_code': 'RUB',
                'description': '1',
            },
        ],
        'cursor': '',
    }


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     owner_park_id, owner_serial_id, asset_type, asset_params,
     driver_id,
     begins_at_tz,
     charging_type,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz,
     transfer_order_number)
    VALUES ('record_id', 'idempotency_token',
     'park_id', 1, 'other', '{"subtype": "misc"}',
     'driver_id',
     '2020-01-10+00',
     'free',
     '2020-01-10+00',
     'creator_uid', '2020-01-10+00',
     '2020-01-10+00',
     'park_id_1')
        """,
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_from_future(web_app_client):
    response = await web_app_client.post(
        '/v1/park/rents/transactions/list',
        params={'park_id': 'park_id', 'record_id': 'record_id'},
        json={},
    )
    assert await response.json() == {'transactions': [], 'cursor': ''}
