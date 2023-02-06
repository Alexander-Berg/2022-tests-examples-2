import datetime

import pytest

from testsuite.utils import http

from fleet_rent.entities import billing
from fleet_rent.entities import park as park_entities
from fleet_rent.generated.web import web_context as context_module


@pytest.mark.config(
    FLEET_RENT_EXTERNAL_PARK_TRANSACTIONS_PROCESSING={
        'send': {
            'is_enabled': True,
            'owner_park_service_id': 222,
            'driver_park_service_id': 124,
        },
    },
)
async def test_park_can_have_rent_ext(
        web_context: context_module.Context, mock_billing_replication,
):
    @mock_billing_replication('/v1/active-contracts/')
    async def _contracts(request: http.Request):
        assert dict(request.query) == {
            'active_ts': '2020-01-01T00:00:00',
            'actual_ts': '2020-01-01T00:00:00',
            'client_id': 'billing_client_id',
            'service_id': '222',
        }
        return [{'ID': 456, 'SERVICES': [222]}]

    park_billing_data = park_entities.ParkBillingClientData(
        clid='100500',
        inn='inn',
        billing_client_id='billing_client_id',
        legal_address='legal_address',
        legal_name='legal_name',
    )
    now = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

    br_service = web_context.external_access.billing_replication

    assert await br_service.park_can_have_rent_external(park_billing_data, now)


@pytest.mark.config(
    FLEET_RENT_EXTERNAL_PARK_TRANSACTIONS_PROCESSING={
        'send': {
            'is_enabled': True,
            'owner_park_service_id': 222,
            'driver_park_service_id': 124,
        },
    },
)
async def test_park_can_not_have_rent_ex(
        web_context: context_module.Context, mock_billing_replication,
):
    @mock_billing_replication('/v1/active-contracts/')
    async def _contracts(request: http.Request):
        assert dict(request.query) == {
            'active_ts': '2020-01-01T00:00:00',
            'actual_ts': '2020-01-01T00:00:00',
            'client_id': 'billing_client_id',
            'service_id': '222',
        }
        return []

    park_billing_data = park_entities.ParkBillingClientData(
        clid='100500',
        inn='inn',
        billing_client_id='billing_client_id',
        legal_address='legal_address',
        legal_name='legal_name',
    )
    now = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

    br_service = web_context.external_access.billing_replication
    assert not await br_service.park_can_have_rent_external(
        park_billing_data, now,
    )


@pytest.mark.config(
    FLEET_RENT_EXTERNAL_PARK_TRANSACTIONS_PROCESSING={
        'send': {
            'is_enabled': True,
            'owner_park_service_id': 222,
            'driver_park_service_id': 124,
        },
    },
)
async def test_get_contract(
        web_context: context_module.Context, mock_billing_replication,
):
    @mock_billing_replication('/v1/active-contracts/')
    async def _contracts(request: http.Request):
        assert dict(request.query) == {
            'active_ts': '2020-01-01T00:00:00',
            'actual_ts': '2020-01-01T00:00:00',
            'client_id': 'billing_client_id',
            'service_id': '222',
        }
        return [{'ID': 456, 'SERVICES': [222], 'CURRENCY': 'RUR'}]

    park_billing_data = park_entities.ParkBillingClientData(
        clid='100500',
        inn='inn',
        billing_client_id='billing_client_id',
        legal_address='legal_address',
        legal_name='legal_name',
    )
    now = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

    br_service = web_context.external_access.billing_replication
    contract = await br_service.get_park_contract(park_billing_data, now)

    assert contract == billing.Contract(id=456, currency='RUB')


@pytest.mark.config(
    FLEET_RENT_EXTERNAL_PARK_TRANSACTIONS_PROCESSING={
        'send': {
            'is_enabled': True,
            'owner_park_service_id': 222,
            'driver_park_service_id': 124,
        },
    },
)
async def test_get_driver_contract(
        web_context: context_module.Context, mock_billing_replication,
):
    @mock_billing_replication('/v1/active-contracts/')
    async def _contracts(request: http.Request):
        assert dict(request.query) == {
            'active_ts': '2020-01-01T00:00:00',
            'actual_ts': '2020-01-01T00:00:00',
            'client_id': 'billing_client_id',
            'service_id': '124',
        }
        return [{'ID': 456, 'SERVICES': [124], 'CURRENCY': 'RUR'}]

    park_billing_data = park_entities.ParkBillingClientData(
        clid='100500',
        inn='inn',
        billing_client_id='billing_client_id',
        legal_address='legal_address',
        legal_name='legal_name',
    )
    now = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

    br_service = web_context.external_access.billing_replication
    contract = await br_service.get_driver_contract(park_billing_data, now)

    assert contract == billing.Contract(id=456, currency='RUB')
