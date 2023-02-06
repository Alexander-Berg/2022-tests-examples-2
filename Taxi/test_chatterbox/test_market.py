import pytest

from chatterbox.components import market
from test_chatterbox import plugins as conftest


@pytest.mark.config(
    CHATTERBOX_MARKET_MOCK={
        'order_returns': [
            {'comment': 'test_market_mocked_response', 'id': 1, 'orderId': 10},
        ],
        'orders': [{'id': 2, 'status': 'mock_status'}],
    },
)
async def test_mocked_checkouter_client(cbox: conftest.CboxWrap):
    client = market.CachingCheckouterClient(
        cbox.app.clients.market_checkouter, cbox.app.config,
    )
    with market.checkouter_cache():
        order_return = await client.get_order_return(1)
        assert order_return.comment == 'test_market_mocked_response'

        order = await client.get_order(2)
        assert order.status == 'mock_status'


async def test_no_cache_init(cbox: conftest.CboxWrap):
    client = market.CachingCheckouterClient(
        cbox.app.clients.market_checkouter, cbox.app.config,
    )
    try:
        await client.get_order(1)
    except RuntimeError as err:
        assert 'Miss cache init' in str(err)


async def test_caching_client(cbox: conftest.CboxWrap, mock_checkouter_order):
    client = market.CachingCheckouterClient(
        cbox.app.clients.market_checkouter, cbox.app.config,
    )

    async def call():
        assert (await client.get_order(1)).status == 'DELIVERY'

    with market.checkouter_cache():
        await call()
        await call()
        with market.checkouter_cache():
            await call()
    assert mock_checkouter_order.times_called == 1

    mock_checkouter_order.flush()
    with market.checkouter_cache():
        await call()
        await call()
        with market.checkouter_cache(reentrant=False):
            await call()
    assert mock_checkouter_order.times_called == 2
