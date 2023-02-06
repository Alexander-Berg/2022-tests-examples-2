import pytest

from taxi.billing import pgstorage


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_storage_create(billing_accounts_storage: pgstorage.Storage):
    storage = billing_accounts_storage

    assert storage is not None
    assert storage.all_vshards()

    for vid in storage.all_vshards():
        executor = await pgstorage.Executor.create(storage, vid)
        schema = storage.vshard_schema(vid)
        rows = await executor.fetch(
            f'SELECT count(*) FROM {schema}.account', log_extra={},
        )
        assert rows

        rows = await executor.execute(
            f'SELECT count(*) FROM {schema}.account', log_extra={},
        )
        assert rows
