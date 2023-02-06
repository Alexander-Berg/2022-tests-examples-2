import uuid

import aiohttp.web
import pytest

from tests_gas_stations_api import responses


PARK_ID = 'park_with_offer'
CONTRACTOR_ID = 'driver_1'
IDEMPOTENCY_TOKEN = uuid.uuid1().hex
TRANSACTION_DESCRIPTION = 'comment'


@pytest.fixture(name='sender')
async def _sender(taxi_gas_stations_api, gas_stations):
    async def _send(park_id=PARK_ID, category='refill', amount='-1'):
        endpoint = '/v1/balances/transaction'
        headers = {'X-Idempotency-Token': IDEMPOTENCY_TOKEN}
        params = {'park_id': park_id, 'contractor_profile_id': CONTRACTOR_ID}
        body = {
            'amount': amount,
            'category': category,
            'description': TRANSACTION_DESCRIPTION,
        }

        response = await taxi_gas_stations_api.post(
            endpoint, headers=headers, params=params, json=body,
        )
        assert gas_stations.has_calls
        return response

    return _send


@pytest.mark.parametrize('amount', ['0', '-100001', '100000.0001', 'trash'])
async def test_amount(sender, amount):
    response = await sender(amount=amount)
    assert response.status_code == 400, response.text
    assert response.json() == responses.make_error(
        '400', 'amount absolute value must be > 0 and <= 100000',
    )


async def test_offer_not_accepted(sender):
    response = await sender(park_id='park_without_offer')
    assert response.status_code == 403, response.text
    assert response.json() == responses.OFFER_NOT_ACCEPTED


async def test_park_not_found(sender):
    response = await sender(park_id='missing_park_id')
    assert response.status_code == 404, response.text
    assert response.json() == responses.PARK_NOT_FOUND


async def test_contractor_not_found(sender, mockserver):
    @mockserver.json_handler(
        '/fleet-transactions-api'
        '/v1/parks/driver-profiles/transactions/by-platform',
    )
    def _fleet_transactions_api(request):
        return aiohttp.web.json_response(
            responses.make_error(
                'driver_profile_not_found', 'driver not found',
            ),
            status=400,
        )

    response = await sender()
    assert response.status_code == 404, response.text
    assert response.json() == responses.CONTRACTOR_NOT_FOUND
    assert _fleet_transactions_api.has_calls


@pytest.mark.parametrize(
    'amount, category, category_id',
    [
        ('-100000', 'refill', 'platform_other_gas'),
        ('-0.0001', 'park_commission', 'platform_other_gas_fleet_fee'),
        ('0.00010', 'cashback', 'platform_other_gas_cashback'),
        ('100000', 'tips', 'platform_other_gas_tip'),
    ],
)
async def test_ok(sender, mockserver, amount, category, category_id):
    @mockserver.json_handler(
        '/fleet-transactions-api'
        '/v1/parks/driver-profiles/transactions/by-platform',
    )
    def _fleet_transactions_api(request):
        assert request.headers['X-Idempotency-Token'] == IDEMPOTENCY_TOKEN
        assert request.headers['X-Ya-Service-Name'] == 'gas-stations-api'
        assert request.json == {
            'park_id': PARK_ID,
            'driver_profile_id': CONTRACTOR_ID,
            'category_id': category_id,
            'amount': amount,
            'description': TRANSACTION_DESCRIPTION,
        }
        return {
            'event_at': '2021-11-20T14:41:01+03:00',
            'park_id': PARK_ID,
            'driver_profile_id': CONTRACTOR_ID,
            'category_id': category_id,
            'amount': amount,
            'currency_code': 'RUB',
            'description': TRANSACTION_DESCRIPTION,
            'created_by': {'identity': 'platform'},
        }

    response = await sender(amount=amount, category=category)
    assert response.status_code == 200, response.text
    assert _fleet_transactions_api.has_calls


async def test_unexpected_transaction_error(sender, mockserver):
    @mockserver.json_handler(
        '/fleet-transactions-api'
        '/v1/parks/driver-profiles/transactions/by-platform',
    )
    def _fleet_transactions_api(request):
        return aiohttp.web.json_response(
            responses.make_error(
                'category_inaccessible', 'category inaccessible',
            ),
            status=400,
        )

    response = await sender()
    assert response.status_code == 500
    assert _fleet_transactions_api.has_calls
