# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name

import asyncio

import pytest

import hiring_plugins_tests.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_plugins_tests.generated.service.pytest_plugins']


@pytest.fixture
def wait_until_ready(mockserver, web_app_client, hiring_forms_mockserver):
    async def _wrapper():
        # handler = hiring_forms_mockserver
        attempts = 3
        for dummy_attempt_num in range(1, attempts + 1):
            response = await web_app_client.get('/ping')
            if response.status == 200:
                return
            await asyncio.sleep(0.01)
        raise RuntimeError('server not ready')

    return _wrapper


@pytest.fixture
def validate_form(web_app_client, wait_until_ready):
    async def _wrapper(fields, accept_language='ru'):
        await wait_until_ready()
        body = {'fields': fields}
        headers = {'Accept-Language': accept_language}
        response = await web_app_client.post(
            '/v1/validate-form', headers=headers, json=body,
        )
        return response

    return _wrapper
