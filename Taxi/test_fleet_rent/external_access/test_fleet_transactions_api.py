import datetime
import decimal

from testsuite.utils import http

from fleet_rent.generated.web import web_context as context_module
from fleet_rent.services import fleet_transactions_api


async def test_internal(
        web_context: context_module.Context, mock_fleet_transactions_api,
):
    transaction = fleet_transactions_api.TransactionData(
        rent_id='r',
        park_id='p',
        driver_id='d',
        amount=decimal.Decimal(10),
        title='Title',
        rent_serial_id=1,
        event_at=datetime.datetime(2020, 1, 2, tzinfo=datetime.timezone.utc),
        event_number=2,
    )

    @mock_fleet_transactions_api(
        '/v1/parks/driver-profiles/transactions/by-platform',
    )
    async def _send(request: http.Request):
        assert request.json == {
            'park_id': 'p',
            'driver_profile_id': 'd',
            'category_id': 'partner_service_recurring_payment',
            'amount': '-10',
            'description': '1 (Title)',
            'event_at': '2020-01-02T03:00:00+03:00',
        }
        return dict(
            **request.json,
            created_by={'identity': 'platform'},
            currency_code='RUB',
        )

    fta = web_context.external_access.fleet_transactions_api

    await fta.send(transaction)
