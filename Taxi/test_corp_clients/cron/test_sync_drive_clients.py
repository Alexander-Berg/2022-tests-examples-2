import pytest

from corp_clients.generated.cron import run_cron


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.config(
    CORP_DRIVE_SYNC_CONTRACTS_ENABLED=True,
    CORP_SYNC_DRIVE_ORDERS_CLIENTS_TO_SKIP=['client_to_ignore'],
)
async def test_sync_drive_clients(
        db, mockserver, load_json, patch, configs_mock, _translations_mock,
):
    @mockserver.json_handler(
        '/taxi-corp-integration/v1/clients/can_order/drive',
    )
    async def _can_order(request):
        return mockserver.make_response(
            json=load_json('corp_int_api_response.json'),
        )

    @patch('taxi.clients.drive.DriveClient.activate')
    async def _activate(accounts, is_active, **kwargs):
        activate_requests = load_json('activate_requests.json')
        expected = activate_requests[str(int(is_active))]
        assert sorted(accounts) == sorted(expected)

    @patch('taxi.clients.drive.DriveClient.accounts_by_account_name')
    async def _accounts_by_account_name(*args, **kwargs):
        return load_json('drive_accounts.json')

    module = 'corp_clients.crontasks.sync_drive_clients'
    await run_cron.main([module, '-t', '0'])
    assert len(_activate.calls) == 2


@pytest.fixture(autouse=True)
def _translations_mock(patch):
    @patch('taxi.translations.Translations.refresh_cache')
    async def _refresh_cache(*args, **kwargs):
        pass
