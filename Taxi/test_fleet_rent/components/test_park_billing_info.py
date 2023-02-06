import datetime

import pytest

from fleet_rent.components import park_billing_info
from fleet_rent.entities import park_billing
from fleet_rent.generated.web import web_context as context_module


async def test_get(
        web_context: context_module.Context,
        patch,
        mock_load_park_info,
        mock_load_billing_data,
        billing_contract_stub_factory,
):
    component = web_context.rent_components.park_billing_info
    now = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

    # Happy path
    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.get_park_contract',
    )
    async def _get_park_contract(*args, **kwargs):
        return billing_contract_stub_factory()

    park = await component.get_owner_billing_info('park_id', now)

    assert park == park_billing.ParkBillingInfo(
        id='park_id',
        clid='100500',
        billing_client_id='billing_client_id',
        billing_contract_id='1',
    )

    # Part of the data is missing
    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.get_driver_contract',
    )
    async def _get_driver_contract(*args, **kwargs):
        return None

    with pytest.raises(park_billing_info.DataError):
        await component.get_driver_billing_info('driver_park_id', now)
