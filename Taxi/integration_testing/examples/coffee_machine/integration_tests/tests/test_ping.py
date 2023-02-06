import aiohttp
import pytest


@pytest.mark.asyncio
async def test_ping(coffee_machine_client: aiohttp.ClientSession):
    async with coffee_machine_client.get('/ping') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert text == 'OK'
