import pytest

from taxi.integration_testing.framework import pgsql


@pytest.mark.asyncio
async def test_ping(postgres: pgsql.TestPostgres):
    postgres.create_db('test')
    postgres.drop_db('test')
