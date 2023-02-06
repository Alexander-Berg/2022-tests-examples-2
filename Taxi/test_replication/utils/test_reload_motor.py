# pylint: disable=protected-access
from concurrent import futures

from motor.frameworks import asyncio as motor_asyncio_framework
import pytest


@pytest.mark.nofilldb()
def test_has_executor():
    assert hasattr(motor_asyncio_framework, '_EXECUTOR')
    assert isinstance(
        motor_asyncio_framework._EXECUTOR, futures.ThreadPoolExecutor,
    )
