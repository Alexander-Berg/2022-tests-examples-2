import asyncio

import pytest

from eats_order_integration.internal import utils


async def test_retry():
    @utils.retry(max_retries=2, exception=Exception, delay=0.1)
    async def filing_func(fails, uuid):
        if not hasattr(filing_func, 'counter') or filing_func.uuid != uuid:
            filing_func.counter = 0
            filing_func.uuid = uuid
        if filing_func.counter < fails:
            filing_func.counter += 1
            raise Exception('Test')

    await filing_func(1, 'call_1')
    await filing_func(1, 'call_2')
    with pytest.raises(Exception, match='Test'):
        await filing_func(2, 'call_3')


async def test_retry_delay_func():
    @utils.retry(
        max_retries=2, exception=Exception, delay=lambda: asyncio.sleep(0.1),
    )
    async def filing_func(fails, uuid):
        if not hasattr(filing_func, 'counter') or filing_func.uuid != uuid:
            filing_func.counter = 0
            filing_func.uuid = uuid
        if filing_func.counter < fails:
            filing_func.counter += 1
            raise Exception('Test')

    await filing_func(1, 'call_1')
    await filing_func(1, 'call_2')
    with pytest.raises(Exception, match='Test'):
        await filing_func(2, 'call_3')


async def test_retry_correct_exc():
    @utils.retry(max_retries=2, exception=ZeroDivisionError, delay=0.1)
    async def filing_func(fails, uuid):
        if not hasattr(filing_func, 'counter') or filing_func.uuid != uuid:
            filing_func.counter = 0
            filing_func.uuid = uuid
        if filing_func.counter < fails:
            filing_func.counter += 1
            raise ZeroDivisionError('Test')

    await filing_func(1, 'call_1')
    await filing_func(1, 'call_2')
    with pytest.raises(ZeroDivisionError, match='Test'):
        await filing_func(2, 'call_3')


async def test_retry_wrong_exc():
    @utils.retry(max_retries=2, exception=ZeroDivisionError, delay=0.1)
    async def filing_func(fails, uuid):
        if not hasattr(filing_func, 'counter') or filing_func.uuid != uuid:
            filing_func.counter = 0
            filing_func.uuid = uuid
        if filing_func.counter < fails:
            filing_func.counter += 1
            raise Exception('Test')

    with pytest.raises(Exception, match='Test'):
        await filing_func(1, 'call_1')
    with pytest.raises(Exception, match='Test'):
        await filing_func(2, 'call_2')
