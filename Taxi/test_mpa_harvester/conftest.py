import pytest

# pylint: disable=redefined-outer-name
import mpa_harvester.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['mpa_harvester.generated.service.pytest_plugins']


@pytest.fixture
def clownductor_mocks(mock_clownductor, load_json):
    @mock_clownductor('/api/projects')
    async def _get_projects():
        return load_json('clownductor.json')['projects']

    @mock_clownductor('/api/services')
    async def _get_services(request):
        assert 'project_id' in request.query
        return [
            service
            for service in load_json('clownductor.json')['services']
            if service['project_id'] == int(request.query['project_id'])
        ]
