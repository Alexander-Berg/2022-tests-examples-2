# coding: utf8
# pylint: disable=protected-access,unused-import


import aiohttp
import pytest

from sibilla import test
from sibilla.test import event

import conftest  # noqa: F401


class ContextData:
    def __init__(self, loop):
        self.container = {}
        self.logger = event.EventCollector()
        self.session = aiohttp.ClientSession(loop=loop)
        self.tvm_client = None


@pytest.mark.asyncio
async def test_error_case(loop, patch_aiohttp_session, response_mock):
    # pylint: disable=unused-variable
    @patch_aiohttp_session('https://example.com', 'POST')
    def patch_request(method, url, headers, json, **kwargs):
        return response_mock(status=200, text='text')

    test_data = {
        'name': 'name',
        'query': [{'data': 'test'}],
        'result': {'status': 200, 'data': '@data'},
        'url': 'https://example.com',
    }
    test_mock = test.Test(ctx=ContextData(loop), **test_data)
    assert not await test_mock.exec()


@pytest.mark.asyncio
async def test_expected_behaviour(loop, patch_aiohttp_session, response_mock):
    # pylint: disable=unused-variable
    @patch_aiohttp_session('https://example.com', 'POST')
    def patch_request(method, url, headers, json, **kwargs):
        return response_mock(
            text='test', status=200, headers={'Content-Type': 'text'},
        )

    test_data = {
        'name': 'name',
        'query': [
            {
                'actual': {'data': 'test'},
                'expected': {'status': 200, 'data': '@data'},
            },
        ],
        'url': 'https://example.com',
    }
    test_mock = test.Test(ctx=ContextData(loop), **test_data)
    assert await test_mock.exec()


@pytest.mark.asyncio
async def test_default_retry_policy(
        loop, patch_aiohttp_session, response_mock,
):
    called = 0

    # pylint: disable=unused-variable
    @patch_aiohttp_session('https://example.com', 'POST')
    def patch_request(method, url, headers, json, **kwargs):
        nonlocal called
        called += 1
        return response_mock(
            text='test', status=500, headers={'Content-Type': 'text'},
        )

    test_data = {
        'name': 'name',
        'query': [
            {
                'actual': {'data': 'test'},
                'expected': {'status': 200, 'data': '@data'},
            },
        ],
        'url': 'https://example.com',
    }
    test_mock = test.Test(ctx=ContextData(loop), **test_data)
    assert not await test_mock.exec()
    assert called == 3
