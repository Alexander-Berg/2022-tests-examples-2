import aiohttp
import pytest


@pytest.mark.asyncio
async def test_dispose_should_decrement_num_cups(coffee_cups_client: aiohttp.ClientSession):
    async with coffee_cups_client.get('/cups') as resp:
        initial_cups = await resp.json()

    async with coffee_cups_client.post('/cups/dispose') as resp:
        assert resp.status == 204

    async with coffee_cups_client.get('/cups') as resp:
        final_cups = await resp.json()

    assert initial_cups.get('num_cups') == final_cups.get('num_cups') + 1
