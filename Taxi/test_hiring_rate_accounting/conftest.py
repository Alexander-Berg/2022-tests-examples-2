# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import hiring_rate_accounting.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from hiring_rate_accounting.generated.cron import run_cron  # noqa: I100

pytest_plugins = ['hiring_rate_accounting.generated.service.pytest_plugins']


@pytest.fixture
def update(web_app_client):
    async def _wrapper(query: dict):
        response = await web_app_client.post(
            '/v1/statistics/update', json=query,
        )
        response_body = await response.json()
        return response, response_body

    return _wrapper


@pytest.fixture
def get_statistics(web_app_client):
    async def _wrapper(query: dict):
        response = await web_app_client.post(
            '/v1/statistics/calculate', json=query,
        )
        assert response.status == 200
        body = await response.json()
        return body

    return _wrapper


@pytest.fixture
def run_remove_old_records():
    async def _run_cron():
        argv = [
            'hiring_rate_accounting.crontasks.remove_old_records',
            '-t',
            '0',
        ]
        await run_cron.main(argv)

    return _run_cron
