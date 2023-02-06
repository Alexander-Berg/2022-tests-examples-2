# pylint: disable=redefined-outer-name,unused-variable,raising-bad-type
import pytest

from taxi.billing.pgstorage import postgres


@pytest.fixture
def patch_create_pool(patch):
    def _patch(user, replica_suffix):
        i = 0

        @patch('asyncpg.create_pool')
        async def create_pool(*args, **kwargs):
            assert kwargs.get('user') == user
            nonlocal i
            i += 1
            # hack, skip master create which are odd
            if replica_suffix and i % 2 == 0:
                assert kwargs['dsn'].endswith(replica_suffix)

    return _patch


@pytest.mark.parametrize('user', [None, 'ro_user'])
@pytest.mark.parametrize('replica_suffix', [None, '_sync_ro_replica'])
async def test_acreate_user_replica(patch_create_pool, user, replica_suffix):
    patch_create_pool(user=user, replica_suffix=replica_suffix)

    await postgres.Cluster.create(
        dsn='host=postgres://host dbname=n1 user=u1 password=p1 port=6432',
        shard_info=postgres.shard_info.ShardInfo(pg_shard_id=0),
        ro_sync_suffix=replica_suffix,
        user=user,
    )


@pytest.fixture
def patch_create_pool_kwargs(patch):
    def _patch(kwargs_expected):
        @patch('asyncpg.create_pool')
        async def create_pool(*args, **kwargs):
            nonlocal kwargs_expected
            for k, expected in kwargs_expected.items():
                assert kwargs.get(k) == expected

    return _patch


@pytest.mark.parametrize('user', [None, 'ro_user'])
@pytest.mark.parametrize(
    'min_size, max_size, statement_cache_size', [(0, 4, 120), (1, 100, 1024)],
)
async def test_acreate_kwargs(
        patch_create_pool_kwargs,
        min_size,
        max_size,
        statement_cache_size,
        user,
):
    patch_create_pool_kwargs(
        {
            'min_size': min_size,
            'max_size': max_size,
            'statement_cache_size': statement_cache_size,
            'user': user,
        },
    )

    await postgres.Cluster.create(
        dsn='host=postgres://host dbname=n1 user=u1 password=p1 port=6432',
        shard_info=postgres.shard_info.ShardInfo(pg_shard_id=0),
        ro_sync_suffix='',
        user=user,
        min_size=min_size,
        max_size=max_size,
        statement_cache_size=statement_cache_size,
    )
