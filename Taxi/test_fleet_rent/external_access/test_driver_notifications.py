import datetime
import decimal

import pytest

from testsuite.utils import http

from fleet_rent.entities import driver_communications_sync
from fleet_rent.generated.web import web_context as context_module


async def test_new_affiliation(
        web_context: context_module.Context,
        mock_client_notify,
        park_stub_factory,
        park_billing_data_stub_factory,
        aff_stub_factory,
):
    notify_expected_req = {
        'intent': 'PartnerAffiliationProposal',
        'service': 'taximeter',
        'client_id': 'OriginalDriverParkId-OriginalDriverId',
        'collapse_key': 'PartnerAffiliationProposal',
        'ttl': 30,
        'data': {
            'park_name': 'ИмяПарка',
            'affiliation_id': 'affiliation_id',
            'park_legal_name': 'legal_name',
            'park_legal_address': 'legal_address',
            'park_inn': 'inn',
            'code': 1351,
        },
    }

    @mock_client_notify('/v2/push')
    async def _push(request: http.Request):
        assert request.json == notify_expected_req
        return {'notification_id': '1'}

    affiliation = aff_stub_factory()
    park_info = park_stub_factory()
    park_billing_data = park_billing_data_stub_factory()

    await web_context.external_access.driver_notifications.new_affiliation(
        affiliation, park_info, park_billing_data,
    )


async def test_new_rent(
        web_context: context_module.Context,
        mock_client_notify,
        park_stub_factory,
        aff_stub_factory,
        rent_stub_factory,
):
    notify_expected_req = {
        'intent': 'PartnerRentProposal',
        'service': 'taximeter',
        'client_id': 'OriginalDriverParkId-OriginalDriverId',
        'collapse_key': 'PartnerRentProposal',
        'ttl': 30,
        'data': {
            'park_name': 'ИмяПарка',
            'rent_number': 1,
            'rent_id': 'record_id',
            'code': 1350,
        },
    }

    @mock_client_notify('/v2/push')
    async def _push(request: http.Request):
        assert request.json == notify_expected_req
        return {'notification_id': '1'}

    affiliation = aff_stub_factory()
    park_info = park_stub_factory()
    rent = rent_stub_factory()

    await web_context.external_access.driver_notifications.new_rent(
        affiliation, park_info, rent,
    )


async def test_rent_terminated(
        web_context: context_module.Context,
        mock_client_notify,
        park_stub_factory,
        aff_stub_factory,
        rent_stub_factory,
):
    notify_expected_req = {
        'intent': 'PartnerRentTermination',
        'service': 'taximeter',
        'client_id': 'OriginalDriverParkId-OriginalDriverId',
        'collapse_key': 'PartnerRentTermination',
        'ttl': 30,
        'data': {
            'park_name': 'ИмяПарка',
            'rent_number': 1,
            'rent_id': 'record_id',
            'code': 1352,
        },
    }

    @mock_client_notify('/v2/push')
    async def _push(request: http.Request):
        assert request.json == notify_expected_req
        return {'notification_id': '1'}

    affiliation = aff_stub_factory()
    park_info = park_stub_factory()
    rent = rent_stub_factory()

    await web_context.external_access.driver_notifications.terminated_rent(
        affiliation, park_info, rent,
    )


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'Forthcoming deduction': {'ru': 'Предстоящее удержание'},
        (
            'Forthcoming deduction for {amount} '
            'on payment order #{id}, {park_name}'
        ): {
            'ru': (
                'По поручению №{id} от парка {park_name} '
                'будет удержано {amount}'
            ),
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'ПереводМосква'}},
)
async def test_forthcoming_deduction(
        web_context: context_module.Context,
        mock_client_notify,
        park_stub_factory,
        billing_contract_stub_factory,
):
    notify_expected_req = {
        'intent': 'MessageNew',
        'service': 'taximeter',
        'client_id': 'DriverParkId-driverId',
        'collapse_key': 'Alert:ForthcomingDeduction/rent_id/1',
        'ttl': 30,
        'data': {
            'id': 'periodic_charging/rent_id/forthcoming_deduction/1',
            'message': (
                'По поручению №1 от парка ИмяПарка будет удержано 100 ₽'
            ),
            'name': 'Предстоящее удержание',
            'code': 100,
        },
    }

    @mock_client_notify('/v2/push')
    async def _push(request: http.Request):
        assert request.json == notify_expected_req
        return {'notification_id': '1'}

    park = park_stub_factory()
    data = driver_communications_sync.ForthcomingDeduction(
        record_id='rent_id',
        record_serial_id=1,
        serial_id=1,
        amount=decimal.Decimal(100),
        park_id='park_id',
        external_driver_id='driverId',
        external_driver_park_id='DriverParkId',
        timestamp=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
    )
    contract = billing_contract_stub_factory()

    driver_notifications = web_context.external_access.driver_notifications

    await driver_notifications.forthcoming_deduction(
        data, park, contract, ['ru'],
    )
