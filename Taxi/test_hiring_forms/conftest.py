# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name

import pytest

import hiring_forms.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_forms.generated.service.pytest_plugins']


@pytest.fixture
def upsert_form(web_app_client):
    async def _wrapper(data: dict):
        response = await web_app_client.post('/v1/form', json=data)
        assert response.status == 200

    return _wrapper


@pytest.fixture
def get_form(web_app_client):
    async def _wrapper(name: str) -> dict:
        response = await web_app_client.get('/v1/form', params={'name': name})
        assert response.status == 200
        response_body = await response.json()
        return response_body

    return _wrapper
