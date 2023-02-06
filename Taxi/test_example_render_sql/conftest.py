# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import example_render_sql.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['example_render_sql.generated.service.pytest_plugins']


@pytest.fixture
def create_user(web_app_client):
    async def _wrapper(login: str, name: str) -> str:
        data = {'login': login, 'name': name}
        response = await web_app_client.post('/v1/user', json=data)
        assert response.status == 200
        response_body = await response.json()
        return response_body['revision']

    return _wrapper
