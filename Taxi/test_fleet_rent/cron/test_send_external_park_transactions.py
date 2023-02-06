import datetime

import pytest

from testsuite.utils import http

from fleet_rent.components import park_billing_info as billing_info_comp
from fleet_rent.entities import park_billing as park_billing_ent
from fleet_rent.generated.cron import cron_context as context
from fleet_rent.generated.cron import run_cron


@pytest.mark.now('2020-01-04T00:00:00')
@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
@pytest.mark.config(
    FLEET_RENT_EXTERNAL_PARK_TRANSACTIONS_PROCESSING={
        'send': {
            'is_enabled': True,
            'owner_park_service_id': 222,
            'driver_park_service_id': 124,
        },
    },
)
async def test_run_sept(
        mock_billing_orders, cron_context: context.Context, patch,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        assert park_id == 'park_id'
        return 'RUB'

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_owner_billing_info',
    )
    async def _get_owner_billing_info(park_id, actual_at):
        assert park_id == 'park_id'
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='p_clid',
            billing_client_id='p_billing_client_id',
            billing_contract_id='p_billing_contract_id',
        )

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_driver_billing_info',
    )
    async def _get_driver_billing_info(park_id, actual_at):
        assert park_id == 'original_driver_park_id'
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='d_clid',
            billing_client_id='d_billing_client_id',
            billing_contract_id='d_billing_contract_id',
        )

    @mock_billing_orders('/v2/process/async')
    async def _process(request: http.Request):
        assert request.json == {
            'orders': [
                {
                    'kind': 'periodic_payment',
                    'topic': 'taxi/periodic_payment/clid/p_clid/1',
                    'external_ref': '3',
                    'event_at': '2020-01-04T03:00:00+03:00',
                    'data': {
                        'schema_version': 'v1',
                        'amount': '100',
                        'currency': 'RUB',
                        'transaction_type': 'PAYMENT',
                        'transfer_order_date': '2020-01-03T03:00:00+03:00',
                        'transfer_order_number': '1',
                        'external_driver': {
                            'clid': 'd_clid',
                            'billing_contract_id': 'd_billing_contract_id',
                            'billing_client_id': 'd_billing_client_id',
                            'db_id': 'original_driver_park_id',
                            'uuid': 'original_driver_id',
                        },
                        'driver': {'db_id': 'park_id', 'uuid': 'driver_id'},
                        'park': {
                            'clid': 'p_clid',
                            'billing_contract_id': 'p_billing_contract_id',
                            'billing_client_id': 'p_billing_client_id',
                            'db_id': 'park_id',
                        },
                    },
                },
                {
                    'kind': 'periodic_payment',
                    'topic': 'taxi/periodic_payment/clid/p_clid/park_id_2',
                    'external_ref': '3',
                    'event_at': '2020-01-04T03:00:00+03:00',
                    'data': {
                        'schema_version': 'v1',
                        'amount': '100',
                        'currency': 'RUB',
                        'transaction_type': 'PAYMENT',
                        'transfer_order_date': '2020-01-03T03:00:00+03:00',
                        'transfer_order_number': 'park_id_2',
                        'external_driver': {
                            'clid': 'd_clid',
                            'billing_contract_id': 'd_billing_contract_id',
                            'billing_client_id': 'd_billing_client_id',
                            'db_id': 'original_driver_park_id',
                            'uuid': 'original_driver_id',
                        },
                        'driver': {'db_id': 'park_id', 'uuid': 'driver_id'},
                        'park': {
                            'clid': 'p_clid',
                            'billing_contract_id': 'p_billing_contract_id',
                            'billing_client_id': 'p_billing_client_id',
                            'db_id': 'park_id',
                        },
                    },
                },
            ],
        }
        return {
            'orders': [
                {
                    'doc_id': 2,
                    'external_ref': '3',
                    'topic': 'taxi/periodic_payment/clid/p_clid/1',
                },
            ],
        }

    await run_cron.main(
        ['fleet_rent.crontasks.send_external_park_transactions', '-t', '0'],
    )

    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_park_transactions_log ORDER BY id',
    )
    upload_dts = [t['uploaded_at_tz'] for t in transactions]
    utc = datetime.timezone.utc
    assert upload_dts == [
        datetime.datetime(2020, 1, 1, tzinfo=utc),
        None,
        datetime.datetime(2020, 1, 4, tzinfo=utc),
        datetime.datetime(2020, 1, 1, tzinfo=utc),
        None,
        datetime.datetime(2020, 1, 4, tzinfo=utc),
    ]


@pytest.mark.parametrize('skip_because', ['currency', 'park', 'driver'])
@pytest.mark.now('2020-01-04T00:00:00')
@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
@pytest.mark.config(
    FLEET_RENT_EXTERNAL_PARK_TRANSACTIONS_PROCESSING={
        'send': {
            'is_enabled': True,
            'owner_park_service_id': 222,
            'driver_park_service_id': 124,
        },
    },
)
async def test_run_sept_skip_curr(
        mock_billing_orders,
        cron_context: context.Context,
        patch,
        skip_because,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        assert park_id == 'park_id'
        if skip_because == 'currency':
            return None
        return 'RUB'

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_owner_billing_info',
    )
    async def _get_owner_billing_info(park_id, actual_at):
        assert park_id == 'park_id'
        if skip_because == 'park':
            raise billing_info_comp.DataError()
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='p_clid',
            billing_client_id='p_billing_client_id',
            billing_contract_id='p_billing_contract_id',
        )

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_driver_billing_info',
    )
    async def _get_driver_billing_info(park_id, actual_at):
        assert park_id == 'original_driver_park_id'
        if skip_because == 'driver':
            raise billing_info_comp.DataError()
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='d_clid',
            billing_client_id='d_billing_client_id',
            billing_contract_id='d_billing_contract_id',
        )

    @mock_billing_orders('/v2/process/async')
    async def _process(request: http.Request):
        assert False

    await run_cron.main(
        ['fleet_rent.crontasks.send_external_park_transactions', '-t', '0'],
    )

    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_park_transactions_log ORDER BY id',
    )
    upload_dts = [t['uploaded_at_tz'] for t in transactions]
    utc = datetime.timezone.utc
    assert upload_dts == [
        datetime.datetime(2020, 1, 1, tzinfo=utc),
        None,
        None,
        datetime.datetime(2020, 1, 1, tzinfo=utc),
        None,
        None,
    ]


@pytest.mark.now('2020-01-04T00:00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['base.sql'],
    queries=[
        """UPDATE rent.records
        SET start_clid = 'old_clid'
        WHERE record_id IN ('record_id1', 'record_id2');""",
    ],
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
async def test_run_sept_do_not_send_clid(
        mock_billing_orders, cron_context: context.Context, patch,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        assert park_id == 'park_id'
        return 'RUB'

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_owner_billing_info',
    )
    async def _get_owner_billing_info(park_id, actual_at):
        assert park_id == 'park_id'
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='p_clid',
            billing_client_id='p_billing_client_id',
            billing_contract_id='p_billing_contract_id',
        )

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_driver_billing_info',
    )
    async def _get_driver_billing_info(park_id, actual_at):
        assert park_id == 'original_driver_park_id'
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='d_clid',
            billing_client_id='d_billing_client_id',
            billing_contract_id='d_billing_contract_id',
        )

    @mock_billing_orders('/v2/process/async')
    async def _process(request: http.Request):
        assert False

    await run_cron.main(
        ['fleet_rent.crontasks.send_external_park_transactions', '-t', '0'],
    )

    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_park_transactions_log ORDER BY id',
    )
    upload_dts = [t['uploaded_at_tz'] for t in transactions]
    utc = datetime.timezone.utc
    assert upload_dts == [
        datetime.datetime(2020, 1, 1, tzinfo=utc),
        None,
        None,
        datetime.datetime(2020, 1, 1, tzinfo=utc),
        None,
        None,
    ]
