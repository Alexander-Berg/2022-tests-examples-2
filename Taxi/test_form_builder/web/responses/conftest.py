# pylint: disable=invalid-name
import pytest


@pytest.fixture
def get_list(web_app_client):
    async def _do_it(params, expected_data):
        response = await web_app_client.get(
            '/v1/builder/responses/list/', params=params,
        )
        assert response.status == 200
        data = await response.json()
        if expected_data is not None:
            assert data == expected_data
        return True

    return _do_it


@pytest.fixture
def get_one(web_app_client):
    async def _do_it(id_, expected_status, expected_data):
        endpoint = '/v1/builder/responses/'
        params = {'id': id_}
        response = await web_app_client.get(endpoint, params=params)
        assert response.status == expected_status
        data = await response.json()
        if expected_data is not None:
            assert data == expected_data
        return True

    return _do_it
