import aiohttp
import pytest


@pytest.mark.asyncio
async def test_cups_dispose(coffee_machine_client: aiohttp.ClientSession):
    async with coffee_machine_client.post('/cups/dispose') as resp:
        assert resp.status == 204
