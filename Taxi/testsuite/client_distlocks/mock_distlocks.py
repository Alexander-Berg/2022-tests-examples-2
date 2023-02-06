# pylint: disable=unused-variable
import pytest


@pytest.fixture
def distlocks_mockserver(mockserver):
    # periodic tasks of distlocks service use it as external service
    @mockserver.json_handler('/distlocks/v1/locks/acquire/')
    def acquire(request):
        data = request.json
        return {
            'status': 'acquired',
            'namespace': data['namespace'],
            'name': data['name'],
            'owner': data['owner'],
        }

    @mockserver.json_handler('/distlocks/v1/locks/release/')
    def release(request):
        return {}
