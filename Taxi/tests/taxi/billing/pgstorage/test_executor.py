# pylint: disable=redefined-outer-name,no-self-use,unused-variable
import pytest

from taxi.billing import pgstorage


async def test_create():
    storage = Storage()
    with pytest.raises(AssertionError):
        await pgstorage.Executor.create(storage)
    await pgstorage.Executor.create(storage, offset=0, limit=10)
    await pgstorage.Executor.create(storage, shard_ids=[0, 1, 2])


async def test_scattered_fetch():
    storage = Storage(rows=[('1', '2', '3')])
    executor = await pgstorage.Executor.create(storage, shard_ids=[0, 1])
    rows = await executor.fetch('SELECT * FROM table', log_extra={})
    assert rows == [('1', '2', '3')]


async def test_sequential_fetch(patch_query_pools):
    rows = [('1', '2', '3'), ('4', '5', '6'), ('7', '8', '9')]
    pools = [Pool(rows)]
    patch_query_pools(pools)
    storage = Storage(rows=rows, all_vshards=[0, 1, 2])
    executor = await pgstorage.Executor.create(storage, offset=0, limit=3)
    returned_rows = await executor.fetch('SELECT * FROM table', log_extra={})
    assert rows == returned_rows


async def test_scattered_execute(patch_query_pools):
    storage = Storage(rows=[('1', '2', '3')])
    executor = await pgstorage.Executor.create(storage, shard_ids=[0, 1])
    rows = await executor.execute('SELECT * FROM table', log_extra={})
    assert rows == [('1', '2', '3')]
    result = await executor.execute_command(
        'SELECT * FROM table', log_extra={},
    )
    assert result is None


async def test_sequential_execute(patch_query_pools):
    storage = Storage(rows=[], all_vshards=[0, 1, 2])
    executor = await pgstorage.Executor.create(storage, offset=0, limit=3)
    with pytest.raises(NotImplementedError):
        await executor.execute('SELECT * FROM table', log_extra={})
    with pytest.raises(NotImplementedError):
        await executor.execute_command('SELECT * FROM table', log_extra={})


@pytest.fixture
def patch_query_pools(patch):
    """
    Because executor uses Storage.query_pools directly
    """

    def patch_pools(pools):
        @patch('taxi.billing.pgstorage.Storage.query_pools')
        async def query_pools(self, shard_ids):
            return pools

    return patch_pools


class Storage:
    def __init__(self, rows=None, all_vshards=None):
        pool = Pool(rows)
        self._query_pools = [pool]
        self._transaction_pools = [pool]
        self._all_vshards = all_vshards

    async def query_pools(self, shard_ids):
        return self._query_pools

    async def transaction_pools(self, shard_ids):
        return self._transaction_pools

    def all_vshards(self):
        return self._all_vshards

    def vshard_schema(self, vshard_id):
        return 'ba_' + f'{vshard_id:02x}'


class Pool:
    def __init__(self, rows=None):
        self.rows = rows or []

    async def fetch(self, query, *args, log_extra: dict):
        return self.rows

    async def execute(self, query, *args, log_extra: dict):
        return self.rows
