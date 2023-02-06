import asyncio

import pytest
import uvloop


@pytest.fixture(autouse=True, scope='session')
def loop():
    """
    One event loop for all tests.
    """
    event_loop = uvloop.new_event_loop()
    asyncio.set_event_loop(event_loop)
    try:
        yield event_loop
    finally:
        event_loop.close()
