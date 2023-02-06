from typing import Optional

import pytest


@pytest.fixture(name='debug_app')
def _debug_app(web_app_client):
    return web_app_client


@pytest.fixture(name='requests_app')
def _requests_app(taxi_clowny_roles_web):
    return taxi_clowny_roles_web


@pytest.fixture(name='requests_get')
def _requests_get(requests_app):
    async def _wrapper(path: str, params: Optional[dict] = None):
        return await requests_app.get(path, params=params)

    return _wrapper


@pytest.fixture(name='requests_post')
def _requests_post(requests_app):
    async def _wrapper(path: str, body: dict, params: Optional[dict] = None):
        return await requests_app.post(path, json=body, params=params)

    return _wrapper
