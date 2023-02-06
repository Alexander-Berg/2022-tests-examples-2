# pylint: disable=protected-access
# pylint: disable=unused-variable
from aiohttp_xmlrpc import client
import pytest

from taxi import settings
from taxi.clients import billing_v2 as billing

from taxi_billing_replication.monrun.checks import failed_balances


@pytest.mark.parametrize('is_check_ok', [True, False])
@pytest.mark.pgsql('billing_replication', files=['data.sql'])
async def test_failed_balances(
        response_mock,
        patch_aiohttp_session,
        billing_replictaion_cron_app,
        is_check_ok,
):
    @patch_aiohttp_session(settings.Settings.BALANCE_XMLRPC_API_HOST)
    def get_partner_balances(method, url, **kwargs):
        data = kwargs['data']
        assert b'67890' in data
        if is_check_ok:
            # billing still raises exception for the contract - it means ok
            raise billing.BillingError from client.exceptions.XMLRPCError(
                '<contract-id>67890</contract-id>',
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

    result = await failed_balances._check(billing_replictaion_cron_app, None)
    if is_check_ok:
        assert result == '0; OK: no contract ids to report'
    else:
        assert result == (
            '1; WARN: '
            'balances of contracts 67890 could not be updated; '
            'balances of contracts 67890 (111) could not be updated'
        )
