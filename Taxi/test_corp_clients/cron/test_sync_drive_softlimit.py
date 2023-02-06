from corp_clients.generated.cron import run_cron


async def test_main(db, patch, load_json):
    @patch('taxi.clients.drive.DriveClient.accounts_by_account_name')
    async def _accounts_by_account_name(*args, **kwargs):
        return load_json('drive_accounts.json')

    @patch('taxi.clients.drive.DriveClient.update_limits')
    async def _update_limits(*args, **kwargs):
        return

    await run_cron.main(
        ['corp_clients.crontasks.sync_drive_softlimit', '-t', '0'],
    )

    assert not _update_limits.calls
    # assert len(_update_limits.calls) == 2
