# pylint: disable=unused-variable
from aiohttp_xmlrpc import client
import pytest

from taxi import settings
from taxi.clients import billing_v2 as billing

from taxi_billing_replication import cron_run


@pytest.mark.config(
    BILLING_REPLICATION_BALANCES_CHUNK_SETTINGS={
        'max_excluding_attempt_count': 3,
        'excluding_attempt_delay': 0,
    },
)
@pytest.mark.pgsql('billing_replication', files=['balances_queue_v2.sql'])
async def test_update_with_failed_exclusion(
        billing_replictaion_cron_app,
        patch,
        patch_aiohttp_session,
        response_mock,
        fixed_secdist,
):
    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _push_data(data, handler=None, log_extra=None):
        pass

    @patch_aiohttp_session(settings.Settings.BALANCE_XMLRPC_API_HOST)
    def get_partner_balances(method, url, **kwargs):
        data = kwargs['data']
        if b'123456' in data:
            raise billing.BillingError from client.exceptions.XMLRPCError(
                '<contract-id>123456</contract-id>',
            )
        elif b'654321' in data:
            raise billing.BillingError from client.exceptions.XMLRPCError(
                '<contract-id>654321</contract-id>',
            )
        else:
            return response_mock(
                read=(
                    b'<?xml version=\'1.0\'?>'
                    b'<methodResponse><params><param><value><array>'
                    b'<data><value><struct>'
                    b'<member>'
                    b'<name>ContractID</name>'
                    b'<value><int>111111</int></value>'
                    b'</member>'
                    b'</struct></value></data>'
                    b'</array></value></param></params></methodResponse>'
                ),
            )

    module = 'taxi_billing_replication.stuff.parks.replicate_balances_v2'
    await cron_run.run_replication_task([module, '-t', '0'])
    assert len(get_partner_balances.calls) == 3

    pool = billing_replictaion_cron_app.pg_connection_pool
    async with pool.acquire() as conn:
        balances_v2_rows = await conn.fetch(
            'SELECT * FROM parks.balances_v2 ORDER BY revision ASC;',
        )
        actual_balances_v2_rows = [
            (
                row['ContractID'],
                row['service_id'],
                row['Balance'],
                row['revision'],
            )
            for row in balances_v2_rows
        ]
        assert actual_balances_v2_rows == [(111111, 111, None, 1)]
