import pytest


@pytest.fixture(name='services_retrieve_mock')
def _services_retrieve_mock(mock_clownductor, clown_services):
    @mock_clownductor('/v1/services/')
    def _services(request):
        if 'project_id' in request.query:
            project_id = int(request.query['project_id'])
            return [
                service
                for service in clown_services
                if service['project_id'] == project_id
            ]
        if 'service_id' in request.query:
            service_id = int(request.query['service_id'])
            return [
                service
                for service in clown_services
                if service['id'] == service_id
            ]
        return clown_services

    return _services
