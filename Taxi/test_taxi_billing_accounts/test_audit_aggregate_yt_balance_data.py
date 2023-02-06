import pytest

from taxi_billing_accounts.audit import actions
from test_taxi_billing_accounts import conftest as tst


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_cron_usage(accounts_audit_cron_app, patch):
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        return tst.MockedRequest(
            tst.MockedResult(tst.YT_STATUS_COMPLETED, [tst.MockedTable([])]),
        )

    task = actions.AggregateYTBalanceData(context=accounts_audit_cron_app)
    await task.aggregate()
    assert len(query.calls) == 1
