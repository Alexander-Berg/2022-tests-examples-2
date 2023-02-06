import datetime as dt

from fleet_rent.entities import billing as billing_entities
from fleet_rent.entities import park
from fleet_rent.generated.web import web_context as context_module


async def test_get_independent_driver_currency(
        web_context: context_module.Context, patch, park_stub_factory,
):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info(park_id):
        assert park_id == 'smz_id'
        return park_stub_factory(
            id=park_id, clid='clidClid', driver_partner_source='yandex',
        )

    @patch(
        'fleet_rent.services.park_info.ParkInfoService.get_park_billing_data',
    )
    async def _get_park_billing_data(clid):
        assert clid == 'clidClid'
        return park.ParkBillingClientData(
            clid=clid,
            inn='inn',
            billing_client_id='billing_client_id',
            legal_address='legal_address',
            legal_name='legal_name',
        )

    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.get_driver_contract',
    )
    async def _get_driver_contract(billing_client_data, actual_at):
        assert actual_at == dt.datetime(2020, 1, 1, 12, tzinfo=dt.timezone.utc)
        assert billing_client_data == park.ParkBillingClientData(
            clid='clidClid',
            inn='inn',
            billing_client_id='billing_client_id',
            legal_address='legal_address',
            legal_name='legal_name',
        )
        return billing_entities.Contract(id=123, currency='RUB')

    currency_provider = web_context.rent_components.currency_provider
    currency = await currency_provider.get_independent_driver_currency(
        'smz_id', dt.datetime(2020, 1, 1, 12, tzinfo=dt.timezone.utc),
    )
    assert currency == 'RUB'


async def test_get_park_external_currency(
        web_context: context_module.Context, patch, park_stub_factory,
):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info(park_id):
        assert park_id == 'park_id'
        return park_stub_factory(id=park_id, clid='clidClid')

    @patch(
        'fleet_rent.services.park_info.ParkInfoService.get_park_billing_data',
    )
    async def _get_park_billing_data(clid):
        assert clid == 'clidClid'
        return park.ParkBillingClientData(
            clid=clid,
            inn='inn',
            billing_client_id='billing_client_id',
            legal_address='legal_address',
            legal_name='legal_name',
        )

    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.get_park_contract',
    )
    async def _get_park_contract(billing_client_data, actual_at):
        assert actual_at == dt.datetime(2020, 1, 1, 12, tzinfo=dt.timezone.utc)
        assert billing_client_data == park.ParkBillingClientData(
            clid='clidClid',
            inn='inn',
            billing_client_id='billing_client_id',
            legal_address='legal_address',
            legal_name='legal_name',
        )
        return billing_entities.Contract(id=222, currency='RUB')

    currency_provider = web_context.rent_components.currency_provider
    currency = await currency_provider.get_park_external_currency(
        'park_id', dt.datetime(2020, 1, 1, 12, tzinfo=dt.timezone.utc),
    )
    assert currency == 'RUB'


async def test_get_park_internal_currency(
        web_context: context_module.Context, patch, park_stub_factory,
):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info(park_id):
        assert park_id == 'park_id'
        return park_stub_factory(id=park_id, country_id='rus')

    @patch(
        'fleet_rent.services.territories.'
        'TerritoriesService.get_currency_by_country_id',
    )
    async def _get_country_currency(country_id):
        assert country_id == 'rus'
        return 'RUB'

    currency_provider = web_context.rent_components.currency_provider
    currency = await currency_provider.get_park_internal_currency(
        'park_id', dt.datetime(2020, 1, 1, 12, tzinfo=dt.timezone.utc),
    )
    assert currency == 'RUB'
