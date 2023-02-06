import datetime as dt

import pytest

from fleet_rent.components import park_billing_info
from fleet_rent.entities import park as park_entities
from fleet_rent.entities import park_billing as park_billing_entities
from fleet_rent.generated.cron import cron_context as context_module
from fleet_rent.services import park_info as park_access

FLEET_RENT_IDS_TESTING_HACK = {
    'hack_clid': {
        'billing_client_id': 'client_id',
        'billing_contract_id': 'contract_id',
        'currency': 'USD',
        'inn': 'nalogi',
        'legal_address': 'Frunze ulitsa',
        'legal_name': 'Sea bream',
        'description': 'Some LLL',
    },
}


@pytest.mark.config(FLEET_RENT_IDS_TESTING_HACK=FLEET_RENT_IDS_TESTING_HACK)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_park_info(
        cron_context: context_module.Context, mock_fleet_parks,
):
    park_accessor: park_access.ParkInfoService = (
        cron_context.external_access.park
    )
    assert (
        (await park_accessor.get_park_billing_data('hack_clid'))
        == park_entities.ParkBillingClientData(
            clid='hack_clid',
            inn='nalogi',
            billing_client_id='client_id',
            legal_address='Frunze ulitsa',
            legal_name='Sea bream',
        )
    )


@pytest.mark.config(FLEET_RENT_IDS_TESTING_HACK=FLEET_RENT_IDS_TESTING_HACK)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_component(cron_context: context_module.Context, patch):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _park_info(park_id: str):
        assert park_id == '1234'
        return park_entities.Park(
            id=park_id, name='Агент 666', clid='hack_clid',
        )

    component: park_billing_info.ParkBillingInfo = (
        cron_context.rent_components.park_billing_info
    )
    billing_info = await component.get_owner_billing_info(
        '1234', dt.datetime.now(dt.timezone.utc),
    )
    assert billing_info == park_billing_entities.ParkBillingInfo(
        id='1234',
        clid='hack_clid',
        billing_client_id='client_id',
        billing_contract_id='contract_id',
    )
