# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
from typing import List

import pytest

import supportai_api.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['supportai_api.generated.service.pytest_plugins']


@pytest.fixture(name='clickhouse_query_storage')
def _clickhouse_query_storage() -> List[str]:
    return []


@pytest.fixture(autouse=True)
def mock_projects(mockserver):
    @mockserver.json_handler(
        '/supportai-projects/supportai-projects/v1/integrations-data',
    )
    async def _dummy_integrations_data(request):
        return mockserver.make_response(
            status=200,
            json={
                'integrations': {'current_ids': [], 'data': []},
                'actions': {'current_ids': [], 'data': []},
                'callbacks': {'current_ids': [], 'data': []},
            },
        )

    @mockserver.json_handler(
        '/supportai-projects/supportai-projects/v1/secret-data',
    )
    async def _dummy_integrations_secrets(request):
        return mockserver.make_response(
            status=200,
            json={
                'project_integrations': [],
                'api_keys': [],
                'allowed_ips': [],
            },
        )


@pytest.fixture(autouse=True)
def mock_clickhouse(
        mock_projects,
        web_context,
        mock_clickhouse_host,
        response_mock,
        clickhouse_query_storage,
):
    def response(*args, **kwargs):
        query = kwargs.get('data')

        if query is not None:
            clickhouse_query_storage.append(query)

        return response_mock(
            json={
                'statistics': {
                    'elapsed': 0.5,
                    'rows_read': 0,
                    'bytes_read': 10,
                },
                'meta': [],
                'data': [],
                'rows': 0,
            },
        )

    host_list = web_context.clickhouse._clickhouse_policy._host_list  # noqa

    mock_clickhouse_host(
        clickhouse_response=response, request_url=host_list[0],
    )
