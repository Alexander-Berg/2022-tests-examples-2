# coding: utf8

import pytest

from sibilla.test import _base
from sibilla.test import request
from sibilla.utils import decorators


class ContextData:
    """Empty context"""


@pytest.mark.asyncio
async def test_no_wait():
    class FalseTest(_base.BaseTest):
        @decorators.retry
        async def get_result(self, headers: dict, query_data: request.Query):
            return False

    context = ContextData()
    test_mock = FalseTest(name='test', wait={}, ctx=context)
    exec_result = await test_mock.get_result(
        headers={}, query_data=request.Query(),
    )
    assert not exec_result


@pytest.mark.asyncio
async def test_no_retry():
    called = 0

    class PositiveTest(_base.BaseTest):
        @decorators.retry
        async def get_result(self, headers: dict, query_data: request.Query):
            nonlocal called
            called += 1
            return True

    context = ContextData()
    test_mock = PositiveTest(name='test', wait={}, ctx=context)
    exec_result = await test_mock.get_result(
        headers={}, query_data=request.Query(),
    )
    assert called == 1
    assert exec_result


@pytest.mark.asyncio
async def test_retry():
    called = 0

    class FalseTest(_base.BaseTest):
        @decorators.retry
        async def get_result(self, headers: dict, query_data: request.Query):
            nonlocal called
            called += 1
            return False

    context = ContextData()
    test_mock = FalseTest(name='test', wait={}, ctx=context)
    exec_result = await test_mock.get_result(
        headers={}, query_data=request.Query(),
    )
    assert called == 3
    assert not exec_result


@pytest.mark.asyncio
async def test_retry_twice():
    called = 0

    class FalseTest(_base.BaseTest):
        @decorators.retry
        async def get_result(self, headers: dict, query_data: request.Query):
            nonlocal called
            called += 1
            return False

    context = ContextData()
    test_mock = FalseTest(name='test', wait={'attempts': 2}, ctx=context)
    exec_result = await test_mock.get_result(
        headers={}, query_data=request.Query(),
    )
    assert called == 2
    assert not exec_result
